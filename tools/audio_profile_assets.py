"""Profilage materiel par marqueurs ; aucun DSP remplace."""
from pathlib import Path

def prepare(root,out,meta,image,base):
 sy=meta['per_track_fx']['symbols'];aliases={**sy,**meta['fx_menu']['symbols']}
 sites=[(0x4005979e,8),(0x400597ba,10),(0x400597cc,8),(0x4005980a,8),(0x40059824,6),(0x40059858,10),(0x40059878,8)]
 asm='.text\n';hooks=[]
 for index,(at,n) in enumerate(sites):
  raw=bytes(image[at-base:at-base+n]);name='hp_mark'+str(index);hooks.append((at,name))
  asm+=f'.globl {name}\n{name}:\n lea -12(%sp),%sp\n movem.l %d0-%d1,(%sp)\n move.w %sr,%d0\n move.l %d0,8(%sp)\n move.l 0xfc07000c,%d0\n move.l %d0,hp_stamp+{4*index}\n move.l 8(%sp),%d0\n move.w %d0,%sr\n movem.l (%sp),%d0-%d1\n lea 12(%sp),%sp\n.byte '+','.join(map(str,raw))+f'\n jmp {at+n:#x}\n'
 (out/'audio-profile-markers.S').write_text(asm,encoding='utf-8')
 body=(root/'tools/machines/track_fx/irq-budget.c').read_text(encoding='utf-8')
 body=body.replace('volatile u32 gb_irq_active','extern volatile u32 gb_irq_active').replace('void gb_finish(','void hp_finish(').replace('void gb_dx_before(','void hp_unused_before(')
 body=body.replace(' gb_irq_active=0;', ' hp_record(now);gb_irq_active=0;')
 prefix="""typedef unsigned int u32;
volatile u32 hp_stamp[7],hp_peak,hp_best[6],hp_frozen[6];
void hp_record(u32 now){
 u32 total=now-gb_irq_t0;if(!gb_enabled||*(volatile u32*)0x40a7883c!=1){hp_peak=0;return;}if(hp_stamp[0]-gb_irq_t0>total||hp_stamp[6]-gb_irq_t0>total||total<=hp_peak)return;hp_peak=total;
 hp_best[0]=hp_stamp[4]-hp_stamp[3];
 hp_best[1]=hp_stamp[5]-hp_stamp[4];
 hp_best[2]=hp_stamp[6]-hp_stamp[5];
 hp_best[3]=hp_stamp[2]-hp_stamp[1];
 hp_best[4]=(hp_stamp[1]-hp_stamp[0])+(hp_stamp[3]-hp_stamp[2]);
 hp_best[5]=(hp_stamp[0]-gb_irq_t0)+(now-hp_stamp[6]);
}
"""
 # Declarer les globales avant la fonction de mesure.
 prefix='extern volatile unsigned int gb_irq_t0,gb_enabled;\n'+prefix
 (out/'audio-profile.c').write_text(prefix+body,encoding='utf-8')
 keys=(root/'tools/machines/fx_menu/keys.c').read_text(encoding='utf-8')
 keys=keys[:keys.index('/* Ancien geste reserve')]+ '\n#endif\n'
 keys=keys.replace('fx_diag_cancel','hp_diag_cancel').replace('fx_diag_gesture','hp_diag_gesture')
 start=keys.index('static void show_diag(void){');end=keys.index('void hp_diag_cancel',start)
 keys=keys[:start]+"""extern volatile u32 hp_peak,hp_best[6],hp_frozen[6];
static u32 hp_page;
static void show_diag(void){
 char text[40];u32 sr;
 __asm__ volatile("move.w %%sr,%0\\nmove.w #0x2700,%%sr":"=d"(sr)::"memory","cc");
 if(!hp_page){for(u32 i=0;i<6;i++)hp_frozen[i]=hp_best[i];hp_peak=0;}
 u32 avg=gr_diag_blocks?(gr_diag_sum/gr_diag_blocks)*100/256:0;
 u32 peak=dx_peak,over=dx_over,drops=dx_new;
 if(!hp_page)dx_peak=dx_over=dx_new=gr_diag_sum=gr_diag_blocks=0;
 __asm__ volatile("move.w %0,%%sr"::"d"(sr):"memory","cc");
 if(!hp_page)N(0x40000e6e)(text,"A%u P%u O%u N%u",avg,peak/901,over,drops);
 else if(hp_page==1)N(0x40000e6e)(text,"V%u F%u X%u",hp_frozen[0]/901,hp_frozen[1]/901,hp_frozen[2]/901);
 else N(0x40000e6e)(text,"L%u S%u R%u",hp_frozen[3]/901,hp_frozen[4]/901,hp_frozen[5]/901);
 N(dx_beat_api[2])(text);hp_page=(hp_page+1)%3;
}
"""+keys[end:]
 (out/'audio-profile-keys.c').write_text('#define FX_CPU_OPT 1\n#define FX_DX_FUNC_FIX 1\n'+keys,encoding='utf-8')
 hooks.extend([(sy['gb_finish'],'hp_finish'),(meta['fx_menu']['symbols']['fx_diag_gesture'],'hp_diag_gesture'),(meta['fx_menu']['symbols']['fx_diag_cancel'],'hp_diag_cancel')])
 return [out/'audio-profile-markers.S',out/'audio-profile.c',out/'audio-profile-keys.c'],hooks,dict(markers=[dict(at=at,size=n) for at,n in sites],hardware_tested=False)
