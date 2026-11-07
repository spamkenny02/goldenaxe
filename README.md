# Golden Axe Warrior — portage Mega Drive

Reconstruction de Golden Axe Warrior depuis la ROM Master System fournie,
puis portage de sa logique Z80 en code natif 68000 avec SGDK.
La fidélité à la Master System passe avant les améliorations.

<!-- ROM-RELEASE:START -->
**Version courante : v0318 — 2048 Kio.**

[Télécharger la ROM v0318](versions/v0318-b9e1f0a0/gaw-megadrive-v0318.bin) · [Toutes les versions](versions/README.md)

Version de développement ; contrôles ciblés réussis, écarts visuels et validation complète encore ouverts.

SHA-256 : `b9e1f0a0543f191e24ffd6d2740a0d717501e0fcd986f8b8953a37a1b3c416a4`
Checksum Mega Drive : `7863`
<!-- ROM-RELEASE:END -->

Aperçu actuel : [c0047, ROM de 2 Mio](versions/candidates/c0047-d3ea2a83/README.md).
Il reprend l’optimisation c0046 et corrige son complément de fichier.
Premier donjon rejoué en PAL et NTSC ; six premiers cristaux et retours extérieurs
rejoués en NTSC, ainsi que l’achat normal de Terre et l’acquisition du canoë.
La campagne complète de cet aperçu reste à valider.

Le quatrième boss est vaincu après retrait de la protection, avec ses 30 PV source.
Le retour sur c0047 concorde sur les 65536 octets de RAM et l’image finale à
107105 images, avec 62/64 PV. [Parcours du quatrième donjon](analysis/c0046_d4_report.json)
· [Rejeu sur c0047](analysis/c0047_d4_auto_report.json).

L’échange réel de l’huile contre Feu, le don de l’épée longue et l’entrée
du cinquième donjon sont également vérifiés, jusqu’à 121528 images :
62/64 PV et 72 PM. [Transactions et parcours](analysis/fire_sword_c0046_report.json)
· [Rejeu sur c0047](analysis/c0047_d5_fire_sword_auto_report.json).

La branche c0046 a aussi obtenu les bottes, reçu deux dons de 30 pièces,
acheté une clé à 60 pièces et utilisé le soin normal. Treize étapes sont
rejouées depuis Nouvelle partie jusqu’au mécanisme précédant le cinquième boss.
[Préparation du cinquième donjon](analysis/d5_supplies_c0046_report.json).
Le cinquième boss et le retour sont maintenant vérifiés : boss à 72 PV source,
huit satellites, protection retirée avant l’entrée, 72/72 PV au retour.
Les cinq étapes finales concordent au rejeu indépendant ; le parcours c0047
retrouve aussi toute la RAM et l’image finale à 150525 images.
[Audit du cinquième cristal](analysis/d5_campaign_c0046_report.json)
· [Rejeu sur c0047](analysis/c0047_d5_auto_report.json).

La préparation du sixième donjon sur c0046 est vérifiée en dix-sept étapes :
cinq acquisitions de clés, six étapes Terre, mécanismes et cloche de glace,
avec HUD physique et rejeu RAM/image. Point préparatoire : 176002 images,
72 PV et 40 PM. Le sixième boss et le retour sont désormais vérifiés ci-dessous.
[Préparation du sixième donjon](analysis/d6_progress_c0046_report.json).

Sixième cristal et retour vérifiés à 185456 images : 80/80 PV et 72 PM.
Le boss garde ses 60 PV source ; la protection est retirée avant l’approche
finale. Les 190 prédictions du combat et les 97 du retour concordent sur
toute la RAM. Le parcours c0047 retrouve aussi la RAM entière et l’image finale.
[Audit du sixième cristal](analysis/d6_campaign_c0046_report.json)
· [Rejeu sur c0047](analysis/c0047_d6_auto_report.json).

