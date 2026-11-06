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
c0040 exécute la simulation. La mesure situe l’écart de cadence. La
comparaison de ce combat avec la SMS reste à faire pour déterminer quel
comportement est le plus fidèle.

- [Rapports, commandes et captures](c0040-pal-campaign-timing/manifest.json)
