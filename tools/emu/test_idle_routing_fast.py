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


from unicorn import UC_HOOK_CODE
pairs=[]
for folder in (a.baseline,a.build):
 meta=json.loads((folder/'BUILD.json').read_text(encoding='utf-8'));fx.metadata=meta
 path=next(folder.glob('*.syx'));fx.boot=lambda p,path=path:bc.boot(path)
 r,files,bind=fixture();sy=meta['activity_masks']['symbols'];bind(0x40000542,lambda args:0);r.u.reg_write(C.UC_M68K_REG_A0,0x931b0000);r.call(sy['am_boot_finish'])
 pairs.append((r,meta,bind))
results=[]
for mode,requested,tail in ((0,0,0),(1,0,0),(1,1,0),(1,0,2)):
 outputs=[];costs=[]
 for r,meta,bind in pairs:
  sy=meta['per_track_fx']['symbols'];calls=[]
  r.w32(sy['mf_mode'],mode);r.w32(sy['mf_audio_ready'],1);r.w32(sy['mf_requested'],requested);r.w32(sy['lt_active'],tail)
  r.u.mem_write(sy['mf_live'],bytes(48));r.w32(sy['mf_side'],0);r.w32(sy['mf_side_on'],0)
  bind(sy['mf_old_post'],lambda args:calls.append('native') or 0)
  bind(sy['lt_run_slots'],lambda args:calls.append('slots') or 0)
  r.u.mem_write(0x93180000,struct.pack('>64i',*range(64)));n=[0]
  h=r.u.hook_add(UC_HOOK_CODE,lambda *args:n.__setitem__(0,n[0]+1));r.call(sy['mf_post'],0x93180000);r.u.hook_del(h)
  outputs.append((bytes(r.u.mem_read(0x93180000,256)),calls));costs.append(n[0])
 assert outputs[0][0]==outputs[1][0]
 assert outputs[1][1]==(['native'] if not mode or not requested and not tail else ['native','slots']),outputs
 if mode and not requested and not tail:assert costs[1]<costs[0],costs
 else:assert outputs[0]==outputs[1],outputs
 results.append(dict(mode=mode,requested=requested,tail=tail,instructions=costs));print('PASS routing state',results[-1],flush=True)
a.output.write_text(json.dumps(dict(post_cases=results,scope='routing only, native DSP calls observed or stubbed; not hardware cycles'),indent=2)+'\n',encoding='utf-8')
