"""Note 109 : corps propre relogeable pour le test MIDI performance."""
import argparse,json,pathlib,re,shutil,subprocess,tempfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
def generate():
 cross=next(p for p in ('m68k-linux-gnu-','m68k-elf-') if shutil.which(p+'gcc'))
 src=ROOT/'tools/machines/midi_performance'
 with tempfile.TemporaryDirectory() as tmp:
  p=pathlib.Path(tmp)
  for name in ('performance.c','trampolines.s'):
   subprocess.run([cross+'gcc','-mcpu=54418','-Os','-ffreestanding','-fno-builtin','-fno-pic','-fno-common','-fno-stack-protector','-fno-asynchronous-unwind-tables','-Wall','-Wextra','-Werror','-c',str(src/name),'-o',str(p/(name+'.o'))],check=True)
  (p/'link.ld').write_text('SECTIONS { .text 0 : { *(.text*) *(.rodata*) } . = ALIGN(4); .data : { *(.data*) } .bss : { *(.bss*) *(COMMON) } . = ALIGN(4); bp_end = .; }')
  subprocess.run([cross+'ld','--emit-relocs','-T',str(p/'link.ld'),'-o',str(p/'e.elf'),str(p/'performance.c.o'),str(p/'trampolines.s.o')],check=True)
  subprocess.run([cross+'objcopy','-O','binary',str(p/'e.elf'),str(p/'e.bin')],check=True)
  sy={row[2]:int(row[0],16) for line in subprocess.check_output([cross+'nm','--defined-only',str(p/'e.elf')],text=True).splitlines() if len(row:=line.split())==3}
  raw=(p/'e.bin').read_bytes();raw+=bytes(sy['bp_end']-len(raw))
  rel=subprocess.check_output([cross+'readelf','-rW',str(p/'e.elf')],text=True)
  offsets=[int(m.group(1),16) for m in re.finditer(r'^([0-9a-f]+)\s+\S+\s+R_68K_32\b',rel,re.M)]
  for off in offsets:assert int.from_bytes(raw[off:off+4],'big')<len(raw)
 return dict(hex=raw.hex(),symbols=sy,reloc=offsets)
def main():
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args();dest=ROOT/'build/midi-performance-data.js'
 text='window.MCMidiPerformanceData='+json.dumps(generate(),separators=(',',':'))+';\n'
 if a.check:assert dest.read_text()==text
 else:dest.write_text(text)
 print('PASS corps MIDI performance relogeable')
if __name__=='__main__':main()
