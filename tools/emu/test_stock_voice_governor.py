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


GB=0x46732000;GATE=0x8000e8a4;END=0x8000e6e0;NOM=90112
pairs=[]
for folder in (a.baseline,a.build):
 meta=json.loads((folder/'BUILD.json').read_text());path=next(folder.glob('*.syx'));fx.boot=lambda p,path=path:bc.boot(path)
 r,files,bind=fixture();r.u.mem_map(0x80000000,0x20000)
 for off,at,n in ((0,0x80001c5c,0x5858),(0x5858,0x8000cac0,0x2020)):r.u.mem_write(at,bytes(r.u.mem_read(0x46700000+off,n)))
 sy=meta['activity_masks']['symbols'];r.u.reg_write(C.UC_M68K_REG_A0,0x931b0000);bind(0x40000542,lambda a:0);r.call(sy['am_boot_finish'])
 assert r.u.mem_read(GATE+18,1)==(b'\x64' if folder==a.build else b'\x67')
 r.u.reg_write(C.UC_M68K_REG_SR,0x2700);pairs.append((r,meta))

def setup(r,meta,engines):
 r.u.mem_write(GB,bytes(0x1200));r.w32(0x40a7883c,1);r.w32(meta['dx_symbols']['dx_enabled'],0);r.w32(0xfc07000c,1000000)
 q=97*256//100
 for off,value in ((0x78,q),(0xf10,q*8),(0xf14,q*256),(0xf04,q),(0xf00,1000000-NOM)):r.w32(GB+off,value)
 for t,engine in enumerate(engines):
  r.u.mem_write(0x8000102c+t*66,struct.pack('>H',engine<<8));r.call(GATE,t,1,engine)
  r.u.mem_write(GB+0x3a+2*t,struct.pack('>H',80));r.w32(GB+0xa+4*t,8000);r.u.mem_write(0x80001858+t*128,struct.pack('>32i',*([300000000]*32)))
  for at in (0x40a78c08,0x40a78be8):r.w32(at+t*4,0x20000000)
  for at in (0x40a78bd0,0x40a78bb8,0x40a78b9c,0x40a78b80):r.w32(at+t*4,0)

def overload(r):
 for i in range(12):
  now=1000000+i*NOM;r.w32(GB+0x80,now);r.w32(0xfc07000c,now+NOM*108//100);r.call(END)
 return list(r.u.mem_read(GB+0x58,6))
rows=[]
for r,meta in pairs:
 setup(r,meta,[0,1,2,3,4,5]);rows.append(overload(r))
assert any(rows[0]) and not any(rows[1]),rows
print('PASS native governor reproduces stock fades before fix; all six stock voices remain protected after fix',rows,flush=True)
r,meta=pairs[1];setup(r,meta,[24,1,2,3,4,5]);mixed=overload(r);assert mixed[0] and not any(mixed[1:]),mixed
print('PASS added engine remains eligible for overload relief; stock neighbours remain protected',mixed,flush=True)
# Le chemin quiet/stolen ne doit pas tuer les fins de notes ni les attaques lentes stock.
for engine in range(25):
 setup(r,meta,[engine,1,2,3,4,5]);r.w32(GB+0x64,1);r.u.mem_write(GB+0x5e,b'\xff');r.u.mem_write(GB+0x4c,b'\1')
 result=r.call(GATE,0,0,engine);assert result==(0 if engine<=6 else 1),(engine,result)
print('PASS stock machines bypass custom quiet/stolen culling; Wizard and added-machine policy retained',flush=True)
quiet_results=[]
for engine in range(8):
 values=[]
 for r,meta in pairs:
  voice=0x931a0000;r.u.mem_write(voice,bytes(0x300));r.w32(voice,engine);r.w32(voice+0x298,5)
  for at in (0x401bcc80,0x401b9b14,0x401ba5e0,0x401ba59c,0x40a78e18):r.w32(at,0)
  r.u.mem_write(0x401adcc0,b'\1'*6)
  for at in (0x40a78c08,0x40a78be8,0x40a78bd0,0x40a78bb8,0x40a78b9c,0x40a78b80):r.u.mem_write(at,bytes(24))
  r.u.mem_write(0x40002ceb,b'\x38');r.u.reg_write(C.UC_M68K_REG_A0,voice);r.u.reg_write(C.UC_M68K_REG_D1,0);values.append(r.call(0x401adb4c))
 assert values==([1,0] if engine<6 and not pairs[1][1]['stock_voice_protection'].get('native_idle_retained') else [1,1]),(engine,values);quiet_results.append(values)
print('PASS Model-TG idle policy matches candidate metadata',flush=True)
a.output.write_text(json.dumps(dict(native_boot=True,stock_overload_before_after=rows,mixed_overload=mixed,quiet_stolen_cases=25,model_tg_quiet_before_after=quiet_results,hardware_tested=False),indent=2)+'\n')
