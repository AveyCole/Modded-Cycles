#!/usr/bin/env python3
"""Callbacks froids no-TG : ABI, délégation stock et absence d'accès UI.

Les fonctions audio stock sont observées comme délégations, pas simulées.
Contexte Banque/LFO nul ; aucun getter UI ou allocateur ne doit être appelé.
Cette preuve isolée ne reproduit pas un cycle d'interruptions matériel.
"""
import argparse,json,pathlib
from unicorn import m68k_const as mk,UC_HOOK_CODE
from test_seq_gen_menu import Rig,OBJ
from test_step_delete_reset import image
from chord_keys_pr87 import load_stock

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--cycles',required=True);p.add_argument('--candidate',required=True);a=p.parse_args();stock=load_stock(a.cycles);t=json.loads(pathlib.Path(a.candidate).read_text());assert t['core']['id']=='performance-core';cat=[t['core'],*t.get('supports',[]),t['bank']];b=t['bank'];core={k:int(v,16) for k,v in t['core']['symbols'].items()};r=Rig(image(stock,cat),{'writes':[]},{'writes':[],'symbols':b['symbols']});s=r.s;u=r.u;seen=[]
 for at in [0x400802e0,0x4000f23e,0x400cf866,0x40012412,0x400060d8,0x400d0974]:
  def forbidden(args,at=at):raise AssertionError('accès UI/allocation à froid '+hex(at))
  r.stubs[at]=forbidden
 def delegate(name,n):
  def f(args):seen.append((name,list(args[:n])));return 0x76543210
  return f
 for at,name,n in [(0x40053330,'audio',0),(0x400567ba,'output',2),(0x40091ab2,'lfo',3),(0x400a7db0,'voice-on',0),(0x400a7de0,'voice-off',0)]:
  if at not in r.stubs:u.hook_add(UC_HOOK_CODE,r.stub,begin=at,end=at)
  r.stubs[at]=delegate(name,n)
 assert r.r32(s['ml_context'])==0 and r.r32(s['mlcc_context'])==0
 for sr in [0x2000,0x2700]:
  u.reg_write(mk.UC_M68K_REG_SR,sr);seen.clear();r.call(s['ml_audio_hook']);assert seen==[('audio',[])],seen
  seen.clear();r.call(s['mlcc_audio'],0x93002000,11,22);assert seen==[('lfo',[0x93002000,11,22])],seen
  seen.clear();before=r.r32(core['blk_clk']);r.call(core['core_audio_end'],0x93002000,33);assert seen==[('output',[0x93002000,33])],seen;assert r.r32(core['blk_clk'])==before+1
  seen.clear();r.w32(0x93006000,0);u.reg_write(mk.UC_M68K_REG_A3,0x93006000);u.reg_write(mk.UC_M68K_REG_A6,OBJ);u.reg_write(mk.UC_M68K_REG_D1,0x93007000);r.call(core['core_pre']);assert seen==[('voice-off',[])],seen
 print('PASS IPL0/IPL7 : callbacks audio/LFO/output et voix inactive ; délégations et arguments exacts, pas UI/allocation.')
 print('LIMITATION : DSP stock, caches et interruptions physiques non reproduits ; écran blanc non corrigé.')
if __name__=='__main__':main()
