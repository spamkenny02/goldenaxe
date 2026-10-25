# v0287 — corde magique native

ROM : `58068350382a19ddc73a62eb747e42d978c36a1daf3c87f819e921f391b0065d`, 2 Mio, checksum `DD1D`.

La possession de la corde (inventaire 13) était enregistrée, mais les routines
38AC/38F6 ne figuraient pas dans le déplacement natif. Le module C ajouté
reproduit les conditions d'alignement, les cellules temporaires 6C/6D et le
travail C098..C09B. Les routines 6D2C/6D40/6DA6 dessinent deux tuiles par
pas de huit pixels. Le jeu publie la rangée au VBlank suivant. La corde est
réinitialisée au chargement des objets de la salle, comme C090..C0AF en 24C5.
Aucun mode invincible n'est intégré au binaire.

## Vérifications

- 1 536 tentatives, dont alignements, refus, limites et colonnes : les 256
  cellules et les quatre octets de travail correspondent au Z80 inchangé.
- 640 étapes de dessin : travail et carte logicielle complète correspondent.
- Jeu natif PAL/NTSC, montée/descente : six rangées par situation, soit 24
  publications physiques de deux tuiles au VBlank suivant, vérifiées dans
  la VRAM du cœur officiel. Ces situations injectent explicitement position,
  possession et terrain pour isoler la fonction ; ce ne sont pas des preuves
  de campagne naturelle avec la corde.
- Premier donjon v0287 : entrée, hache, premier boss/cristal et sortie sans
  aide et sans décès. Les quatre étapes sont rejouées depuis le démarrage
  par commandes fixes : RAM complète et PNG finals identiques. Sortie B9,
  hache équipée, premier cristal, 32/32 PV.
- Observation de pile à chaque instruction sur le nouveau parcours de
  16 129 frames : SP minimal F79C, limite tas F600, marge observée 412 octets ;
  chaîne d'allocation valide. Cela ne borne pas tous les parcours possibles.

L'ancien enregistrement v0286 de sortie D1 échoue à rejoindre son objectif
sur cette compilation. Il reste archivé comme essai échoué ; les preuves
ci-dessus utilisent de nouvelles commandes adaptatives puis leur relecture
froide indépendante. Aucun état de sauvegarde ou SRAM n'est transplanté.

## Troisième donjon, essais historiques v0286

L'approche autorisée à compteur de blessure protégé est désormais enregistrée
par épisodes : le combat et la sortie D2 restent protégés contre toute nouvelle
écriture lorsque commence l'approche D3. Le contrôleur emprunte le véritable
portail 1E7→1E2 à son point de contact ; il ne téléporte pas le héros.

La corde est récupérée en 1F4 sur SMS et MD. Les relectures assistées reproduisent
toute la RAM et le PNG de chaque machine ; les 256 indicateurs persistants,
1 280 octets de carte et 17 octets d'inventaire correspondent entre systèmes.
Le boss SMS passe sans aide au combat. Sur MD, deux essais atteignent 1C3 avec
48 PV ; le compteur est libéré avant le combat, puis le héros meurt. Ils ne
prouvent ni victoire native ni à eux seuls une différence de logique du boss.
Les premiers itinéraires bloqués et les défaites sont conservés.

Ces résultats D2/D3 appartiennent à la v0286. La v0287 doit encore prolonger
sa propre campagne, déployer naturellement la corde et terminer les autres
boss. RNG/R/IRQ source, vitesse globale, audio mesuré et matériel réel restent
à vérifier ; aucun pourcentage global n'est déduit de ces seuls contrôles.

Voir `magic_rope_v0287_report.json` pour les SHA et la portée des preuves.
