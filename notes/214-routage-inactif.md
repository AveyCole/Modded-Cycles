# 214 — Contourner le routage inactif

Demande du31/10/2026 : poursuivre l optimisation avant un essai sans6ch. Generateur gen_activity_masks_test.py --routing-fast-path, candidat prive Full2.68. Adresses : VA OS1.13.

## Reponse courte

La base reste le comportement2.65 : pas de protection2.66/2.67 qui empeche le regulateur de soulager une surcharge stock. Aucun retrait6ch ni filtre, aucune promotion. Gain mesure modeste, pas une resolution prouvee du timing.

## 1. Contrat

mf_requested est recalcule par slot-state/runtime lors des choix et chargements de pattern. Si nul, aucun send custom n est redirige : sf_sum6/sf_sum7 appellent les memes melangeurs natifs sans reconstruire les tableaux de gain. sf_post appelle toujours mf_old_post ; si aucune affectation et lt_active nul, il retourne sans preparer12routes. Si une queue persiste, traitement historique conserve. Aucun reset arbitraire des masques au chargement de pattern.

Les trois fonctions sont recompilees ensemble depuis firmware-bridge.c afin de partager leurs memes nouveaux buffers sends/enabled. Boot tardif detourne les trois anciens points mf_sum6/mf_sum7/mf_post. Le module primaire reste4691a000..4691f000, BSS borne avant46920000 ; code13320octets. USB, FX natifs, routage Wizard et enveloppes conserves.

## 2. Preuves

[FAIT en emulation] test_idle_routing_fast.py : post inactif mode per-track106->19instructions ; mode standard12->13 ; affectation active ou queue106->105. Appels DSP observes/stubbes dans cette preuve de routage, aucune revendication PCM de noyau.

measure_idle_routing_pcm.py : vrai mixeur natif et DSP natifs, six voix avec sends delay/reverbe, trois blocs. Hashes PCM pistes et mix identiques avant/apres, mix non nul. Cout stable du mixeur21171->20714instructions, soit457economisees. Poll de configuration fixe stubbe ; completion DMA modelisee immediate, transfert/bus non mesures. Les appels voix, LFO et post sont separes : ne pas additionner comme une vraie IRQ profilee.

Tests stock sixmachines PUNCH ON40blocs, Wizard USB et commit/dessin MACHINES passent. Regeneration --check identique.

## 3. Limites

[A FAIRE] Temps IRQ sur appareil, A01 piste5 et precision sequenceur. Le gain est inferieur a1% d un chemin complet typique en instructions ; insuffisant pour promettre de corriger un ralentissement severe. Les masques ne remplacent pas le profilage bus/cache/DMA.6ch reste inclus, retrait compare reporte a la demande utilisateur. CTRL-ALL latch differe.

## 4. Extension des preuves et mesure utilisateur

[FAIT en emulation] Ring Mod reel force sur les sixpistes avec kit non nul ; lt_calls[4]>0 exige au bloc2. Retrait des affectations au bloc3,14blocs executes au total : PCM pistes/mix identiques avant/apres. Surcout actif21instructions au premier bloc ; apres retrait gain542instructions sur le mixeur dans ce cas. La completion DMA reste modelisee, pas de revendication temporelle physique.

[FAIT, retour utilisateur31/10/2026] Sur sa2.65 : A76 P108 O10 N9 apres environ10secondes sur le pattern problematique. C est compatible avec une surcharge de pointe et des vols de voix, malgre une moyenne sous budget. Variante2.65 exacte demandee car les fichiers EMAC/reseau portent aussi ce titre. Il faut mesurer/reduire les pics, sans seulement interdire les vols.
