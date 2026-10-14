#!/usr/bin/env python3
"""Audit branche indépendante : frontière boot -> initialisation native.

Compare l'OS stock et un catalogue sans TG jusqu'à l'entrée réelle du runtime.
Ne simule ni les caches ColdFire ni le cycle de vie complet : ne prouve pas
une correction de l'écran blanc matériel. Aucune page/main modifiée.
"""
import argparse,importlib.util,json,pathlib,struct
from unicorn import UC_HOOK_CODE,m68k_const as mk
from test_seq_gen_menu import Rig,STACK,STOP
from chord_keys_pr87 import load_stock
import build
TARGET=0x400cefa0
REGS=[getattr(mk,'UC_M68K_REG_'+n) for n in ['D2','D3','D4','D5','D6','D7','A2','A3','A4','A5','A6']]
def run(image,recipes):
 r=Rig(image,{'writes':[]},{'writes':[],'symbols':{}});u=r.u
 u.mem_map(0xfc044000,0x1000);u.mem_write(0xfc044000,struct.pack('>I',0x100))
 u.mem_write(STACK,struct.pack('>I',STOP));u.reg_write(mk.UC_M68K_REG_A7,STACK);u.reg_write(mk.UC_M68K_REG_SR,0x2700)
 expected={reg:0x93002000+4*i for i,reg in enumerate(REGS)}
 for reg,val in expected.items():u.reg_write(reg,val)
 ranges=[(build.BASE,image)]
 for t in recipes:
  for p in t.get('append',{}).get('parts',[]):
   if 'hex' in p:ranges.append((int(p['dest'],16),bytes.fromhex(p['hex'])))
 sites={at+i for at,b in ranges for i in range(0,len(b)-3,2) if b[i:i+2]==b'\x4e\x7b'}
 def movec(u,pc,size,data):u.reg_write(mk.UC_M68K_REG_PC,pc+4)
 for at in sites:u.hook_add(UC_HOOK_CODE,movec,begin=at,end=at)
 u.emu_start(0x40000530,TARGET,count=40000000)
 assert u.reg_read(mk.UC_M68K_REG_PC)==TARGET,'runtime non atteint'
 for reg,val in expected.items():assert u.reg_read(reg)==val,(reg,hex(u.reg_read(reg)),hex(val))
 assert u.reg_read(mk.UC_M68K_REG_A7)==STACK-4
 assert bytes(u.mem_read(STACK-4,4))==struct.pack('>I',0x4000055c)
 assert u.reg_read(mk.UC_M68K_REG_A0)==0xfc044000
 assert u.reg_read(mk.UC_M68K_REG_D0)==0x4007e020
 assert u.reg_read(mk.UC_M68K_REG_D1)==6
 assert bytes(u.mem_read(0xfc044000,4))==struct.pack('>I',0x106)
 assert u.reg_read(mk.UC_M68K_REG_SR)&0x2700==0x2700
 return u

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--cycles',required=True);p.add_argument('--catalog',required=True);p.add_argument('--build-module',required=True);a=p.parse_args()
 stock=load_stock(a.cycles);cat=json.loads(pathlib.Path(a.catalog).read_text());cat=cat.get('tweaks',cat) if isinstance(cat,dict) else cat
 assert not any(t['id'].startswith('model-tg') for t in cat)
 assert not any(t.get('append',{}).get('syntakt') for t in cat),'audit sans moteurs Syntakt'
 spec=importlib.util.spec_from_file_location('audit_build',a.build_module);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 img,_=build.apply_writes(stock,cat);extra,_=module.build_payload(cat,stock,None);full=bytes(img)+extra
 stock_u=run(stock,[]);u=run(full,cat)
 for cpu in [stock_u,u]:
  cpu.emu_start(TARGET,0x400cf012,count=100000)
  assert cpu.reg_read(mk.UC_M68K_REG_PC)==0x400cf012
  assert bytes(cpu.mem_read(0x40000000,1024))==struct.pack('>I',0x40001976)*256
  assert bytes(cpu.mem_read(0x422feec8,64))==bytes(64)
  assert bytes(cpu.mem_read(0x40fe4178,4))==bytes(4)
 assert bytes(stock_u.mem_read(0x422fef0c,40))==bytes(u.mem_read(0x422fef0c,40))
 print('PASS init vecteurs native : 256 entrées et état scheduler identiques ; singleton UI pas encore construit.')
 bank=next(t for t in cat if t['id']=='midi-bank-bundle');raw=bytes.fromhex(bank['append']['parts'][0]['hex']);dest=int(bank['append']['dest'],16)
 assert bytes(u.mem_read(dest,len(raw)))==raw
 for at in [0x4019b590,0x40210000,0x41000000,0x423380a0]:assert bytes(u.mem_read(at,16))==bytes(16),hex(at)
 print('PASS stock et sans TG : pile, D2-D7/A2-A6, IRQ masquées, registre matériel et entrée native400cefa0 ; RAW préservé.')
 print('LIMITATION : init native, interruptions et caches matériels après cette entrée restent à auditer ; écran blanc non corrigé.')
if __name__=='__main__':main()
