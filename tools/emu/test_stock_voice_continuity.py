"""Comparer le PCM des six machines natives : PUNCH ON, filtres/LFO ajoutes inactifs."""
from pathlib import Path
import sys,json,struct,hashlib,inspect,gc,argparse
import numpy as np
R=Path(__file__).resolve().parents[2];T=R/'tools'
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--expect-regression',action='store_true');p.add_argument('--build',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args();W=args.output.parent;W.mkdir(parents=True,exist_ok=True)
sys.path[:0]=[str(R.parent/'boot-check-deps'),str(T/'emu'),str(T)]
import boot_candidate
DEV=Path('H:/CREATURE-source/retrosyn-integration-step-rec-solo')
sys.path.extend([str(DEV/'tools/emu'),str(DEV/'tools')])
boot_candidate.ROOT=DEV
real_boot,real_load=boot_candidate.boot,boot_candidate.load
current={}
def mapped(path):
 path=Path(path)
 return current['path'] if path.name==current.get('source_name') else path
def cached_boot(path):
 saved=boot_candidate.ROOT
 try:boot_candidate.ROOT=W/'history-cache';return real_boot(mapped(path))
 finally:boot_candidate.ROOT=saved
boot_candidate.boot=cached_boot;boot_candidate.load=lambda p:real_load(mapped(p))
import test_wizard_playback as tw
from test_chord_cpu import configure
from unicorn import m68k_const as C
import mcengine as E,emac
source=inspect.getsource(tw.fixtures)
source=source.replace("m=json.loads((ROOT/'output/firmware'/(stem+'.json')).read_text())","m=history_metadata()")
source=source.replace("folder=ROOT/'tmp/emu-runtime-code'",'folder=pathlib.Path('+repr(str(W/'history-code'))+')')
tw.history_metadata=lambda:current['meta'];exec(compile(source,'history-fixtures','exec'),tw.__dict__)

meta=json.loads((args.build/'BUILD.json').read_text(encoding='utf-8'));path=next(args.build.glob('*.syx'));stem='staging/all-features-polivoks-cpu-trim-test-v215';current.update(path=path,source_name=Path(stem).name+'.syx',meta=meta)
e=tw.fixtures(False,127,0,[stem],native_chordkeys=False,audit_count=False)[0];configure(e,False)
fx=meta['per_track_fx'];sy=fx['symbols'];f=W/'env-module.bin';f.write_bytes(e.uc.mem_read(fx['code'],fx['code_bytes']));e.emac.install(emac.disasm(str(f),fx['code'],fx['code'],fx['code']+fx['code_bytes']))
e.emac.fast[0x400a82cc]=lambda:None;e.emac.next[0x400a82cc]=sy['dry_osc']

patched='acid_arp' in meta or meta.get('acid_articulation',{}).get('arp_retrigger',False)
if patched:
 art=meta.get('acid_arp',meta.get('acid_articulation'));
 if 'acid_articulation' in meta:sy=dict(sy,trk=art['symbols']['trk'])
 f=W/'arp-module.bin';f.write_bytes(e.uc.mem_read(art['code'],art['code_bytes']));e.emac.install(emac.disasm(str(f),art['code'],art['code'],art['code']+art['code_bytes']))

f=W/'native-extra.bin';f.write_bytes(e.uc.mem_read(0x468c2000,0x1000));e.emac.install(emac.disasm(str(f),0x468c2000,0x468c2000,0x468c3000))
if meta.get('stock_voice_protection',{}).get('enabled'):
 def native_continue(u,pc,size,data):
  sp=u.reg_read(C.UC_M68K_REG_A7);u.reg_write(C.UC_M68K_REG_PC,int.from_bytes(u.mem_read(sp,4),'big'));u.reg_write(C.UC_M68K_REG_A7,sp+4)
 from unicorn import UC_HOOK_CODE
 e.uc.hook_add(UC_HOOK_CODE,native_continue,begin=0x40000542,end=0x40000542);e.uc.reg_write(C.UC_M68K_REG_SR,0x2700);e.uc.reg_write(C.UC_M68K_REG_A0,E.PARAMS+0x8000);e.call(meta['activity_masks']['symbols']['am_boot_finish'])
 assert e.uc.mem_read(0x8000e8b6,1)==b'\x64'
stock=tw.engine(real_load(DEV/'firmware/model-cycles_OS1.13.syx'))

for eng in (stock,e):
 for t in range(6):
  eng.set(t,machine=4 if t==4 else 0,note=48,pitch=64,finetune=64,color=40,shape=38,sweep=52,contour=42,decay=127,punch=1,gate=1)
  eng.uc.mem_write(E.PARAMS+14+66*t+46,struct.pack('>3H',0,32512,0));eng.uc.mem_write(0x40fe4cdc+2*t,struct.pack('>H',127<<8))
 eng.solo(4)
first=None;peak=0;difference=0
for block in range(700):
 if block in (100,550):
  for eng in (stock,e):
   for at in (0x40a78c08,0x40a78be8,0x40a78bd0,0x40a78bb8,0x40a78b9c,0x40a78b80):eng.uc.mem_write(at+16,struct.pack('>I',0 if block==100 else 0x20000000 if at==0x40a78c08 else 0))
 outputs=[]
 for eng in (stock,e):eng.uc.reg_write(C.UC_M68K_REG_SR,0x2700);outputs.append(eng.block(16 if block==0 else 0,16 if block==650 else 0)[4])
 delta=int(np.max(abs(outputs[0].astype(np.int64)-outputs[1].astype(np.int64))));difference=max(difference,delta)
 if delta and first is None:first=block
 peak=max(peak,int(np.max(abs(outputs[0].astype(np.int64)))))
 if block%100==99:print('CONTINUITY',block+1,'first difference',first,flush=True)
assert peak>100000
if args.expect_regression:assert first is not None,'regression not reproduced'
else:assert first is None,(first,difference)
print('PASS', 'old stock continuity regression reproduced' if args.expect_regression else '700 blocks match native stock TONE through mixer mute/unmute and note release',flush=True)
args.output.write_text(json.dumps(dict(blocks=700,first_difference=first,max_difference=difference,premix_continuity=True,hardware_tested=False),indent=2)+'\n')
