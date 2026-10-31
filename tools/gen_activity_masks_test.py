"""Prototype2.65 : PUNCH stock, masques LFO et voix Wizard independante du mix principal."""
from pathlib import Path
import argparse,hashlib,json,math,os,struct,subprocess,sys
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from gen_governor_recovery_test import read,BASE,START
from mtlib import aplib,container
from mtlib.syx import wrap,BYTES_PER_MSG
from bootstrap205_assets import pack
import aplib_grow
CODE=0x4691a000;BSS=0x4691f000;S=R/'tools/machines/acid'
def main():
 global CODE
 p=argparse.ArgumentParser()
 for k in ('source','metadata','cycles','output'):p.add_argument('--'+k,type=Path,required=True)
 p.add_argument('--check',action='store_true');p.add_argument('--emac-dsp',action='store_true');p.add_argument('--reverb-network-opt',action='store_true');p.add_argument('--stock-voice-protection',action='store_true');p.add_argument('--stock-native-idle',action='store_true');p.add_argument('--routing-fast-path',action='store_true');p.add_argument('--sram-mixer',action='store_true');p.add_argument('--stock-selection-only',action='store_true');p.add_argument('--audio-profile',action='store_true');p.add_argument('--mono-mixer-reuse',action='store_true');p.add_argument('--one-mod-osc',action='store_true');p.add_argument('--baremetal-routing',action='store_true')
 a=p.parse_args();assert not a.baremetal_routing or (a.routing_fast_path and not a.one_mod_osc and not a.mono_mixer_reuse);assert not a.mono_mixer_reuse or a.routing_fast_path;assert not (a.stock_selection_only and a.stock_voice_protection);assert not a.stock_native_idle or a.stock_voice_protection;sha=lambda b:hashlib.sha256(b).hexdigest();raw=a.source.read_bytes();m=json.loads(a.metadata.read_text(encoding='utf-8'));assert sha(raw)==m['sha256'];assert (m.get('acid_articulation',{}).get('arp_retrigger') or 'ae_mode' not in m['per_track_fx']['symbols']) and m['sha256'] in ('8d9d7df60e212c1c8e1848c0e3b2d015c8e9a2d91269efde5177431d4554e72f','09c5352b647f6c50a0d1a4eca710739d30d9a1a12247513cf51824af2c82b111','e564a32da1bba5bc022ac776eebcfbe0c18b8a8e7dbe9b8c8fdca05861de7c5c','4630dd01d50f860bc57980d865dd262f7e955d6599d55db5ea683e739ee5e26f')
 assert sha(a.cycles.read_bytes())=='44fe586269631a0ca7da25a3383fc6733c314809505fc3cc52f1e0ed9800640c'
 _,_,stock,ops=read(a.cycles);info,pkg,image,_=read(a.source);image=bytearray(image);O=a.output;O.mkdir(parents=True,exist_ok=True)
 cross='H:/CREATURE-source/retrosyn-integration/build/m68k-toolchain/pkg/bin/m68k-elf-';os.environ['PATH']=str(Path(cross).parent)+os.pathsep+os.environ.get('PATH','')
 def run(t,*v):return subprocess.check_output([cross+t+'.exe',*map(str,v)],text=True)
 optional='rm_step' not in m['per_track_fx']['symbols']
 if optional:CODE=0x4691c400
 full='ae_mode' in m['per_track_fx']['symbols'];assert m['per_track_fx']['symbols']['lt_bss_end']<=CODE
 network_blob=b'';network=None
 if a.reverb_network_opt:
  assert a.emac_dsp
  from reverb_network_assets import prepare
  network_blob,network=prepare(R,O,m,run);network_blob+=bytes((-len(network_blob))&3)
 aliases={**m['direct_jump']['aliases'],**m['direct_jump']['symbols'],**m['acid_articulation']['symbols'],**m['per_track_fx']['symbols']};aliases['pp_native']=aliases['mf_old_voice_playability'];aliases.pop('pp_voice_loop');aliases.pop('li_dispatch')
 lfo=(R/'tools/machines/track_fx/lfo-direct.c').read_text(encoding='utf-8').replace('volatile u32 li_noapply,li_active_tracks[3];','extern volatile u32 li_noapply;volatile u32 li_active_tracks[3];')
 (O/'lfo.c').write_text(lfo)
 (O/'punch.c').write_text('#define PP_UNIQUE 1\n#define PP_REMOVE_LEGACY '+str(int(not optional))+'\n'+(R/'tools/machines/track_fx/voice-punch.c').read_text(encoding='utf-8'))
 (O/'wizard-usb.S').write_text('.text\n.globl am_wizard_usb\nam_wizard_usb:\n moveq #0,%d0\n move.b 0x40002ceb,%d0\n cmpi.l #0x38,%d0\n bne.s 1f\n move.l %d2,-(%sp)\n move.l %d1,%d2\n lsl.l #2,%d2\n jmp 0x401adbfc\n1: jmp 0x401adc3a\n')
 assert image[0x4000053a-BASE:0x40000542-BASE]==stock[0x4000053a-BASE:0x40000542-BASE]
 with (O/'wizard-usb.S').open('a') as f:f.write('.globl am_boot_finish\nam_boot_finish:\n lea -8(%sp),%sp\n movem.l %d0/%a1,(%sp)\n lea 0x401adbf6,%a1\n move.w #0x4ef9,(%a1)+\n move.l #am_wizard_usb,(%a1)\n movem.l (%sp),%d0/%a1\n lea 8(%sp),%sp\n.byte '+','.join(map(str,stock[0x4000053a-BASE:0x40000542-BASE]))+'\n jmp 0x40000542\n')
 aliases.update(mb_old_key=m['acid_articulation']['symbols']['sg_key'],mb_old_encoder=m['acid_articulation']['symbols']['sg_encoder'],mb_old_draw=m['acid_articulation']['symbols']['sg_draw'],mb_old_edit=m['direct_jump']['symbols']['jp_edit'],mb_old_frame=m['acid_articulation']['symbols']['sg_frame'],mb_native_rotate=int.from_bytes(image[0x400a2714-BASE:0x400a2718-BASE],'big'))
 for name in ('machine-confirm.c','machine-confirm-menu.c'):(O/name).write_text((R/'tools/machines/track_fx'/name).read_text(encoding='utf-8'))
 if optional:
  fx=m['fx_menu']['symbols'];aliases.update({k:fx[v] for k,v in [('rm_machine_valid','machine_valid'),('rm_machine_stamp','machine_stamp'),('rm_machine_result','machine_result')]})
  order=list(range(17))+list(range(18,28))+[17] if full else list(range(6))
  f=O/'machine-confirm.c';body=f.read_text(encoding='utf-8').replace('if(machine==21)machine=4;','')
  body=body.replace('extern const u8 rm_order[];extern const u32 rm_count;', 'static const u8 rm_order[]={'+','.join(map(str,order))+'};static const u32 rm_count='+str(len(order))+';\nu32 mb_display_count;static u32 mb_enabled(u32 m){u32 md=*(volatile u32*)(0x4683c800+41*56+12)==(27u<<8),mask=md?*(volatile u32*)0x469c423c:*(volatile u32*)0x468d0ff0;if(!md&&!mask)mask=0x7ffff;return m<6||(m<28&&((mask>>(m-6))&1));}')
  body=body.replace('if(delta>0&&pos+1<rm_count)pos++;if(delta<0&&pos)pos--;', 'if(delta)for(s32 i=(s32)pos+(delta>0?1:-1);i>=0&&i<(s32)rm_count;i+=delta>0?1:-1)if(mb_enabled(rm_order[i])){pos=(u32)i;break;}')
  f.write_text(body,encoding='utf-8')
 view=(R/'tools/machines/direct_jump/global.S').read_text(encoding='utf-8').replace('mf_global_draw','mb_global_draw').replace('ae_global_edit','mb_edit').replace('gc_tree_row','mb_tree_row').replace('moveq #11,%d0','moveq #13,%d0')
 view=view.replace('    jsr mb_tree_row','    clrb %a0@(1004)\n    clrb %a0@(1088)\n    jsr mb_tree_row',1)
 if not full:
  view=view.replace('moveq #13,%d0','moveq #12,%d0').replace('    clrb %a0@(1088)\n','')
  menu_source=O/'machine-confirm-menu.c';body=menu_source.read_text(encoding='utf-8').replace('rows[13]={0,0,1,2,3,4,5,8,9,10,11,12,13}','rows[12]={0,0,1,2,3,4,5,8,9,10,11,12}').replace('(d>0?1:12))%13','(d>0?1:11))%12');menu_source.write_text(body,encoding='utf-8')
 view=view.replace('.Lallocator: .byte 0','.Lmac: .asciz "Mac"\n.Ljump: .asciz "JUMP"\n.Lallocator: .byte 0')
 at=view.index('.Lts_rows:');prefix,rows=view[:at+len('.Lts_rows:')],view[at+len('.Lts_rows:'):]
 entries=[line for line in rows.splitlines() if line.startswith('.long') and (full or 'ae_value' not in line)];entries.insert(1,'.long 0,0,0,.Lmac,0,1,.Lts_label,0,0,0,0,0,0,1,mb_value,0,0,0,0,0,0');entries.append('.long 0,0,0,.Ljump,0,1,.Lts_label,0,0,0,0,0,0,1,jp_value,0,0,0,0,0,0')
 callbacks='typedef unsigned int u32;extern volatile u32 gc_tree_cursor;\n'
 for i,line in enumerate(entries):
  fields=line.split(',');fn=fields[14];wrapper='mb_callback'+str(i);fields[14]=wrapper;entries[i]=','.join(fields)
  callbacks+=f'extern void {fn}(u32,u32,u32,u32,u32);void {wrapper}(u32 a,u32 b,u32 c,u32 x,u32 y){{u32 saved=gc_tree_cursor;if(saved>1)gc_tree_cursor--;{fn}(a,b,c,x,y);gc_tree_cursor=saved;}}\n'
 (O/'browse-global.S').write_text(prefix+'\n'+'\n'.join(entries)+'\n');(O/'browse-values.c').write_text(callbacks)
 with (O/'wizard-usb.S').open('a') as f:
  for name,at in (('mb_native_key',0x400a292c),('mb_native_draw',0x400a24ca)):
   assert image[at-BASE:at-BASE+8]==stock[at-BASE:at-BASE+8]
   f.write(f'.globl {name}\n{name}:\n.byte '+','.join(map(str,stock[at-BASE:at-BASE+8]))+f'\n jmp {at+8:#x}\n')
 assert image[0x400a25e0-BASE:0x400a25e8-BASE]==bytes.fromhex('701841f940071a04' if full else '700541f940071a04')
 with (O/'wizard-usb.S').open('a') as f:f.write('.globl mb_display_hook\nmb_display_hook:\n lea -16(%sp),%sp\n movem.l %d0-%d1/%a0-%a1,(%sp)\n move.l %a2,-(%sp)\n move.l %d3,-(%sp)\n jsr mb_display_machine\n addq.l #8,%sp\n move.l %d0,%d3\n movem.l (%sp),%d0-%d1/%a0-%a1\n lea 16(%sp),%sp\n moveq #'+str(24 if full else 5)+',%d0\n lea 0x40071a04,%a0\n jmp 0x400a25e8\n')
 if a.emac_dsp:
  import re
  original=subprocess.check_output(['git','show','909e6a0:tools/machines/fx_menu/dsp.c'],cwd=R).decode('utf-8')
  body=original[original.index('/* Mixeur EMAC natif.'):original.index('void fx_post(')]
  wet_start=body.index(')for(u32 i=0;i<64;i++){',body.index('/* Gain wet seul'))
  wet_end=body.index('\n#endif',wet_start)
  body=body[:wet_start]+')wet_gain(out);'+body[wet_end:]
  fade_start=body.index(' if(gain!=256||prior_gain!=256)')
  fade_end=body.index('\n#ifdef FX_SIDECHAIN_RETURNS',fade_start)
  body=body[:fade_start]+' if(gain!=256||prior_gain!=256)fade_block(out,prior_gain,gain);'+body[fade_end:]
  if a.reverb_network_opt:
   dispatch_start=body.index(' if(active==0)ch_native')
   default_start=body.index('#ifdef FX_LEAN_FX\n else{',dispatch_start)
   dispatch_end=body.index('#ifdef FX_REVERB101\n /* Gain wet seul',default_start)
   fallback=body[default_start:dispatch_end].replace(' else{',' {')
   dispatch=' switch(active){\n case 0:ch_native(out,in,params);break;\n case 1:case 2:{s16 p[2]={(s16)(fx_speed*256),(s16)(fx_depth*256)};ch_chorus(out,in,p,active,256);break;}\n case 7:fx_ps1(out,in,params);break;\n case 8:fx_room(out,in,params);break;\n case 9:fx_ring(out,in);break;\n case 10:fx_gated(out,in,params);break;\n case 11:fx_hall(out,in,params);break;\n default:{\n'+fallback+'break;}}\n'
   body=body[:dispatch_start]+dispatch+body[dispatch_end:]
  states=('active','ready','gain','prior_gain','correction_on','gain_aux','left','right','aux','effect','correction','dust_target')
  for name in states:
   body=re.sub(r'\b'+name+r'\b','em_state_'+name,body);aliases['em_state_'+name]=m['fx_menu']['symbols'][name]
  for name in ('fx_side','fx_side_on','ch_state','fx_vinyl','fx_vinyl_reset','ch_mode','ch_native','ch_chorus','fx_speed','fx_depth','fx_aux_vi','fx_aux_ch','fx_ps1','fx_room','fx_hall','fx_ring','fx_gated'):
   if name in m['fx_menu']['symbols']:aliases[name]=m['fx_menu']['symbols'][name]
  body=body.replace('void fx_reverb(', 'void em_reverb(')
  declarations='extern u32 em_state_active,em_state_ready,em_state_gain,em_state_prior_gain,em_state_correction_on,em_state_dust_target[2];\nextern s32 em_state_gain_aux[2][6],em_state_left[192],em_state_right[192],em_state_aux[64],em_state_effect[64],em_state_correction[64];\nextern volatile u32 fx_side,fx_side_on;extern u8 ch_state[];extern void fx_vinyl(s32*,const s32*),fx_hall(s32*,const s32*,const s16*);\n'
  (O/'emac-dsp.c').write_text('#include "fx.h"\n#include "emac-math.h"\n'+declarations+body)
 if a.routing_fast_path:
  bridge=(R/'tools/machines/track_fx/firmware-bridge.c').read_text(encoding='utf-8')
  bridge=bridge.replace('extern u32 lt_active,','extern volatile u32 mf_requested;\nextern u32 lt_active,')
  bridge=bridge.replace('if(mf_mode&&mf_audio_ready&&((u32)g==','if(mf_requested&&mf_mode&&mf_audio_ready&&((u32)g==')
  bridge=bridge.replace('mf_old_post(mix);if(!mf_mode||!mf_audio_ready)return;','mf_old_post(mix);if(!mf_mode||!mf_audio_ready||(!mf_requested&&!lt_active))return;')
  for old,new in (('mf_sum6','sf_sum6'),('mf_sum7','sf_sum7'),('mf_post','sf_post')):bridge=bridge.replace('void '+old+'(','void '+new+'(')
  if a.baremetal_routing:
   from baremetal_routing_assets import apply
   bridge=apply(bridge)
  if a.mono_mixer_reuse:
   from mono_mixer_assets import apply
   bridge=apply(bridge)
  (O/'routing-fast.c').write_text(bridge,encoding='utf-8')
 osc_sources=[]
 if a.one_mod_osc:
  aliases['om_previous']=m['per_track_fx']['symbols']['dry_osc'];(O/'one-mod-osc.S').write_text((R/'tools/machines/track_fx/one-mod-osc.S').read_text(encoding='utf-8'),encoding='utf-8');osc_sources=[O/'one-mod-osc.S']
 profile_sources=[];profile_hooks=[];profile=None
 if a.audio_profile:
  from audio_profile_assets import prepare
  profile_sources,profile_hooks,profile=prepare(R,O,m,image,BASE);aliases.update(m['fx_menu']['symbols'])
 # Installer les relais UI apres les chargeurs2.64 qui possedent les memes slots.
 late=[(0x400a2712,'mb_rotate'),(0x400a292c,'mb_key'),(0x400a25e0,'mb_display_hook'),(m['fx_menu']['symbols']['fx_machine_step'] if optional else m['per_track_fx']['symbols']['rm_step'],'mb_step')]
 for key,target in (('key','mb_gc_key'),('encoder','mb_gc_encoder'),('draw','mb_gc_draw')):late.append((m['groove_strum']['symbols']['gc_'+key],target))
 if network:
  for old,new in (('fx_room','er_room_core'),('fx_hall','er_hall_core'),('fx_ps1_cold','er_ps1_core'),('ps_ap_kernel','er_ps_ap_kernel')):
   aliases[new]=network['symbols'][new];late.append((m['fx_menu']['symbols'][old],new))
 if a.routing_fast_path:
  for old,new in (('mf_sum6','sf_sum6'),('mf_sum7','sf_sum7'),('mf_post','sf_post')):late.append((m['per_track_fx']['symbols'][old],new))
 if a.one_mod_osc:
  assert image[0x400a8152-BASE:0x400a815a-BASE]==bytes.fromhex('45e8006c2f4c0040')
  late.extend([(0x400a82cc,'om_osc'),(0x400a8152,'om_first')])
 late+=profile_hooks
 late.append((m['lfo_reload']['symbols']['xp_frame'],'mb_frame'))
 if a.emac_dsp:late.append((m['fx_menu']['symbols']['fx_reverb'],'em_reverb'))
 asm=(O/'wizard-usb.S').read_text(encoding='utf-8');needle=' lea 0x401adbf6,%a1\n'
 if optional:
  asm=asm.replace(' moveq #24,%d0\n lea 0x40071a04,%a0',' move.l mb_display_count,%d0\n lea 0x40071a04,%a0').replace(' moveq #5,%d0\n lea 0x40071a04,%a0',' move.l mb_display_count,%d0\n lea 0x40071a04,%a0')
  asm=asm.replace(needle,' moveq #0,%d0\n move.b 0x400a25e1,%d0\n move.l %d0,mb_display_count\n'+needle,1)

 extra=''
 for at,fn in late:extra+=f' lea {at:#x},%a1\n move.w #0x4ef9,(%a1)+\n move.l #{fn},(%a1)\n'
 asm=asm.replace(needle,extra+needle)
 if network:
  asm=asm.replace(' lea -8(%sp),%sp\n movem.l %d0/%a1,(%sp)',' lea -12(%sp),%sp\n movem.l %d0/%a0-%a1,(%sp)').replace(' movem.l (%sp),%d0/%a1\n lea 8(%sp),%sp',' movem.l (%sp),%d0/%a0-%a1\n lea 12(%sp),%sp')
  copy=f' move.l er_source,%a0\n lea {network["code"]:#x},%a1\n move.l #{len(network_blob)//4},%d0\n.Lnetcopy: move.l (%a0)+,(%a1)+\n subq.l #1,%d0\n bne.s .Lnetcopy\n'
  asm=asm.replace(' movem.l %d0/%a0-%a1,(%sp)\n',' movem.l %d0/%a0-%a1,(%sp)\n'+copy,1)
  asm+='\n.data\n.balign 4\n.globl er_source\ner_source: .long 0\n'
 (O/'wizard-usb.S').write_text(asm)
 if a.stock_voice_protection or a.sram_mixer or a.stock_selection_only:
  end=int.from_bytes(image[0x40195ad0-BASE:0x40195ad4-BASE],'big')-BASE;raw_rt=image[START:end]
  runtime,_=aplib.depack(struct.pack('>II',len(raw_rt),sum(raw_rt)&0xffffffff)+raw_rt)
 if a.stock_selection_only:
  anchor=bytes.fromhex('2800ef8c41f980001858');keyoff=runtime.find(anchor);assert keyoff>=0 and runtime.count(anchor)==1
  assert 0x5858<=keyoff<0x7878;ss_key=0x8000cac0+keyoff-0x5858
  asm=(O/'wizard-usb.S').read_text(encoding='utf-8');asm=asm.replace(' lea 0x401adbf6,%a1\n',f' lea {ss_key:#x},%a1\n move.w #0x4ef9,(%a1)+\n move.l #ss_stock_key,(%a1)\n lea 0x401adbf6,%a1\n')
  asm+='\n.text\n.globl ss_stock_key\nss_stock_key:\n move.l %d0,%d1\n lsl.l #5,%d1\n add.l %d0,%d1\n add.l %d1,%d1\n lea 0x8000102c,%a0\n moveq #0,%d2\n move.b (%a0,%d1.l),%d2\n cmpi.l #6,%d2\n bcc.s .Lss_added\n moveq #-1,%d2\n rts\n.Lss_added:\n.byte '+','.join(map(str,anchor))+f'\n jmp {ss_key+10:#x}\n'
  (O/'wizard-usb.S').write_text(asm)
 if a.sram_mixer:
  at=0x8000ea48;offset=0x5858+at-0x8000cac0;kernel=stock[0x40056698-BASE:0x40056716-BASE]
  assert len(kernel)==126 and not any(runtime[offset:offset+152])
  assert kernel[:8]==bytes.fromhex('4fefffd848d73cfc') and kernel[-2:]==bytes.fromhex('4e75')
  (O/'sram-mixer.bin').write_bytes(kernel)
  asm=(O/'wizard-usb.S').read_text(encoding='utf-8');asm=asm.replace(' lea 0x401adbf6,%a1\n',' lea 0x8000ea48,%a1\n'+''.join(f' move.w #{int.from_bytes(kernel[i:i+2],"big")},(%a1)+\n' for i in range(0,len(kernel),2))+' lea '+hex(m['per_track_fx']['symbols']['mf_old_sum7'])+',%a1\n move.w #0x4ef9,(%a1)+\n move.l #0x8000ea48,(%a1)\n lea 0x401adbf6,%a1\n');(O/'wizard-usb.S').write_text(asm)
 if a.stock_voice_protection:
  off=0x5858+0x8000e8a4-0x8000cac0
  assert runtime[off:off+20]==bytes.fromhex('2f0243f946732000202f00087206b2af00106720')
  anchor=bytes.fromhex('4ab9401bcc80670ab2b9401bcc64');quiet_off=runtime.find(anchor);assert quiet_off>=0 and runtime.find(anchor,quiet_off+1)<0
  asm=(O/'wizard-usb.S').read_text(encoding='utf-8')
  asm=asm.replace(' lea 0x401adbf6,%a1\n',' lea 0x8000e8b6,%a1\n move.b #0x64,(%a1)\n lea 0x401adbf6,%a1\n')
  if not a.stock_native_idle:
   asm=asm.replace(' lea 0x401adbf6,%a1\n',' lea 0x401adb4c,%a1\n move.w #0x4ef9,(%a1)+\n move.l #sp_stock_quiet,(%a1)\n lea 0x401adbf6,%a1\n')
   asm+='\n.text\n.globl sp_stock_quiet\nsp_stock_quiet:\n move.l (%a0),%d0\n cmpi.l #5,%d0\n bls.s .Lstock_run\n.byte '+','.join(map(str,runtime[quiet_off:quiet_off+6]))+'\n jmp 0x401adb52\n.Lstock_run: moveq #0,%d0\n rts\n'
  (O/'wizard-usb.S').write_text(asm)

 objects=[]
 for src in (O/'lfo.c',O/'punch.c',O/'wizard-usb.S',O/'machine-confirm.c',O/'machine-confirm-menu.c',O/'browse-global.S',O/'browse-values.c')+((O/'emac-dsp.c',) if a.emac_dsp else ())+((O/'routing-fast.c',) if a.routing_fast_path else ())+tuple(profile_sources)+tuple(osc_sources):
  obj=O/(src.stem+'.o');run('gcc','-mcpu=54418','-O3','-ffreestanding','-fno-builtin','-fno-pic','-fno-stack-protector','-fwrapv','-Wall','-Wextra','-Werror','-Wno-misleading-indentation',*(['-I',str(R/'tools/machines/fx_menu')] if src.name=='audio-profile-keys.c' else []),*(['-fno-unroll-loops','-DFX_LEAN_FX','-DFX_VOICE_OPT','-DFX_DUST','-DFX_PS1','-DFX_CHEAP','-DFX_EXTRA','-DFX_GATED','-DFX_REVERB101','-DFX_POLISH','-DFX_SIDECHAIN_RETURNS',*(['-DFX_FAST_WRAPPER'] if a.reverb_network_opt else []),'-I',str(R/'tools/machines/fx_menu'),'-I',str(R/'tools/machines/track_fx')] if src.name=='emac-dsp.c' else []),'-c',src,'-o',obj);objects.append(obj)
 (O/'module.ld').write_text(f'SECTIONS {{ .text {CODE:#x} : {{ *(.text*) *(.rodata*) }} . = ALIGN(4); .data : {{ *(.data*) }} .bss {BSS:#x} (NOLOAD) : {{ *(.bss*) *(COMMON) }} aa_end = .; }}\n'+''.join(f'PROVIDE({k} = {v:#x});\n' for k,v in aliases.items()))
 run('ld','-T',O/'module.ld','-e','am_wizard_usb','-o',O/'module.elf',*objects);run('objcopy','-O','binary',O/'module.elf',O/'module.bin');sy={v[2]:int(v[0],16) for line in run('nm',O/'module.elf').splitlines() if len(v:=line.split())==3};blob=(O/'module.bin').read_bytes();blob+=bytes((-len(blob))&3);assert CODE+len(blob)<=BSS and sy['aa_end']<0x46920000
 oldentry=int.from_bytes(image[0x40195adc-BASE:0x40195ae0-BASE],'big');pad=(-len(image))&3;loader=BASE+len(image)+pad;source=loader+512
 # La continuation native ne revient pas : installer avant le saut de fin.
 load=f'.text\n.globl aa_load\naa_load:\n lea -12(%sp),%sp\n movem.l %d0/%a0-%a1,(%sp)\n lea {source:#x},%a0\n lea {CODE:#x},%a1\n move.l #{len(blob)//4},%d0\n1: move.l (%a0)+,(%a1)+\n subq.l #1,%d0\n bne.s 1b\n lea {BSS:#x},%a0\n move.l #{(sy["aa_end"]-BSS+3)//4},%d0\n2: clr.l (%a0)+\n subq.l #1,%d0\n bne.s 2b\n'
 hooks=[]
 for at,target in ((m['per_track_fx']['symbols']['li_dispatch'],'li_dispatch'),(m['per_track_fx']['symbols']['pp_voice_loop'],'pp_voice_loop'),(0x4000053a,'am_boot_finish')):
  hooks.append(dict(at=at,target=sy[target]));load+=f' lea {at:#x},%a0\n move.l #0x4ef9,%d0\n move.w %d0,(%a0)+\n move.l #{sy[target]:#x},%d0\n move.l %d0,(%a0)\n'
 if network:load+=f' lea {sy["er_source"]:#x},%a0\n move.l #{source+len(blob):#x},(%a0)\n'
 load+=f' movem.l (%sp),%d0/%a0-%a1\n lea 12(%sp),%sp\n jmp {oldentry:#x}\n';(O/'load.S').write_text(load)
 run('gcc','-mcpu=54418','-c',O/'load.S','-o',O/'load.o');run('ld','-Ttext',hex(loader),'-e','aa_load','-o',O/'load.elf',O/'load.o');run('objcopy','-O','binary',O/'load.elf',O/'load.bin');stub=(O/'load.bin').read_bytes();assert len(stub)<=512
 struct.pack_into('>I',image,0x40195adc-BASE,loader);image+=bytes(pad)+stub+bytes(512-len(stub))+blob+network_blob
 from title204_assets import apply as apply_title
 def title_patch(at,old,new,buf):
  assert bytes(buf[at-BASE:at-BASE+len(old)])==old;buf[at-BASE:at-BASE+len(old)]=new
 m['title_screen']=apply_title(Path('H:/CREATURE-source/retrosyn-integration-step-rec-solo'),O,image,title_patch,'2.74' if a.baremetal_routing else '2.73' if a.one_mod_osc else '2.72' if a.mono_mixer_reuse else '2.71' if a.audio_profile else '2.70' if a.stock_selection_only else '2.69' if a.sram_mixer else '2.68' if a.routing_fast_path else '2.67' if a.stock_native_idle else '2.66' if a.stock_voice_protection else '2.65',lite=not full,previous=m['title_screen'])
 dirty=bytes(x!=y for x,y in zip(image[:START],stock))+b'\1'*(len(image)-START);packed=aplib_grow.repack_grow(bytes(image),ops,dirty,START);packed,_=pack(packed);assert aplib.depack(packed,bootstrap_gap=0x1ffc00)[0]==image
 plains=[]
 for sec in pkg['sections']:
  try:plains.append(aplib.depack(pkg['blob'][sec['off']:sec['off']+sec['size']])[0])
  except Exception:pass
 key=container.find_key(plains,pkg['blob'][:-32],pkg['blob'][-32:]);assert key;rebuilt=container.rebuild(pkg,{3:packed},key);assert len(rebuilt)<=0x1c0000
 result=wrap(container.build_stream(rebuilt,BYTES_PER_MSG),info['product'],info['start_seq']);target=O/('Supermodel_2.74_Baremetal_Routing_Experimental.syx' if a.baremetal_routing else 'Supermodel_2.73_One_Mod_Osc_Experimental.syx' if a.one_mod_osc else 'Supermodel_2.72_Mono_Mixer_Experimental.syx' if a.mono_mixer_reuse else 'Supermodel_2.71_Audio_Profile_Experimental.syx' if a.audio_profile else 'Supermodel_2.70_Stock_Selection_Experimental.syx' if a.stock_selection_only else 'Supermodel_2.69_SRAM_Mixer_Experimental.syx' if a.sram_mixer else 'Supermodel_2.68_Idle_Routing_Experimental.syx' if a.routing_fast_path else 'Supermodel_2.67_Stock_Voice_Native_Idle_Experimental.syx' if a.stock_native_idle else 'Supermodel_2.66_Stock_Voice_Protection_Experimental.syx' if a.stock_voice_protection else 'Supermodel_2.65_EMAC_Reverb_Network_Comparison.syx' if network else 'Supermodel_2.65_EMAC_DSP_Comparison.syx' if a.emac_dsp else 'Supermodel_2.65_Activity_Masks_Experimental.syx')
 if a.check:assert target.read_bytes()==result
 else:target.write_bytes(result)
 m['stock_voice_protection']=dict(enabled=a.stock_voice_protection,gate=0x8000e8a4,branch=0x8000e8b6,stock_machine_ids=[0,1,2,3,4,5],wizard_protection_retained=True,native_idle_retained=a.stock_native_idle)
 m['baremetal_routing']=a.baremetal_routing
 m['optional_choices_preserved']=optional
 m['one_mod_osc']=a.one_mod_osc
 m['mono_mixer_reuse']=a.mono_mixer_reuse
 m['audio_profile']=profile
 m['stock_selection_only']=dict(enabled=a.stock_selection_only,key=ss_key if a.stock_selection_only else None,idle_policy_unchanged=True)
 m['sram_mixer']=dict(enabled=a.sram_mixer,address=0x8000ea48,size=126,original=0x40056698)
 m['idle_routing_fast_path']=a.routing_fast_path
 m['reverb_network_comparison']=network
 m['emac_dsp_comparison']=dict(enabled=a.emac_dsp,acc3_reserved=False,existing_routing_preserved=True)
 m.update(sha256=sha(result),main_os_sha256=sha(image),activity_masks=dict(loader=loader,previous_loader=oldentry,code=CODE,code_bytes=len(blob),bss=BSS,bss_end=sy['aa_end'],symbols=sy,hooks=hooks,flash_bytes=len(rebuilt),hardware_tested=False,full=full,machine_confirmation=True,late_hooks=[dict(at=at,target=sy[fn]) for at,fn in late]));(O/'BUILD.json').write_text(json.dumps(m,indent=2)+'\n');print('BUILT activity masks',len(blob),'code bytes',len(rebuilt),'flash bytes',flush=True)
if __name__=='__main__':main()
