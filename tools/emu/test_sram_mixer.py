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
pairs=[];kernel=(a.build/'sram-mixer.bin').read_bytes()
for folder in (a.baseline,a.build):
 meta=json.loads((folder/'BUILD.json').read_text(encoding='utf-8'));fx.metadata=meta;path=next(folder.glob('*.syx'));fx.boot=lambda p,path=path:bc.boot(path)
 r,files,bind=fixture();r.u.mem_map(0x80000000,0x20000)
 for off,at,n in ((0,0x80001c5c,0x5858),(0x5858,0x8000cac0,0x2020)):r.u.mem_write(at,bytes(r.u.mem_read(0x46700000+off,n)))
 guards=(bytes(r.u.mem_read(0x8000ea40,8)),bytes(r.u.mem_read(0x8000eac6,26)))
 bind(0x40000542,lambda args:0);r.u.reg_write(C.UC_M68K_REG_A0,0x931b0000);r.call(meta['activity_masks']['symbols']['am_boot_finish'])
 assert guards==(bytes(r.u.mem_read(0x8000ea40,8)),bytes(r.u.mem_read(0x8000eac6,26)))
 if folder==a.build:assert bytes(r.u.mem_read(0x8000ea48,126))==kernel
 mac=ExtendedEMAC(r.u)
 mac.install(emac.disasm(str(a.build/'sram-mixer.bin'),0x40056698,0x40056698,0x40056716))
 if folder==a.build:mac.install(emac.disasm(str(a.build/'sram-mixer.bin'),0x8000ea48,0x8000ea48,0x8000eac6))
 pairs.append((r,meta,mac))
rng=random.Random(54415);hits=[0]
from unicorn import UC_HOOK_CODE
pairs[1][0].u.hook_add(UC_HOOK_CODE,lambda *args:hits.__setitem__(0,hits[0]+1),begin=0x8000ea48,end=0x8000eac5)
for case in range(64):
 source=struct.pack('>224i',*[rng.randrange(-0x40000000,0x40000000) for _ in range(224)]);gain=struct.pack('>7i',*[rng.randrange(-0x40000000,0x40000000) for _ in range(7)]);delta=struct.pack('>7i',*[rng.randrange(-10000,10001) for _ in range(7)]);results=[]
 for r,meta,mac in pairs:
  r.u.mem_write(0x93180000,b'\x5a'*256);r.u.mem_write(0x93181000,source);r.u.mem_write(0x93182000,gain);r.u.mem_write(0x93183000,delta)
  mac.macsr=0x20
  for acc in range(4):mac.put_physical(acc,0)
  r.call(meta['per_track_fx']['symbols']['mf_old_sum7'],0x93180000,0x93181000,0x93182000,0x93183000)
  results.append((bytes(r.u.mem_read(0x93180000,256)),bytes(r.u.mem_read(0x93182000,28)),[mac.physical(i) for i in range(4)],mac.macsr))
 assert results[0]==results[1],case
assert hits[0]>0
print('PASS64 native mixer cases: exact PCM/gain/EMAC, execution in SRAM, neighboring bytes preserved',flush=True)
a.output.write_text(json.dumps(dict(cases=64,sram_instructions=hits[0],pcm_gain_emac_exact=True,guards_preserved=True,hardware_tested=False),indent=2)+'\n',encoding='utf-8')
