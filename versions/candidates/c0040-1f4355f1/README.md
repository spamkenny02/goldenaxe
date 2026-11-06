# Aperçu Mega Drive c0040

La demande du thème du premier donjon intervient une interruption plus tôt
que sur c0039. Elle arrive à la même image relative que sur Master System,
33 images après l’entrée en PAL et 36 en NTSC. Le chargement masqué, l’écran
noir et les 72 unités d’horloge de jeu conservent les durées mesurées sur c0039.
[Télécharger c0040](gaw-megadrive-c0040.bin)

Sur la fenêtre de la transition, les 400 octets normalisés du lecteur audio
correspondent à la SMS sur 53 images sur 69 en PAL et sur zéro image sur 72
en NTSC. Les registres PSG présentent encore des écarts dans les deux régions.
Les 6 500 images de démarrage sans entrée reproduisent les états audio et
les registres PSG de la V318.

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
