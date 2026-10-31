"""Parite du dispatch natif pour tous les masques de six/sept contributeurs."""
from pathlib import Path
src=Path(__file__).with_name('test_mono_mixer.py').read_text(encoding='utf-8').replace('a=p.parse_args()', 'a=p.parse_args();a.output.parent.mkdir(parents=True,exist_ok=True)')
exec(compile(src[:src.index('rng=random.Random(272)')],str(Path(__file__).with_name('test_mono_mixer.py')),'exec'))
from unicorn import UC_HOOK_CODE
# Ajouter le noyau7 SRAM et le noyau sparse sans stub de calcul.
for r,meta,mac in pairs:
 sy=meta['per_track_fx']['symbols']
 for at,n in [(meta['sram_mixer']['address'],126),(sy['lt_native_one'],sy['lt_native_zero']-sy['lt_native_one'])]:
  tmp=a.output.parent/('baremetal-%x.bin'%at);tmp.write_bytes(r.u.mem_read(at,n));mac.install(emac.disasm(str(tmp),at,at,at+n))
rng=random.Random(274);rows=[]
for count in (6,7):
 for mask in range(1<<count):
  for ramp in (False,True):
   gains=[rng.randrange(-0x40000000,0) if mask&(1<<i) and not ramp else 0 for i in range(count)]
   deltas=[rng.randrange(-100000,0) if mask&(1<<i) and ramp else 0 for i in range(count)]
   samples=struct.pack('>%di'%(32*count),*[rng.randrange(-0x40000000,0x40000000) for i in range(32*count)])
   results=[];costs=[]
   for r,meta,mac in pairs:
    sy=meta['per_track_fx']['symbols']
    for key,v in [('mf_mode',1),('mf_audio_ready',1),('mf_requested',0),('lt_active',0)]:r.w32(sy[key],v)
    r.u.mem_write(sy['mf_live'],bytes(48));r.u.mem_write(0x93180000,b'\x5a'*256);r.u.mem_write(0x93181000,samples);r.u.mem_write(0x93182000,struct.pack('>%di'%count,*gains));r.u.mem_write(0x93183000,struct.pack('>%di'%count,*deltas))
    mac.macsr=0xa0 if ramp else 0x20
    for i in range(4):mac.put_physical(i,0)
    n=[0];h=r.u.hook_add(UC_HOOK_CODE,lambda *x:n.__setitem__(0,n[0]+1));r.call(sy['mf_sum6' if count==6 else 'mf_sum7'],0x93180000,0x93181000,0x93182000,0x93183000);r.u.hook_del(h)
    costs.append(n[0]);results.append((bytes(r.u.mem_read(0x93180000,256)),bytes(r.u.mem_read(0x93182000,4*count)),mac.macsr,[mac.physical(i) for i in range(4)]))
   assert results[0]==results[1],(count,mask,ramp)
   rows.append(dict(count=count,mask=mask,ramp=ramp,instructions=costs))
from unicorn import UC_HOOK_MEM_READ
poll=[]
for mode,ready,requested,tail in [(0,1,0,0),(1,0,0,0),(1,1,0,0),(1,1,1,0),(1,1,0,2)]:
 counts=[]
 for r,meta,mac in pairs:
  sy=meta['per_track_fx']['symbols']
  for key,v in [('mf_mode',mode),('mf_audio_ready',ready),('mf_requested',requested),('lt_active',tail)]:r.w32(sy[key],v)
  r.u.mem_write(sy['mf_live'],bytes(48));r.w32(0x40a78888,0);r.u.mem_write(0x40a78bd0,bytes(24));r.u.mem_write(0x93183000,bytes(24))
  reads=[0];sync=[0]
  h=r.u.hook_add(UC_HOOK_MEM_READ,lambda *args:reads.__setitem__(0,reads[0]+1),begin=0x40a78888,end=0x40a7888b)
  k=r.u.hook_add(UC_HOOK_CODE,lambda *args:sync.__setitem__(0,sync[0]+1),begin=sy['mf_sync_audio'],end=sy['mf_sync_audio'])
  r.call(sy['mf_sum6'],0x93180000,0x93181000,0x40a78bd0,0x93183000);r.u.hook_del(h);r.u.hook_del(k)
  assert sync[0]==1,sync
  counts.append(reads[0])
 assert bool(counts[1])==bool(mode and ready and(requested or tail)),(mode,ready,requested,tail,counts)
 poll.append(dict(mode=mode,ready=ready,requested=requested,tail=tail,kit_reads=counts))
print('PASS kit poll gating: sync always runs, assignments and draining tails retain kit reads',flush=True)
print('PASS',len(rows),'native mixer masks/ramp cases: PCM/gain/EMAC exact',flush=True)
a.output.write_text(json.dumps(dict(cases=rows,poll=poll,hardware_tested=False),indent=2)+'\n',encoding='utf-8')
