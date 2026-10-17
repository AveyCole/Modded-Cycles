"""Note 106 : surcharge puis retour, vrais callbacks du regulateur.
Sorties de voix et minuteur synthetiques ; pas de mesure CPU physique.
"""
import argparse,json,pathlib,struct,sys
from test_seq_gen_menu import Rig
from test_sdvintage import main_os_from_syx
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
import build

def main():
 p=argparse.ArgumentParser();p.add_argument('--tweak',default='build/swarm-lite/governor.json');p.add_argument('--case');a=p.parse_args()
 if a.case:
  from test_midi_current_audio import boot
  stock,payload,ts,ram=boot(a.case,with_sram=True);tw=next(t for t in ts if t.get('gov'));dest=0x46700000
 else:
  tw=json.loads(pathlib.Path(a.tweak).read_text());stock=main_os_from_syx('firmware/model-cycles_OS1.13.syx')
  payload,_=build.build_payload([tw],stock,'firmware/Syntakt_OS1.42.syx');dest=int(tw['append']['dest'],16);ram=None
 r=Rig(stock,{'writes':[] if a.case else tw['writes']},{'writes':[],'symbols':{}});u=r.u;u.mem_map(dest,0x800000);u.mem_map(0x80000000,0x20000);u.mem_map(0xfc070000,0x1000)
 u.mem_write(dest,payload)
 if ram:u.mem_write(0x80000000,ram)
 sy={k:int(v,16) for k,v in tw['gov'].items()};buf=0x80001858;period=90112;now=10_000_000;cuts=0
 put=lambda addr,v:u.mem_write(addr,struct.pack('>I',v&0xffffffff))
 read=lambda name:bytes(u.mem_read(sy[name],6))
 for base in (0x40a78c08,0x40a78be8,0x40a78bd0,0x40a78bb8,0x40a78b9c,0x40a78b80):
  for lane in range(6):put(base+lane*4,0x20000000)
 for block in range(160):
  # Nouvelle note sur toutes les pistes apres la surcharge, puis moteurs stock.
  trig=block in (0,96,112);engine=10 if block<112 else 0
  for lane in range(6):
   put(0xfc07000c,now)
   gate=r.call(sy['voice_gate'],lane,int(trig),engine)
   if not gate:
    samples=[(1 if i%2 else -1)*((lane+1)*1_000_003+i*311) for i in range(32)]
    u.mem_write(buf+128*lane,struct.pack('>32i',*samples));put(0xfc07000c,now+5000)
    r.call(sy['voice_after'],lane,buf+128*lane)
    if block>=96:
     assert list(struct.unpack('>32i',u.mem_read(buf+128*lane,128)))==samples,('fade residuel',block,lane)
   elif block>=96:raise AssertionError(('voix restee coupee',block,lane))
  put(sy['gov_t0_audio'],now);put(0xfc07000c,now+period*(110 if 24<=block<64 else 45)//100)
  r.call(sy['audio_end']);now+=period;cuts+=sum(bool(v) for v in read('gov_fading'))
  if block>=96:assert not any(read('gov_fading')) and not any(read('gov_stolen')),('etat residuel',block)
 assert cuts>0,'fixture sans extinction'
 print('PASS surcharge 110% : fondus observes ; retour 45%, six retriggers et remplacement stock sans etat ni quantification residuels')
 print('LIMITE : callbacks seuls ; ni SY DSP, ni filtre, ni repeat, ni interruption physique')
if __name__=='__main__':main()

