/* Note 109 : repetition des dernieres notes B et filtre Control All depuis B.
 * File MIDI native avec reservation Off ; aucune sortie physique dans l'audio.
 */
typedef unsigned int u32;
typedef signed int i32;
typedef unsigned char u8;
typedef signed short i16;
/* Pointeurs lies au catalogue effectivement construit, jamais supposes fixes. */
u32 bp_api[25]={0};
u32 bp_zero=0,bp_none=~0u,bp_mask=0,bp_ui_keys=0;
u32 bp_midi_mask=0,bp_config_owned=0;
#define PTR(n) (*(volatile u32 *)bp_api[n])
#define KEYS PTR(0)
#define REQUEST ((i32)PTR(1))
#define CANCEL PTR(2)
#define MASK (*(volatile u8 *)bp_api[3])
#define BOBJ PTR(4)
#define SELECT PTR(5)
#define PATTERN PTR(6)
#define RUNTIME PTR(7)
#define DIVS ((const u32 *)bp_api[8])
#define LOADED PTR(9)
#define PLAYPAT PTR(10)
extern u32 bp_step_original(u32,u32,u32,u32);
extern u32 bp_clock_original(u32,u32,u32,u32,u32);
extern u32 bp_enc_original(u32);
extern u32 bp_menu_original(u32,u32);
extern u32 bp_view_enc_original(u32,u32);
extern void bp_render_original(u32,u32);
extern void bp_led_original(u32,u32,u32);
static u32 selected(void);
/* Les masques A et B sont independants, en RAM comme la configuration stock. */
static u32 held_ui(u32 code);
static u32 config_key(u32 event,u32 audio){
 u32 *e=(u32 *)event,code=e[3],flags=e[4];
 if(code<16||code>27)return 0;
 u32 lane=code-16,bit=1u<<lane;
 if(!(flags&1)){if(bp_config_owned&bit){bp_config_owned&=~bit;return 1;}return 0;}
 if(bp_config_owned&bit)return 1;
 if((flags&0x28)||KEYS==3||!held_ui(2))return 0;
 if(lane<6){if(!audio||!bp_api[22])return 0;MASK^=bit;}
 else bp_midi_mask^=1u<<(lane-6);
 bp_config_owned|=bit;return 1;
}

u32 bp_enc(u32 event);
static u32 filter_visible,filter_time,filter_all,filter_values[2];
static u32 clock_ui(void){return PTR(14);}
static void redraw(void){if(BOBJ)((void (*)(u32))bp_api[15])(BOBJ);}
static u32 held_ui(u32 code){
 u32 bit=code==2?1u:4u;
 return (bp_ui_keys&bit)||((u32 (*)(u32))0x4007faf4)(code);
}
static u32 filter_gesture(u32 event){
 u32 code=((u32 *)event)[3];
 return BOBJ&&bp_api[18]&&(code==8||code==9)&&held_ui(5);
}
/* La page B consomme des evenements bruts avant le getter global. Relier le
 * geste ici aussi, sans fermer B ni transmettre les pads de division au clavier. */
u32 bp_menu(u32 view,u32 event){
 u32 *e=(u32 *)event,code=e[3],down=e[4]&1;
 if(code==2||code==5){u32 bit=code==2?1u:4u;if(down)bp_ui_keys|=bit;else bp_ui_keys&=~bit;}
 if(code==5){redraw();return 1;}
 /* Le chord de sortie garde sa chaine globale, meme depuis le callback brut. */
 if(BOBJ&&code==2&&down&&((e[4]&2)||PTR(21))&&(PTR(19)||PTR(20))){
  u32 taken=((u32 (*)(u32))0x4007240c)(event);
  if(!taken){if(!BOBJ){bp_ui_keys=0;filter_visible=0;}return 1;}
 }
 if(config_key(event,1)){redraw();return 1;}
 if(bp_api[12]){
  u32 copy[6];for(u32 i=0;i<6;i++)copy[i]=e[i];
  if(((u32 (*)(u32))bp_api[12])((u32)copy)){redraw();return 1;}
 }
 u32 result=bp_menu_original(view,event);
 if(!BOBJ){bp_ui_keys=0;filter_visible=0;}
 return result;
}
u32 bp_view_enc(u32 view,u32 event){
 if(filter_gesture(event)){bp_enc(event);return 1;}
 return bp_view_enc_original(view,event);
}
static void text(u32 canvas,u32 x,u32 y,const char *format,u32 value){
 ((void (*)(u32,u32,u32,u32,u32,const char *,u32))0x40071a04)(canvas,0x40ea14cc,x,y,0x10,format,value);
}
/* Fenetre dessinee dans B avec les primitives/polices stock, meme expiration
 * que les valeurs CC natives. Aucun objet/menu A ouvert derriere B. */
