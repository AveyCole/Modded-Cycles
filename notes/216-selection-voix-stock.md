# 216 — Exclure les voix stock de la seule selection du regulateur

Retour utilisateur31/10/2026 :2.69 coupe encore la meme voix d A01, contrairement au stock ; USB deja2ch. Candidat prive Full2.70, --routing-fast-path --sram-mixer --stock-selection-only. Adresses : VA OS1.13.

## Reponse courte

Ne pas toucher voice_gate, O_FREE ni voice_quiet. Changer seulement la cle de candidature au vol : moteur natif0..5 -> cle exclueffffffff. Les autres moteurs gardent le calcul natif et le regulateur. Cela ne recupere pas les cycles manquants et ne revendique pas une correction des overruns ; il s agit d isoler le vol ajoute sans forcer les voix inactives a tourner.

## 1. Difference avec2.66/2.67

Ces candidats protegeaient via O_FREE dans voice_gate ; cela court-circuitait aussi le comptage/arrêt des voix faibles dans voice_after.2.66 court-circuitait en plus voice_quiet.2.67 ne retirait que ce dernier bypass. La lenteur rapportee n autorisait donc pas a conclure qu une exclusion de selection seule ralentirait autant.2.70 garde strictement les chemins de sommeil2.65.

## 2. Contrat

Ancre unique2800ef8c41f980001858 du gov_key : runtime+76e2 -> SRAM8000e94a. Jmp ss_stock_key apres copie SRAM, avant caches. D0=piste, doit rester intact ; D3/D6/D7/A2..A6 intacts. D1/D2/A0 scratch. Lire l octet moteur du frame lisse8000102c+66*piste.0..5 : D2=-1, RTS.6+ : rejouer les10octets du prologue puis reprendre8000e954. Le flag FREE du sampler reste traite avant la cle par govern. Aucune ecriture de l horloge, de l enveloppe ou des seuils CPU.

Les optimisations privees2.68/2.69 sont conservees.6ch reste disponible mais le retour appareil etablit que le souci existe deja en2ch ; ne pas attribuer le probleme a la copie six pistes sans autre preuve.

## 3. Preuves

[FAIT en emulation] test_stock_selection_only.py, vrai audio_end et govern, pression97% moyenne/108% pic : avant [2,2,2,0,0,0] fades, apres aucune. Cas mixte moteur24+5stock : seul24 reste coupe.25cas quiet/stolen : native0..5 toujours arretees comme avant,6 seul protege ; retours voice_quiet identiques sur0..7. Branch voice_gate toujours67, pas64. Stock sixmachines PUNCH ON40blocs exact ; USB Wizard passe. Regeneration --check identique.

## 4. Limites

[A FAIRE] A01 piste5, tempo/LED et commandes sur appareil. Les coupures de voix natives tres faibles et leur arret a l extinction restent possibles comme en2.65. La cause des pics106..108% reste a optimiser. Si la charge stock+FX seuls devient soutenue au-dessus du budget, cette exclusion ne peut pas recuperer de temps CPU ; une protection de budget des fonctions ajoutees reste une piste distincte. Ne pas presenter2.70 comme une solution universelle de charge.
