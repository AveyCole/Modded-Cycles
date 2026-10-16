"""Note 106 : helper sinus, 1 024 etats extremes/aleatoires, sortie/etat/acc exacts."""
import sys,struct,random
from pathlib import Path
sys.path=sys.path[1:];sys.path[:0]=['tools/emu','tools']
from test_seq_gen_menu import Rig
from test_sdvintage import main_os_from_syx
from unicorn import UC_HOOK_CODE
import emac
stock=main_os_from_syx('firmware/model-cycles_OS1.13.syx');old=Path('build/profile-0x80000000.bin').read_bytes();new=Path('build/swarm-recurrence.bin').read_bytes();rigs=[]
for index in range(2):
 r=Rig(stock,{'writes':[]},{'writes':[],'symbols':{}});r.u.mem_map(0x80000000,0x10000);r.u.mem_map(0x46a00000,0x10000)
 r.u.mem_write(0x80000000,old);r.u.mem_write(0x46a00000,new);r.emac=emac.EMAC(r.u)
 r.emac.install(emac.disasm('build/profile-0x80000000.bin',0x80000000,0x80003470,0x800034ae))
 r.emac.install(emac.disasm('build/swarm-recurrence.bin',0x46a00000,0x46a00000,0x46a00000+len(new)));r.count=0
 def count(u,pc,size,data,r=r):r.count+=1
 r.u.hook_add(UC_HOOK_CODE,count,begin=0x80003470,end=0x800034ad);r.u.hook_add(UC_HOOK_CODE,count,begin=0x46a00000,end=0x46a00000+len(new));rigs.append(r)
rng=random.Random(106);counts=[0,0]
for case in range(1024):
 vals=[rng.choice([-2147483648,2147483647,0,rng.randint(-2147483648,2147483647)]) for _ in range(4)];n=[0,1,32,64][case%4];results=[]
 for i,r in enumerate(rigs):
  r.u.mem_write(0x93070000,bytes(256));r.u.mem_write(0x93071000,struct.pack('>4i',*vals));r.emac.macsr=0xa0;r.emac.acc[:]=[0,111,222,333];r.count=0
  r.call(0x80003470 if i==0 else 0x46a00000,0x93070000,n,0x93071000);counts[i]+=r.count
  results.append((bytes(r.u.mem_read(0x93070000,256)),bytes(r.u.mem_read(0x93071000,16)),r.emac.acc[:]))
 assert results[0]==results[1],(case,n,vals,results)
print('PASS 1024 oscillator-helper blocks, extreme/random state, output/state/acc identical',counts,flush=True)
