"""Preuve native des reglages ACID, navigation et sauvegarde globale."""
from pathlib import Path
import argparse,inspect,json,struct,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/emu')]
p=argparse.ArgumentParser();p.add_argument('--build',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
import boot_candidate as bc
import test_fx_menu_control as fx
from test_seq_gen_menu import EVENT
from unicorn import m68k_const as C
m=json.loads((a.build/'BUILD.json').read_text(encoding='utf-8'));s=m['activity_masks']['symbols'];al=m['direct_jump']['aliases']
bc.ROOT=a.output.parent/'ui-cache';fx.metadata=m;fx.boot=lambda path:bc.boot(next(a.build.glob('*.syx')))
src=inspect.getsource(fx.fixture).replace("m=json.loads((ROOT/'output/firmware'/(stem+'.json')).read_text())",'m=metadata');exec(src,fx.__dict__)
def fixture():
 r,_,h,log,files,key,turn,data,bind=fx.fixture('unused');bind(al['gc_input_quiet'],lambda a:1);bind(0x400423e4,lambda a:0);return r,files,bind

r,files,bind=fixture();r.u.mem_map(0x80000000,0x20000)
for off,at,n in ((0,0x80001c5c,0x5858),(0x5858,0x8000cac0,0x2020)):r.u.mem_write(at,bytes(r.u.mem_read(0x46700000+off,n)))
bind(0x40000542,lambda args:0);r.u.reg_write(C.UC_M68K_REG_A0,0x931b0000);r.call(s['am_boot_finish'])
sy=m['per_track_fx']['symbols'];r.w32(sy['gb_enabled'],1);r.w32(0x40a7883c,1);r.w32(sy['gb_irq_t0'],1000)
stamps=[1100,1300,1600,1700,2300,2700,3200]
for i,v in enumerate(stamps):r.w32(s['hp_stamp']+4*i,v)
r.call(s['hp_record'],3500);expected=[600,400,500,300,300,400]
assert [r.r32(s['hp_best']+4*i) for i in range(6)]==expected
assert sum(expected)==2500
# Un bloc sans marqueurs dans la fenetre ne remplace pas le precedent.
r.w32(sy['gb_irq_t0'],10000);r.call(s['hp_record'],20000);assert [r.r32(s['hp_best']+4*i) for i in range(6)]==expected
texts=[]
def text_at(at):return bytes(r.u.mem_read(at,80)).split(b'\0')[0].decode()
def formatter(args):
 dest,fmt=args[:2];fmt=text_at(fmt);vals=args[2:2+fmt.count('%u')];text=fmt%tuple(vals);r.u.mem_write(dest,text.encode()+b'\0');return len(text)
bind(0x40000e6e,formatter)
beat=m['fx_menu']['symbols']['dx_beat_api'];popup=r.r32(beat+8);bind(popup,lambda args:texts.append(text_at(args[0])) or 0)
for key in ('menu','fx_menu_open','fx_tap_force'):r.w32(m['fx_menu']['symbols'][key],0)
r.w32(m['fx_menu']['symbols']['dx_enabled'],1)
for i,v in enumerate((11,22,33,44,55,66)):r.w32(s['hp_best']+4*i,v*901)
for key,v in [('dx_peak',108*901),('dx_over',13),('dx_new',0),('gr_diag_sum',194*10),('gr_diag_blocks',10)]:r.w32(m['fx_menu']['symbols'][key],v)
event=0x93190000
for page in range(3):
 start=200000000+page*200000000
 for tick,flags in ((start,1),(start+10000000,16),(start+20000000,1),(start+100000000,16)):
  r.w32(0xfc07000c,tick);r.u.mem_write(event,struct.pack('>6I',0,0,0,1,flags,0));r.call(s['hp_diag_gesture'],event)
assert texts==['A75 P108 O13 N0','V11 F22 X33','L44 S55 R66'],texts
# Les stubs rejouent les instructions deplacees avec pile/registres/CCR exacts.
image=bc.load(next(a.build.glob('*.syx')));bind(0x40056ea8,lambda args:0)
registers=[getattr(C,'UC_M68K_REG_D'+str(i)) for i in range(8)]+[getattr(C,'UC_M68K_REG_A'+str(i)) for i in range(8)]+[C.UC_M68K_REG_SR]
for index,mark in enumerate(m['audio_profile']['markers']):
 at,n=mark['at'],mark['size'];raw=image[at-0x40000400:at-0x40000400+n];reference=0x931a0000;r.u.mem_write(reference,raw)
 states=[]
 for start,end in ((reference,reference+n),(s['hp_mark'+str(index)],at+n)):
  r.u.mem_write(0x931b0000,bytes(range(256))*16);r.u.mem_write(0x931a2000,bytes(128))
  for i,reg in enumerate(registers[:16]):r.u.reg_write(reg,0x931a2000 if i==11 else 0x931b0800 if i==15 else 0x12340000+i)
  r.u.reg_write(C.UC_M68K_REG_SR,0x2715);r.w32(0xfc07000c,1234567);r.u.emu_start(start,end,count=10000)
  assert r.u.reg_read(C.UC_M68K_REG_PC)==end
  states.append(([r.u.reg_read(reg) for reg in registers],bytes(r.u.mem_read(0x931b0700,512))))
 assert states[0][0]==states[1][0],('registers/CCR',index,states[0][0],states[1][0])
 # La pile sous SP contient naturellement les scratchs du marqueur ; la pile active est identique.
 sp=states[0][0][15];assert states[0][1][sp-0x931b0700:sp-0x931b0700+16]==states[1][1][sp-0x931b0700:sp-0x931b0700+16]
 assert r.r32(s['hp_stamp']+4*index)==1234567
print('PASS seven native timing markers: registers, CCR, active stack and continuation contracts',flush=True)
print('PASS worst-frame timing sum, stale-frame rejection and three native DX gesture pages',texts,flush=True)
a.output.write_text(json.dumps(dict(stage_ticks=expected,pages=texts,hardware_tested=False),indent=2)+'\n',encoding='utf-8')
