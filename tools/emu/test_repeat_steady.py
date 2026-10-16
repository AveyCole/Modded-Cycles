"""Note 106 : chemins repeat etablis et bords, etats natifs valides aleatoires."""
import argparse,json,pathlib,random,struct
from unicorn import UC_HOOK_CODE,m68k_const as mk
from test_seq_gen_menu import Rig,STACK,STOP
from test_sdvintage import main_os_from_syx
ROOT=pathlib.Path(__file__).resolve().parents[2];ORIGIN=0x46a00000;N=131072

def main():
 p=argparse.ArgumentParser();p.add_argument('--data',required=True);p.add_argument('--cases',type=int,default=256);a=p.parse_args()
 old=json.loads((ROOT/'docs/flasher/beat-repeat-data.js').read_text().split('window.MCBeatRepeat=',1)[1].strip().rstrip(';'));new=json.loads(pathlib.Path(a.data).read_text());stock=main_os_from_syx(str(ROOT/'firmware/model-cycles_OS1.13.syx'));rng=random.Random(106);rigs=[];history=rng.randbytes(12*N*2);calls=[0]
 for data in (old,new):
  r=Rig(stock,{'writes':[]},{'writes':[],'symbols':{}});u=r.u;u.mem_map(ORIGIN,0x10000);u.mem_map(0x80000000,0x200000);code=bytearray.fromhex(data['hex'])
  for off in data['reloc']:struct.pack_into('>I',code,off,struct.unpack_from('>I',code,off)[0]+ORIGIN)
  u.mem_write(ORIGIN,bytes(code));r.s={k:ORIGIN+v for k,v in data['symbols'].items()};u.mem_write(0x41000000,history)
  if 'br_fast_enabled' in r.s:r.w32(r.s['br_fast_enabled'],1)
  for name in r.s:
   if name.startswith('steady_channel'):
    def count(u,pc,size,user):calls[0]+=1
    u.hook_add(UC_HOOK_CODE,count,begin=r.s[name],end=r.s[name])
  rigs.append(r)
 for case in range(a.cases):
  length=[1,4,8,12,33,63,64,65,96,127,128,129,375,1500,6000,N-4096][case%16];ramp=max(1,min(length//4,32));phase=rng.choice([0,1,ramp-1,ramp,ramp+1,length//2,max(0,length-33),max(0,length-32),length-1]);phase=min(phase,length-1);elapsed=rng.choice([0,1,2,7,N//length])*length+phase
  if case%11==0:elapsed=(0xffffffff-rng.randrange(64))
  blocks=rng.getrandbits(32);now=(blocks<<5)&0xffffffff;mask=rng.randrange(64);side=0x800018d8 if case%17==0 else (0x80010000 if case%2 else 0)
  samples=struct.pack('>192i',*[rng.choice([-2147483648,2147483647,rng.randint(-2147483648,2147483647)]) for _ in range(192)]);sides=rng.randbytes(6*128);flags=[rng.randrange(2) for _ in range(6)]
  for r in rigs:
   for name,value in [('br_history',0x41000000),('br_keys',3),('br_cancel',0),('br_requested',0),('br_active',0),('br_valid',1),('br_wet',65536),('br_start',(now-elapsed)&0xffffffff),('br_length',length),('br_blocks',blocks),('br_side',side),('br_side_on',0x80011000),('br_mask_address',0x80012000),('br_pattern',0x41400000)]:r.w32(r.s[name],value)
   for lane in range(6):r.w32(r.s['br_lane_wet']+4*lane,0 if mask&(1<<lane) else 65536)
   r.w32(0x40a7883c,1);r.w32(0x40a78888,0x41400000);r.w32(0x40a78840,0);r.u.mem_write(0x80012000,bytes([mask]));r.u.mem_write(0x80011000,struct.pack('>6I',*flags));r.u.mem_write(0x80001858,samples)
   if side:r.u.mem_write(side,sides)
   r.u.mem_write(STACK,struct.pack('>I',STOP));r.u.reg_write(mk.UC_M68K_REG_A7,STACK);r.u.emu_start(r.s['br_audio'],STOP,count=1000000);assert r.u.reg_read(mk.UC_M68K_REG_PC)==STOP
  for at,size in [(0x41000000,12*N*2),(0x80001858,6*128)]+([(side,6*128)] if side else []):assert bytes(rigs[0].u.mem_read(at,size))==bytes(rigs[1].u.mem_read(at,size)),(case,length,phase,elapsed,hex(at))
  for name in ('br_wet','br_start','br_length','br_blocks','br_valid','br_active'):assert rigs[0].r32(rigs[0].s[name])==rigs[1].r32(rigs[1].s[name]),(case,name)
  assert bytes(rigs[0].u.mem_read(rigs[0].s['br_lane_wet'],24))==bytes(rigs[1].u.mem_read(rigs[1].s['br_lane_wet'],24))
 assert calls[0]>0;print('PASS',a.cases,'etats repeat : sorties/historique/etats exacts, bords/wraps/alias ; fast channel calls',calls[0],flush=True)
if __name__=='__main__':main()
