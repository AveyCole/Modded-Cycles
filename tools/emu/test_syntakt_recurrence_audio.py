"""Note 106 : exploration compteurs payload, fixture SY silencieuse : pas de preuve sonore."""
import sys,struct,collections
from pathlib import Path
sys.path=sys.path[1:];sys.path[:0]=['tools/emu','tools']
from test_midi_current_audio import boot
from test_model_tg import engine,MIX_GAIN
from unicorn import UC_HOOK_CODE
import mcengine as E
img,rt,ts=boot('build/filter-load-main/all-midi');body=Path('build/profile-0x80000000.bin').read_bytes()[0x3470:0x34ae];offset=rt.find(body);assert offset>=0 and rt.find(body,offset+1)<0
new=Path('build/swarm-recurrence.bin').read_bytes();assert len(new)<=len(body);patched=rt[:offset]+new+bytes.fromhex('4e71')*((len(body)-len(new))//2)+rt[offset+len(body):]
es=[];counts=[0,0]
for payload in (rt,patched):
 e=engine(img,payload=(0x46700000,payload));e.count=0
 for lane in range(6):
  e.set(lane,machine=0 if lane in (0,5) else 11,note=48+lane*3,color=64,shape=0,sweep=64,contour=0,decay=90)
  e.uc.mem_write(MIX_GAIN+4*lane,struct.pack('>I',0x20000000))
 def count(u,pc,size,user,e=e):e.count+=1
 e.uc.hook_add(UC_HOOK_CODE,count);es.append(e)
for block in range(8):
 outputs=[]
 for index,e in enumerate(es):
  e.count=0;outputs.append(e.block(63 if block%4==0 else 0));counts[index]+=e.count
 assert (outputs[0]==outputs[1]).all(),block
print('EXPLORATORY fixture outputs equal (SY audio not validated); instructions',counts,'saving',round(100*(1-counts[1]/counts[0]),2),'%',flush=True)