Sur la suite c0046, l’entrée cachée d’A5 s’ouvre après l’élimination normale
des ennemis de l’écran, comme le prévoit la source. Le combat, la case
transformée et l’entrée réelle chez le marchand concordent au rejeu indépendant.
[Boutique cachée A5](analysis/a5_hidden_shop_c0046_report.json).
La préparation du septième donjon est vérifiée sur c0046 : dix points de
contrôle, clé achetée à 40 pièces, deux acquisitions de clés dans le donjon
et deux actions Terre consommant 16 PM. Le héros arrive devant le gardien
intermédiaire avec 80/80 PV, 56 PM et deux clés.
[Préparation D7](analysis/d7_prep_c0046_report.json).
Le gardien intermédiaire est ensuite vaincu sans protection ni dégât reçu :
ses 30 PV source, les 92 prédictions RAM et quatre points du rejeu indépendant
sont vérifiés. La protection d’approche reprend seulement après sa mort.
[Gardien intermédiaire D7](analysis/d7_midboss_c0046_report.json).
Le bateau est aussi récupéré et vérifié sur c0046 à 215194 images, avec
80/80 PV, 72 PM et deux clés. Le trajet sud réveille les ennemis cachés
par une marche normale sur leur sol ; le mécanisme distant et les trois
points RAM/image concordent au rejeu indépendant.
[Bateau D7](analysis/d7_ship_c0046_report.json).
Le boss principal et le septième cristal restent à valider.
[Captures des retours D4 ratés archivées, environ 9 Mio libérés](analysis/c0046-d4-failed-exit-captures/manifest.json).

Nouvel aperçu [c0046](versions/candidates/c0046-9e747d38/README.md) :
préparation des motifs du héros mesurée 44,79 % moins coûteuse ;
marche contrôlée conforme SMS et premier cristal/retour vérifiés en PAL et NTSC.
La suite NTSC a aussi obtenu la hache, reçu la première amélioration de vie
et rejoint le deuxième donjon. Le parcours complet de cet aperçu reste à valider.

Nouvel aperçu [c0045](versions/candidates/c0045-415ba9e1/README.md) :
essai de copie des lignes de sprites, sans mise à jour PAL supplémentaire ;
la V318 reste la version de référence.

