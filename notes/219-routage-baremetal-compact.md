# 219 — Routage bare-metal compact

Demande utilisateur du 31/10/2026 : implementer les reductions possibles dans le code bare-metal apres la regression 2.73. Generateur `tools/gen_activity_masks_test.py --baremetal-routing` ; transformation `tools/baremetal_routing_assets.py`. Adresses : VA de l'OS 1.13.

## En bref

[FAIT] Full experimental 2.74 revient aux oscillateurs et au mix stereo 2.70. Les changements 2.72/2.73 sont exclus par assertion. Aucun nouveau noyau de calcul audio.

## 1. Changements

Le dispatch compte seulement jusqu'au deuxieme contributeur (gain OU delta non nul), puis appelle le noyau natif6/7 qui traite tous les inputs. Zero et un contributeur conservent les chemins sparse exacts. Aucun changement de rampe.

Apres `mf_sync_audio`, le masque enabled est reconstruit seulement si le mode par piste est pret ET qu'une affectation ou queue est active. La synchronisation de projet/pattern reste executee a chaque appel ; les queues gardent les lectures kit/mute. Aucun reset arbitraire de bitmask au chargement.

La seule unite de routage est compilee O2 plutot que O3. Module complet : 13 660 octets (2.70) -> 12 028 (2.74). Les noyaux natifs ne sont pas recompiles. Placement DDR 0x4691a000 et BSS 0x4691f000 inchanges ; SRAM sum7 2.69 conservee.

## 2. Preuves

[FAIT en emulation] `test_baremetal_routing.py` : 384 combinaisons exhaustives des masques6/7 avec gains statiques ou rampes : PCM/gains/EMAC identiques a2.70. Test des lectures kit : inactif saute, affectation/queue conserve ; sync toujours appele une fois.

Les preuves stock PUNCH, USB Wizard, mix natif inactif et RingMod actif/queue sont executees sur la construction finale ; leurs fichiers JSON restent dans output/parity265. `--check` identique.

## 3. Limites

[HYP] Le code plus compact pourrait reduire la pression sur le cache instructions. Aucune mesure materielle ne le prouve. Les instructions Unicorn ne donnent pas les cycles. Ce changement ne constitue pas une correction confirmee du depassement A01. Ni push, ni promotion au flasher.

[FAIT en emulation] Comparaison finale des hashes PCM : inactif et14 blocs RingMod/retrait/queue identiques. Compromis O2 : mix inactif20 714 ->20 683 instructions ; RingMod actif peut augmenter environ2 %. Le gain de cache reste une hypothese, pas un gain CPU prouve.

## 4. Retour materiel utilisateur (31/10/2026)

[FAIT rapporte par utilisateur] « still way worse clickin and slowdown ». 2.74 rejetee. Ni code compact O2 ni les nouvelles gardes ne constituent une correction validee. Exclure les changements 2.72, 2.73 et2.74 de la suite ; reprendre une image2.70 exacte pour separer une regression de la compilation/layout d'un changement de logique. Cause encore inconnue ; aucune conclusion sur le cache a partir des seuls compteurs Unicorn.
