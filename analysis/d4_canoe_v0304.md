# v304 : canoë acquis et téléporteur du quatrième donjon

La ROM reste la v304,
`b7b4e15008a6f0a913c9ad43f15386abcdfbb719e5a575873d92712ba52503a8`.

La reprise depuis le passage de Terre utilise des départs de hache après la
fin du déplacement. Cette modification des boutons du contrôleur évite le
cas de capture simultanée avec un coup mortel précédemment documenté ; le
comportement du jeu reste identique.

Quatre segments supplémentaires sont terminés, puis rejoués indépendamment
depuis le démarrage avec toute la RAM et le PNG final identiques :

| Étape | Frame finale | Salle | PV | Clés | Magie |
| --- | ---: | --- | ---: | ---: | ---: |
| Salle des voleurs nettoyée et clé supplémentaire | 71 684 | 1A1 | 56/56 | 2 | 48 |
| Canoë obtenu dans son coffre et salle nettoyée | 74 012 | 1A2 | 56/56 | 0 | 48 |
| Terre révèle le téléporteur ; transfert réel | 75 052 | 192 | 56/56 | 0 | 40 |
| Clé de la seconde partie du donjon | 76 662 | 182 | 56/56 | 1 | 40 |

Les observations des relectures constatent la possession du canoë, le vrai
drapeau d'eau peu profonde et des déplacements : 62 frames de mouvement
observées dans la relecture du coffre. Ce décompte ne mesure pas une vitesse
équivalente à la SMS. La salle d'arrivée 192 n'est pas déclarée nettoyée par
la seule traversée du téléporteur.

Deux parcours SMS antérieurement vérifiés utilisent la même ROM originale.
Les données de leurs coffres/téléporteurs correspondent aux nouveaux états
MD : 160 cellules, 1 280 octets de carte logicielle, 17 octets d'inventaire
et quatre mots de carte VDP traduits pour chaque mécanisme. Les indices de
couleur des tuiles statiques du coffre correspondent aussi. Cette comparaison
ne porte pas sur les acteurs, PV, monnaie, chemins, horloges, pixels animés du
téléporteur, images complètes ou audio.

Le [rapport consolidé](d4_canoe_v0304_report.json) conserve les empreintes des
captures, commandes, gardes d'approche et relectures. Seul le délai de protection
du héros est écrit par l'aide de test ; aucune vie, clé, monnaie, possession ou
progression n'est injectée. La campagne reste explicitement assistée pendant
les approches.

Ce jalon ne valide pas le quatrième boss, son cristal ni le retour. Ces étapes
requièrent leur propre preuve, ainsi que la fin, les sauvegardes et la fidélité
complète vidéo/audio.
