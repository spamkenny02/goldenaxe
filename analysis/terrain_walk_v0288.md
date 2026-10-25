# v0288 — vitesses originales selon le terrain

ROM : `5c2b91e5aab65403cd1213eb4e25b9ea5fbc1c41529e34e0a944144675817e2f`,
2 Mio, checksum `A476`.

Le parcours réel de corde a révélé un écart reproductible : sur la v0287,
le second pas utilise cinq ticks, tandis que la SMS en utilise douze.
Le code source 32DE..32F6 sélectionne une ligne de 17 octets selon C041,
à partir de 33DB ou de 3441 avec les bottes. Le port ne sélectionnait que
les tables du sol normal et de l'eau ; les autres contextes utilisaient
la ligne normale. La v0288 raccorde les douze lignes originales complètes.
Leurs 204 octets sont vérifiés directement dans la ROM compilée.

## Vérifications

- Six terrains, deux états de bottes, quatre directions, PAL et NTSC :
  96 situations et 3 072 frames. Position fixe, vitesses, direction,
  animation, compteur et classification de terrain correspondent.
- Corde, PAL et NTSC : 32 frames par région. Déploiement, colonne de terrain,
  travail d'animation, dix rangées de carte et déplacement correspondent,
  avec le pas de douze ticks. Les situations contrôlent explicitement
  carte, possession, position initiale et acteurs ; ce ne sont pas des
  parcours naturels ni une comparaison de tout le framebuffer.
- Premier donjon v0288 sans aide ni décès : entrée, hache équipée, boss,
  cristal et sortie B9 à 32/32 PV. Les quatre étapes sont rejouées depuis
  le démarrage avec RAM complète et PNG finals identiques.
- Pile observée à chaque instruction sur ces 16 131 frames : minimum F79C,
  limite du tas F600, marge observée 412 octets et chaîne du tas valide.
  La RAM et le PNG correspondent également dans l'exécution observée.

Les cas de mouvement réinitialisent les PV à chaque situation : une première
série avait accumulé des dégâts dans le jeu source entre plusieurs cas.
Les effets des terrains sur les PV, notamment 2EB6..2EDA pour le contexte 4,
restent à comparer et à porter ; ce test n'en prouve pas la fidélité.

Le troisième donjon et la corde acquise ont été parcourus sur la v0287
historique. Ils ont permis de trouver cette correction, mais ne valident
pas automatiquement ces mêmes parcours sur la v0288. Le reste de la campagne,
le flux RNG/R/IRQ, la vitesse globale des transitions et des ennemis,
l'audio mesuré et le matériel réel restent à vérifier.

Rapport : `terrain_walk_v0288_report.json`.
