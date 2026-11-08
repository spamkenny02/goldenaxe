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

Ajout suivant : [septième cristal, bateau et retour PAL](../../analysis/palc0046_d7_report.json)
et [rejeu c0047/V319](../../analysis/c0047_pal_d7_report.json), à 217575 images,
88/88 PV et 64 PM. Les deux boss sont affrontés sans protection ; les dix
étapes de la seconde partie passent, dont les mots physiques du HUD.
La RAM entière et l'image finale correspondent au point contrôlé.

Ajout suivant : [huitième cristal et retour PAL](../../analysis/palc0046_d8_report.json)
et [rejeu c0047/V319](../../analysis/c0047_pal_d8_report.json), à 260858 images,
96/96 PV et 72 PM. Clé du voleur acquise ; 365 prédictions RAM entière
pendant le boss principal et 29 au retour, sans aide après retrait.
RAM entière et PNG final exacts au point contrôlé ; suite PAL ouverte.

Ajout suivant : [neuvième cristal, ballon et retour PAL](../../analysis/palc0046_d9_report.json)
et [rejeu c0047/V319](../../analysis/c0047_pal_d9_report.json), à 302755 images,
104/104 PV et 72 PM. Deux gardiens et boss principal affrontés sans
protection ; douze étapes finales rejouées, HUD des neuf cristaux vérifié.
Le financement du passage provient de vrais ramassages, sans écriture
argent ou ressources. Palais final, générique et sauvegarde PAL restent ouverts.

Ajout suivant : [vraie sauvegarde PAL et Continue](../../analysis/c0047_pal_real_save_report.json).
La V319 écrit sa propre SRAM au slot0 à neuf cristaux ; Continue recharge
ces mêmes octets et permet un déplacement. RAM entière et images finales
du sauvegardeur et du chargement identiques au candidat vérifié. Les autres
slots/refus, la fidélité globale et le palais final PAL restent ouverts.

Ajout suivant : [campagne PAL et fin complète](../../analysis/palc0046_palace_ending_report.json)
et [rejeu c0047/V319](../../analysis/c0047_pal_ending_report.json), à 382208 images.
Le géant du palais, le gardien de la Hache d’or et Death Adder sont vaincus
sans protection de test pendant leurs combats. La Hache d’or est acquise,
les neuf gemmes de fin s’affichent, le générique se déroule entièrement
et le jeu revient à l’intro. Les parcours complets NTSC et PAL, ainsi que
leurs sauvegardes/Continue, passent désormais sur ces mêmes octets.
La phase globale R/IRQ source, les révélations/fondus résiduels, toutes
les formes d’onde PCM et la console réelle restent hors certification.

Ajout suivant : [PSG du démarrage comparé directement à la SMS](../../analysis/sms_psg_v0319_report.json).
Les huit états PSG exposés correspondent à chaque frame de deux boucles
sans entrée, soit14000frames enNTSC et14000enPAL. Aucun décalage ni
normalisation ; états de tonalité, volume et bruit variés. Cette preuve
porte sur les états par frame, sans certification des écritures dans la
frame, des formes d’onde PCM ou des effets interactifs du reste du jeu.

Erratum et mesure complémentaire : [octets PSG et espacement](../../analysis/sms_psg_writes_v0319_report.json).
Les volumes exposés sont des amplitudes décodées, zéro signifie muet ;
le précédent comptage d’activité était incorrect. Les états restent égaux.
Les octets et leur ordre correspondent dès la première frame sonore active
(23 NTSC, 20 PAL), avec quatre frames d’initialisation différentes par région.
L’espacement entre écritures reste différent : aucune équivalence PCM annoncée.
