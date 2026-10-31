"""Profil natif par etape ; exclut l IRQ USB et le lissage des parametres."""
from pathlib import Path
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_READ
source=Path(__file__).with_name('test_stock_machine_parity.py').read_text(encoding='utf-8')
source=source[:source.index('peaks=[0]*6')]
exec(compile(source,str(Path(__file__).with_name('test_stock_machine_parity.py')),'exec'))
if meta.get('sram_mixer',{}).get('enabled'):
 d=meta['sram_mixer'];e.emac.install(emac.disasm(str(args.build/'sram-mixer.bin'),d['address'],d['address'],d['address']+d['size']))
for key in ('fx_menu','stereo_chorus','delay_crush'):
 d=meta[key];raw=W/('profile-'+key+'.bin');raw.write_bytes(e.uc.mem_read(d['code'],d['code_bytes']));e.emac.install(emac.disasm(str(raw),d['code'],d['code'],d['code']+d['code_bytes']))
rows=[]
for eng in (stock,e):
 eng.uc.mem_map(0xfc040000,0x10000)
 # DMA termine immediatement : aucun cout de bus n est revendique.
 def dma_done(uc,access,addr,size,value,data):
  uc.mem_write(addr,bytes(size))
 eng.uc.hook_add(UC_HOOK_MEM_READ,dma_done,begin=0xfc0453de,end=0xfc0453df)
 eng.uc.reg_write(C.UC_M68K_REG_SR,0x2700);eng.call(0x40057260);eng.call(0x4005770e)
 assert eng.uc.reg_read(C.UC_M68K_REG_PC)==E.STOP
 eng.uc.mem_write(E.PARAMS+428,struct.pack('>4H',11000,0,10752,16384))
 for t in range(6):
  eng.uc.mem_write(E.PARAMS+2*t,struct.pack('>H',32512))
  eng.uc.mem_write(E.PARAMS+54+t*66,struct.pack('>3H',64*256,64*256,64*256))
  eng.uc.mem_write(E.PARAMS+14+t*66+56,struct.pack('>H',16384))
  eng.uc.mem_write(E.PARAMS+14+t*66+38,struct.pack('>H',32512))
for block in range(3):
 for label,eng in [('stock',stock),('mod',e)]:
  eng.uc.reg_write(C.UC_M68K_REG_SR,0x2700);eng.block(63 if block==0 else 0)
  post=int.from_bytes(eng.uc.mem_read(0x40059854,4),'big')
  eng.uc.reg_write(C.UC_M68K_REG_A2,E.PARAMS);eng.uc.reg_write(C.UC_M68K_REG_A3,E.PARAMS+0x2000)
  for name,entry,argv in [('lfo',meta['activity_masks']['symbols']['li_dispatch'] if label=='mod' else 0x40091ab2,(E.PARAMS,57600,63 if block==0 else 0)),('post',post,(E.TRACK_BASE,E.PARAMS)),('mix',0x400567ba,(0x4a3ed080,E.PARAMS))]:
   n=[0]
   def tick(*a):n[0]+=1
   h=eng.uc.hook_add(UC_HOOK_CODE,tick)
   try:eng.call(entry,*argv)
   except Exception:
    print('FAULT',label,name,hex(eng.uc.reg_read(C.UC_M68K_REG_PC)),eng.unmapped,flush=True);raise
   finally:eng.uc.hook_del(h)
   assert eng.uc.reg_read(C.UC_M68K_REG_PC)==E.STOP,('incomplete',label,hex(eng.uc.reg_read(C.UC_M68K_REG_PC)))
   row=dict(block=block,build=label,stage=name,instructions=n[0]);rows.append(row);print(row,flush=True)
args.output.write_text(json.dumps(dict(scope='separate LFO, volume/filter and mixer calls; DMA completion modeled; no complete IRQ, hardware cycles or bus timing',rows=rows,mono_reused=int.from_bytes(e.uc.mem_read(meta['activity_masks']['symbols']['sf_pair_reused'],4),'big') if meta.get('mono_mixer_reuse') else 0),indent=2)+'\n',encoding='utf-8')
