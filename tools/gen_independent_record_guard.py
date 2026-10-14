#!/usr/bin/env python3
"""Prototype branche : bornes records natifs, sans TG ni moteurs ajoutés.

Préserve les records des six machines stock. Un ancien index non disponible
utilise le record KICK au lieu du pointeur hors table natif. Ceci ne prouve
pas que l'écran blanc vient des records ; aucun flasher principal modifié.
"""
import argparse,copy,json,pathlib,struct,subprocess,tempfile
import aplib_dense,build
from chord_keys_pr87 import load_stock

def generate(stock,data):
 t=copy.deepcopy(data);assert t['core']['id']=='performance-core' and not t.get('engine')
 b=t['bank'];ap=b['append'];origin=int(ap['dest'],16);raw=bytearray.fromhex(ap['parts'][0]['hex']);s={k:int(v,16) for k,v in b['symbols'].items()};start=origin+len(raw)
 assert start==s['ML_BANK_END'] and start%4==0
 assert not any(build.BASE+w['off'] in [0x4004df5c,0x4004df76] for x in [t['core'],*t.get('supports',[]),b] for w in x.get('writes',[]))
 source='''.text
.globl safe_record_at,safe_record_of
safe_record_at:
 moveq #6,%d1
 movel %sp@(4),%d0
 cmpl %d0,%d1
 bcc .Lat
 moveq #1,%d0
.Lat:
 jmp 0x4004df62
safe_record_of:
 moveq #5,%d1
 movel %sp@(4),%d0
 cmpl %d0,%d1
 bcc .Lof
 moveq #0,%d0
.Lof:
 jmp 0x4004df7c
'''
 with tempfile.TemporaryDirectory() as d:
  p=pathlib.Path(d);(p/'guard.s').write_text(source)
  subprocess.run(['m68k-elf-as','-march=cfv4e','-o',str(p/'guard.o'),str(p/'guard.s')],check=True)
  subprocess.run(['m68k-elf-ld','-Ttext='+hex(start),'-o',str(p/'guard.elf'),str(p/'guard.o')],check=True,stderr=subprocess.DEVNULL)
  subprocess.run(['m68k-elf-objcopy','-O','binary',str(p/'guard.elf'),str(p/'guard.bin')],check=True)
  code=(p/'guard.bin').read_bytes();syms={r[2]:int(r[0],16) for l in subprocess.check_output(['m68k-elf-nm',str(p/'guard.elf')],text=True).splitlines() if len(r:=l.split())==3}
 raw+=code;raw+=bytes((-len(raw))%16);end=origin+len(raw);assert (end-origin+16383)//16384==b['cache_blocks']
 off=s['ml_boot_skip']-origin;assert raw[off:off+6]==b'\x20\x7c'+struct.pack('>I',start);raw[off+2:off+6]=struct.pack('>I',end)
 for at,name,old in [(0x4004df5c,'safe_record_at','7206202f0004'),(0x4004df76,'safe_record_of','7205202f0004')]:
  assert stock[at-build.BASE:at-build.BASE+6].hex()==old;b['writes'].append(dict(off=at-build.BASE,old=old,new=(b'\x4e\xf9'+struct.pack('>I',syms[name])).hex()))
 packed=aplib_dense.pack(bytes(raw),depth=128);assert int(ap['at'],16)+len(packed)<=build.END_LIMIT
 ap.update(size=len(raw),parts=[dict(dest=hex(origin),hex=raw.hex())],compressed_hex=packed.hex());b['symbols'].update({k:hex(v) for k,v in syms.items()},ML_BANK_END=hex(end),ML_BANK_SIZE=hex(len(raw)));t['record_boundary_guard']={'hardware_verified':False,'unsupported_record':'KICK','white_screen_cause_confirmed':False}
 return t

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['cycles','candidate','output']:p.add_argument('--'+n,required=True)
 p.add_argument('--check',action='store_true');a=p.parse_args();data=generate(load_stock(a.cycles),json.loads(pathlib.Path(a.candidate).read_text()));text=json.dumps(data,ensure_ascii=False,indent=1)+'\n';out=pathlib.Path(a.output)
 if a.check:assert out.read_text()==text
 else:out.write_text(text)
 print('ok : prototype records bornés ; démarrage matériel non confirmé')
if __name__=='__main__':main()
