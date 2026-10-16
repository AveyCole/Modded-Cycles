"""Note 106 : profil reel Kick / SYSwm x4 / Kick ; dumps uniquement dans build ignore."""
import sys,struct,collections
from pathlib import Path
sys.path=sys.path[1:]
sys.path[:0]=['tools/emu','tools']
from test_midi_current_audio import boot
from test_model_tg import engine,MIX_GAIN
from unicorn import UC_HOOK_CODE
import mcengine as E
img,rt,ts=boot('build/filter-load-main/all-midi');e=engine(img,payload=(0x46700000,rt))
for lane in range(6):
 e.set(lane,machine=0 if lane in (0,5) else 11,note=48+lane*3,color=64,shape=0,sweep=64,contour=0,decay=90)
 e.uc.mem_write(MIX_GAIN+4*lane,struct.pack('>I',0x20000000))
e.block(63)
counts=collections.Counter()
def count(u,pc,size,user):counts[pc]+=1
h=e.uc.hook_add(UC_HOOK_CODE,count);e.block(0);e.uc.hook_del(h)
regions=collections.Counter()
for pc,n in counts.items():regions[pc&~63]+=n
print('TOTAL',sum(counts.values()),flush=True)
for at,n in regions.most_common(18):print(hex(at),n,flush=True)
for lo,hi in [(0x80000000,0x80010000),(0x46700000,0x46790000)]:
 Path('build/profile-'+hex(lo)+'.bin').write_bytes(bytes(e.uc.mem_read(lo,hi-lo)))

