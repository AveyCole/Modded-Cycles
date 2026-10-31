"""Reuse exact du cote droit pour les paires mono natives prouvees identiques."""
def apply(source):
 source=source.replace('void sf_sum6(', 'static void sf_sum6_core(')
 source+="""
/* Paire native immediate : sorties entrelacees, memes sources/gains/rampes.
 * ACC0 est nul apres le mix gauche, comme exige par le caller natif.
 * Aucun send custom ne peut etre actif dans le chemin copie. */
static struct {u32 valid,right;const s32*in;s32*out,g[6],d[6];} sf_pair;
volatile u32 sf_pair_reused;
static u32 sf_mono(void){
 if(mf_mode&&mf_audio_ready&&mf_requested)return 0;
 const u32*on=(const u32*)mf_side_on;
 if(on)for(u32 i=0;i<6;i++)if(on[i])return 0;
 return 1;
}
void sf_sum6(s32*out,const s32*in,s32*g,const s32*d){
 u32 at=(u32)g,right=at==0x40a78c08?0x40a78be8:at==0x40a78bd0?0x40a78bb8:0;
 if(right){
  sf_pair.valid=0;
  u32 eligible=sf_mono(),used=0;
  if(eligible){for(u32 i=0;i<6;i++){sf_pair.g[i]=g[i];sf_pair.d[i]=d[i];used+=!!(g[i]||d[i]);}}
  sf_sum6_core(out,in,g,d);
  if(eligible&&used>1&&sf_mono()){sf_pair.valid=1;sf_pair.right=right;sf_pair.in=in;sf_pair.out=out;}
  return;
 }
 if(sf_pair.valid&&at==sf_pair.right&&in==sf_pair.in&&out==sf_pair.out+1&&sf_mono()){
  u32 same=1;for(u32 i=0;i<6;i++)if(g[i]!=sf_pair.g[i]||d[i]!=sf_pair.d[i]){same=0;break;}
  if(same){
   sf_pair.valid=0;
   for(u32 i=0;i<32;i++)out[2*i]=sf_pair.out[2*i];
   for(u32 i=0;i<6;i++)g[i]=(s32)((u32)g[i]+((u32)d[i]<<5));
   sf_pair_reused++;return;
  }
 }
 sf_pair.valid=0;sf_sum6_core(out,in,g,d);
}
"""
 return source