La **v318** applique le fondu avant le titre pendant l’interruption vidéo.
Elle ajoute 34 images identiques à la Master System dans chaque région.
La campagne PAL V318 va désormais de Nouvelle partie à la victoire, au
générique et au retour à l’intro, avec rejeu indépendant RAM/image.
Le rejeu de la campagne NTSC retrouve les 393 707 états comparés de la v317
et les quatre captures de fin. La sauvegarde v317 à neuf cristaux se recharge.
[Mesures et limites de la v318](analysis/fade_v0318.md)
· [Mesures des transferts partiels de la troisième scène](analysis/scene3_reveal_experiment_v0318.md)
· [Essais de transfert des lignes de révélation](analysis/scene_reveal_row_count_v0318.md)
· [Nettoyage partiel des essais archivés, 6 Mio libérés](analysis/intro_archived_files_cleanup_v0318_report.json)
· [Premier cristal en PAL et comparaison de l’entrée](analysis/pal_d1_v0318.md)
· [Hache, fée et deuxième cristal en PAL](analysis/pal_d2_v0318.md)
· [Huile, corde et troisième cristal en PAL](analysis/pal_d3_v0318.md)
· [Achat de Terre et entrée du quatrième donjon en PAL](analysis/pal_earth_v0318_report.json)
· [Canoë et quatrième cristal en PAL](analysis/pal_d4_v0318.md)
· [Feu, épée longue et entrée du cinquième donjon en PAL](analysis/pal_fire_sword_v0318_report.json)
· [Bottes, achat de clé et soin avant le cinquième cristal en PAL](analysis/pal_d5_supplies_v0318_report.json)
· [Cinquième cristal et retour à l’extérieur en PAL](analysis/pal_d5_campaign_v0318.md)
· [Cloche de glace, sixième cristal et retour en PAL](analysis/pal_d6_v0318.md)
· [Ravitaillement et préparation du septième donjon en PAL](analysis/pal_d7_prep_v0318.md)
· [Gardien intermédiaire du septième donjon en PAL](analysis/pal_d7_midboss_v0318.md)
· [Mécanisme et bateau du septième donjon en PAL](analysis/pal_d7_ship_v0318.md)
· [Septième cristal et retour à l’extérieur en PAL](analysis/pal_d7_campaign_v0318.md)
· [Passage payant, entrée et gardien intermédiaire D8 en PAL](analysis/pal_d8_midboss_v0318.md)
· [Clé du voleur et approche du boss D8 en PAL](analysis/pal_d8_approach_v0318.md)
· [Huitième cristal et sortie en PAL](analysis/pal_d8_campaign_v0318.md)
· [Passeur, entrée et premier gardien D9 en PAL](analysis/pal_d9_midboss_v0318.md)
· [Géant du neuvième donjon en PAL](analysis/pal_d9_giant_v0318.md)
· [Ballon récupéré dans le neuvième donjon en PAL](analysis/pal_d9_balloon_v0318_report.json)
· [Neuf cristaux et retour à l’extérieur en PAL](analysis/pal_d9_exit_v0318.md)
· [Ballon et entrée du palais en PAL](analysis/pal_palace_entry_v0318.md)
· [Deux premiers mécanismes du palais en PAL](analysis/pal_palace_mechanisms_v0318_report.json)
· [Premier géant du palais vaincu en PAL](analysis/pal_palace_giant_v0318.md)
· [Premier portail intérieur du palais en PAL](analysis/pal_palace_portal_v0318_report.json)
· [Passage Terre en salle 14E du palais en PAL](analysis/pal_palace_earth_v0318_report.json)
· [Portails, Terre et mécanisme 129 du palais en PAL](analysis/pal_palace_inner_v0318.md)
· [Antichambre du gardien de la Golden Axe en PAL](analysis/pal_palace_pre_guardian_v0318_report.json)
· [Gardien de la Golden Axe vaincu en PAL, rejeu depuis Nouvelle partie](analysis/pal_palace_guardian_v0318_report.json)
· [Golden Axe récupérée normalement en PAL](analysis/pal_palace_golden_axe_v0318_report.json)
· [Tous les passages du palais jusqu’à l’antichambre de Death Adder en PAL](analysis/pal_palace_pre_final_v0318_report.json)
· [Victoire PAL, générique complet et retour à l’intro](analysis/pal_palace_ending_v0318_report.json)
· [Reprise en PAL de la sauvegarde V317 à neuf cristaux](analysis/pal_save_compatibility_v0318_report.json)
· [Écriture et reprise d’une vraie sauvegarde V318 en PAL](analysis/game_written_save_pal_v0318_nine_crystals_report.json)
· [Comparaison du générique avec la Master System, en PAL et NTSC](analysis/ending_controlled_v0318.md)
· [Défilements et sprites vérifiés à nouveau sur V318](analysis/scroll_recheck_v0318_report.json)
· [Compilation propre et correspondance de la ROM source](analysis/rebuild_v0318_report.json)

L’aperçu [c0038](versions/candidates/c0038-e7ee40cb/README.md) est conservé
avec son rejeu divergent. L’ancien aperçu [c0029](versions/candidates/c0029-c3fca1d6/README.md) reste disponible.
L’aperçu [c0039](versions/candidates/c0039-aafa3255/README.md) recale la durée
de la première entrée du donjon 1 en PAL et NTSC. Un parcours NTSC adapté
atteint le premier cristal. L’aperçu [c0040](versions/candidates/c0040-1f4355f1/README.md)
recale aussi la demande musicale et rejoue le donjon dans les deux régions.
L’aperçu [c0042](versions/candidates/c0042-4d3efb5b/README.md) récupère une
mise à jour de la salve du boss 6A observée sur Master System en PAL.
L’aperçu [c0043](versions/candidates/c0043-3554bad2/README.md) recale le
début du générique dans le test contrôlé.
L’aperçu [c0044](versions/candidates/c0044-cc4c9830/README.md) lit les motifs
des ennemis depuis la RAM du donjon et récupère une mise à jour de salve PAL.

