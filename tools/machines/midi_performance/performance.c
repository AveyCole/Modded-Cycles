/* Note 109 : repetition des dernieres notes B et filtre Control All depuis B.
 * File MIDI native avec reservation Off ; aucune sortie physique dans l'audio.
 */
typedef unsigned int u32;
typedef signed int i32;
typedef unsigned char u8;
typedef signed short i16;
/* Pointeurs lies au catalogue effectivement construit, jamais supposes fixes. */
u32 bp_api[13]={0};
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
static u32 last[6],frozen[6],next[6],off_at[6];
static u32 owned,running,seen_pattern,scope,active_mask;
static i32 division=-1;
static u32 cc_value[6][2]={{127,0},{127,0},{127,0},{127,0},{127,0},{127,0}};
static u32 selected(void){u32 s=BOBJ?SELECT:*(volatile u32 *)0x40a700c4;return s<6?s:0;}
static u32 included(u32 lane){return !(MASK&(1u<<lane))||lane==selected();}
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
 if(!BOBJ||(code!=8&&code!=9)||ipl())return bp_enc_original(event);
 u32 (*held)(u32)=(void *)0x4007faf4;
 if(!held(5)||!held(2))return bp_enc_original(event);
 i32 delta=((i32 (*)(u32,u32,u32))0x4006f73a)(event,1,1);
 if(!delta||!LOADED)return 1;
 u32 project=((u32 (*)(void))0x400cf866)(),which=code-8,cc=which?71:74;
 u8 *pattern=(u8 *)PATTERN;
 if(!project||!pattern)return 1;
 for(u32 lane=0;lane<6;lane++)if(included(lane)){
  u32 *handle=(u32 *)(project+212+68*lane),raw=0;
  if(*handle){u32 getter=*(u32 *)(*handle+40);if(getter)raw=((u32 (*)(u32))getter)((u32)handle);}
  i32 value=(i32)cc_value[lane][which];
  if(raw){
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
  if(pattern[264*lane]&&!pattern[264*lane+1]&&*(volatile u32 *)0x40fe4228){
   u32 channel=pattern[264*lane+2],port=pattern[264*lane+3];
   if(channel<16&&port>=2&&port<=4){
    u32 packet=((0xb0+channel)<<24)|(cc<<16)|((u32)value<<8);
    ((void (*)(u32,u32,u32))0x400826b0)(3,(u32)&packet,port);
   }
  }
 }
 return 1;
}
