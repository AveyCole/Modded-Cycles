# Audit startup indépendant — branche séparée

Branche : `codex/independent-startup-20261014`, depuis main2ccc53fe8c8af0a06cd012cae26f43586b7ddff1. Aucun changement du flasher principal dans cet audit.

## État matériel

Deux essais sans Model-TG, presque tous les autres mods sauf machines supplémentaires : logo puis écran blanc et appareil entier figé. La garde UI/LED n’a pas corrigé le problème. Banque seule sans TG non essayée sur matériel. Aucune correction matérielle revendiquée.

## Nouvelle frontière vérifiée

`tools/emu/test_independent_startup_handoff.py` compare stock et le catalogue réel sans TG jusqu’à l’entrée native400cefa0, au-delà de la reprise4000053a où les anciennes preuves s’arrêtaient. BSS effacée, RAW privé préservé ; D2–D7 et A2–A6 conservés ; même pile/retour, masque IRQ et accès au registre matériel simulé. PASS.

Le décompresseur n’utilise pas A3–A6/D7. D0/D1 et A0 sont établis par le code natif de reprise ; ses valeurs à l’entrée ont été vérifiées. A1 est volatile et n’est pas revendiqué identique.

## Limites et suite

Les MOVEC sont observés puis sautés ; le comportement réel des caches ColdFire n’est pas simulé. Le périphérique mémoire est contrôlé. Cette preuve ne couvre pas l’initialisation native après400cefa0, les premières interruptions audio/UI et les callbacks pendant construction des objets. Priorité : tracer cette phase et les contrats des hooks, puis isoler un candidat minimal avant un nouvel essai matériel. Ne pas proposer une nouvelle garde comme solution sans preuve.

Extension vérifiée : après400cefa0, exécution réelle jusqu’à400cf012. Table native de256vecteurs identique, état initial scheduler identique, singleton UI encore nul ; RAW privé toujours intact. La prochaine frontière est le premier service natif d’initialisation400057e8 puis l’activation IRQ/TRAP.

Première tâche et configuration IRQ : exécution native jusqu’à400cf040, avant TRAP0 ; structures tâche, pile initiale et writes périphériques simulés identiques, PASS. Le changement de contexte architectural réel et les callbacks UI/audio ne sont pas couverts.

Hypothèse distincte : projet ancien contenant des machines retirées. Les helpers stock record_at/of retournent REC_BASE−76 pour certains indices hors des six machines ; cette valeur n’est pas un record des six machines stock. Son rôle exact comme éventuelle sentinelle n’est pas établi. Une garde locale réserve un record KICK aux indices hors plage, sans toucher les six machines ni les valeurs du projet. Deux helpers×259indices PASS ; boot/vecteurs/première tâche avec candidat PASS. Cause de l’écran blanc NON confirmée. Le candidat reste local/non proposé au flasher ; la branche contient générateur et preuves.

AveyCole confirme que les six pistes au démarrage utilisent les machines stock : l’hypothèse du projet avec machines retirées est donc écartée pour l’échec rapporté. La garde records reste un prototype de durcissement, pas une correction de cet écran blanc.

Callbacks froids : IPL0/IPL7, contexte Banque/LFO nul, wrappers audio/LFO/output et voix inactive ; délégations stock/arguments exacts et aucun accès UI/allocation, PASS. Les fonctions DSP déléguées ne sont pas émulées dans cette preuve. Suite : phase de construction UI et callbacks après création des contextes ; comportement cache/interruptions réel toujours non couvert.
