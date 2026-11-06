# Rejeu PAL étendu de l’aperçu c0040

Après recalage de trois images à la première entrée du donjon 1, le rejeu
compare 37 champs de jeu sur 230 950 images. Le premier écart arrive
à l’image de référence 80 003, pendant le combat contre le boss 6A.
Les compteurs et positions des acteurs divergent tandis que les PV, la
position du héros, le générateur aléatoire et l’horloge logique concordent
encore. Les commandes enregistrées divergent ensuite jusqu’à la fin du rejeu.

L’observation en lecture seule du 68000 retrouve les captures RAM et PNG
du cœur standard. Les deux ROM sautent un appel à la simulation à l’image
de référence 80 001. La V318 saute aussi l’appel à 80 003, tandis que
c0040 exécute la simulation. La mesure situe l’écart de cadence.

Dans un essai contrôlé, la ROM Master System PAL charge la salle 180,
puis reprend l’état des acteurs qui précède l’écart. À chacune des 16
phases testées, dont la phase 193 de l’écart, elle produit exactement les
768 octets d’acteurs obtenus par c0040. Le rejeu d’un combat SMS enregistré
en NTSC retrouve la RAM et les pixels finaux. Les 480 compteurs de
projectiles admissibles avancent d’une unité, sur 60 images distinctes.
La campagne PAL complète de c0040 et l’image sautée par les deux ROMs
restent à vérifier séparément.

- [Rapports, commandes et captures](c0040-pal-campaign-timing/manifest.json)
- [Essais sur la ROM Master System](c0040-source-burst-cadence/manifest.json)
