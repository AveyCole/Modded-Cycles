#!/usr/bin/env python3
"""Records invalides hors table : natif stock vs garde indépendante.

Chargement direct du code pour ce contrat isolé ; pas une preuve de boot.
"""
import argparse,json,pathlib
from test_seq_gen_menu import Rig
from test_step_delete_reset import image
from chord_keys_pr87 import load_stock

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--cycles',required=True);p.add_argument('--candidate',required=True);a=p.parse_args();stock=load_stock(a.cycles);t=json.loads(pathlib.Path(a.candidate).read_text());cat=[t['core'],*t.get('supports',[]),t['bank']]
 old=Rig(stock,{'writes':[]},{'writes':[],'symbols':{}});new=Rig(image(stock,cat),{'writes':[]},{'writes':[],'symbols':{}})
 for entry,limit,fallback in [(0x4004df5c,6,1),(0x4004df76,5,0)]:
  kick=old.call(entry,fallback)
  for n in list(range(256))+[-1,0x7fffffff,0x80000000]:
   native=old.call(entry,n&0xffffffff);actual=new.call(entry,n&0xffffffff)
   assert actual==(native if 0<=n<=limit else kick),(hex(entry),n,hex(native),hex(actual),hex(kick))
  assert old.call(entry,7)==0x40a714f4
 print('PASS 2 helpers ×259 indices : records stock identiques ; invalides vers KICK, plus de record à base−76.')
 print('LIMITATION : sauvegardes/projets et démarrage matériel non reproduits ; cause écran blanc non confirmée.')
if __name__=='__main__':main()
