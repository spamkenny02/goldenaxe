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
pas à lui seul une validation du quatrième cristal ; le parcours suivant le vérifie.

[Rejeu jusqu’à l’achat de Terre](../../../analysis/c0047_d4_earth_auto_report.json).

Le canoë, le quatrième cristal et le retour extérieur sont désormais rejoués
sur c0047 jusqu’à 107105 images : 62/64 PV, RAM entière et image finale identiques
au parcours c0046. Les deux passages Terre consomment chacun leurs 8 PM.
Le boss conserve ses 30 PV source ; la protection est retirée avant son entrée.
Les essais de retour bloqué et perdu restent séparés du parcours réussi.

[Audit du quatrième donjon](../../../analysis/c0046_d4_report.json)
· [Rejeu sur c0047](../../../analysis/c0047_d4_auto_report.json).

L’échange de l’huile contre Feu, l’épée longue offerte par le PNJ et l’entrée
du cinquième donjon sont rejoués jusqu’à 121528 images. La capacité magique
passe normalement de 48 à 72 PM ; la RAM entière et l’image finale concordent
avec c0046. Le cinquième cristal est vérifié par le parcours suivant.

[Audit des transactions et du parcours](../../../analysis/fire_sword_c0046_report.json)
· [Rejeu sur c0047](../../../analysis/c0047_d5_fire_sword_auto_report.json).

Le cinquième cristal et le retour extérieur concordent à 150525 images :
72/72 PV, RAM entière et image finale identiques à c0046. Le parcours inclut
les bottes, les dons d’or, l’achat de clé, le soin et les mécanismes.
Le boss conserve ses 72 PV source et ses huit satellites ; la protection
de test est retirée avant l’entrée. La suite de la campagne reste à valider.

[Audit du cinquième cristal](../../../analysis/d5_campaign_c0046_report.json)
· [Rejeu sur c0047](../../../analysis/c0047_d5_auto_report.json).

Le sixième cristal et le retour sont rejoués à 185456 images : 80/80 PV,
72 PM, cloche de glace possédée et six cristaux. La RAM entière et l’image
finale concordent avec c0046. Le boss conserve ses 60 PV source et la
protection est retirée avant son approche finale. La suite reste à valider.

[Audit du sixième cristal](../../../analysis/d6_campaign_c0046_report.json)
· [Rejeu sur c0047](../../../analysis/c0047_d6_auto_report.json).

Le septième cristal et le retour concordent à 227539 images : 88/88 PV,
64 PM, une clé, 27 pièces et bateau possédé. Le parcours comprend la boutique
cachée A5 ouverte par combat, le gardien intermédiaire et le boss principal,
tous deux combattus après retrait de la protection. Les dix étapes finales
de c0046 passent au rejeu indépendant ; c0047 retrouve aussi les 65536 octets
de RAM et l’image finale. La suite reste à valider.

[Audit du septième cristal](../../../analysis/d7_campaign_c0046_report.json)
· [Rejeu sur c0047](../../../analysis/c0047_d7_auto_report.json).

Le huitième cristal et le retour concordent à269376 images :96/96PV,72PM,
une clé,25 pièces et clé du voleur possédée. La RAM entière et le PNG final
concordent avec c0046. Le boss6B garde80PV source, est combattu après retrait
de la protection et vaincu sans dégât reçu ;344 prédictions RAM exactes.
Le retour utilise30 prédictions sans nouvelle aide. La suite reste à valider.

[Audit du huitième cristal](../../../analysis/d8_campaign_c0046_report.json)
· [Rejeu sur c0047](../../../analysis/c0047_d8_auto_report.json).

Le démarrage de cet aperçu est vérifié sur deux boucles sans entrée en
PAL et NTSC. Les 14000 images normalisées de chaque région sont identiques
à V318 ; 13636 sont identiques à la SMS en NTSC et13682 en PAL. Les écarts
résiduels de révélation et de fondu restent présents. Les402 octets d’état
audio et huit registres PSG concordent avec V318 sur6500 images par région ;
ce contrôle ne compare pas les formes d’onde PCM.

[Audit du démarrage c0047](../../../analysis/c0047_boot_report.json).

Les six retours d’inventaire sont également vérifiés en PAL et NTSC,
dans l’extérieur et les deux premières maisons du village. Les motifs
statiques du décor sont identiques à la SMS après fermeture du menu ;
la phase des quatre motifs animés des maisons reste hors de cette égalité.
Ces trajets suivent les commandes normales, sans import de RAM ou SRAM.

[Audit des retours d’inventaire](../../../analysis/c0047_inventory_report.json).

En PAL, la suite après le premier cristal est également rejouée jusqu’à
29846 images : hache obtenue, vraie récompense de la fée (32→40 PV),
puis entrée normale de D2. Les sept étapes sont vérifiées sur c0046 ;
le rejeu c0047 concorde sur toute la RAM et l’image finale de l’entrée.
Le deuxième cristal PAL reste à valider.

[Parcours PAL](../../../analysis/palc0046_after_d1_report.json)
· [Rejeu c0047](../../../analysis/c0047_pal_after_d1_report.json).

Les neuf cristaux et retours sont maintenant rejoués en NTSC jusqu’à
308670 images : 104/104 PV, 72 PM et une clé, ballon, canoë et bateau
conservés. Le boss de D9 garde ses90PV source et tombe sans protection
ni dégât reçu pendant le combat. Les douze points finaux du parcours
c0046 concordent au rejeu indépendant ; c0047 retrouve toute la RAM et
l’image finale du retour. Le palais et la fin restent à valider sur cet aperçu.

[Neuvième cristal et retour](../../../analysis/d9_campaign_c0046_report.json)
· [Rejeu c0047](../../../analysis/c0047_d9_auto_report.json).
