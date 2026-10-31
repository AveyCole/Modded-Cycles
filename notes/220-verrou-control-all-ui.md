# 220 — Verrou CTRL-ALL borne a l UI

Demande utilisateur du31/10/2026 : double tap TRACK, sortie TRACK/BACK ; appliquer au fichier Activity Masks2.65 stock-screen exact. Generateur `tools/gen_control_all_latch_test.py`, source `tools/machines/control_all_latch/latch.c`, preuve `tools/emu/test_control_all_latch.py`. Adresses : VA de l OS1.13.

## En bref

[FAIT] Candidat Full prive2.75, base SHA256011b1ab5905e51ef77086515bfecc1bba2936c6092a8a54d4ab43218c0f13911. Ne reprend ni DSP, ni protections, ni routage des essais2.66-2.74. La version identifie seulement ce patch UI.

## 1. Geste et contrat

Deux taps TRACK propres, chacun de350ms maximum et ecart release/press de350ms maximum. Comparaison timer non signee135168ticks/ms. Repeats/long, touches intermediaires, encodeurs, FUNC/RETRIG/MACHINES/SETTINGS annulent l armement. TRACK ou BACK quitte et consomme sa paire ; les releases normales sont transmises avant l activation.

TRACK virtuel seulement pendant le handler encodeur, pour indices2..13 et event0x400fbebc, hors Mod Setup/Song et hors MACHINES/SETTINGS. DATA et selecteurs FX14/15 exclus. Ni TrackSelectionView ni etat des trigs verrouilles. Etat non sauvegarde, Off au boot.

## 2. Implementation et memoire

Module980octets a0x4691e000 ; BSS a0x4691f800, limite0x46920000. Les bornes du module Activity Masks precedent sont verifiees. Nouveau loader copie/efface ces zones, puis garde toute la chaine native. L immediat du relais tardif am_boot_finish du loader2.65 est redirige vers cal_finish ; celui-ci installe les wrappers UI puis execute le relais2.65 original avant activation cache.

Wrappers de aa_face_key0x469310c4 et aa_face_encoder0x46931160 avec prologues verifies/rejoues sans instruction relative. Getter0x4007faf4 delegue vers son ancien JMP0x468037ce, sauf TRACK dans la portee encodeur. Aucun hook ajoute dans l IRQ audio. Titre2.75 ; pas de publication.

## 3. Preuves

[FAIT en emulation] Tests des taps, des longs/repeats, wrap timer, sorties, delegation release, menus/modificateurs, TRACK+PAGE et virtualisation strictement encodeur. Getter physique reste faux apres retour.

[FAIT en emulation] Six machines stock PUNCH40blocs exacts ; affichage et commit natif des machines inchanges ; boot et USB Wizard independant du main-send conserves. Tests executes avec cal_finish installe. Regeneration --check identique.

[FAIT] Audit byte a byte : sur toute l ancienne image decompressee, seulement9octets changent dans le titre, le pointeur loader et l immediat du relais tardif. Le reste est identique, puis nouveau loader/module ajoutes. Le binaire audio existant n est pas recompile.

## 4. Limites

[A FAIRE] Essai materiel du verrou et du comportement musical sur six pistes, masques CTRL-ALL et p-locks, trigs, raccourcis, playback. Preuve UI instrumente la delegation encodeur ; ne pas pretendre avoir valide toutes les editions sonores sur le materiel. Aucun resultat hardware revendique.
