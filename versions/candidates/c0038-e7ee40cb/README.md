# Aperçu Mega Drive c0038

La publication de chaque couleur du fondu entre le titre et l’intro est
repoussée d’une interruption vidéo. Les deux attentes de chaque étape et
le traitement des commandes sont conservés. [Télécharger la ROM c0038](gaw-megadrive-c0038.bin)

| 14 000 images par région | v0317 | c0038 |
| --- | ---: | ---: |
| Images identiques à la SMS en NTSC | 13 602 | 13 636 |
| Images identiques à la SMS en PAL | 13 648 | 13 682 |
| Pixels différents en NTSC | 538 303 | 147 429 |
| Pixels différents en PAL | 515 308 | 124 148 |

La comparaison image par image du démarrage sans entrée ne relève aucun
nouveau pixel divergent. Les états audio logiques et les huit registres
PSG correspondent à la SMS des images 23 à 14 000, selon la normalisation
décrite dans le rapport. Deux parties fraîches atteignent le premier
donjon en PAL et NTSC et déplacent le héros par les commandes normales.
Les 210 cas de saisie du premier caractère du nom passent.

Le rejeu depuis le démarrage avec les commandes de la campagne v0317 diverge
à partir de l’image 4081. Sur 393 707 images comparées en jeu, 205 263 ont
un état différent et les quatre captures de fin diffèrent. Le rejeu c0038
termine dans la salle 95 avec 24 PV. La v0317 reste la version de référence.

Les 17 premiers écarts observés touchent seulement le miroir logiciel de
la VRAM. À 190968, dans la salle 1C7 du septième donjon, l’état des ennemis
diverge. La position du héros diverge à 190970 et le générateur aléatoire
à 190971. Les deux rejeux atteignent la salle 1C6 à 192500, avec des
quantités d’or et de clés différentes.
[Rapport du rejeu de la campagne](campaign-replay.json)

ROM de 2 Mio. Checksum Mega Drive `2E44`. SHA-256
`e7ee40cb477905b478d849d52a687ff4a319fc7217f29be5f138cbbcce8febeb`.
Le build propre reproduit le binaire à l’octet près. Pour reconstruire,
appliquer le patch au commit `8959e46c7d8c6c1bfc6e96ae4773d5f073b13a7a`
et utiliser le build SGDK du dépôt. [Patch source](source.patch)

- [Comparaison vidéo NTSC](video-ntsc.json) et [PAL](video-pal.json)
- [Audio PAL et NTSC](audio.json)
- [Saisie du nom](names.json)
- [Trajet NTSC](d1-ntsc.json) et [trajet PAL](d1-pal.json) jusqu’au premier donjon
