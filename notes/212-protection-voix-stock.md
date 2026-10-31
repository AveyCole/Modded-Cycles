# 212 — Protection des voix stock

Demande du 31/10/2026 : A01 piste5 coupe sur plusieurs prototypes. Generateur : `tools/gen_activity_masks_test.py --stock-voice-protection`. Adresses : VA OS1.13.

## Reponse courte

[FAIT] Le regulateur ajoute autorisait le vol des machines natives0..5. Le candidat prive Full2.66 les protege, ainsi que Wizard6 deja protege. Les moteurs ajoutes restent soumis au regulateur. Aucun changement EMAC ou reseau de reverbe dans ce candidat.

## 1. Contrat

La branche a `0x8000e8b6` dans voice_gate passe de BEQ a BCC : D1=6, comparaison avec le moteur. Les IDs0..6 effacent fading/stolen et utilisent O_FREE. Installation apres copie SRAM par am_boot_finish, avant activation des caches. Le raccourci generique voice_quiet a `0x401adb4c` retourne0 pour les voix natives ; autres voix : instructions originales puis continuation `0x401adb52`. Aucun changement des enveloppes natives.

## 2. Preuves

[FAIT en emulation] Le vrai regulateur, sous pression controlee, selectionne trois voix stock avant correction ; aucune apres. Un moteur ajoute reste selectionnable. Wizard USB et dessin/commit MACHINES natifs passent. Les six machines PUNCH ON correspondent exactement au PCM stock pendant40 blocs. TONE piste5 correspond pendant700 blocs, avec mute/unmute du mixeur et relachement de note.

Le test long ne reproduit pas une difference dans le candidat ancien sans pression : il ne constitue donc pas une reproduction du pattern usine A01. Le test direct voice_quiet demontre la difference de retour, pas une coupure audible A01.

## 3. Limites

[A FAIRE] Verification physique A01 piste5 et A11. Le projet usine exact ne figure pas dans les fixtures. La protection ne supprime pas le cout CPU des fonctions ajoutees. Aucun resultat appareil revendique, aucune promotion dans le flasher.

## 4. Suite demandee

CTRL-ALL : double appui TRACK pour verrouiller ; TRACK simple ou BACK pour sortir. La selection de piste doit rester physique/momentanee. Le verrou doit entourer uniquement les edits encodeur, sans maintien synthetique global de TRACK. Verification des accords existants et preuves natives avant livraison.

## 5. Retour appareil et correction isolee2.67 (31/10/2026)

[FAIT, retour utilisateur]2.66 modifie les coupures, mais ralentit fortement les commandes et desynchronise les LEDs ; timing general affecte. Candidat rejete, ne pas publier.

[HYP] L interdiction totale de voice_quiet augmente le travail audio meme apres extinction des notes.2.67 conserve la protection du regulateur mais ne detourne plus voice_quiet : le raccourci d inactivite Model-TG est exactement celui de la base. Option --stock-native-idle, exige --stock-voice-protection. Cela isole une cause possible ; aucune garantie temporelle sans essai appareil.

[FAIT en emulation] Le regulateur protege toujours0..5, conserve Wizard et peut soulager un moteur ajoute. Les retours voice_quiet sont identiques a la base pour0..7. Verification USB Wizard reussie.
