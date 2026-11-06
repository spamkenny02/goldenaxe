# c0042 — Cadence des salves du boss 6A

Cet aperçu de 2 Mio part de la V318 et simplifie le cache temporaire de
masques de sprites. Dans le rejeu ciblé PAL, la V318 saute la simulation
aux images 80 001 et 80 003. L’aperçu récupère la mise à jour à 80 003.
Ses 768 octets d’acteurs à cette image correspondent au résultat de
l’essai contrôlé dans la salle 180 de la Master System PAL.

Les 37 champs observés concordent avec la V318 jusqu’à l’image 80 002.
Le rejeu ciblé s’arrête à 80 012. La mise à jour de 80 001 reste sautée.
En NTSC, c0042 saute une mise à jour à l’image 7 697 que la V318 exécute.
Les états des acteurs, du butin et du générateur aléatoire divergent.
Le rejeu complet des commandes enregistrées termine en salle 95, hors
donjon. La V318 reste la version de référence.

Checksum Mega Drive `AEE0`. SHA-256
`4d3efb5b253d3431cfa32bfce6bef8357ae0cb409bc624dfc02e27e41e8f34a0`.

- [ROM de test c0042](gaw-megadrive-c0042.bin)
- [Patch source](source.patch)
- [Rapports et captures du rejeu](../../../analysis/c0042-pal-burst-cadence/manifest.json)
- [Comparaison sur la Master System](../../../analysis/c0040_pal_campaign_timing.md)
- [Écart NTSC et captures du rejeu](../../../analysis/c0042-ntsc-campaign-divergence/manifest.json)
