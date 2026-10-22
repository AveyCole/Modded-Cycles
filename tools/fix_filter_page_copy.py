"""Corrige les textes publics du filtre ; aucune ecriture DSP ni image modifiee.

Les anciennes pages de test embarquent des copies du catalogue. La correction
conserve leur code et leurs octets de patch, et remplace seulement la prose.
"""
from pathlib import Path
import re,subprocess

ROOT=Path(__file__).resolve().parents[1]
PATTERN=r'high[ -]?pass|passe[ -]?haut|LP\s*/\s*(OFF\s*/\s*)?HP'
REPLACEMENTS={
 'Per-track filter (LP / OFF / HP)':'Per-track lowpass filter',
 'Filtre par piste (LP / OFF / HP)':'Filtre passe-bas par piste',
 'Filtre par piste : passe-bas, OFF, passe-haut':'Filtre passe-bas par piste',
 'low-pass/high-pass filter with resonance and envelope':'lowpass filter with resonance',
 'passe-bas/passe-haut par piste avec résonance et enveloppe':'passe-bas par piste avec résonance',
 'Add a filter and filter envelope to each track.':'Add a lowpass filter with resonance to each track.',
 'Ajoutez filtre et enveloppe de filtre à chaque piste.':'Ajoutez un filtre passe-bas avec résonance à chaque piste.',
 'low-pass to the left, off in the centre, high-pass to the right':'lowpass cutoff from closed to fully open',
 'low-pass left, off center, high-pass right':'lowpass cutoff (0–127; 127 = fully open)',
 'low-pass left of centre, high-pass right of centre':'lowpass cutoff',
 'passe-bas à gauche, rien au centre, passe-haut à droite':'coupure du passe-bas, de fermé à ouvert',
 'passe-bas a gauche, rien au centre, passe-haut a droite':'coupure du passe-bas, de ferme a ouvert',
 'passe-bas à gauche, off au centre, passe-haut à droite':'coupure passe-bas (0–127 ; 127 = ouvert)',
 'passe-bas à gauche du centre, passe-haut à droite':'coupure du passe-bas',
 "like a DJ mixer, with the Model:Samples' range (5 Hz to 20 kHz)":"with resonance",
 'comme sur une table de mixage DJ, avec la plage du Model:Samples (5 Hz à 20 kHz)':'avec résonance',
 'CONTOUR sets the resonance, COLOR and SHAPE a filter envelope (amount up or down, decay) restarted by each note. Four real parameters on every machine:':'CONTOUR sets resonance. Use the native modulation controls:',
 'CONTOUR règle la résonance, COLOR et SHAPE une enveloppe du filtre (quantité vers le haut ou le bas, decay) relancée à chaque note. Quatre vrais paramètres de toutes les machines :':'CONTOUR règle la résonance. Commandes de modulation natives :',
 'CONTOUR : resonance ; COLOR et SHAPE : enveloppe du filtre (quantite, decay).':'CONTOUR : resonance.',
 'MACHINES + CONTOUR: resonance; + COLOR: envelope amount; + SHAPE: envelope decay.':'MACHINES + CONTOUR: resonance.',
 'MACHINES + CONTOUR : résonance ; + COLOR : quantité d’enveloppe ; + SHAPE : durée d’enveloppe.':'MACHINES + CONTOUR : résonance.',
 'This shared version replaces the older LP/OFF/HP filter: it has no high-pass or separate filter-envelope controls.':'This is a lowpass filter with cutoff and resonance controls.',
 'Cette variante remplace LP/OFF/HP ; pas de passe-haut ni enveloppe de filtre séparée.':'Ce filtre passe-bas propose les commandes de coupure et de résonance.',
 'This is a low-pass filter, without the previous high-pass or filter-envelope controls.':'This is a lowpass filter with cutoff and resonance controls.',
 'No high-pass or separate filter envelope.':'Lowpass cutoff and resonance controls.',
 'Pas de passe-haut ni enveloppe séparée.':'Commandes de coupure et de résonance du passe-bas.',
 'sets LP/OFF/HP filter; CONTOUR resonance, COLOR/SHAPE envelope.':'sets lowpass cutoff; CONTOUR sets resonance.',
}

SECTION='''<section id="track-filter">
<h2><span data-l="en">Per-track lowpass filter</span><span data-l="fr">Filtre passe-bas par piste</span></h2>
<p class="lede"><span data-l="en">Shape each track with a lowpass filter and resonance. Lower the cutoff to soften the sound; raise it to let more high frequencies through.</span><span data-l="fr">Sculptez chaque piste avec un filtre passe-bas et sa résonance. Baissez la coupure pour adoucir le son ; montez-la pour laisser passer davantage d’aigus.</span></p>
<ol>
<li><span data-l="en">Hold <b>MACHINES</b> and turn <b>SWEEP</b> for cutoff (0–127; 127 is fully open).</span><span data-l="fr">Maintenez <b>MACHINES</b> et tournez <b>SWEEP</b> pour la coupure (0–127 ; 127 est complètement ouvert).</span></li>
<li><span data-l="en">Hold <b>MACHINES</b> and turn <b>CONTOUR</b> for resonance.</span><span data-l="fr">Maintenez <b>MACHINES</b> et tournez <b>CONTOUR</b> pour la résonance.</span></li>
<li><span data-l="en">Fully open cutoff with resonance at zero bypasses the filter. Sample Wizard keeps its own filter.</span><span data-l="fr">Coupure complètement ouverte et résonance à zéro : le filtre est contourné. Sample Wizard conserve son propre filtre.</span></li>
<li><span data-l="en">Use parameter locks, LFOs, MIDI CC74 for cutoff and CC71 for resonance. Settings save with the sound.</span><span data-l="fr">Utilisez les locks, les LFO, CC74 pour la coupure et CC71 pour la résonance. Les réglages sont sauvegardés avec le son.</span></li>
</ol>
</section>'''

def main():
 result=subprocess.run(['rg','-l','-i',PATTERN,'docs','tools/web','-g','*.html','-g','*.js','-g','*.md','-g','*.svg'],cwd=ROOT,capture_output=True,text=True,encoding='utf8')
 assert result.returncode in (0,1)
 paths=[ROOT/p for p in result.stdout.splitlines()]
 paths += [ROOT/'tools/gen_flasher_tweaks.py',ROOT/'docs/index.html',ROOT/'tools/gen_midi_machine_main.py']
 changed=[]
 for p in dict.fromkeys(paths):
  before=p.read_text(encoding='utf8');s=before
  if p.suffix=='.html' and 'id="track-filter"' in s and re.search(PATTERN,s,re.I):
   s=re.sub(r'<section id="track-filter">.*?</section>',lambda _:SECTION,s,flags=re.S)
  for old,new in REPLACEMENTS.items():s=s.replace(old,new)
  # Metadonnees descriptives embarquees : remplacer la phrase entiere, pas le DSP.
  s=re.sub(r'L64\.\.OFF\.\.H63 : coupure du passe-bas, de fermé à ouvert, 5 Hz à 20 kHz','0–127 : coupure du passe-bas',s)
  s=s.replace('Per-track filter and envelope are included.','The per-track lowpass filter is included.').replace('Filtre et enveloppe par piste sont inclus.','Le filtre passe-bas par piste est inclus.')
  if s!=before:p.write_text(s,encoding='utf8');changed.append(str(p.relative_to(ROOT)))
 print('Updated',len(changed),'page/source files')
 for p in changed:print(p)

if __name__=='__main__':main()
