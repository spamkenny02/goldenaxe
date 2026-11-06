# c0045 — Copie des lignes de sprites

Aperçu de développement de 1152 Kio, basé sur c0044. Le choix entre RAM et
VDP se fait une seule fois pour les huit lignes ; les lignes RAM masquées
ne sont plus lues. Les lectures VDP restent effectuées dans leur ordre.

Sur la salve PAL mesurée, mises à jour récupérées parmi 80 001 et 80 003 :
80003. Aucune mise à jour supplémentaire par rapport à c0044 :
le saut à 80 001 reste présent. Premier écart des champs de jeu avec la V318 :
[80003]. Un écart de chronologie ne prouve
pas à lui seul la fidélité à la Master System.

Les 108 images de sprites physiques des douze scénarios contrôlés
concordent avec la V318. Le début NTSC jusqu’à 7 710 concorde sur les champs
de jeu comparés. Parcours complet et fidélité audio/vidéo restent à vérifier.
La V318 reste la version de référence.

Checksum : 3268. SHA-256 : `415ba9e186a49f9cd3e38865206603f6354b807a231f0c723e5756fd36734dbb`.

- [ROM c0045](gaw-megadrive-c0045.bin)
- [Patch source](source.patch)
- [Mesures et captures](../../../analysis/c0045-clone-rows/manifest.json)

Correction de format : ce fichier annonce 2 Mio dans son en-tête mais ne
contient que 1152 Kio. Il est conservé pour reproduire ses essais.
Voir c0047 pour le programme de c0046 complété à 2 Mio.
