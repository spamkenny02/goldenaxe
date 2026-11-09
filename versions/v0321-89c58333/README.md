# V321 — publication des animations du titre

Correction du retard d’une image de la cape, des lignes du logo et du
clignotement de l’invite. Code natif 68000, sans relier à nouveau le jeu.
Le correctif des crédits V320 est conservé.

- ROM : `gaw-megadrive-v0321.bin`, 2 Mio, checksum `CB3C`.
- SHA-256 : `89c5833351312ffaa591efb1939161910a298af06437080e2cf84fb3fb8ac86e`.
- 33 poses de cape de six images : 198 images conformes à la SMS en PAL et NTSC
  après conversion des niveaux de couleur matériels connus.
- Huit parcours de contrôle PAL/NTSC : transitions, image finale, registres PSG
  et état du lecteur sonore identiques à la V320 à chaque image observée.
- Les échantillons PCM diffèrent ; pas de certification sonore matérielle.
- Une image NTSC pendant la première ligne du logo présente encore 262 pixels
  différents. Révélations de scènes et autres animations restent à finaliser.

[Rapport complet](title_publication_v0321_report.json).

Reconstruction depuis la racine :
`python tools/build_title_publication_overlay.py --out validation/title-build-local`.
La base V320 et chaque instruction remplacée sont vérifiées.
Une compilation SGDK générale produit la base V319 ; appliquer d’abord
`tools/build_credits_border_overlay.py`, puis fournir sa V320 avec `--base`.
Les archives de passation V320 restent des instantanés de cette ancienne version.
