# Golden Axe Warrior — portage Mega Drive

Reconstruction de la ROM Master System fournie, puis portage de sa logique
Z80 en code natif 68000 avec SGDK. La fidélité précède les améliorations.

<!-- ROM-RELEASE:START -->
**Version courante : v0319 — 2048 Kio.**

[Télécharger la ROM v0319](versions/v0319-d3ea2a83/gaw-megadrive-v0319.bin) · [Toutes les versions](versions/README.md)

Version de développement ; contrôles ciblés réussis, écarts visuels et validation complète encore ouverts.

SHA-256 : `d3ea2a83ea24ed8a0d3c9857f9fbe70d000a4f73358452c1887f40e78966c56e`
Checksum Mega Drive : `DA29`
<!-- ROM-RELEASE:END -->

La V319 reprend exactement le binaire testé de l’aperçu c0047. Les sources
principales intègrent maintenant l’atlas RAM des motifs d’ennemis et les
écritures directes des trois plans du héros. La préparation d’une nouvelle
pose passe de 123060 à 67942 cycles maîtres médians, soit −44,79 % pour
cette routine ; la cadence de jeu visée reste celle de la Master System.
[Mesures et captures](analysis/c0046-hero-three-plane/manifest.json).

## État vérifié de la V319

| Domaine | Contrôles passés | Périmètre restant |
| --- | --- | --- |
| NTSC | Nouvelle partie → neuf cristaux → ballon → palais → Hache d’or → Death Adder → générique complet → retour à l’intro | Fidélité globale SMS et console réelle |
| PAL | Huit cristaux et retours, hache, fée, huile, corde, Terre, canoë, Feu, épée longue, Clochette de glace, bateau, clé du voleur | D9 et suite de la campagne ; sauvegarde PAL |
| Sauvegarde NTSC | Vraie écriture SRAM à neuf cristaux, puis Continue et déplacement sur cette même SRAM | Autres slots/refus et PAL sur cette version |
| Démarrage | Deux boucles de 14000 images par région identiques à V318 après normalisation ; états audio et huit registres PSG comparés sur 6500 images | Écarts SMS résiduels de révélations/fondus et formes d’onde PCM |
| Inventaire | Six retours normaux : extérieur et deux maisons, PAL/NTSC, décor statique restauré | Phase des quatre motifs animés des maisons séparée de l’égalité statique |

Les parcours emploient une protection de test uniquement durant les approches,
retirée avant chaque boss. Aucun PV, objet, ennemi ou état de progression
n’est importé. La reprise de sauvegarde importe uniquement la SRAM réellement
écrite par le jeu, conformément au fonctionnement normal de Continue.

Le rejeu NTSC de 403488 images retrouve les 65536 octets de RAM et l’image
finale du parcours c0046. Les étapes intermédiaires ont leurs propres
preuves indépendantes. Ce contrôle ne compare pas chaque image émise à
la SMS. Le départ PAL et les huit retours sont aussi rejoués sur le binaire
publié ; retour D8 à 260858 images, 96/96 PV et 72 PM. Le cinquième boss et ses
huit satellites sont affrontés sans protection ; les vrais dons et
l’achat d’une clé à 60 pièces sont conservés dans les preuves.

