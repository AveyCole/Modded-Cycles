"""Boot des variantes et navigateur silencieux : masques et MD visibles exacts."""
from pathlib import Path
source=Path(__file__).with_name('test_control_all_latch.py').read_text(encoding='utf-8').split('held=set();')[0]
source=source.replace("p.add_argument('--output',type=Path,required=True)","p.add_argument('--output',type=Path,required=True);p.add_argument('--variants',type=Path,required=True)")
exec(compile(source,__file__,'exec'))
rows=[];ps=m['activity_masks']['symbols']
for file in sorted(a.variants.glob('*-mask-*.syx')):
 md=file.name.startswith('md-');mask=int(file.stem.split('-')[-1],16)
 fx.boot=lambda unused,file=file:bc.boot(file)
 r,_,h,log,files,key,turn,data,bind=fx.fixture('unused');bind(0x40000542,lambda args:0);r.u.reg_write(C.UC_M68K_REG_A0,0x931b0000);r.call(s['cal_finish'])
 assert r.r32(ps['mb_display_count'])==(27 if md else 24),(file,r.r32(ps['mb_display_count']))
 expected=list(range(6))+[i for i in list(range(6,17))+list(range(18,28))+[17] if mask&(1<<(i-6))]
 if not md:expected=[i for i in expected if i<25]
 seen=[0];machine=0
 for k in range(40):
  r.w32(ps['rm_machine_valid'],0);r.w32(0xfc07000c,100000000+k*10000000)
  nxt=r.call(ps['mb_step'],machine,1)
  if nxt==machine:break
  seen.append(nxt);machine=nxt
 assert seen==expected,(file,seen,expected)
 # Ni le verrou CTRL-ALL ni le masque ne modifient la release native TRACK.
 assert not r.r32(s['cal_latched'])
 rows.append(dict(file=file.name,mask=mask,native_boot=True,picker=seen,display_limit=27 if md else 24));print('PASS native optional picker',file.name,seen,flush=True)
a.output.write_text(json.dumps(dict(cases=rows,hardware_tested=False),indent=2)+'\n')
