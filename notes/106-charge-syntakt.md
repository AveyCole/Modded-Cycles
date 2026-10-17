# 106 — Charge Syntakt et clicks avec repeat

Retour AveyCole du 16/10/2026 apres principal 1.78 : plusieurs Syntakt cliquent encore ; changer une piste vers une machine stock ne suffit pas et le symptome revient apres reboot a l entree du combo Control All repeat. Test projet vierge / toutes machines stock / combo relache NON effectue : utilisateur en voiture. Ne pas conclure a une corruption permanente ni a un projet fautif.

## En bref

[FAIT en emulation] Profil du vrai principal : Kick / SYSwm x4 / Kick, 73 286 instructions pour un bloc tenu de la boucle des voix, sans traitement repeat/filtre/mix/FX. Principaux groupes de 64 octets : 0x80003900 (17 024), 0x80003940 (6 636), 0x80003480 (5 432). Les moteurs et tampons chauds sont deja en SRAM interne ; deplacer simplement tout en SRAM n est pas une nouvelle optimisation disponible.

[HYP] Charge et/ou comportement a l entree du combo. Le seuil quatre/cinq/six machines est compatible avec la charge, mais aucune deadline physique mesuree. Reboot sans projet vierge ne tranche pas le diagnostic.

## Prototype natif, non publie

`tools/machines/syntakt_load/recurrence.s` : helper sinus reecrit, MAC produit double equivalent et compteur de boucle simplifie ; 60 octets contre 62, aucun etat/allocation supplementaire. Registres non volatils preserves. Adresses de la fixture principal complet : helper 0x80003470..0x800034ae, origine dynamique dans le payload retrouvee par correspondance unique au runtime. Aucun octet Elektron dans le depot ; dumps uniquement ignores sous build.

`tools/emu/profile_syntakt_load.py` produit les fixtures runtime locales depuis `build/filter-load-main/all-midi`. Compiler le helper propre avec GCC ColdFire puis `test_syntakt_recurrence.py` et `test_syntakt_recurrence_audio.py`. Tous scripts lances depuis la racine du depot.

[FAIT en emulation] 1 024 cas avec etats int32 extremes/aleatoires et longueurs 0/1/32/64 : sorties, etats et accumulateurs identiques ; 380 672 vers 305 152 instructions du helper. Huit blocs du vrai moteur six pistes avec retriggers : sortie exacte, 481 366 vers 473 218 instructions, soit seulement -1,69 % de la boucle complete. PAS une correction hardware demontree. Aucune publication, principal inchange.

## A faire

Verifier un projet vierge quand l utilisateur aura acces a la machine. Preference demandee : prototype SWARM facultatif avec moins d oscillateurs internes pour gagner davantage, ou son rigoureusement identique. Ne pas reduire le nombre d oscillateurs en silence ni annoncer ce prototype comme fix. Si une nouvelle modification sort en test, preuve moteur complet et regulateur de charge avant publication.

## Prototype facultatif et diagnostic (16/10/2026)

AveyCole accepte d essayer Swarm leger, puis demande d optimiser tous les moteurs SY si possible : Toy, Bits, Swarm, tous concernes selon son retour en arrangement six pistes. Aucun nouveau resultat hardware.

Lite garde les oscillateurs 0, 3 et 6 (fondamental et deux desaccordes), au lieu de sept. Quatre appels render supprimes, arguments/nettoyage pile conserves ; somme propre de ces trois buffers dans le meme emplacement. Les niveaux ne sont PAS compenses : timbre/niveau peuvent changer. Helper exact separe et facultatif ; pas de gain Toy/Bits revendique.

[FAIT en emulation] `test_sy_load.py` utilise le vrai programme DSP Syntakt complet, six voix audibles, defaults propres a chaque moteur, notes/retriggers, Swarm MIX 64 pour rendre les voix omises audibles. Sur huit blocs : Toy 265 508 / 265 508 instructions, Bits 286 699 / 286 699, audio exact ; Swarm 402 968 / 252 416 (-37,36 %), audio modifie comme attendu. Appels oscillateurs Swarm : indices 0..6, puis uniquement 0/3/6. MIX 127 rendait deja les detunes inaudibles dans cette fixture, d ou sortie identique malgre reduction des calculs. Ce ne sont pas des cycles ni la charge totale du Cycles.

