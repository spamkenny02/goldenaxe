# Aperçu Mega Drive c0039

Cet aperçu ajuste le premier passage de l’extérieur vers le donjon 1.
Le fondu commence à publier chaque couleur après une attente vidéo. Le
chargement masqué utilise des attentes adaptées au PAL et au NTSC.
[Télécharger la ROM c0039](gaw-megadrive-c0039.bin)

| Première entrée naturelle | SMS PAL | V318 PAL | c0039 PAL | SMS NTSC | V318 NTSC | c0039 NTSC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Chargement masqué en images | 17 | 14 | 17 | 20 | 17 | 20 |
| Aire de jeu noire en images | 38 | 36 | 38 | 41 | 39 | 41 |
| Entrée jusqu’au contrôle du héros | 86 | 83 | 86 | 89 | 86 | 89 |

En PAL, le rejeu des commandes V318 décalées de trois images après l’entrée
reproduit les champs de jeu comparés jusqu’au premier cristal et à la sortie
en B9. L’image finale est identique. La comparaison du rejeu exclut le miroir
VRAM et les octets du lecteur audio. En NTSC, le rejeu des commandes décalées
diverge à l’image 4 418 de référence et l’image de fin diffère. Un nouveau
parcours NTSC avec des commandes adaptées aux rencontres obtient le premier
cristal et ressort en B9 à 24/32 PV. Les quatre points de contrôle reproduisent
la RAM et l’image finale. La protection d’approche est retirée en 185 avant
le boss. La V318 reste la version de référence pour la campagne complète.
[Rapport du parcours NTSC](../../../analysis/c0039_ntsc_d1_report.json)

L’horloge de jeu avance de 72 unités entre l’entrée et le retour du contrôle,
comme sur Master System. La V318 en avance de 73 en NTSC. La demande du
thème du donjon arrive encore une image plus tard que sur Master System
dans les deux régions.

Sur 14 000 images sans entrée par région, les écarts vidéo mesurés contre
la Master System sont identiques à ceux de la V318. Les états du lecteur
audio et les huit registres PSG sont identiques à ceux de la V318 sur les
6 500 premières images sans entrée en PAL et en NTSC.

ROM de 2 Mio, checksum `0623`. SHA-256
`aafa32557159a3c18d0cbbaf1b10926aa05d1ef5fda26d534acf94093e913737`.
Deux compilations propres donnent le même binaire et la même table de symboles.
Le [patch source](source.patch) s’applique au commit `c6c705be`.

- [Mesures PAL](pal-door.json) et [NTSC](ntsc-door.json)
- [Rejeu PAL](pal-replay.json) et [NTSC](ntsc-replay.json)
- [Démarrage PAL](pal-boot.json) et [NTSC](ntsc-boot.json)
- [Audio du démarrage](boot-audio.json)
- [Horloge et demandes musicales en PAL](pal-clock.json) et [NTSC](ntsc-clock.json)
