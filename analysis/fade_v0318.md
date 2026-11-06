# V318 — fondu avant le titre

Le fondu applique chaque nouvelle palette pendant l’interruption verticale.
Il réutilise le mécanisme de publication de l’intro et conserve les deux
attentes vidéo par étape.

| 14 000 images sans entrée par région | V317 | V318 |
| --- | ---: | ---: |
| Images identiques à la Master System en NTSC | 13 602 | 13 636 |
| Images identiques à la Master System en PAL | 13 648 | 13 682 |
| Pixels différents en NTSC | 538 303 | 147 429 |
| Pixels différents en PAL | 515 308 | 124 148 |

Les pixels modifiés pendant ce test se rapprochent tous de l’image SMS.
Les états audio logiques et les huit registres PSG restent identiques à
la référence SMS des images 23 à 14 000 avec la normalisation du rapport.

Le rejeu NTSC depuis Nouveau jeu reproduit les 393 707 états comparés en
jeu sur V317 et les quatre captures de la fin. Les écritures de test sont
limitées à la protection des approches, retirée avant les boss. La reprise
de la sauvegarde V317 à neuf cristaux restitue les 60 PV, le déplacement
et les sept captures attendues. Les VRAM et CRAM finales sont identiques.
Le registre VDP 21, qui contient l’octet bas de la source DMA, diffère.

Les 210 cas de saisie du premier caractère du nom, quatre cas de bruitages
au menu, six restaurations du décor statique après l’inventaire et deux
trajets jusqu’au premier donjon passent. La campagne complète en PAL et
la fidélité audiovisuelle sur l’ensemble du jeu restent à valider.

- [Mesures NTSC](fade-v0318/ntsc-video.json) et [PAL](fade-v0318/pal-video.json)
- [Audio du démarrage](fade-v0318/audio.json)
- [Rejeu de la campagne](fade-v0318/campaign.json)
- [Compatibilité de la sauvegarde V317](fade-v0318/save-load.json)
- [Binaire et empreintes des rapports](fade_v0318_report.json)