## État du portage

La logique du jeu est portée en code natif 68000. SGDK fournit notamment
le démarrage et les accès vidéo ; les ressources et les tables proviennent
de la ROM Master System. Le lecteur audio est également natif.
Sources principales : [boucle et transitions](megadrive/src/main.c),
[acteurs](megadrive/src/actors.c), [générateur source](megadrive/src/source_rng.c).

Les résultats de la V318 et des aperçus sont distincts. La V318 reste la
référence ; c0047 contient l’optimisation des motifs du héros et poursuit
sa propre campagne. Un numéro de version ne constitue pas un statut de finale.

## Campagne et travail restant

| Binaire | Parcours vérifié | Limite |
| --- | --- | --- |
| V318 NTSC | Neuf cristaux, palais, Death Adder, générique et retour à l’intro ; 393707 états comparés au parcours V317 | Ce rejeu ne prouve pas une identité globale avec la SMS. |
| V318 PAL | Nouvelle partie jusqu’à la victoire et au générique, avec rejeux indépendants RAM/image | La comparaison audiovisuelle source reste ciblée. |
| c0047 NTSC | Six cristaux et retours, canoë, Feu, épée longue, bottes, cloche de glace, achats et soin | Septième donjon en cours ; fin de campagne et sauvegarde à revalider sur cet aperçu. |
| c0047 PAL | Premier cristal et retour extérieur | Les autres donjons restent à vérifier sur cet aperçu. |

Les contrôles V318 couvrent aussi l’intro et le titre, la saisie du nom,
des bruitages de menu, six restaurations de décor après inventaire et les
défilements entre cartes. Une vraie sauvegarde V318 est écrite puis rechargée
en PAL ; la compatibilité d’une sauvegarde V317 à neuf cristaux est contrôlée.
Les rapports et leurs périmètres sont liés plus haut.

La récurrence du hasard SMS est intégrée, mais son fournisseur de registre R
utilise encore SGDK : la phase globale R/IRQ reste à porter.
[Adaptateur actuel](megadrive/src/source_rng_runtime.c).
Des écarts restent dans des révélations partielles et des fondus.
Les comparaisons de registres audio ne certifient ni toutes les formes d’onde
PCM ni tous les bruitages de toutes les scènes. La fidélité globale et les
essais sur console réelle ne sont pas déclarés validés.

## ROMs et compilation

Chaque ROM différente conserve son numéro et son SHA-256 dans
[l’index des versions](versions/index.json). Les deux fichiers racine,
`gaw-megadrive.bin` et `gaw-title-megadrive.bin`, contiennent la V318.
Les aperçus gardent leur binaire et leur patch dans `versions/candidates`.
Toutes les anciennes ROMs numérotées sont conservées.

Depuis ce répertoire, avec la ROM source dans `input/original.sms`,
SGDK, Java et Python disponibles :

```powershell
.\build.ps1
python tools/verify_git_roms.py
```

`build.ps1` accepte `-Sgdk` et `-Java` pour leurs emplacements. Il compile
les sources de référence, complète la ROM à 2 Mio, recalcule le checksum
et numérote les nouveaux binaires. Le vérificateur Git compare les ROMs
aux objets du dernier commit ; il s’exécute après l’enregistrement de la livraison.

Le [module de démarrage SGDK](megadrive/src/gaw_sgdk_sys.c) conserve
l’[attribution MIT](megadrive/SGDK-license.txt).
Les preuves volumineuses sont archivées sans perte et relues avant tout
nettoyage des doublons générés. Les ROMs numérotées restent conservées.

## Historique et reprise

- [Notes détaillées des versions précédentes](HISTORIQUE_PORTAGE.md).
- [Reprise du projet et processus courant](REPRISE_CODEX.md).
- [ROMs numérotées](versions/README.md).
