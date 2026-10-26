# v0291 : arbres et passages à la hache

ROM : `e6d968e1983b59d3a6e2856af114a7caeeb21fa32130aa5adb68b268a9453391`,
2 Mio, checksum `6ADA`.

La routine native animait la hache sans traduire la suite 34D3–35B4.
L'original teste la classe extérieure et la phase de coup 7, puis sélectionne
zéro, une ou deux cases selon direction, alignement et bord d'écran. Les
cinq enregistrements à 3620 transforment les arbres 80–84 et, si elle
correspond, leur case de support. Le chemin 35B7 peut aussi marquer le
progrès et appliquer une transformation de pièce.

La v0291 reprend ce ciblage et réutilise la routine native de changement
terrain/carte/son déjà employée par la magie de Terre. Les lignes modifiées
sont publiées au VBlank avec la file existante. La compilation exporte les
21 octets du tableau directement depuis la ROM SMS.

## Vérification

- 4 356 cas exécutent les gardes, le tableau de branchement, les décalages et
  le calcul de cellule 232F originaux, comparés à la fonction C compilée.
- 128 situations dans les boucles réelles SMS et MD, PAL/NTSC : les cinq
  types d'arbres, les orientations/alignements actifs, les supports associés,
  la transformation réelle de 13 et son drapeau préalable, puis deux
  exclusions intérieures. Cases, carte, état, orientation, animation et
  phase correspondent sur 5 120 frames.
- 122 cas positifs comparent aussi chaque case modifiée dans la carte VDP
  réelle et les indices de couleur de ses tuiles. Le test historique sur la
  v0290 reproduit l'absence de coupe.
- Le premier donjon est rejoué sur la v0291 sans aide, avec hache, cristal et
  sortie à 32/32 PV. Tous les segments naturels ci-dessous ont une seconde
  exécution depuis le démarrage, RAM et PNG finals identiques.

Le [rapport consolidé](axe_terrain_v0291_report.json) lie ces observations à
la ROM. Les sondes isolées couvrent aussi des coordonnées hors jeu ; leurs
mutations dans les alias RAM extérieurs à la carte visible ne sont pas
présentées comme validées par l'intégration, qui borne les cases visibles.

## Progression naturelle

La route coupe les arbres avec la hache réellement acquise au premier
donjon. En E6, elle coupe d'abord la case spéciale 7B : son drapeau ouvre
la case distante 75. Le contrôleur vérifie cette ouverture avant d'utiliser
le passage, puis atteint la maison BF et peut monter de huit pixels après
la transition. Le héros parle au maître de la Foudre et ressort en E6,
avec le drapeau de première présentation. Le sort lui-même reste à zéro :
il faut encore apporter une Pomme d'Or.

La SMS originale exécute sa propre route et le même premier dialogue, sans
aide ni décès. Après la sortie, les 1 280 octets de carte, les 160 cellules,
les 17 objets et le drapeau E6 correspondent entre les machines. Les PV,
l'or, rencontres et temps globaux ne sont pas annoncés identiques.

La route MD poursuit vers F4, ouvre la maison cachée 3F et reçoit les
50 cornes prévues. Elle ressort avec 57 cornes et 16 PV, sans injection,
aide ni décès. L'observation de pile à chaque instruction jusqu'à cette
sortie, frame 20 804, donne F798 face au tas F600 : marge observée de
408 octets, chaîne du tas valide. La capture finale correspond au cœur
normal sur toute la RAM et l'image.

Le contrôleur propose maintenant les coupes depuis les tables de la ROM,
puis laisse les vrais coups modifier le jeu. Il conserve le terrain réel
du préfixe et les drapeaux déjà acquis. Les essais de navigation ratés sont
conservés : passage distant supposé ouvert trop tôt, arbre à la bouche
finale d'une maison, carte réelle non développée pour proposer les coupes,
et budget SMS plus court que son préfixe. Les preuves retenues sont
`thunder-entry04`, `gold-entry03` et la route SMS `source-thunder-entry03`.
Un ancien compteur supposait aussi une entrée à x=128 ; il teste maintenant
x=136 dans les maisons et le vrai déplacement vertical de huit pixels.

## Reste à faire

Le projet ne se limite pas à ces cas : la campagne fidèle complète reste
l'objectif. La proposition de marche vers le maître de la Terre en A3
échoue encore ; il faut étendre le parcours aux falaises, à la corde et aux
transports nécessaires, puis acquérir et utiliser le sort pour avancer dans
le quatrième donjon. Ni canoë ni quatrième boss ne sont annoncés réussis.

Le transfert intermédiaire des tuiles, les formes d'onde sonores, toute la
chronologie, le flux RNG/R/IRQ, les donjons suivants et le matériel réel
restent à vérifier. Les captures sont conservées sans perte avant nettoyage,
avec SHA-256 et relecture intégrale : [manifeste](axe-terrain-v0291/manifest.json).
