"""Preuve native des reglages ACID, navigation et sauvegarde globale."""
from pathlib import Path
import argparse,inspect,json,struct,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/emu')]
p=argparse.ArgumentParser();p.add_argument('--first',action='store_true');p.add_argument('--build',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
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
a.output.parent.mkdir(parents=True,exist_ok=True)
pairs=[];original_image=bc.load(Path('H:/CREATURE-source/retrosyn-integration-step-rec-solo/firmware/model-cycles_OS1.13.syx'));lo,hi=(0x400a80e6,0x400a8204) if a.first else (0x400a8204,0x400a835e)
native=original_image[lo-0x40000400:hi-0x40000400];f=a.output.parent/'om-native.bin';f.write_bytes(native)
for variant in (0,1):
 meta=json.loads((a.build/'BUILD.json').read_text(encoding='utf-8'));fx.metadata=meta;fx.boot=lambda p:bc.boot(next(a.build.glob('*.syx')))
 r,files,bind=fixture();r.u.mem_write(lo,native);mac=ExtendedEMAC(r.u);mac.install(emac.disasm(str(f),lo,lo,hi))
 for key,at,size in [('primary',meta['activity_masks']['code'],meta['activity_masks']['code_bytes']),('old',meta['per_track_fx']['symbols']['dry_osc'],512)]:
  raw=a.output.parent/('om-'+key+'.bin');raw.write_bytes(r.u.mem_read(at,size));mac.install(emac.disasm(str(raw),at,at,at+size))
 if variant:
  target=meta['activity_masks']['symbols']['om_first' if a.first else 'om_osc'];entry=0x400a8152 if a.first else 0x400a82cc;r.u.mem_write(entry,b'\x4e\xf9'+struct.pack('>I',target));
  if not a.first:mac.fast[entry]=lambda:None;mac.next[entry]=target
 pairs.append((r,mac))
from unicorn import UC_HOOK_CODE
rng=random.Random(273);costs={};regs=[getattr(C,'UC_M68K_REG_D'+str(i)) for i in range(2,8)]+[getattr(C,'UC_M68K_REG_A'+str(i)) for i in range(2,7)]
for mode in ('a','b','a_ramp','b_ramp','both','dry','ramp_a','ramp_b'):
 total=[0,0]
 for case in range(32):
  state=bytearray(rng.randbytes(208));source_a=rng.randbytes(132);source_b=rng.randbytes(132);table=rng.randbytes(1028)
  for offset,address in [(148,0x93180000),(152,0x93181000),(168,0x93182000),(192,0x93183000),(196,0x93184000)]:struct.pack_into('>I',state,offset,address)
  if case>=8:struct.pack_into('>I',state,148 if case%2 else 152,(0x93183000 if case%4<2 else 0x93184000)+(-4,0,4)[case%3])
  wa=0 if mode in ('a','a_ramp','dry') else rng.randrange(1,0x10000000);wb=0 if mode in ('b','b_ramp','dry') else rng.randrange(1,0x10000000)
  for offset,value in [(132,wa),(140,wa),(136,wb),(144,wb)]:struct.pack_into('>I',state,offset,value)
  if mode in ('ramp_a','b_ramp'):struct.pack_into('>I',state,132,wa+4096)
  if mode in ('ramp_b','a_ramp'):struct.pack_into('>I',state,136,wb+8192)
  status=0xa0 if case%2 else 0x20;acc=[rng.getrandbits(48) for i in range(4)];seed=[rng.getrandbits(32) for i in regs];outputs=[]
  for index,(r,mac) in enumerate(pairs):
   for at,raw in [(0x93170000,bytes(state)),(0x93180000,source_a),(0x93181000,source_b),(0x93182000,table),(0x93183000,b'\x5a'*128),(0x93184000,b'\xa5'*128)]:r.u.mem_write(at,raw)
   mac.macsr=status
   for i,v in enumerate(acc):mac.put_physical(i,v)
   for reg,v in zip(regs,seed):r.u.reg_write(reg,v)
   n=[0];hook=r.u.hook_add(UC_HOOK_CODE,lambda *args:n.__setitem__(0,n[0]+1));
   try:r.call(lo,0,0x93170000)
   except Exception:print('FAULT',mode,case,index,hex(r.u.reg_read(C.UC_M68K_REG_PC)),flush=True);raise
   r.u.hook_del(hook);total[index]+=n[0]
   assert [r.u.reg_read(reg) for reg in regs]==seed
   outputs.append((bytes(r.u.mem_read(0x93170000,208)),bytes(r.u.mem_read(0x93183000,128)),bytes(r.u.mem_read(0x93184000,128)),mac.macsr,[mac.physical(i) for i in range(4)]))
  assert outputs[0]==outputs[1],(mode,case,[i for i,(x,y) in enumerate(zip(*outputs)) if x!=y])
 costs[mode]=total
 if mode in ('a','b','a_ramp','b_ramp'):assert total[1]<total[0],(mode,total)
 print('PASS native oscillator',('first' if a.first else 'second'),mode,'32 cases exact PCM/state/EMAC/ABI; instructions',total,flush=True)
a.output.write_text(json.dumps(dict(cases=256,pcm_state_emac_abi_exact=True,instructions=costs,hardware_tested=False),indent=2)+'\n',encoding='utf-8')
