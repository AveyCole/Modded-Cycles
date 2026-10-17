"""Note 109 : vrai boot/cache et file MIDI native ; geste filtre B.
Horloge de sequence isolee pour les mesures de repetition, I/O simulees.
"""
import argparse,json,pathlib,struct,sys
from unicorn import UC_HOOK_CODE,m68k_const as mk
HERE=pathlib.Path(__file__).resolve().parent;sys.path[:0]=[str(HERE),str(HERE.parent)]
from test_seq_gen_menu import Rig,STACK,STOP,OBJ,VT,GET,RAW,SIGNAL,EVENT
from test_sdvintage import main_os_from_syx
import build
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);a=p.parse_args();prefix=pathlib.Path(a.case)
 cat=json.loads(prefix.with_suffix('.json').read_text())['tweaks'];sg=next((t for t in cat if t.get('symbols',{}).get('sg_q_hook')),{'symbols':{}});bank=next((t for t in cat if t['id']=='midi-out-bank'),None)
 img=main_os_from_syx(str(prefix.with_suffix('.syx')));r=Rig(img,{'writes':[]},{'writes':[],'symbols':sg['symbols']});u=r.u;bs={k:int(v,16) for k,v in bank['symbols'].items()} if bank else {}
 for at,n in [(0x43000000,0x800000),(0x46700000,0x400000),(0x80000000,0x200000),(0x90000000,0x20000)]:u.mem_map(at,n)
 def cache(u,pc,size,data):u.reg_write(mk.UC_M68K_REG_PC,pc+4)
 sites=set()
 for at,raw in [(build.BASE,img)]+[(int(p['dest'],16),bytes.fromhex(p['hex'])) for t in cat if t.get('append') for p in t['append']['parts'] if 'hex' in p]:sites.update(at+i for i in range(0,len(raw)-3,2) if raw[i:i+2]==b'\x4e\x7b')
 for at in sites:u.hook_add(UC_HOOK_CODE,cache,begin=at,end=at)
 u.reg_write(mk.UC_M68K_REG_A7,STACK);u.mem_write(STACK,struct.pack('>I',STOP));u.emu_start(0x40000530,0x4000053a,count=200_000_000);assert u.reg_read(mk.UC_M68K_REG_PC)==0x4000053a;r.call(0x4007929c)
 if bank:
  for part in bank['append']['parts']:
   if 'hex' in part:
    at=int(part['dest'],16);raw=bytes.fromhex(part['hex']);assert bytes(u.mem_read(at,len(raw)))==raw,'code altere par boot/cache'


 repeat=next(t for t in cat if t['id']=='control-all-beat-repeat');r.s.update(bs);r.s.update({k:int(v,16) for k,v in repeat['symbols'].items()})
 origin=int(repeat['append']['dest'],16);end=origin+repeat['append']['size']
 for part in repeat['append']['parts']:
  at=int(part['dest'],16);raw=bytes.fromhex(part['hex']);assert bytes(u.mem_read(at,len(raw)))==raw
 print('PASS vrai boot/cache : extension et trampolines exacts',flush=True)
 u.reg_write(mk.UC_M68K_REG_SR,0x2000)
 rt,pat,state=0x93050000,0x93070000,0x93080000
 r.w32(bs['ml_runtime'],rt);r.w32(bs['ml_context'],0x93060000);r.w32(bs['ml_pattern'],pat);r.w32(bs['ml_play_pattern'],pat)
 for lane in range(6):u.mem_write(pat+264*lane,bytes((1,0,6+lane,4,16,2,0,0))+bytes(256))
 r.w32(0x40a700c4,0);r.w32(bs['mlp_obj'],0)
 maskaddr=int(next(t['symbols']['cac_mask'] for t in cat if t.get('symbols',{}).get('cac_mask')),16)
 # Seule la boucle de sequence A/B est isolee ici : file/step/stop/take restent natifs.
 at=r.s['bp_clock_original'];r.stubs[at]=lambda a:0;u.hook_add(UC_HOOK_CODE,r.stub,begin=at,end=at)
 def take():
  messages=[]
  while (packet:=r.call('ml_take',rt)):messages.append(packet)
  return messages
 def clock(now,playing=1):return r.call(bs['ml_clock'],rt,pat,state,now&0xffffffff,playing)
 def seed():
  for lane in range(6):assert r.call(bs['ml_step'],rt,lane,((0x96+lane)<<24)|((60+lane)<<16)|(100<<8)|4,1)==1
  take()
 def off(p):return p&0xefff00ff
 clock(0);seed();r.w32(r.s['br_keys'],3);r.w32(r.s['br_requested'],0xffffffff);clock(10);assert take()==[]
 print('PASS combo seul : aucun MIDI repete sans division',flush=True)
 for division in range(16):
  r.w32(r.s['br_requested'],division);interval=r.r32(r.s['br_divs']+4*division);now=(interval*(division+1))&0xffffffff
  clock(now);got=take();assert sum((p>>28)==9 for p in got)==6,(division,got)
  clock(now+interval//2);got=take();assert len(got)==6 and all(p>>28==8 for p in got),(division,got)
  due=now+interval-now%interval;clock(due);got=take();assert len(got)==6 and all(p>>28==9 for p in got),(division,got)
  clock(due+3*interval+1);got=take();assert sum(p>>28==9 for p in got)==6,'rafale rattrapage'
  r.w32(r.s['br_requested'],0xffffffff);clock(due+3*interval+2);got=take();assert all(p>>28==8 for p in got) and len(got)==6
 print('PASS seize divisions musicales, Off demi-intervalle/release, retard sans rafale',flush=True)
 for mask in range(64):
  r.w32(r.s['bp_midi_mask'],mask);r.w32(r.s['br_requested'],4);clock(100000+mask*10000000);got=take()
  want=[i for i in range(6) if not mask&(1<<i) or i==0]
  assert [(p>>24)&15 for p in got if p>>28==9]==[6+i for i in want],(mask,got)
  r.w32(r.s['br_requested'],0xffffffff);clock(100001+mask*10000000);take()
 r.w32(r.s['bp_midi_mask'],0);u.mem_write(maskaddr,b'\x00');r.w32(r.s['br_requested'],4);clock(800000000);take();clock(800000001,0);assert all(p>>28==8 for p in take())
 clock(800000002);take();u.mem_write(pat+1,b'\x01');clock(800000003);assert all(p>>28==8 for p in take());u.mem_write(pat+1,b'\x00')
 r.w32(r.s['br_requested'],0xffffffff);clock(0xfffffff0);take()
 r.w32(r.s['br_requested'],0);clock(0xfffffff0);take();clock(0x100100000);got=take();assert sum(p>>28==9 for p in got)<=6
 r.w32(r.s['br_requested'],0xffffffff);clock(0x100100001);assert all(p>>28==8 for p in take())
 # Un changement de pattern ne reutilise pas les anciennes notes.
 newpat=pat+0x1000;u.mem_write(newpat,bytes(u.mem_read(pat,1584)))
 r.w32(r.s['br_requested'],0);r.call(bs['ml_clock'],rt,newpat,state,100,1);assert not any(p>>28==9 for p in take())
 r.w32(r.s['br_requested'],0xffffffff);clock(101);take()
 print('PASS 64 masques Control All, stop/mute, wrap32 et changement de pattern sans notes tenues',flush=True)
 # Projet et Context natifs identiques a la preuve SCRAMBLE, six sons reels.
 KIT,SVT,SGET,NOTIFY,ZVT,ZERO=0x93100000,0x93130000,0x93131000,0x93132000,0x93133000,0x93134000
 RAWBASE,CTXBASE=0x93120000,0x93110000
 calls=[];sent=[]
 r.stubs[0x400cf866]=lambda a:KIT;r.stubs[0x400cf9a8]=lambda a:0x931f0000
 r.stubs[0x4000f26c]=lambda a:CTXBASE+64*a[1]
 r.stubs[ZERO]=lambda a:0;r.stubs[NOTIFY]=lambda a:calls.append(a) or 0
 r.stubs[SGET]=lambda a:RAWBASE+128*((a[0]-KIT-212)//68)
 r.stubs[0x4007faf4]=lambda a:int(a[0] in (2,5))
 def send(a):sent.append((bytes(u.mem_read(a[1],3)),a[2]));return 0
 r.stubs[0x400826b0]=send
 for at in [0x400cf9a8,0x4000f26c,ZERO,NOTIFY,SGET,0x4007faf4,0x400826b0]:u.hook_add(UC_HOOK_CODE,r.stub,begin=at,end=at)
 trace=[]
 def tracing(u,pc,size,data):
  trace.append(pc)
  if len(trace)>25:trace.pop(0)
 u.hook_add(UC_HOOK_CODE,tracing)
 r.trace=trace
 r.w32(SVT+40,SGET);r.w32(SVT+16,NOTIFY);r.w32(ZVT+80,ZERO)
 for lane in range(6):
  handle=KIT+212+68*lane;raw=RAWBASE+128*lane;ctx=CTXBASE+64*lane
  r.w32(handle,SVT);r.w32(ctx,0x400fd134);r.w32(ctx+4,handle)
  r.w32(KIT+116+8*(63+lane),ZVT);r.w32(KIT+116+620,ZVT)
  data=bytearray(100);data[38]=lane
  struct.pack_into('>h',data,20+48,100*256);struct.pack_into('>h',data,20+50,10*256);u.mem_write(raw,bytes(data))
 r.call(0x4005a274);r.w32(bs['mlp_obj'],OBJ);r.w32(bs['mlp_track'],2);r.w32(0x40fe4228,1);r.delta=-5
 u.mem_write(maskaddr,b'\x06');r.w32(r.s['bp_midi_mask'],6)
 # Les invalidations de vue sont la frontiere UI externe.
 at=bs['mlp_redraw'];r.stubs[at]=lambda a:0;u.hook_add(UC_HOOK_CODE,r.stub,begin=at,end=at)
 for code,cc,key in [(8,74,24),(9,71,25)]:
  r.event(code,1,500+code);sent.clear();calls.clear()
  try:assert r.call(bs['mlkc_enc'],EVENT)==1
  except Exception:
   print('TRACE',[hex(x) for x in trace],flush=True)
   print('FILTER FAULT',hex(u.reg_read(mk.UC_M68K_REG_PC)),hex(u.reg_read(mk.UC_M68K_REG_A7)),flush=True);raise
  for lane in range(6):
   value=struct.unpack('>h',bytes(u.mem_read(RAWBASE+128*lane+20+2*key,2)))[0]//256
   want=(100 if key==24 else 10)-(0 if lane==1 else 5)
   assert value==want,(code,lane,value,want,sent,len(calls))
  assert [data[0]&15 for data,port in sent]==[6,8,9,10,11],sent
  assert all(data[1]==cc and port==4 for data,port in sent)
  assert len(calls)==5
 print('PASS B TRACK + MACHINES + SWEEP/CONTOUR : vrais setters audio, CC74/71, masque avec piste B active',flush=True)
 u.mem_write(pat+264*4+1,b'\x01');sent.clear();r.delta=1;r.event(8,1,600);r.call(bs['mlkc_enc'],EVENT)
 assert all((data[0]&15)!=10 for data,port in sent)
 assert struct.unpack('>h',bytes(u.mem_read(RAWBASE+128*4+20+48,2)))[0]//256==96
 print('PASS voie MIDI muette : filtre audio modifie, aucun CC sortant',flush=True)

 # Appeler les vrais callbacks de la vue B, pas uniquement les helpers internes.
 r.stubs[0x4007faf4]=lambda a:0
 at=bs['ml_bank_ui_sync'];r.stubs[at]=lambda a:1;u.hook_add(UC_HOOK_CODE,r.stub,begin=at,end=at)
 r.w32(bs['TG_set_held'],0);r.w32(bs['ml_genie_settings'],0);r.w32(bs['mlp_func'],0);r.w32(bs['mlp_setup'],0)
 r.w32(r.s['br_history'],0x93300000)
 at=r.s['br_popup'];r.stubs[at]=lambda a:0;u.hook_add(UC_HOOK_CODE,r.stub,begin=at,end=at)
 tick=1000
 def rawkey(code,flags):
  nonlocal tick
  tick+=1;event=r.event(code,flags,tick);result=r.call(bs['mlp_menu_key'],OBJ,event)
  if not result:r.call(0x4007240c,event)
  return result
 r.w32(r.s['br_keys'],0);r.w32(r.s['br_requested'],0xffffffff)
 before=bytes(u.mem_read(pat,1584));assert rawkey(2,1)==1;assert rawkey(4,1)==1
 assert r.r32(r.s['br_keys'])==3 and r.r32(bs['mlp_obj'])==OBJ
 assert rawkey(20,1)==1 and r.r32(r.s['br_requested'])==4
 assert bytes(u.mem_read(pat,1584))==before,'division edite B'
 leds=[]
 for at,fn in [(0x400cfaf4,lambda a:0x931f8000),(0x40005f86,lambda a:leds.append(a) or 0)]:
  r.stubs[at]=fn;u.hook_add(UC_HOOK_CODE,r.stub,begin=at,end=at)
 out=0x931f9000;r.w32(out,0);r.call(bs['mlp_led'],OBJ+0x500,0xffffffff,out)
 assert len(leds)==16 and r.r32(out)&0x1fffe==0x1fffe
 assert rawkey(20,0)==1 and r.r32(r.s['br_requested'])==0xffffffff
 rawkey(4,0);rawkey(2,0);assert r.r32(r.s['br_keys'])==0
 print('PASS callbacks bruts B : TRACK+RETRIG+division, aucune edition/clavier B, seize LEDs, releases',flush=True)
 # Configuration B depuis les deux faces ; chaque masque reste independant.
 rawkey(2,1);a_mask=bytes(u.mem_read(maskaddr,1));b_mask=r.r32(r.s['bp_midi_mask'])
 assert rawkey(22,1)==1 and r.r32(r.s['bp_midi_mask'])==b_mask^1
 assert rawkey(22,9)==1 and r.r32(r.s['bp_midi_mask'])==b_mask^1
 assert rawkey(22,0)==1 and bytes(u.mem_read(maskaddr,1))==a_mask
 leds.clear();r.w32(out,0);r.call(bs['mlp_led'],OBJ,0xffffffff,out)
 assert [a[1] for a in leds]==list(range(1,13)) and r.r32(out)&0x1ffe==0x1ffe
 assert rawkey(22,1)==1;rawkey(22,0);rawkey(2,0)
 r.w32(r.s['br_keys'],1);r.w32(r.s['bp_ui_keys'],1)
 assert r.call(r.r32(0x40100ee8),OBJ,r.event(27,1))==1
 assert r.r32(r.s['bp_midi_mask'])==b_mask^32
 assert r.call(r.r32(0x40100ee8),OBJ,r.event(27,0))==1
 r.w32(r.s['bp_midi_mask'],b_mask);r.w32(r.s['br_keys'],0);r.w32(r.s['bp_ui_keys'],0)
 print('PASS configuration 12 pads A/B, masques independants, appui long et relache',flush=True)

 def draw(a):
  fmt=r.string(a[5]);label=r.string(a[6]) if fmt=='%s' else fmt%a[6] if '%d' in fmt else fmt
  r.texts.append((a[2],a[3],label));return 0
 r.stubs[0x40071a04]=draw
 assert rawkey(5,1)==1
 sent.clear();r.delta=-1;r.event(8,1,1200);r.call(bs['mlp_enc'],OBJ,EVENT)
 assert len(sent)==1 and sent[0][0][0]&15==8
 r.texts.clear();r.call(bs['mlp_render'],OBJ,0x93090000)
 assert 'FILTER B3' in [x[2] for x in r.texts],r.texts
 assert any(x[2].startswith('Cutoff ') for x in r.texts) and any(x[2].startswith('Reso ') for x in r.texts)
 assert r.r32(bs['mlp_obj'])==OBJ and r.r32(bs['mlp_setup'])==0
 rawkey(2,1);sent.clear();r.delta=1;r.event(9,1,1201);r.call(bs['mlp_enc'],OBJ,EVENT)
 assert len(sent)==4  # voie B4 muette et voie B2 exclue
 r.texts.clear();r.call(bs['mlp_render'],OBJ,0x93090000);assert 'FILTER ALL' in [x[2] for x in r.texts]
 rawkey(2,0);rawkey(5,0)
 delegated=[];at=r.s['bp_render_original'];r.stubs[at]=lambda a:delegated.append(a) or 0;u.hook_add(UC_HOOK_CODE,r.stub,begin=at,end=at)
 r.w32(bs['TG_blk_clk'],r.r32(bs['TG_blk_clk'])+1500);r.call(bs['mlp_render'],OBJ,0x93090000)
 assert delegated and r.r32(bs['mlp_obj'])==OBJ and r.r32(bs['mlp_setup'])==0
 print('PASS callback encodeur B : MACHINES seul / TRACK+MACHINES, valeurs filtre natives, expiration retourne B',flush=True)
 # Les sorties restent celles de B ; la destruction externe de la vue est simulee.
 r.w32(0x40fe4178,0x93005000);r.w32(0x93005000+88,0x93005500);r.w32(0x93005500+8,OBJ)
 dtor=0x93135000;r.w32(OBJ,VT);r.w32(VT+40,dtor)
 exits=[]
 def close(a):exits.append(a);r.w32(bs['mlp_obj'],0);return 0
 r.stubs[dtor]=close;u.hook_add(UC_HOOK_CODE,r.stub,begin=dtor,end=dtor)
 rawkey(12,1);assert exits and not r.r32(bs['mlp_obj'])
 r.w32(bs['mlp_obj'],OBJ);rawkey(1,1);rawkey(13,1)
 rawkey(2,3)
 assert len(exits)==2 and not r.r32(bs['mlp_obj']),(len(exits),r.r32(bs['mlp_func']),r.r32(bs['ml_genie_settings']),r.r32(bs['TG_set_held']),r.r32(bs['mlp_setup']))
 print('PASS BACK et accord FUNC+SETTINGS+TRACK atteignent la fermeture B existante',flush=True)
 print('LIMITES : I/O physiques et boucle sequence isolees ; verification hardware requise',flush=True)
if __name__=='__main__':main()
