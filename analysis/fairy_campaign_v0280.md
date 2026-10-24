# Ravitaillement naturel avant le deuxième donjon

Le code du jeu et la ROM restent ceux de la v0280. Le travail porte sur un
parcours de progression exécuté par des commandes ordinaires depuis le démarrage,
sur SMS et MD, sans injection de RAM ou de sauvegarde.

La fée de la salle extérieure C9 est visitée après le premier cristal.
Les deux machines accomplissent le dialogue, la récompense de capacité,
le remplissage de la jauge et la sortie normale de la maison AF :

| État à la sortie | SMS | MD |
|---|---:|---:|
| Vie maximale | 40 | 40 |
| Vie actuelle | 40 | 40 |
| Indicateur extérieur C9 | 2 | 2 |
| Premier cristal | 128 | 128 |
| Position extérieure | C9, 104, 96 | C9, 104, 96 |

Les 256 indicateurs persistants et les 1 280 octets de carte extérieure sont
identiques. Chaque parcours est rejoué depuis le démarrage avec les commandes
fixes enregistrées, sans retour d'état pour décider des boutons. La RAM finale
complète — 8 192 octets SMS, 65 536 octets MD — et le PNG final sont reproduits
exactement pour chaque machine. Cela ne signifie pas que les images SMS et MD
sont déclarées identiques à chaque frame, ni que leurs horaires absolus ou
leurs formes d'onde ont été vérifiés.

Le nouveau trajet vers la deuxième entrée ne comporte aucun décès. Il y arrive
avec 32 points de vie sur MD et 26 sur SMS ; le précédent trajet MD arrivait
avec 14. Cette amélioration provient des choix de parcours et de la récompense
déjà présente dans le jeu, sans réduction des dégâts ou modification des règles.

## Deuxième cristal non acquis

Les essais supplémentaires échouent encore. Le meilleur essai MD avec placement
latéral laisse le boss 63 à 14 points de vie avant la mort du héros. Les variantes
de placement, d'attente pendant la préparation des tirs et d'esquive sont des
expériences du pilote, activées par une option explicite ; elles ne sont pas
présentées comme des stratégies validées. Le code exact de chaque variante est
conservé avec les captures et les commandes.

Sur SMS, le combat de la salle 151 peut aussi immobiliser le pilote face à un
ennemi inaccessible. La table de scripts prévoit dans cette salle un mécanisme
de redessin à la coordonnée 360, accessible depuis le point 184,40. Le pilote
actuel privilégie le combat avant ce mécanisme. L'essai qui tente seulement
de traverser la salle est mort ; cela ne suffit pas à conclure à un problème
du portage. La prochaine étape est de traiter ce mécanisme avant le combat
quand l'ennemi est inaccessible, puis de poursuivre le deuxième cristal.

Le [rapport](fairy_campaign_v0280_report.json) conserve séparément les preuves
positives de la fée et les résultats négatifs des essais de donjon. Reproduction :
`tools/summarize_fairy_campaign_v0280.py`. La campagne complète, la campagne PAL,
le flux R/IRQ original et la fidélité audio physique restent ouverts.
