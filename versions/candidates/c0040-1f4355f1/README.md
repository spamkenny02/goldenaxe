# Aperçu Mega Drive c0040

La demande du thème du premier donjon intervient une interruption plus tôt
que sur c0039. Elle arrive à la même image relative que sur Master System,
33 images après l’entrée en PAL et 36 en NTSC. Le chargement masqué, l’écran
noir et les 72 unités d’horloge de jeu conservent les durées mesurées sur c0039.
[Télécharger c0040](gaw-megadrive-c0040.bin)

Sur les 53 images après la demande du thème, les 400 octets normalisés du
lecteur audio et les registres PSG qui influent sur le son correspondent
à la SMS en PAL. En NTSC, le trajet initial laisse le compteur de tempo
décalé d’une unité et produit sept écarts de période sur le troisième canal
tonal. Une image d’attente avant le dernier mouvement sur SMS aligne ce
compteur et les 53 états audio observés. Le comparateur conserve les écarts
des registres bruts des canaux muets.

Les 6 500 images de démarrage sans entrée reproduisent les états audio et
les registres PSG de la V318. Les mesures d’entrée couvrent les états du
lecteur et du PSG par image. Les formes d’onde restent à comparer.

Les rejeux reprennent les commandes du parcours PAL de la V318, décalées
de trois images au chargement, et celles du parcours NTSC de c0039. Les
37 champs de jeu comparés concordent sur 24 040 images cumulées jusqu’au
premier cristal et à la sortie. Les deux images finales sont identiques.
Le miroir VRAM et la RAM du lecteur audio sont mesurés séparément de ce rejeu.

Le démarrage vidéo PAL reproduit les 14 000 images normalisées de la V318.
En NTSC, quatre images diffèrent. La comparaison avec la SMS relève 22 pixels
améliorés et 64 pixels dégradés, avec le même nombre d’images exactes.
La V318 reste la référence de campagne.

ROM de 2 Mio, checksum `A5F1`, SHA-256
`1f4355f1e6ba49b2264cd4ba08652a1292062567fe596a6ae0b9910cffd63f31`.
Deux compilations propres ont reproduit le binaire et les symboles.
Le [patch source](source.patch) s’applique à la V318 du commit `3c14c51d`.

- [Entrée PAL](pal-door.json) et [NTSC](ntsc-door.json)
- [Audio de l’entrée](door-audio.json) et [du démarrage](boot-audio.json)
- [Rejeu PAL](pal-replay.json) et [NTSC](ntsc-replay.json)
- [Vidéo au démarrage PAL](pal-boot.json) et [NTSC](ntsc-boot.json)
- [Après le thème en PAL](pal-after-theme.json), [NTSC](ntsc-after-theme.json) et [NTSC avec tempo aligné](ntsc-phase-aligned.json)
