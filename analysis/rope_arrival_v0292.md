# v0292 : corde et arrivée dans une nouvelle carte

La routine originale 19C6–1A01 continue une corde dans la carte fraîchement
chargée si le terrain précédent vaut 5 et que la pièce est extérieure.
En montant, elle remonte depuis la dernière ligne et remplace les falaises
0C par 6C ; dans l'autre direction, elle descend depuis la première ligne
et termine par une ancre 6D. La préparation native omettait cette étape.

La v0292 applique ces mutations après les transformations persistantes et
avant la reconstruction de carte. Les gardes et les cellules correspondent
au Z80 exécuté sur 5 456 cas. Les accès inhabituels de l'original hors des
256 octets de cet alias et le calendrier de file DD00 ne sont pas validés.

Quatre situations contrôlées dans les jeux réels font déployer la corde et
franchir la limite B2/A2, en montant et descendant, en PAL et NTSC. À
l'arrivée : 160 cases, 1 280 octets de carte, coordonnées entières et terrain
identiques. La v0291 reproduit le défaut avec les mêmes tests. Les quatre
colonnes finales dans la mémoire VDP correspondent aussi, soit 160 mots
de carte et les indices de couleur des tuiles qu'ils référencent.
Ces fixtures fournissent la position initiale, la pièce et la corde ; elles
ne constituent pas encore une acquisition naturelle de la corde sur v0292.

Le premier donjon est rejoué depuis le démarrage sans aide : hache, cristal,
sortie B9 à 32/32 PV, puis seconde exécution avec toute la RAM et le PNG
final identiques. Le contrôle de pile à chaque instruction sur ce parcours
observe 408 octets de marge minimale au-dessus du tas, sans corruption de
ses en-têtes ; son état final correspond à l'exécution normale.

## Progression de référence et tests assistés

La SMS originale atteint le maître de la Terre via la corde de B2, traverse
A2, coupe l'arbre spécial 4A de A3 et ouvre le passage distant 48. Le vrai
dialogue retire 50 cornes, accorde le niveau 1 et augmente la capacité
magique de 24 à 48. Le héros ressort à 16 PV et 10 cornes. Les deux segments
ont des relectures indépendantes depuis le démarrage, RAM et PNG exacts.
La campagne conserve son ancienne approche assistée du troisième donjon,
retirée avant son boss ; aucune nouvelle aide n'est ajoutée après ce préfixe.
Il s'agit d'une référence SMS, pas d'une preuve de cette route sur v0292 MD.

Des preuves distinctes sur v0291 terminent le deuxième donjon à 48/48 PV,
avec protection pendant l'approche, retirée avant le combat. Le trajet,
le combat, le cristal et la sortie ont leurs relectures RAM/image exactes.
Ces résultats historiques ne sont pas transférés à la v0292.

Le [rapport consolidé](rope_arrival_v0292_report.json) lie les preuves et
leurs empreintes aux versions. Les outils n'ajoutent aucune invincibilité
aux ROMs publiées. La campagne native avec corde acquise, la Terre, le
quatrième donjon, le canoë et le reste du jeu demandent encore validation.
Le timing intermédiaire du scrolling, les sprites et l'audio ne sont pas
prouvés par les comparaisons de colonnes finales.
