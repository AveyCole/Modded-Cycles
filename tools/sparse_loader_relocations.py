"""Relocaliser tous les chargeurs sparse lors du deplacement du bank compresse."""
import struct
BASE=0x40000400

def collect(image,meta):
 first=meta['direct_jump']['loader'];loaders=set()
 def visit(value):
  if isinstance(value,dict):
   for key,v in value.items():
    if key in ('loader','previous_loader') and isinstance(v,int) and first<=v<BASE+len(image):loaders.add(v)
    elif isinstance(v,(dict,list)):visit(v)
  elif isinstance(value,list):
   for v in value:visit(v)
 visit(meta);loaders.add(int.from_bytes(image[0x40195adc-BASE:0x40195ae0-BASE],'big'))
 fixes={}
 for loader in sorted(loaders):
  assert first<=loader<BASE+len(image)
  for off in range(loader-BASE,min(loader-BASE+512,len(image)-3),2):
   value=int.from_bytes(image[off:off+4],'big')
   if first<=value<BASE+len(image):fixes[BASE+off]=value
 assert fixes
 return [dict(at=at,old=v) for at,v in sorted(fixes.items())]