- [Rapport initial V319](analysis/optimization_v0319_report.json)
- [Campagne NTSC et fin](analysis/cold_palace_final_c0046_report.json) · [Rejeu sur le binaire publié](analysis/c0047_palace_final_auto_report.json)
- [Vraie sauvegarde et Continue](analysis/c0047_real_save_report.json)
- [Huitième cristal et retour PAL](analysis/palc0046_d8_report.json) · [Rejeu publié](analysis/c0047_pal_d8_report.json)
- [Intermédiaire du huitième donjon PAL](analysis/palc0046_d8_midboss_report.json) · [Rejeu publié](analysis/c0047_pal_d8_midboss_report.json) — victoire sans protection.
- [Clé du voleur et approche du boss D8](analysis/palc0046_d8_approach_report.json) — clé obtenue par interaction normale.
- [Septième cristal, bateau et retour PAL](analysis/palc0046_d7_report.json) · [Rejeu publié](analysis/c0047_pal_d7_report.json)
- [Intermédiaire du septième donjon PAL](analysis/palc0046_d7_midboss_report.json) · [Rejeu publié](analysis/c0047_pal_d7_midboss_report.json) — victoire sans protection.
- [Préparation du septième donjon PAL](analysis/palc0046_d7_preparation_report.json) · [Rejeu publié](analysis/c0047_pal_d7_preparation_report.json) — achat normal de la clé et deux préparations de Terre.
- [Sixième cristal et retour PAL](analysis/palc0046_d6_report.json) · [Rejeu publié](analysis/c0047_pal_d6_report.json)
- [Cinquième cristal et retour PAL](analysis/palc0046_d5_report.json) · [Rejeu publié](analysis/c0047_pal_d5_report.json)
- [Feu, épée longue et entrée D5 PAL](analysis/palc0046_fire_sword_report.json) · [Rejeu publié](analysis/c0047_pal_fire_sword_report.json)
- [Quatrième cristal PAL](analysis/palc0046_d4_report.json) · [Rejeu publié](analysis/c0047_pal_d4_report.json)
- [Démarrage](analysis/c0047_boot_report.json) · [Retours d’inventaire](analysis/c0047_inventory_report.json)
- [Écritures et poses du héros](versions/candidates/c0046-9e747d38/README.md)

## Sources et compilation

Les fichiers racine `gaw-megadrive.bin` et `gaw-title-megadrive.bin` contiennent
la V319. Les anciennes ROMs numérotées sont conservées dans
[l’index des versions](versions/README.md). L’aperçu c0047 reste conservé
avec le même SHA-256 que V319 pour la traçabilité.

Avec la ROM source dans `input/original.sms`, SGDK, Python et Java disponibles :

```powershell
.\build.ps1
python tools/verify_git_roms.py
```

Le script accepte `-Sgdk` et `-Java`. Il régénère les ressources, compile,
conserve l’alignement initial SGDK et complète la ROM à2Mio avec des octets
FF avant de finaliser le checksum. Une nouvelle ROM différente reçoit un
numéro ; une recompilation identique conserve le numéro existant.
`-ExpectedSha256` permet de vérifier l’empreinte avant de remplacer les ROMs
racine et de numéroter le résultat.

La reconstruction propre des226 fichiers versionnés de base et du patch
publié reproduit exactement la ROM et ses symboles.
[Preuve de reconstruction](analysis/c0047_clean_rebuild_report.json).
Pour répéter cette vérification dans un nouveau dossier, avec l’historique Git :

```powershell
python validation/rebuild_c0047.py --work validation/rebuild-check01
```

Le code jouable se trouve notamment dans [main.c](megadrive/src/main.c),
[actors.c](megadrive/src/actors.c) et les modules `source_*` de
[megadrive/src](megadrive/src). Les données graphiques, tables et textes
proviennent de la ROM source fournie.

## Travail encore ouvert

La suite PAL reste en cours de validation sur ces octets. La récurrence
aléatoire SMS est intégrée, mais le fournisseur du registre R utilise encore
SGDK : la phase globale R/IRQ reste à porter.
[Adaptateur actuel](megadrive/src/source_rng_runtime.c).
Des écarts restent dans des révélations partielles et des fondus.
Les contrôles audio logiques ne certifient pas toutes les formes d’onde PCM,
et les essais sur console réelle ne sont pas déclarés validés.
Le projet reste donc une version de développement.

[Reprise technique](REPRISE_CODEX.md) · [Jalons c0046/c0047](JALONS_C0046_C0047.md)
· [Historique des versions précédentes](HISTORIQUE_PORTAGE.md)
