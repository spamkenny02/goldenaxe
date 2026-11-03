# Campagne v0309 depuis Nouveau Jeu — Death Adder,FIN et retour intro/titre

Le parcours de la ROM v0309 atteint maintenant la fin du jeu depuis Nouveau
Jeu :neuf cristaux,palais,Hache d'or,Death Adder,generique complet et retour
au cycle intro/titre. Aucun import SRAM/RAM et aucune ecriture de PV,objets,
argent,cles,ennemis ou progression. Les gardes de test sont exclusivement
sur les approches et retires avant les combats de boss. Cette validation de
progression ne termine pas l'objectif complet de fidelite du portage.
La ROM distribuee reste identique,v0309 de2048Kio,checksum4080.

| Etape | Image finale | Salle | Etat jeu | PV | PM |
| --- | ---: | --- | ---: | ---: | ---: |
| earth13e01 | 369442 | 16A | 12 | 100 | 64 |
| switch17c01 | 376548 | 17C | 12 | 104 | 72 |
| portal13c01 | 378052 | 13C | 12 | 104 | 72 |
| switch14b01 | 378952 | 14B | 12 | 104 | 72 |
| portal15a01 | 383148 | 15A | 12 | 96 | 72 |
| earth15b01 | 384732 | 16B | 12 | 96 | 64 |
| switch16c01 | 386046 | 16C | 12 | 96 | 72 |
| pre-final01 | 386941 | 15C | 12 | 104 | 72 |
| release01 | 386942 | 15C | 12 | 104 | 72 |
| final01 | 392967 | 14C | 14 | 100 | 72 |
| ending01 | 401556 | 14C | 0 | 100 | 72 |

Terre13E ouvre le passage vers16A,puis le levier17C ouvre le teleporteur
17B. Les boucles autour des compartiments permettent ensuite13C,le levier
14B,le teleporteur15A,Terre15B,le levier16C et l'approche15C. Chaque etape
est executee dans le jeu,puis relue depuis le demarrage avec les boutons
fixes. Les anciens essais SRAM controles ne sont pas reutilises comme
preuves de cette campagne ;leurs itineraires servaient de propositions.

Le dernier garde est retire a386942 en15C a104PV/72PM. Une perte naturelle
104->100 est observee a386950,encore en15C. Premier combat387036 en14C :
hero100PV/hurt0,Death Adder6D90PV,hache2. Aucune ecriture de test apres
386942 et aucun degat recu pendant ce combat. Les180predictions concordent
sur les65536octets RAM,sans tolerance particuliere pour la pile.

La victoire source est effective392966 (flag du dernier donjon et etat14),
checkpoint392967 a100PV. Neuf cristaux visibles393310,generique de394003 a
401426 (7424images inclusives),nouvelle pressionC apres sa fin,retour au
flux intro/titre401456 et checkpoint401556. L'image finale montre le debut
de l'intro suivante ;elle n'est pas une preuve de chaque image du titre.
Musiques demandees :8D a393266,88 a393671,85 a401464.

Les onze nouveaux checkpoints ont une relecture independante exacte des
65536octets de RAM et du PNG final. Le HUD physique128mots et les neuf
marqueurs sont exacts avant le boss. Le tableau des neuf cristaux,FIN et
l'intro suivante ont ete inspectes visuellement. Rapport et audit :
analysis/cold_palace_final_v0309_report.json et
tools/summarize_cold_palace_final_v0309.py. Sources mesurees dans
validation/v0309-cold-palace-final01-sources.

Le rapport final reste full_game_validated=false :la recurrence aleatoire
SGDK encore utilisee,la phase globale SMS,les sauvegardes normales,le
contenu optionnel et les essais materiels ne sont pas prouves par cette
campagne. Les preuves SRAM controlees restent des composants distincts.
La verification d'une sauvegarde ecrite normalement et de Continuer est
l'etape suivante,sur une branche separee issue du vrai retourD9.
