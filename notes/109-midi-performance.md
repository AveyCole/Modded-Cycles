# 109 — Repeat MIDI et filtre Control All depuis B

AveyCole demande apres promotion 909.2 un beat repeat sur les notes MIDI et le filtre Control All depuis B, affectant a la fois les pistes audio internes et les instruments MIDI. Nouvelle combinaison test seulement. Adresses : VA OS 1.13.

## Reponse courte

Le test 909 dedie utilise les memes divisions et le geste TRACK + RETRIG maintenus. Il repete la derniere note **sequencee B** de chaque voie incluse, avec canal/port actuels. Il ne boucle pas une capture historique de phrase MIDI ni les notes MIDI natives A. Pas de note connue : silence. Stop/pause, mute, changement de pattern ou relachement annulent les notes repetees. Le MIDI conserve la division musicale choisie ; l audio garde sa limite de buffer aux tempos lents.

Depuis B, TRACK + MACHINES + SWEEP/CONTOUR applique un delta aux filtres audio inclus et transmet CC74/CC71 sur les canaux/ports B configures. Une voie MIDI muette ne recoit pas de CC, mais son filtre audio change. Hors de ce geste, assignations CC et menus gardent leur chaine originale.

## Construction

`tools/gen_midi_performance.py` compile `tools/machines/midi_performance/` avec GCC ColdFire 15.2. Corps propre lie a zero, relocalisations R_68K_32 exportees et controlees. `tools/web/midi-performance.js` lie les symboles du vrai catalogue prepare : wrappers de `ml_step`, `ml_clock`, `mlkc_enc`, trampolines de huit octets strictement verifies. L extension est ajoutee au payload repeat ; longueur/source du chargeur sont recalculees apres recompression de la banque modifiee. References writes/payload mises a jour, limite ROM toujours controlee par le builder.

La file native `ml_step` reserve un Off avant chaque On. Le wrapper ne fait aucune sortie physique dans l interruption audio. Les notes normales des voies incluses sont suspendues seulement pendant la repetition ; le sequenceur continue sa phase. Une note maximum par voie et appel, retard sans rattrapage en rafale. Off a demi-intervalle, plus Off a toute annulation. Les CC UI utilisent le writer existant a IPL0.

`[FAIT en emulation]` Les descripteurs du filtre 909 etaient absents de la table relogee `0x46734000` : les nouveaux descripteurs restaient dans MAIN OS tandis que la table moteurs venait de l OS officiel. Le test propage les deux descripteurs actuels dans la recette de relocalisation avec gardes sur les octets officiels. Les appels natifs inverse CC et setters audio rendent alors les vrais changements k24/25. Cette correction reste dans le test ; aucun changement silencieux du 909 publie.

## Preuves et limites

`test_midi_performance.py --case build/midi-performance/all` execute le vrai boot/cache et verifie chaque partie de l extension. File MIDI native, seize divisions, 64 masques, stop/mute/release, wrap32, changement de pattern ; le corps du sequenceur est isole pour les mesures deterministes de repetition. Pas de MIDI sur le combo sans pad division. Filtre : vrais Project::setParameter et SoundParameterContext, deux potards, notifications et CC exacts, masque et piste B active, voie MIDI muette. Singletons, observateurs, peripheriques et sortie physique simules.

Regressions sur le SYX navigateur reel : banque/scheduler, persistance, Genie, filtre courant, repeat audio, six voix 909. Test navigateur : quatre FileReader, signature, refus firmware modifie, remplacement/retrait WAV et absence de transfert automatique. Parite Python/navigateur. Aucun firmware, dump ni sample utilisateur publie.

`gen_midi_performance_page.py` cree uniquement `docs/flasher-midi-performance-test`. Nouvelle combinaison experimentale, verification hardware requise. Le 909 publie et le main ne recoivent pas ces nouveaux comportements avant validation AveyCole.
