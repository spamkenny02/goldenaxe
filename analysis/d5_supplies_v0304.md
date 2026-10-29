# v304 : ravitaillement et mécanismes avant le cinquième boss

La ROM reste la v304,
`b7b4e15008a6f0a913c9ad43f15386abcdfbb719e5a575873d92712ba52503a8`.
Le parcours prolonge la [sortie après les bottes](d5_progress_v0304.md).
Le programme du jeu ne change pas à cette étape.

Deux dons réels de 30 cornes aux maisons A1 et B4 portent la monnaie de
22 à 52 puis 82. Le héros achète une clé à 60 cornes chez le marchand 94,
puis utilise son soin gratuit : 50 vers 64 PV. Il ressort avec une clé et
22 cornes. Cette route achète une seule clé ; l'ancien ravitaillement v292
en achetait deux et collectait davantage de dons.

Le retour dans le donjon conserve les bottes, le canoë, la corde et les
quatre cristaux. Le trajet aborde le mécanisme de 154 par le bas. Terre
détruit le rocher 44 de 153 et révèle le téléporteur vers 162, en dépensant
huit unités de magie. Une commande HAUT au mécanisme de 162 ouvre ensuite
le passage vers 172. Le dernier état validé est à 64/64 PV, une clé et
32 unités de magie, avant le boss.

Les neuf étapes ont chacune une relecture indépendante depuis le démarrage,
par boutons fixes : les 65 536 octets de RAM et le PNG final correspondent.
Les dons, l'achat et le soin passent par les dialogues normaux. Aucune
monnaie, clé, vie, possession, position ou progression n'est injectée.
L'aide d'approche reste explicitement consignée dans le compteur de blessures.

## Correction du contrôleur de parcours

Deux propositions vers B4 s'arrêtaient sur une assertion de l'outil de test.
Le drapeau de prérequis était déjà présent ; le numéro de salle était publié
avant que le chargement replace le héros. L'outil recalculait alors un trajet
depuis une position de l'ancienne salle. Utiliser la carte réelle au départ
ne suffisait pas à corriger cette attente.

Le contrôleur attend désormais un état de jeu normal et un héros immobile
dans l'intérieur de la nouvelle salle avant ce recalcul. Le trajet B4 suivant
atteint la maison, puis sa relecture fixe reproduit exactement RAM et image.
Cette modification concerne les boutons du contrôleur, sans modifier la ROM.

Un autre essai, devant le mécanisme de 162, reprenait involontairement le
téléporteur réciproque et finissait son budget dans la salle 153. Il n'est
pas compté comme un mécanisme réussi. Le parcours retenu évite cette case
de téléporteur par les commandes de déplacement normales et atteint 172.

Le [rapport reproductible](d5_supplies_v0304_report.json) lie les neuf
relectures, les contrôles, les sources figées et les essais de diagnostic.
Le cinquième boss, son cristal et son retour ne sont pas validés par ce
jalon. La fin, les sauvegardes et la fidélité globale restent ouvertes.
