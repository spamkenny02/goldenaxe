# c0047 — ROM de 2 Mio correctement complétée

Cet aperçu contient le programme et les ressources de c0046. Seuls le
complément final à FF et le checksum changent. L’optimisation des motifs
du héros reste identique.

c0046 annonçait 2 Mio dans son en-tête mais son fichier ne faisait que
1152 Kio. c0047 complète le fichier à 2048 Kio et recalcule le checksum.
Les captures et parcours c0046 restent attachés au binaire c0046 ; les
rejeux sur cette image complétée sont indiqués séparément.

SHA-256 : `d3ea2a83ea24ed8a0d3c9857f9fbe70d000a4f73358452c1887f40e78966c56e`. Checksum : DA29.

- [ROM c0047](gaw-megadrive-c0047.bin)
- [Programme source, patch par rapport à V318](source.patch)
- [Vérification du contenu et de l’en-tête](packaging.json)
- [Mesures de l’optimisation c0046](../c0046-9e747d38/README.md)

La V318 reste la référence. Le parcours complet de cet aperçu reste à valider.

Les deux rejeux du premier cristal et du retour extérieur concordent avec
c0046 sur toute la RAM (65536 octets) et l’image finale : 17169 images en
NTSC et 19596 en PAL.

- [Rejeu NTSC](../../../analysis/c0047_d1_auto_report.json)
- [Rejeu PAL](../../../analysis/c0047_d1_pal_report.json)

Le parcours NTSC jusqu’au deuxième cristal et au retour extérieur est
également rejoué : 56219 images, 37/48 PV au retour, RAM entière et image
finale identiques au parcours c0046. Le combat du deuxième boss commence
avec ses 30 PV source et la protection retirée avant l’entrée.

[Rejeu du deuxième cristal sur c0047](../../../analysis/c0047_d2_auto_report.json).

L’entrée du troisième donjon et l’acquisition normale de la corde sont
également rejouées sur c0047 jusqu’à 67763 images : RAM entière et image
finale identiques à c0046. Le troisième cristal et le retour extérieur sont désormais aussi rejoués
sur cet aperçu, comme indiqué ci-dessous.

[Rejeu jusqu’à la corde](../../../analysis/c0047_d3_rope_auto_report.json).

Le troisième cristal et la sortie sont rejoués en NTSC jusqu’à 75250 images,
avec 48/56 PV au retour. Les 65536 octets de RAM et l’image finale sont
identiques à ceux du parcours c0046. Les trois boss ont été affrontés
après retrait de la protection de test.

[Rejeu du troisième cristal et du retour](../../../analysis/c0047_d3_auto_report.json).

Le don réel de 50 pièces puis l’achat de Terre pour 50 pièces sont rejoués
sur c0047 jusqu’à 81636 images. La RAM entière et l’image finale concordent
avec c0046 : 48 PV, 12 pièces et 48 PM, Terre niveau 1. Cela ne constitue
pas encore une validation du quatrième cristal.

[Rejeu jusqu’à l’achat de Terre](../../../analysis/c0047_d4_earth_auto_report.json).