void bp_render(u32 view,u32 canvas){
 if(filter_visible&&(u32)(clock_ui()-filter_time)<1500){
  ((void (*)(u32,u32,u32,u32,u32,i32))0x40070dea)(canvas,0,0,127,63,0);
  text(canvas,7,7,filter_all?"FILTER ALL":"FILTER B%d",selected()+1);
  text(canvas,7,27,"Cutoff %d",filter_values[0]);
  text(canvas,7,43,"Reso %d",filter_values[1]);return;
 }
 if(filter_visible){filter_visible=0;PTR(16)=0;}
 bp_render_original(view,canvas);
}
static void config_leds(u32 available,u32 out,u32 audio){
 u32 leds=((u32 (*)(void))0x400cfaf4)();
 for(u32 lane=audio?0:6;lane<12;lane++){
  if(lane<6&&!bp_api[22])continue;
  u32 bit=1u<<(lane+1),mask=lane<6?MASK:bp_midi_mask,index=lane<6?lane:lane-6;
  if(available&bit)((void (*)(u32,u32,u32,u32))0x40005f86)(leds,lane+1,mask&(1u<<index)?1:2,0x404a8c68);
  *(u32 *)out|=bit;
 }
}
u32 bp_track_keys(u32 view,u32 event){
 if(config_key(event,0)){((void (*)(u32))0x400760ba)(view);return 1;}
 return ((u32 (*)(u32,u32))bp_api[23])(view,event);
}
void bp_track_leds(u32 view,u32 available,u32 out){
 ((void (*)(u32,u32,u32))bp_api[24])(view,available,out);
 if(KEYS!=3)config_leds(available,out,0);
}
void bp_led(u32 view,u32 available,u32 out){
 if(bp_api[13]&&KEYS==3){((void (*)(u32,u32,u32))bp_api[13])(view,available,out);return;}
 if(held_ui(2)){config_leds(available,out,1);return;}
 bp_led_original(view,available,out);
}
static u32 last[6],frozen[6],next[6],off_at[6];
static u32 owned,running,seen_pattern,scope,active_mask;
static i32 division=-1;
static u32 cc_value[6][2]={{127,0},{127,0},{127,0},{127,0},{127,0},{127,0}};
static u32 selected(void){u32 s=BOBJ?SELECT:*(volatile u32 *)0x40a700c4;return s<6?s:0;}
static u32 included(u32 lane){return !(bp_midi_mask&(1u<<lane))||lane==selected();}
static u32 armed(void){return running&&KEYS==3&&REQUEST>=0&&REQUEST<16&&!CANCEL&&LOADED;}
static void stop(u32 rt,u32 lane){((void (*)(u32,u32))bp_api[11])(rt,lane);owned&=~(1u<<lane);}
/* Les appels ordinaires continuent de faire avancer le sequenceur ; seule leur
 * emission de notes est remplacee pour les voies incluses pendant le geste. */
u32 bp_step(u32 rt,u32 lane,u32 packet,u32 gate){
 if(lane>=6||rt!=RUNTIME)return bp_step_original(rt,lane,packet,gate);
 if(armed()&&included(lane))return 1;
 u32 ok=bp_step_original(rt,lane,packet,gate);
 if(ok&&(packet&0xf0808000u)==0x90000000u&&(packet&0x7f00u))last[lane]=packet;
 return ok;
}
u32 bp_clock(u32 rt,u32 pattern,u32 state,u32 now,u32 playing){
 if(scope&&scope!=rt){owned=0;active_mask=0;division=-1;}
 scope=rt;running=playing==1;
 if(!BOBJ){bp_ui_keys=0;filter_visible=0;}
 if(pattern!=seen_pattern){
  for(u32 i=0;i<6;i++){if(owned&(1u<<i))stop(rt,i);last[i]=0;}
  seen_pattern=pattern;division=-1;active_mask=0;
 }
 u32 enabled=armed(),changed=division!=REQUEST;
 u8 *p=(u8 *)pattern;
 for(u32 lane=0;lane<6;lane++){
  u32 bit=1u<<lane;
  u32 take=enabled&&included(lane)&&p[lane*264]&&!p[lane*264+1];
  if(!take){if(owned&bit)stop(rt,lane);active_mask&=~bit;continue;}
  if(changed||!(active_mask&bit)){
   if(owned&bit)stop(rt,lane);
   frozen[lane]=last[lane];next[lane]=now;active_mask|=bit;
  }
  if(owned&bit)if((i32)(now-off_at[lane])>=0)stop(rt,lane);
  if((i32)(now-next[lane])<0)continue;
  u32 interval=DIVS[REQUEST],packet=frozen[lane];
  next[lane]=now+interval-(now%interval);
  if(!packet)continue;
  u32 channel=p[lane*264+2],port=p[lane*264+3];
  if(channel>15||port<2||port>4)continue;
  packet=(packet&0x00ffff00u)|((0x90u+channel)<<24)|port;
  if(bp_step_original(rt,lane,packet,1)){owned|=bit;off_at[lane]=now+interval/2;}
 }
 division=enabled?REQUEST:-1;
 return bp_clock_original(rt,pattern,state,now,playing);
}
static u32 ipl(void){unsigned short sr;__asm__ volatile("move.w %%sr,%0":"=d"(sr));return sr&0x700;}
static i32 clamp(i32 n){return n<0?0:n>127?127:n;}
/* mlkc_enc(event), avant les assignations CC ordinaires : MACHINES + TRACK,
 * SWEEP/CONTOUR. Les autres gestes restent transmis a leur routine intacte. */
