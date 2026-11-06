# c0046 — Préparation des motifs du héros

Aperçu de développement de 2 Mio, basé sur c0044. Les petites copies de
trois octets dans la préparation des motifs du héros deviennent des
écritures directes. L’atlas RAM des ennemis de c0044 reste présent.

Le coût médian des nouvelles poses passe de 123060 à 67942 cycles maîtres,
soit une réduction de 44,79 %, dans les deux régions. Les poses et motifs
concordent sur 561 images par région ; 108 images de sprites physiques
concordent aussi. Les 16 essais de marche contrôlés face à la Master System
passent : quatre directions, vitesse normale et bottes, PAL et NTSC.

L’ancien rejeu PAL exécute désormais la simulation à 80001 et 80003,
deux images sautées par la V318. Sa première divergence de champs de jeu
se situe toutefois à 23709, avant cette
salve : on ne prétend pas conserver l’ancienne trajectoire des acteurs.
En NTSC, la première divergence est à 3396 : c0046 exécute la simulation
alors que la V318 la saute. Les anciennes commandes de campagne doivent
être adaptées. Le parcours complet de c0046 et la fidélité générale SMS
ne sont pas validés. La V318 reste la référence.

Checksum : 6AB5. SHA-256 : `9e747d38e0c6fb2d69b7c1aa8c2b296a61e8b6af41171d14e543ed9a6cb49cf5`.

- [ROM c0046](gaw-megadrive-c0046.bin)
- [Patch source](source.patch)
- [Mesures, pilotes et captures](../../../analysis/c0046-hero-three-plane/manifest.json)
- [Profil qui motive le changement](../../../analysis/c0044_burst_stages.md)
