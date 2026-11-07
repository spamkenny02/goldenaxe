# V319 — optimisation de la préparation des sprites

ROM de développement de 2 Mio, identique octet par octet à c0047.
SHA-256 : `d3ea2a83ea24ed8a0d3c9857f9fbe70d000a4f73358452c1887f40e78966c56e`.
Checksum : DA29.

[Télécharger la ROM](gaw-megadrive-v0319.bin)
· [Patch depuis les sources V318](source-v0318-to-v0319.patch)
· [Rapport initial](optimization_v0319_report.json)
· [Reconstruction propre](c0047_clean_rebuild_report.json).

La préparation des nouvelles poses du héros coûte 44,79 % de cycles maîtres
en moins dans les mesures médianes ; l’atlas RAM évite des lectures VDP.
La campagne NTSC est rejouée depuis Nouvelle partie jusqu’à la victoire,
au générique complet et au retour à l’intro. Une vraie sauvegarde à neuf
cristaux et Continue passent aussi. Les comparaisons RAM/image sont exactes
aux points contrôlés, sans normalisation de pile. Les approches utilisent
une protection de test retirée avant chaque boss, sans import de ressources.

Au jalon initial, quatre cristaux et retours PAL sont vérifiés. La suite PAL,
la phase globale R/IRQ source, des révélations/fondus et la fidélité générale
PCM/console restent ouverts. Le [README courant](../../README.md) indique
les preuves ajoutées ultérieurement sur le même binaire.

Ajout sur le même binaire : [cinquième cristal et retour PAL](../../analysis/palc0046_d5_report.json)
et [rejeu c0047/V319](../../analysis/c0047_pal_d5_report.json), à 137596 images.
Les 65536 octets de RAM et le PNG final sont identiques. Huit satellites
observés ; aucune protection durant le boss ou le retour. Le détour de
portail du pilote est documenté avec l'échec initial conservé.

Ajout suivant : [sixième cristal, Clochette de glace et retour PAL](../../analysis/palc0046_d6_report.json)
et [rejeu c0047/V319](../../analysis/c0047_pal_d6_report.json), à 176650 images,
80/80 PV et 72 PM. Vingt points froids vérifiés ; 209 prédictions RAM entière
pendant le boss, sans protection. Fidélité globale et suite PAL ouvertes.
