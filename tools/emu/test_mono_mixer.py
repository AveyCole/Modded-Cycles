"""Preuve native des reglages ACID, navigation et sauvegarde globale."""
from pathlib import Path
import argparse,inspect,json,struct,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/emu')]
p=argparse.ArgumentParser();p.add_argument('--build',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
import boot_candidate as bc
import test_fx_menu_control as fx
from test_seq_gen_menu import EVENT
from unicorn import m68k_const as C
m=json.loads((a.build/'BUILD.json').read_text(encoding='utf-8'));s=m['activity_masks']['symbols'];al=m['direct_jump']['aliases']
bc.ROOT=a.output.parent/'ui-cache';fx.metadata=m;fx.boot=lambda path:bc.boot(next(a.build.glob('*.syx')))
src=inspect.getsource(fx.fixture).replace("m=json.loads((ROOT/'output/firmware'/(stem+'.json')).read_text())",'m=metadata');exec(src,fx.__dict__)
def fixture():
 r,_,h,log,files,key,turn,data,bind=fx.fixture('unused');bind(al['gc_input_quiet'],lambda a:1);bind(0x400423e4,lambda a:0);return r,files,bind


import random,subprocess,emac
from emac_state import ExtendedEMAC
cross='H:/CREATURE-source/retrosyn-integration/build/m68k-toolchain/pkg/bin/m68k-elf-';original=subprocess.run
def cross_run(cmd,*args,**kw):
 if isinstance(cmd,list) and cmd[0]=='m68k-linux-gnu-objdump':cmd=[cross+'objdump.exe',*cmd[1:]]
 return original(cmd,*args,**kw)
subprocess.run=cross_run
pairs=[]
stock=bc.load(Path('H:/CREATURE-source/retrosyn-integration-step-rec-solo/firmware/model-cycles_OS1.13.syx'))
f=a.output.parent/'mono-native6.bin';f.write_bytes(stock[0x40056716-0x40000400:0x400567ba-0x40000400])
for folder in (a.baseline,a.build):
 meta=json.loads((folder/'BUILD.json').read_text(encoding='utf-8'));fx.metadata=meta;path=next(folder.glob('*.syx'));fx.boot=lambda p,path=path:bc.boot(path)
 r,files,bind=fixture();r.u.mem_map(0x80000000,0x20000)
 for off,at,n in ((0,0x80001c5c,0x5858),(0x5858,0x8000cac0,0x2020)):r.u.mem_write(at,bytes(r.u.mem_read(0x46700000+off,n)))
 bind(0x40000542,lambda args:0);r.u.reg_write(C.UC_M68K_REG_A0,0x931b0000);r.call(meta['activity_masks']['symbols']['am_boot_finish'])
 sy=meta['per_track_fx']['symbols'];bind(sy['mf_sync_audio'],lambda args:0)
 mac=ExtendedEMAC(r.u);mac.install(emac.disasm(str(f),0x40056716,0x40056716,0x400567ba));pairs.append((r,meta,mac))
rng=random.Random(272);cases=0
for mode in ('same','pan','ramp','stereo','custom','input','output'):
 for trial in range(16):
  samples=struct.pack('>192i',*[rng.randrange(-0x40000000,0x40000000) for i in range(192)])
  gains=[rng.randrange(-0x40000000,0x40000000) for i in range(6)];deltas=[rng.randrange(-100000,100001) for i in range(6)];results=[];before=0
  acc=[0]+[rng.getrandbits(48) for i in range(3)]
  for r,meta,mac in pairs:
   sy=meta['per_track_fx']['symbols'];ps=meta['activity_masks']['symbols']
   for key,v in [('mf_mode',mode=='custom'),('mf_audio_ready',mode=='custom'),('mf_requested',mode=='custom'),('mf_side_on',0x931a3000 if mode=='stereo' else 0)]:r.w32(sy[key],v)
   r.u.mem_write(sy['mf_live'],bytes(48));r.u.mem_write(0x931a3000,struct.pack('>6I',1,0,0,0,0,0))
   r.u.mem_write(0x93180000,b'\x5a'*1024);r.u.mem_write(0x93181000,samples);r.u.mem_write(0x93182000,struct.pack('>6i',*deltas));r.u.mem_write(0x40a78c08,struct.pack('>6i',*gains));r.u.mem_write(0x40a78be8,struct.pack('>6i',*[v+int(mode=='pan' and i==0) for i,v in enumerate(gains)]))
   right_d=[v+int(mode=='ramp' and i==0) for i,v in enumerate(deltas)];r.u.mem_write(0x93183000,struct.pack('>6i',*right_d));r.u.mem_write(0x93184000,samples)
   mac.macsr=0x20 if trial%2 else 0xa0
   for i,v in enumerate(acc):mac.put_physical(i,v)
   previous=r.r32(ps['sf_pair_reused']) if meta.get('mono_mixer_reuse') else 0
   r.call(sy['mf_sum6'],0x93180000,0x93181000,0x40a78c08,0x93182000)
   r.call(sy['mf_sum6'],0x93180200 if mode=='output' else 0x93180004,0x93184000 if mode=='input' else 0x93181000,0x40a78be8,0x93183000)
   if meta.get('mono_mixer_reuse'):assert r.r32(ps['sf_pair_reused'])-previous==int(mode=='same'),mode
   results.append((bytes(r.u.mem_read(0x93180000,1024)),bytes(r.u.mem_read(0x40a78be8,56)),mac.macsr,[mac.physical(i) for i in range(4)]))
  assert results[0]==results[1],(mode,trial)
  cases+=1
print('PASS',cases,'native stereo pair cases: PCM/gains/EMAC exact, panning/ramp/stereo/custom/input/output guards',flush=True)
a.output.write_text(json.dumps(dict(cases=cases,guards=7,pcm_gain_emac_exact=True,hardware_tested=False),indent=2)+'\n',encoding='utf-8')
