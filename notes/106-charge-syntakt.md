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
