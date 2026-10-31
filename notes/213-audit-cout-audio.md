# 213 — Audit du cout audio apres2.67

Demande utilisateur du31/10/2026 : timing fortement perturbe en2.67, seulement apres PLAY ; verifier les masques et l efficacite globale. Adresses : VA OS1.13.

## Reponse courte

[FAIT] Les masques ne suppriment pas automatiquement le cout des wrappers.2.66/2.67 ne constituent pas une correction valide des problemes temporels rapportes. Ne pas promouvoir ces candidats.

## 1. Perimetre etabli

Dans les sources : lt_active/lt_sent pilotent les DSP FX par piste ; li_active_tracks exclut les banques secondaires inutilisees ; pp_custom_mask exclut les transients custom sur0..5. Les rampes, queues, reveils et p-locks interdisent un simple masque de boutons. Le fichier fx_menu/dsp.c contient aussi fx_aux_active_mask, absent du module fx_menu historique embarque par le generateur actuel : ne pas revendiquer cette optimisation dans le binaire. Son chemin make_aux ne correspond pas au mode REVERB natif0 ; ce n est pas une explication demontree du souci usine.

## 2. Mesure native reproductible

`tools/emu/measure_stock_voice_cost.py --build ../stock-voice-native-idle/full --output output/parity265/stock-native-idle-voice-cost.json`.

[FAIT en emulation] Six machines natives, PUNCH ON,12 blocs de32samples, PCM exact : attaque45842instructions stock contre45126mod ; bloc stable42257contre39671 (environ-6,1%). Les fixtures reprennent celles de test_stock_machine_parity.py, avec le vrai bootstrap tardif. Ce compteur couvre seulement la boucle des voix. Aucun resultat sur les cycles materiels, caches, USB, mixeur, filtres ou IRQ complete.

## 3. Priorites

[A FAIRE] Mesurer le pic de l IRQ complete face au delai de90112ticks/32samples, puis attribuer le cout aux sends/mixeur, filtres, retours FX, repeat et USB. Le code gb_finish mesure deja le total et conserve gb_last_total ; un compteur voix seul ne suffit pas. Prevoir mesures inactif, usine, queues et combinaisons lourdes.

[A FAIRE] Conserver les caches/rampes/queues mais contourner les wrappers supplementaires quand aucun utilisateur de la fonction ne subsiste. Eviter de recalculer en IRQ les choix/routages inchanges ; publier un snapshot borne, verifier invalidations pattern/projet, p-lock et modulation avant application. Ne pas inventer un gain en cycles a partir d un masque.

[A FAIRE] Candidat diagnostic a changement unique, puis preuve audio et appareil. Ne pas reutiliser le premier wrapper EMAC : les mesures note211 montrent davantage d instructions. Ne pas alterer les longueurs acoustiques pour gagner un AND sans accord explicite.

Le verrou CTRL-ALL reste differe jusqu a stabilite du playback.
