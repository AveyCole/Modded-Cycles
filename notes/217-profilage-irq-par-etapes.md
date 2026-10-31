# 217 — Profilage materiel du pire bloc audio

Retour utilisateur31/10/2026 :2.70 ne vole plus la voix A01 mais clique, meme apres boot neuf sans aucun geste filtre. Pas une regression exclusivement CTRL-ALL. Candidat prive diagnostic Full2.71, option --audio-profile ; outils audio_profile_assets.py/test_audio_profile.py. Adresses : VA OS1.13.

## Reponse courte

Instrumenter avant une nouvelle optimisation speculative. Sept marqueurs lisent le timer materiel ; hp_finish reprend gb_finish puis memorise les etapes du pire bloc. Meme audio2.70, donc pas une correction sonore. Ce candidat ne doit pas etre promu.

## 1. Marqueurs et contrat

Sites4005979e/8,400597ba/10,400597cc/8,4005980a/8,40059824/6,40059858/10,40059878/8. Chaque stub sauvegarde D0/D1/SR, lit FC07000C, ecrit son timestamp, restaure registres/CCR et rejoue exactement les instructions originales avant continuation. Les instructions deplacees ne contiennent aucun branchement relatif ; l unique JSR accounting reste absolu. Les7sites et les relais gb_finish/diagnostic sont poses au boot tardif, avant caches. Aucun EMAC touche par les marqueurs.

hp_record : actif seulement DX et PLAY ; refuser un timestamp hors de l IRQ courante. Le cout ajoute des marqueurs et de la copie de pic est une perturbation de mesure ; aucun gain de cycles revendique. Aucun DMA simule sur appareil.

## 2. Affichage

Geste DX habituel, trois fois : A/P/O/N puis V/F/X puis L/S/R. Le premier geste fige les6etapes du pire bloc observe pour les deux pages suivantes. Pourcentages du budget90112ticks, arrondis vers le bas.

V : voices, avec traitements inclus dans le caller. F : apres voices jusqu a fin Volume/Dist+filtres, inclut velocite/copie d etats. X : accounting+mixeur/retoursFX. L : dispatch LFO. S : autres preparatifs audio. R : avant/apres la fonction audio dans l IRQ, inclut USB et travail restant ; ce n est pas uniquement du cout USB. La somme des ticks partitionne le meme bloc, pas les maxima de blocs differents. La moyenne A et les compteurs O/N gardent leur intervalle DX historique.

## 3. Preuves

[FAIT en emulation] Les7stubs vs instructions natives : registres D/A, CCR, pile active et continuations exacts. Horloge injectee : ticks600+400+500+300+300+400=2500 pour le meme bloc ; timestamps perimes rejetes. Vrai geste natif teste sur3pages, snapshots preserves, format A75 P108 O13 N0 puis V11 F22 X33 puis L44 S55 R66. USB Wizard passe ; --check identique. Aucun resultat temporel appareil encore disponible.

## 4. Acceptation

[A FAIRE] En2ch, boot neuf, A01 sans geste,10secondes ; relever les3pages. Selon etape dominante, profiler/optimiser son vrai noyau et verifier son audio. L objectif reste voix stock conservees ET absence de clics/retard, jamais N=0 seul.