Limite de fixture : le banc Cycles complet reutilise pour ce travail produisait des zeros sur les voix SY dans son initialisation reduite. Il n est donc PAS retenu comme preuve audio. Le DSP complet Syntakt sert a la preuve sonore ; vrai boot/cache et placement des corps du navigateur sont controles separement. La chaine audio physique complete reste a tester. Les anciennes mesures de boucle Cycles en debut de note sont exploratoires, pas une validation sonore de ces voix.

Diagnostic CPU facultatif : nouveau module repeat seulement lorsque la carte `sy-load-meter` est cochee ; sinon octets principaux 1.78 conserves. Lire gov_load (Q8) pour le pic du combo, gov_avg au relachement ; popup `CPU moyenne% / pic%` depuis UI, jamais formatte/alloue en interruption. Pointeurs issus des metadonnees gov du moteur choisi, gardes zeros et hashes. Les SY originales peuvent etre essayees avec diagnostic seul. Le compteur mesure la fonction audio comme le regulateur existant ; pas toute la latence interrupt/peripheriques.

Toutes options de test decochees : gros profils avec/sans Banque MIDI identiques bit a bit au principal 1.78. Option lite et diagnostic compatibles avec/sans Banque ; versions individuelles Toy/Bits/Swarm compilees. Gardes SHA sur chaque region native et recette d origine ; aucun octet OS exporte, seulement code propre et hashes. Trois cartes experimentales ; principal, MODEL TG bloque, TINY et Wizard facultatif conserves.

Reproduction : `gen_swarm_lite.py`, `gen_beat_repeat.py --catalog build/beat-idle-catalog.json --output build/swarm-lite/beat-meter-data.json`, `gen_swarm_lite_flasher.py`, chacun avec `--check`. `test_swarm_lite_flasher.js` exporte onze profils locaux, `check_midi_current_builds.py --directory build/swarm-lite` compare Python/navigateur. Le catalogue de reservation retire uniquement control-all-beat-repeat du catalogue complet courant. `test_beat_repeat.py --meter` couvre conversion Q8/pic et popup release ; preuves boot/cache avec/sans Banque et filtre/MIDI/sauvegarde.

GCC ColdFire 15.2 / binutils Linux ; code somme/helper assemble uniquement. Douze profils, dont sans Wizard, controles ; desactivation/re-activation sur meme page restaure les references et firmware principal exact. Diagnostic charge UI/peak natif, vrai boot/cache Banque active/inactive et regressions filtre/MIDI/sauvegarde passent. Helper commun exact n est pas presente comme optimisation Toy/Bits : leur compteur DSP est inchange dans les fixtures. Test audio natif complet Syntakt et tests Cycle de boot/callbacks ont des portees distinctes.

`test_sy_load_boot.py` controle chaque region modifiee du payload ET de la SRAM apres vrai boot/cache, avec/sans Banque. `test_beat_repeat.py --meter --case ...` passe aussi sans Wizard. Douze parites de build dont mode sans Wizard ; aucune nouvelle garantie hardware. Verification du regulateur en cours sur son banc long : charges normales, pics isoles/soutenus/severes et selection audible deja passes.

## Test 2 : marge partagee pour toutes les SY

La demande tous moteurs SY conduit a alleger le chemin commun repeat sans modifier les generateurs Toy/Bits. `br_fast_enabled` active un chemin seulement pour bloc etabli : wet plein, fades de voies stabilises, enveloppe pleine sur les 32 samples, indices sans wrap et capture/lecture sans chevauchement futur. Capture par bloc puis mix constant ; sinon chemin general conserve. Copie historique deroulee quatre samples, clamps et quantification identiques, sans hypothese de niveau d entree. Aucun buffer audio nouveau ni format projet.

