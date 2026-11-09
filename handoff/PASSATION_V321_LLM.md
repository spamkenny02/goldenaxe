# Lire en premier — projet V321, 9 novembre 2026

Objectif : portage fidèle de Golden Axe Warrior SMS en 68000 natif sur Mega
Drive, avec SGDK. Les améliorations viennent après la fidélité. Cette archive
est un instantané de développement ; le portage n'est pas certifié terminé.

## Compilation autonome Windows

Extraire dans un chemin sans espaces, par exemple `C:\gaw-v321`.
Lancer `powershell -ExecutionPolicy Bypass -File .\BUILD_V321.ps1`.
SGDK et Java sont fournis. Python et Git ne sont pas nécessaires à ce build.
Résultat : `dist/gaw-megadrive-v0321.bin`, SHA-256 attendu :
`89c5833351312ffaa591efb1939161910a298af06437080e2cf84fb3fb8ac86e`.
La ROM de référence figure également dans `reference/`.

Le C produit la base V319 auditée. BUILD_V320 assemble ensuite le correctif
du générique à 1F0000, puis BUILD_V321 assemble celui du titre à 1F0100.
Les SHA et instructions de branchement sont vérifiés. Une modification du C
peut déplacer les fonctions avec le LTO : réexaminer les branchements ; ne
pas supprimer les vérifications pour appliquer des adresses devenues fausses.
`BUILD_V320.ps1` est une étape du build, pas la version finale du paquet.

## Priorité actuelle : tous les PNJ sur SMS ET Mega Drive

Une nouvelle campagne SMS continue a battu le premier boss et quitté son
donjon. Neuf conversations ont été déclenchées et acquittées dans les villages
94 et C7. L'observateur SMS enregistre l'entrée originale 050C et le retour
627A ; les neuf visites sont suivies d'un déplacement et d'une relecture
indépendante des entrées depuis le démarrage. Cela ne couvre pas encore tous
les PNJ, tous les états conditionnels ou une campagne SMS entière.

Lire `analysis/sms_npc_coverage_report.json` et
`analysis/paired_npc_coverage_report.json`. Les nouvelles visites MD appariées
restent à faire : leur compteur est zéro. Les 65 contextes statiques des
maisons ordinaires ne représentent pas tous les PNJ ou toutes les variantes.
Inclure marchands, enseignants, fées, dons, indices, quêtes, mini-jeux et
passages payants, choix/refus/réussites, puis revisiter après les objets et
événements. Comparer textes/pages/effets, restauration graphique, transitions
et audio en PAL/NTSC. Ne pas compter un texte simplement présent en ROM comme
ayant été affiché en jeu.

Trois textes SMS aux offsets DA58, DA7C, ED3C sont absents des données MD.
Leur déclenchement demeure inconnu. Ne pas inventer un PNJ ou une condition
pour les rendre accessibles. Voir `analysis/reported_missing_texts_v0320_report.json`.

Dernier préfixe SMS continu sélectionné :
`validation/natural-service-route/sms-npc-villagec7-house1f-01`.
Son replay canonique indépendant et ceux des étapes précédentes sont inclus.
Correction de libellé après la création du ZIP : les noms historiques
`oil`/`oil_stairs` suivent le slot d'inventaire 8, qui est la **pomme d'or**
(récompense 12, texte SMS BBEB). L'huile magique est le slot 2/récompense 6.
Le ZIP livré reste l'instantané immuable antérieur à cette correction de note.

Protection autorisée uniquement sur certaines approches, via l'octet hurt
C305 ; retirée avant le boss. Premier boss combattu sans protection, dégâts
normaux observés. Aucun import de sauvegarde/progression. Toute assistance
est consignée ; ne pas présenter la campagne entière comme sans écritures.
Le fichier `assistance.json` reste indispensable avec les contrôles.

## Autres résultats et limites

V321 : correction d'une image de retard de publication au titre, après le
correctif de bordure du générique V320. Les parcours MD enregistrés rejoignent
la fin en PAL et NTSC ; ce n'est pas une preuve de tous les dialogues.
Graphismes et animations ne sont pas certifiés à 100 %. Une différence de
262 pixels sur une image NTSC du logo et des révélations partielles de scènes
restent ouvertes. Consulter README.md et les rapports, avec leurs limites.
Les expériences `source_title_wait` et `title_logo_raster` sont non sélectionnées.
Le candidat raster améliore un cas par calibration ; ne pas le publier comme
correction générale validée. Les diagnostics de coût ne sont pas les FPS du jeu.

## Contenu et utilisation des tests

Sources Mega Drive complètes, outils Python/Lua/C, ROM SMS d'entrée, ROM MD
V321, rapports d'analyse de premier niveau, kit de parcours, preuves de la
nouvelle campagne SMS et chaîne de compilation Windows sont inclus.
`CONTENTS_SHA256.json` contrôle chaque fichier. `SNAPSHOT.json` indique le
commit de référence et les limites de l'instantané.

`testkit/replay_libretro.py` est le lecteur réellement utilisé pour les
parcours distribués. La DLL GX fournie dans `testkit/runtime/` permet ces
relectures sous Windows avec Python et Pillow. Le Lua BizHawk est une adaptation
contrôlée syntaxiquement et avec des mocks, pas une campagne validée dans
EmuHawk. Ses routes SMS distribuées couvrent encore seulement l'introduction.
Les traces SMS récentes sont distinctes dans `validation/`.

Les nombreux outils historiques référencent parfois des chemins absolus ou
des cœurs instrumentés externes ; leur présence ne les rend pas tous portables.
La compilation autonome et le lecteur du kit sont les points d'entrée.
Les gros caches historiques, vidéos, anciennes ROMs, historique .git et sorties
de builds sont exclus. Leurs références dans des rapports restent historiques.
Les anciennes notes REPRISE_CODEX/HISTORIQUE peuvent mentionner V320 ou plus
ancien : ce document et le README actuel priment.
