# Coût des étapes natives lors de la salve PAL

ROM c0044 inchangée. Observation des PC d’entrée et de retour sur le
parcours enregistré. Le témoin et la mesure sont lancés dans deux processus
neufs ; leurs 65 536 octets de RAM et leur image finale concordent.
La capture finale concorde aussi visuellement avec le rejeu précédent.
Les appels incluent les interruptions qui surviennent entre entrée et retour.

À l’image 80 000 :

| Étape | Cycles maîtres |
| --- | ---: |
| Simulation complète | 230146 |
| Dont acteurs | 115304 |
| Préparation des motifs du héros, pose changée | 241332 |
| Construction de la liste de sprites | 154168 |
| Masquage des lignes | 313677 |

Le masquage traverse l’interruption suivante, qui occupe 79702 cycles
maîtres. Le retirer de ce seul appel donne 233975 cycles hors interruption.
À 80 002, la préparation des motifs sans changement de pose coûte 2772
cycles. La préparation d’une nouvelle pose mérite donc une optimisation,
en particulier ses copies séparées de trois octets. Cela reste une mesure
de coût Mega Drive et ne prouve pas une cadence conforme à la Master System.

Les deux premiers essais de comparaison utilisaient des chargements de
cœur dans des contextes de processus différents. Ils échouaient sur 24
octets de pile, sans différence des champs de jeu ni de l’image. Ils ne
servent pas de preuve d’équivalence complète. Le témoin en processus neuf
corrige la méthode et conserve la comparaison de toute la RAM.

[Archive des pilotes, mesures et captures](c0044-burst-stages/manifest.json).
