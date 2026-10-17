"""Note 109 : page separee 909 pour les essais MIDI et filtre B."""
import argparse,pathlib,re,shutil,tempfile
ROOT=pathlib.Path(__file__).resolve().parents[1];STAMP='2026-10-16-midi-performance-test-2'
def main():
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args();target=ROOT/'docs/flasher-midi-performance-test';tmp=tempfile.TemporaryDirectory(dir=ROOT/'build') if a.check else None;out=pathlib.Path(tmp.name) if tmp else target;out.mkdir(exist_ok=True)
 for f in (ROOT/'docs/flasher-supermodel-909').iterdir():
  if f.is_file():shutil.copyfile(f,out/f.name)
 for name,source in [('midi-performance.js',ROOT/'tools/web/midi-performance.js'),('midi-performance-data.js',ROOT/'build/midi-performance-data.js')]:shutil.copyfile(source,out/name)
 s=(out/'index.html').read_text(encoding='utf-8');s=re.sub(r'(?<=\?v=)[\w.-]+',STAMP,s);s=re.sub(r"window.MC_BUILD='[^']+'",f"window.MC_BUILD='{STAMP}'",s);s=s.replace('window.MC909Released=true','window.MC909Released=false')
 s=s.replace('<title>Supermodel 909 — A.V.’s Edition</title>','<title>909 MIDI performance test</title>').replace('Hardware tested','Experimental MIDI performance test').replace('Teste sur machine','Test MIDI performance experimental')
 text='<p><span data-l="en"><strong>Test only.</strong> TRACK + RETRIG + division pad retriggers the latest sequenced note on each included MIDI B lane. Release stops repeated notes. MIDI runs at the selected musical division; audio retains its existing buffer limit. In B-side, hold MACHINES and turn SWEEP/CONTOUR for the selected track, or add TRACK for Control All. The filter controls appear briefly, then return to B-side. Use the established combo or BACK to exit B-side. Turn SWEEP/CONTOUR to control the included audio filters and send MIDI CC74/CC71. Muted MIDI lanes receive no CC. Hold TRACK: pads 1–6 configure audio inclusion, pads 7–12 independently configure MIDI lanes. RAM choices reset at power-on; the selected lane always follows. Same six-voice 909 profile and four local WAV inputs.</span><span data-l="fr"><strong>Test uniquement.</strong> TRACK + RETRIG + pad division repete la derniere note sequencee de chaque voie B incluse ; relacher arrete ces notes. Division musicale MIDI exacte ; limite historique audio conservee. Cote B, tenir MACHINES et tourner SWEEP/CONTOUR pour la piste choisie, ajouter TRACK pour Control All. Affichage filtre bref puis retour B ; accord habituel ou BACK pour sortir de B. SWEEP/CONTOUR regle les filtres audio inclus et transmet CC74/CC71. Pas de CC vers voies MIDI muettes. Tenir TRACK : pads 1–6 audio, 7–12 MIDI independant. Choix en RAM, voie choisie toujours incluse. Profil six voix 909, quatre WAV locaux.</span></p>'
 s=s.replace('<main class="wrap fl">','<main class="wrap fl">'+text).replace('</body>',f'<script src="midi-performance-data.js?v={STAMP}"></script><script src="midi-performance.js?v={STAMP}"></script></body>');(out/'index.html').write_text(s,encoding='utf-8')
 (out/'909-release.js').write_text('window.MC_RELEASES=[{version:"MIDI-performance-test.2",date:"2026-10-16",changes:[{en:"Experimental MIDI beat repeat and B-side audio/MIDI filter.",fr:"Repeat MIDI et filtre audio/MIDI depuis B experimentaux."}]}];\n',encoding='utf-8')
 (out/'BUILD.json').write_text('{"status":"experimental","hardware_tested":false,"samples_hosted":false}\n',encoding='utf-8')
 (out/'ABOUT.md').write_text('Experimental MIDI beat repeat and B-side Control All audio/MIDI filter. Hardware verification pending.\n',encoding='utf-8')
 if a.check:
  for f in out.iterdir():assert f.read_bytes().replace(b'\r\n',b'\n')==(target/f.name).read_bytes().replace(b'\r\n',b'\n'),f.name
 print('PASS page MIDI performance separee')
if __name__=='__main__':main()
