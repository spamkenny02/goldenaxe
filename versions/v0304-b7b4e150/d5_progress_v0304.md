# v304 : bottes acquises dans le cinquième donjon

La ROM reste la v304,
`b7b4e15008a6f0a913c9ad43f15386abcdfbb719e5a575873d92712ba52503a8`.
Cette étape poursuit le [retour du quatrième donjon](d4_campaign_v0304.md)
sans modification du programme du jeu.

Cinq nouveaux segments sont exécutés puis rejoués indépendamment depuis le
démarrage. Chacun reproduit les 65 536 octets de RAM et le PNG final :

| Étape | Frame finale | Salle | PV | Clés | Magie |
| --- | ---: | --- | ---: | ---: | ---: |
| Entrée du cinquième donjon avec le canoë acquis | 91 661 | 186 | 62/64 | 0 | 48 |
| Première clé obtenue après le combat | 92 664 | 176 | 62/64 | 1 | 48 |
| Terre ouvre le passage vers 166 | 93 117 | 166 | 62/64 | 1 | 40 |
| Bottes obtenues, salle nettoyée | 95 655 | 157 | 50/64 | 0 | 40 |
| Sortie pour ravitaillement | 96 329 | Extérieur 49 | 50/64 | 0 | 40 |

Le lancer de Terre détruit le rocher 4A et consomme huit unités de magie.
Les bottes sont obtenues dans leur coffre ; l'inventaire 14 et le sélecteur
de vitesse passent réellement à 1. La clé est dépensée entre le passage
de Terre et le coffre. Canoë, corde et quatre cristaux sont conservés.

Le héros ressort avec 22 cornes et aucune clé. Cette sortie prépare le
ravitaillement : le cinquième boss n'est pas entré et son cristal n'est pas
obtenu. Elle n'est pas comptée comme un donjon terminé. La protection de
test reste explicitement active pendant les approches, uniquement par le
compteur de blessures ; aucune vie, monnaie, clé, possession ou progression
n'est injectée dans cette campagne.

## Déplacement avec et sans bottes

Un banc séparé exécute les boucles du jeu SMS et de la v304 sur six terrains,
quatre directions et bottes présentes/absentes, en mode automatique et PAL.
Les 96 cas, soit 3 072 frames comparées, donnent zéro différence pour les
positions et vitesses 8.8, direction, animation, compteur de marche et
contexte de terrain. Les fichiers d'observation complets sont comparés,
en plus du bilan du banc.

Ce banc utilise des situations contrôlées : carte logicielle, héros,
acteurs et équipement sont initialisés par cas ; la vie est réinitialisée
à 24 PV entre les cas. Il ne prouve pas l'accumulation
des dégâts de terrain, les transitions, le rythme global ni la fidélité
complète des images et de l'audio. Les cinq parcours de campagne restent
distincts de ces situations contrôlées.

Le [rapport reproductible](d5_progress_v0304_report.json) relie les captures,
commandes, relectures, sources figées et observations de déplacement.
La marge de pile précédemment mesurée, 496 octets, concerne toujours le
parcours jusqu'au retour du quatrième donjon ; elle n'est pas étendue ici.

Le ravitaillement, le cinquième boss et son retour, la suite de campagne,
la fin, les sauvegardes et la fidélité globale restent à vérifier.


Erratum2026-10-30 : la marge de496 octets citee ci-dessus concerne les points instrumentes. Le minimum avant chaque instruction est478 octets sur les parcours D1-D6. Voir la [correction de mesure](stack_minimum_v0304_erratum.md).