[FAIT en emulation] Face au principal 1.78 : benchmark mono six voies etabli 9 004 vers 5 068 instructions (-43,7 %) ; capture combo seul mono/stereo 55 304 vers 47 464 (-14,2 %) ; 96 blocs mixtes/fondus/masques/divisions 2 196 248 vers 1 972 069 (-10,2 %). Samples, historique integral et etats exacts. `test_repeat_steady.py` : 256 etats supplementaires, longueurs petites/grandes, bords enveloppe, masques, wraps compteur/circulaire, alias des buffers ; identite et 161 appels du chemin rapide prouves. Pas des cycles physiques.

Le module nouveau est installe si diagnostic OU optimisation est coche. Diagnostic seul garde `br_fast_enabled=0` pour comparaison ; optimisation active la voie rapide. Toutes cartes decochees restaurent exactement les octets principaux. Statut repeat affiche experimental pendant ces options, et retourne au statut principal lorsqu elles sont decochees. Swarm Lite reste un choix sonore distinct. Module propre 4 464 octets ; seize divisions/controle all/fondus/stereo/ABI/erreurs allocation conservent les preuves existantes.

Banc long du regulateur termine : TOUT OK, y compris charge soutenue moyenne initiale zero (600 blocs), pics et choix audible. Test 2 est une nouvelle publication separee ; aucune nouvelle confirmation physique, principal toujours 1.78.

Validation finale test 2 : quatorze profils navigateur/Python identiques, dont Lite seul sans repeat (cinq edits), optimisation sept oscillateurs et sans Wizard. Regressions natives repeat/filtre/MIDI/sauvegarde et boot/cache passent ; regulateur long TOUT OK. Principal 1.78 inchange.

## Retour materiel test 2 et enquete recuperation (16/10/2026)

AveyCole mesure 79 % moyen / 103 % pic avec optimisation active et Lite inactif ; clicks encore presents. Son dernier precisement : ajout de Syntakt declenche filtre/repeat clicky, puis symptome encore avec Toy/Bits apres premiere occurrence. Le projet vierge stock n a toujours pas ete verifie. Ces retours ne prouvent ni corruption d etat ni causalite Swarm seule. Test 2 non confirme comme correction.

[FAIT en emulation] `test_governor_recovery.py` execute les callbacks natifs gate/after/audio_end avec six signaux synthetiques et minuteur force : 110 % pendant 40 blocs, puis 45 %, retrigger des six voies et remplacement par stock. Extinctions observees, puis aucun flag fading/stolen ni quantification residuelle apres retrigger. Cette preuve isolee ne couvre pas DSP SY/filtre/repeat, cache physique ni interruption ; elle ne reproduit pas le defaut utilisateur.

Test 3 diagnostique : la carte diagnostic lit, sans ecrire, les six octets fading et stolen du regulateur a chaque bloc pendant TRACK + RETRIG. Union des pistes pendant le combo, remise a zero au debut du combo ; popup CPU moyenne/pic CUT n. CUT est le nombre de pistes distinctes vues en fondu ou suspendues, y compris deja suspendues avant le combo. Ce n est ni un compteur d underruns ni le nombre de voix coupees au moment exact du popup. Aucun changement d algorithme sonore ni seuil du regulateur. L objectif est de distinguer activite du regulateur et depassement de temps physique avant de proposer un correctif.

[FAIT en emulation] Recuperation egalement sur vrais builds navigateur, boot/cache avec et sans Banque. CUT prouve cumulatif par piste, remise a zero entre combos, lecture seule des flags ; fondu/repeat/masques/ABI et 256 etats conservent leur sortie. Audit exploratoire DSP Syntakt natif Toy/Bits/Swarm, cinq blocs : MACSR restaure et quatre accumulateurs vides a chaque fin de boucle. Pas de corruption persistante demontree.

Validation test 3 : quatorze profils navigateur/Python, memes hashes 1.78 toutes options decochees ; vrais boots/callbacks avec et sans Banque, CUT cumulatif/reset/read-only et 256 etats audio passes. check_overlaps/registry et generateurs --check passent. Aucun correctif des clicks annonce.
