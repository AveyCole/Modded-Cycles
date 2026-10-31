"""Retirer le travail de controle inutile sans remplacer les noyaux natifs."""

def apply(source):
 old='u32 used=0,single=0;for(u32 t=0;t<count;t++)if(g[t]||d[t]){used++;single=t;}'
 new='u32 used=0,single=0;\n /* Deux contributeurs suffisent : le noyau natif gere tous les suivants. */\n for(u32 t=0;t<count;t++)if(g[t]||d[t]){\n  if(used){if(count==6)mf_old_sum6(out,in,g,d);else mf_old_sum7(out,in,g,d);return;}\n  used=1;single=t;\n }'
 assert source.count(old)==1
 source=source.replace(old,new)
 old='mf_sync_audio();if(mf_mode&&mf_audio_ready){enabled=0;'
 new='mf_sync_audio();enabled=0;if(mf_mode&&mf_audio_ready&&(mf_requested||lt_active)){'
 assert source.count(old)==1
 return '#pragma GCC optimize ("O2")\n'+source.replace(old,new)
