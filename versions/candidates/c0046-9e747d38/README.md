# c0046 — Préparation des motifs du héros

Aperçu de développement de 1152 Kio, basé sur c0044. Les petites copies de
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

Le premier cristal et le retour à l’extérieur sont maintenant vérifiés
avec de nouvelles commandes en PAL et NTSC, sans mort. La protection de
test est retirée avant chaque combat. Les sept points de contrôle de chaque
parcours reproduisent la RAM entière et l’image en rejeu indépendant depuis
Nouvelle partie. Aucun PV, objet, état de progression ou SRAM n’est importé.

| Région | Premier combat | Retrait de protection | Retour extérieur | PV au retour |
| --- | ---: | ---: | ---: | ---: |
| NTSC | 14465 | 14253 | 17169 | 28/32 |
| PAL | 16449 | 16248 | 19596 | 32/32 |

Le premier essai de pilote avait laissé la seconde clé en salle 193 et
s’arrêtait devant la porte du boss. Le parcours validé retourne ramasser
cette clé normalement. Ces commandes régénérées ne prouvent pas une
chronologie identique à celle de la Master System.

- [Premier cristal NTSC, rapport](../../../analysis/c0046_d1_auto_report.json)
- [Premier cristal PAL, rapport](../../../analysis/c0046_d1_pal_report.json)

La continuation NTSC a aussi récupéré la hache en 1B6, reçu normalement
la première amélioration de vie auprès de la fée et rejoint le deuxième
donjon à l’image 27553, avec 40/40 PV. Ces sept étapes passent leurs
rejeux RAM/image depuis Nouvelle partie.

[Hache, fée et entrée du deuxième donjon](../../../analysis/c0046_after_d1_report.json).

Correction de format : ce fichier annonce 2 Mio dans son en-tête mais ne
contient que 1152 Kio. Il est conservé pour reproduire ses essais.
Voir c0047 pour le programme de c0046 complété à 2 Mio.
