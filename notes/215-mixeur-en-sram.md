# 215 — Petit noyau mixeur natif en SRAM

Demande du31/10/2026 : examiner SRAM et pics CPU sans retirer6ch. Candidat prive Full2.69, gen_activity_masks_test.py --routing-fast-path --sram-mixer. Adresses : VA OS1.13.

## Reponse courte

Deplacer le vrai sum7 natif126octets vers8000ea48..8000eac6. Pas de changement des tailles de buffers, filtres, arrondis ou multiplication. Ni attribut GCC symbolique, ni adresse arbitraire. Le gain temporel reste a mesurer sur appareil.

## 1. Reservation

La recette31-syntakt-tg-sd-cp-toy-bits-swarm-macro.json termine son dernier bloc hot en transit467077de, soit SRAM8000ea46 ; fin de banque8000eae0. Aligner a8000ea48 laisse152octets. Le generateur exige que cette queue complete soit nulle dans le runtime de la base epinglee ; les etats/regions precedents restent intacts. La copie de126octets laisse26octets apres le noyau. Ne pas generaliser cette adresse a d autres firmwares.

## 2. Installation et contrat

Les octets sont extraits du sum7 stock40056698..40056716 ; prologue8octets et RTS verifies. Un seul branchement relatif de boucle, cible interne. Copier par mots pendant am_boot_finish, apres les copies SRAM natives et avant activation des caches. Detourner mf_old_sum7 vers8000ea48. Appels, pile, callee-save, MACSR, EMAC, sept gains et rampes natifs conserves.6ch, CHORD, banques Syntakt et regulateur conservent leur comportement2.65.

## 3. Preuves

[FAIT en emulation] test_sram_mixer.py :64 jeux aleatoires, vrai code MAC ColdFire, PCM/gains/etat EMAC exacts ; trace executee a8000ea48 ; voisins avant8octets et apres26octets preserves. USB Wizard passe. Pas de revendication de cycles economises ni suppression prouvee des coupures.

## 4. Resultats appareil precedents

Utilisateur : Activity Masks2.65 A76/P108/O10/N9 ;2.68 A75/P106/O13/N13 et memes coupures piste5. La petite optimisation de routage ne resout pas le probleme.2.66/2.67 restent rejetes pour lenteur/timing.2.69 garde le regulateur au lieu d interdire sa protection contre les overruns.

## 5. Suite

[A FAIRE] Comparer A/P/O/N et A01 piste5 en2.69, meme configuration que2.68. Ne pas donner un gain de cycles exact depuis Unicorn : instruction/bus/cache et DMA materiels distincts. Pas de conversion EMAC universelle ni unrolling impose ; comparer arrondis, accumulateurs, ABI et taille du code pour chaque noyau. Test sans6ch reste une comparaison separee.
