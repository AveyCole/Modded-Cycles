# 218 — Oscillateurs : entrees de modulation nulles

Demande utilisateur du 31/10/2026 : reduire la charge sans modifier les sons stock. Generateur `tools/gen_activity_masks_test.py --one-mod-osc`, source `tools/machines/track_fx/one-mod-osc.S`. Adresses : VA de l'OS 1.13.

## En bref

[FAIT en emulation] Full prive 2.73 : 512 comparaisons PCM/etat/EMAC/ABI exactes. Aucun resultat materiel pour cette version. Gain total modeste ; correction des clics non confirmee.

## 1. Contexte et capture

[FAIT rapporte par utilisateur] 2.71 : A85 P108 O118 N0 ; V58 F6 X26 ; L3 S1 R11. T5 A01 est KICK. Les echeances restent depassees sans vol.

[FAIT] Capture MIDI WinMM en lecture seule, sans commande sortante. Codecs natifs pour le pattern et les six sons ; donnees utilisateur hors versionnement. Le codec modifie restaure cutoff 32512 : ne pas interpreter les champs ajoutes avec le codec stock.

## 2. Contrat

[FAIT] Hooks 0x400a8152 et 0x400a82cc, module DDR 0x4691a000, 16 348 octets sur 20 480 disponibles. Epilogues natifs conserves. Aucun nouveau placement SRAM de ces noyaux.

Une entree est retiree seulement si poids et delta sont nuls ; l'autre peut evoluer. Interpolation, MSAC de gain et ordre de prelecture pour le feedback conserves. Boucles deroulees par quatre. Le cas general conserve le calcul natif avec un petit surcout de garde.

## 3. Preuves

[FAIT en emulation] `test_one_mod_osc.py` : 256 cas par operateur, rampes actives, accumulateurs physiques aleatoires, aliases aux sorties, PCM/etat/EMAC/ABI exacts. Gain isole a une entree : environ 11 a 38 % des instructions, pas du cout total.

[FAIT en emulation] Six machines stock PUNCH, 40 blocs exacts ; boot natif et USB Wizard independant du main ; regeneration --check identique.

[FAIT en emulation] Six presets A01 captures, 32 blocs synthetiques exacts. Total voix 1 287 655 -> 1 267 356 (-1,58 %) contre 2.70. Pic 46 026 -> 44 796 ; bloc stable 40 023 -> 39 408. Reutilisation mono 2.72 seule trop faible pour resoudre le depassement.

## 4. Limites

[A FAIRE] Test materiel A01 au boot neuf, T5, clics, CTRL-ALL filtre et DX normal. Banc de presets, pas la sequence complete avec p-locks. Instructions emulees sans mesure des cycles/stalls ColdFire. Aucun push ni promotion ; latch CTRL-ALL differe.

## 5. Retour materiel utilisateur (31/10/2026)

[FAIT rapporte par utilisateur] 2.73 : « worse clicking and slowdown than before ». Version rejetee, aucune promotion. Les preuves PCM et les instructions Unicorn ne predisent pas le temps IRQ materiel.

[FAIT] 2.70 avait un module de 13 660 octets ; 2.72, 14 660 ; 2.73, 16 348. Deux changements depuis 2.70 : reutilisation mono et noyaux oscillateurs. Le retour ne permet pas de les departager. [HYP] Cout des acces DDR, cache instructions ou ordonnancement EMAC ; aucune cause prouvee. Reprendre une reference sans ces deux changements avant toute autre optimisation ; ne pas annoncer une amelioration sur la seule reduction d'instructions emulees.
