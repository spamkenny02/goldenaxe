# c0044 — Lecture des motifs du donjon depuis la RAM

Cet aperçu de 2 Mio utilise la copie RAM des motifs des ennemis pendant
la préparation des sprites d’un donjon. Les motifs en attente de transfert
gardent leur priorité. Cette lecture réduit les accès au VDP.

Le rejeu PAL récupère la mise à jour de la salve du boss 6A à l’image
80 003. Les 768 octets d’acteurs concordent avec l’essai contrôlé sur
Master System à la même phase. Le saut de l’image 80 001 reste présent.
Les champs de jeu du début NTSC concordent jusqu’à 7 710, y compris
le point de régression de c0042 à 7 697.

Les douze cas de sprites contrôlés, avec classe graphique de donjon
imposée pour ce test, comparent 108 images de sprites physiques. Leurs
pixels concordent avec la V318. Le rejeu NTSC étendu concorde sur les
37 champs de jeu jusqu’à 44 800, puis diverge à 44 801. Les anciennes
commandes atteignent ensuite un boss avant leur retrait enregistré de la
protection d’approche. Ce rejeu est arrêté à 55 789. La V318 reste la
version de référence.

Checksum Mega Drive CEAF. SHA-256
cc4c983037441cfb8d81e1233b1326c75ead18c22e3d2b09306ddb64ab0eea18.

- [ROM de test c0044](gaw-megadrive-c0044.bin)
- [Patch source](source.patch)
- [Rapports et captures](../../../analysis/c0044-dungeon-pattern-ram/manifest.json)
- [Premier écart NTSC](../../../analysis/c0044-ntsc-divergence/manifest.json)

À la première divergence NTSC, la V318 saute l’appel à la simulation.
c0044 l’exécute. Les compteurs des acteurs avancent d’une unité, tandis
que les PV et la position du héros ainsi que les générateurs aléatoires
concordent encore. Dans un essai contrôlé de la salle 1E2 sur Master System,
les 768 octets des acteurs après cette mise à jour correspondent à c0044
à la phase 73. La chronologie naturelle complète entre les deux consoles
reste à comparer.

- [Mise à jour NTSC comparée à la source](../../../analysis/c0044-ntsc-first-update/manifest.json)