u32 bp_enc(u32 event){
 u32 code=((u32 *)event)[3];
 if(!filter_gesture(event)||ipl())return bp_enc_original(event);
 u32 all=held_ui(2);
 i32 delta=((i32 (*)(u32,u32,u32))0x4006f73a)(event,1,1);
 if(!delta||!LOADED)return 1;
 u32 project=((u32 (*)(void))0x400cf866)(),which=code-8,cc=which?71:74;
 u8 *pattern=(u8 *)PATTERN;
 if(!project||!pattern)return 1;
 for(u32 lane=0;lane<6;lane++){
  u32 audio=all?(!(MASK&(1u<<lane))||lane==selected()):lane==selected();
  u32 midi=all?included(lane):lane==selected();
  if(!audio&&!midi)continue;
  u32 *handle=(u32 *)(project+212+68*lane),raw=0;
  if(*handle){u32 getter=*(u32 *)(*handle+40);if(getter)raw=((u32 (*)(u32))getter)((u32)handle);}
  i32 value=(i32)cc_value[lane][which];
  if(raw&&audio){
   u32 machine=*(u8 *)(raw+38);
   i32 desc=((i32 (*)(u32,u32,u32))0x4005a8ce)(lane,machine,cc);
   if(desc>=0&&desc<512){
    u32 table=*(u32 *)0x4005a2de,key=*(u32 *)(table+56*(u32)desc+4);
    if(key<=32){
     value=(*(i16 *)(raw+20+2*key))>>8;
     value=clamp(value+delta);
     ((void (*)(u32,u32,u32,u32,u32))0x4000f2a2)(project,cc,(u32)value,lane,0);
    }else value=clamp(value+delta);
   }else value=clamp(value+delta);
  }else value=clamp(value+delta);
  cc_value[lane][which]=(u32)value;
  if(midi&&pattern[264*lane]&&!pattern[264*lane+1]&&*(volatile u32 *)0x40fe4228){
   u32 channel=pattern[264*lane+2],port=pattern[264*lane+3];
   if(channel<16&&port>=2&&port<=4){
    u32 packet=((0xb0+channel)<<24)|(cc<<16)|((u32)value<<8);
    ((void (*)(u32,u32,u32))0x400826b0)(3,(u32)&packet,port);
   }
  }
 }
 filter_all=all;filter_values[which]=cc_value[selected()][which];
 /* Lire aussi l'autre reglage, pour afficher les deux valeurs audio actuelles. */
 u32 *handle=(u32 *)(project+212+68*selected()),raw=0;
 if(*handle){u32 getter=*(u32 *)(*handle+40);if(getter)raw=((u32 (*)(u32))getter)((u32)handle);}
 if(raw)for(u32 k=0;k<2;k++){
  i32 desc=((i32 (*)(u32,u32,u32))0x4005a8ce)(selected(),*(u8 *)(raw+38),k?71:74);
  if(desc>=0&&desc<512){u32 key=*(u32 *)(*(u32 *)0x4005a2de + 56*(u32)desc+4);if(key<=32)filter_values[k]=(u32)clamp((*(i16 *)(raw+20+2*key))>>8);}
 }
 filter_time=clock_ui();filter_visible=1;PTR(16)=2;PTR(17)=filter_time;redraw();return 1;
}
