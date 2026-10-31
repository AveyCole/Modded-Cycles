"""Compter les instructions de la vraie boucle voix ; pas une mesure des cycles IRQ."""
from pathlib import Path
import sys,json
from unicorn import UC_HOOK_CODE
# Reutiliser exactement la fixture de parite, sans son test40 blocs.
source=Path(__file__).with_name('test_stock_machine_parity.py').read_text(encoding='utf-8')
source=source[:source.index('peaks=[0]*6')]
exec(compile(source,str(Path(__file__).with_name('test_stock_machine_parity.py')),'exec'))
rows=[]
for block in range(12):
 counts=[];outs=[]
 for eng in (stock,e):
  count=[0]
  def tick(*a):count[0]+=1
  hook=eng.uc.hook_add(UC_HOOK_CODE,tick)
  eng.uc.reg_write(C.UC_M68K_REG_SR,0x2700)
  outs.append(eng.block(63 if block==0 else 0))
  eng.uc.hook_del(hook);counts.append(count[0])
 assert np.array_equal(outs[0],outs[1]),block
 rows.append(counts)
print('VOICE INSTRUCTIONS stock/mod',rows,flush=True)
args.output.write_text(json.dumps(dict(scope='six native voices only, not complete interrupt or hardware cycles',blocks=rows,stock_pcm_exact=True,hardware_tested=False),indent=2)+'\n',encoding='utf-8')
