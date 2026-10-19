"""Note130 : test tap SCRAMBLE / maintien Pad Setup, sans changement audio."""
import argparse,json,pathlib,re,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];STAMP='2026-10-18-pad-tap-test-1'
def main():
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args()
 subprocess.run([sys.executable,str(ROOT/'tools/gen_pad_mode.py'),'--tap-test'],check=True,cwd=ROOT)
 data=json.loads((ROOT/'build/pad-tap/data.json').read_text())
 files={f.name:f.read_bytes() for f in (ROOT/'docs/flasher').iterdir() if f.is_file()}
 for name in ('beat-diagnostic-data.js','beat-diagnostic.js'):files[name]=(ROOT/'docs/flasher-machine-combinations-test'/name).read_bytes()
 preset=files['midi-machine-main.js'].decode().replace('pageReady,window.MCLfoDestinationsReady','pageReady,window.MCLfoDestinationsReady,window.MCBeatDiagnosticReady').replace("'startup-animation','boot-anim','audio-load-diagnostic'","'startup-animation','boot-anim'").replace("select('audio-load-diagnostic',false)","select('audio-load-diagnostic',true)");files['midi-machine-main.js']=preset.encode()
 files['pad-mode-data.js']=('window.MCPadMode='+json.dumps(data,separators=(',',':'))+';\n').encode()
 js=(ROOT/'tools/web/pad-mode.js').read_text(encoding='utf-8').replace("status:'tested'","status:'experimental'")
 js=js.replace("values.push(0,common?n(common.symbols.set_held):0,common?n(common.symbols.mod_used):0);", "const scramble=r.tweaks.find(t=>t.symbols?.sc_key);if(!scramble)throw Error('Pad tap: SCRAMBLE handler missing');values.push(0,common?n(common.symbols.set_held):0,common?n(common.symbols.mod_used):0,n(scramble.symbols.sc_key));")
 files['pad-mode.js']=js.encode()
 html=files['index.html'].decode();html=re.sub(r'(?<=\?v=)[\w.-]+',STAMP,html);html=re.sub(r"window.MC_BUILD='[^']+'",f"window.MC_BUILD='{STAMP}'",html)
 html=html.replace('<script src="midi-machine-main.js?',f'<script src="beat-diagnostic-data.js?v={STAMP}"></script><script src="beat-diagnostic.js?v={STAMP}"></script><script src="midi-machine-main.js?')
 notice='<p role="note"><strong data-l="en">SCRAMBLE / Pad Setup gesture test.</strong><strong data-l="fr">Test geste SCRAMBLE / Pad Setup.</strong> <span data-l="en">Hold SETTINGS, then tap TRACK for SCRAMBLE on release. Keep both held until the native long-press event to open Pad Setup without scrambling. Press DATA before turning to choose Silent/Stock; BACK exits. Pad mode resets to Silent after reboot. Main audio/filter behavior retained; no sample-lock filter experiment. CPU/CUT diagnostics included. Released main and 909 unchanged.</span><span data-l="fr">Tenir SETTINGS puis appuyer brievement sur TRACK : SCRAMBLE au relachement. Maintenir les deux jusqu’au maintien long natif : Pad Setup sans SCRAMBLE. Presser DATA puis tourner pour Silent/Stock ; BACK ferme. Retour Silent au redemarrage. Audio/filtre principal conserves, sans test filtre sample locks. Diagnostic CPU/CUT inclus. Principal et909 publies inchanges.</span></p>'
 html=html.replace('SETTINGS + TRACK opens Pad Setup.', 'A short SETTINGS + TRACK tap runs SCRAMBLE on release; a long hold opens Pad Setup.').replace('SETTINGS + TRACK ouvre Pad Setup.', 'Un appui court SETTINGS + TRACK lance SCRAMBLE au relachement ; un maintien long ouvre Pad Setup.')
 html=html.replace('<main class="wrap fl">','<main class="wrap fl">'+notice);files['index.html']=html.encode()
 guide=files['shortcut-guide.html'].decode().replace('Pad selection mode</td><td>SETTINGS + TRACK', 'Pad selection mode</td><td>Hold SETTINGS + TRACK').replace('Mode de selection des pads</td><td>SETTINGS + TRACK', 'Mode de selection des pads</td><td>Maintenir SETTINGS + TRACK')
 files['shortcut-guide.html']=guide.encode()
 files['BUILD.json']=(json.dumps(dict(stamp=STAMP,base='2026-10-18-pad-mode-main-197',scope='test-only',diagnostics=True,hardware_verified=False,short_tap_scramble=True,long_hold_pad_setup=True,pad_mode_persistent=False,sample_lock_filter=False),indent=2)+'\n').encode()
 files['midi-machine-release.js']=('window.MC_RELEASES='+json.dumps([dict(version='Pad-tap-test.1',date='2026-10-18',changes=[dict(en='SETTINGS + TRACK: short tap restores native SCRAMBLE on release; long hold opens Pad Setup without scrambling. Audio unchanged; test diagnostics included.',fr='SETTINGS + TRACK : appui court restaure SCRAMBLE natif au relachement ; maintien long ouvre Pad Setup sans SCRAMBLE. Audio conserve ; diagnostic de test inclus.')])])+';\n').encode()
 out=ROOT/'docs/flasher-pad-tap-test';out.mkdir(exist_ok=True)
 for name,raw in files.items():
  istext=pathlib.Path(name).suffix in ('.js','.html','.css','.json','.md','.txt')
  if istext:raw=raw.replace(b'\r\n',b'\n').rstrip(b'\n')+b'\n'
  if a.check:assert ((out/name).read_bytes().replace(b'\r\n',b'\n') if istext else (out/name).read_bytes())==raw,name
  else:(out/name).write_bytes(raw)
 print('PASS test tap/long genere ; diagnostics inclus, aucun hook audio ajoute')
if __name__=='__main__':main()
