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
| Campagnes NTSC/PAL | Nouvelle partie → neuf cristaux → ballon → palais → Hache d’or → Death Adder → générique complet → retour à l’intro | Fidélité globale SMS et console réelle |
| Sauvegarde NTSC/PAL | Vraies écritures SRAM à neuf cristaux, puis Continue et déplacement sur ces mêmes SRAM | Autres slots/refus et console réelle |
| Démarrage vidéo | Deux boucles de 14000 images par région identiques à V318 après normalisation | Écarts SMS résiduels de révélations/fondus |
| Audio du démarrage | Huit états PSG exposés identiques sur 14000 frames par région ; octets et ordre des écritures identiques dès le premier état sonore actif | Espacement des écritures différent dans la frame ; PCM et sons interactifs du reste du jeu |
| Inventaire | Six retours normaux : extérieur et deux maisons, PAL/NTSC, décor statique restauré | Phase des quatre motifs animés des maisons séparée de l’égalité statique |

Les parcours emploient une protection de test uniquement durant les approches,
retirée avant chaque boss. Aucun PV, objet, ennemi ou état de progression
n’est importé. La reprise de sauvegarde importe uniquement la SRAM réellement
écrite par le jeu, conformément au fonctionnement normal de Continue.

Le rejeu NTSC de 403488 images retrouve les 65536 octets de RAM et l’image
finale du parcours c0046. Les étapes intermédiaires ont leurs propres
preuves indépendantes. Ce contrôle ne compare pas chaque image émise à
la SMS. Le parcours PAL complet est aussi rejoué sur le binaire publié,
jusqu’au retour à l’intro à 382208 images, avec RAM entière et image finale
identiques. Les vrais dons et l’achat d’une clé à 60 pièces sont conservés
dans les preuves ; les huit satellites du cinquième boss sont aussi vérifiés.

- [PSG et espacement des écritures face à la SMS](analysis/sms_psg_writes_v0319_report.json) — 28000 frames ; 31546 écritures musicales NTSC et 36915 PAL identiques par système. Les écarts d’initialisation et de timing restent documentés.
- [Rapport initial V319](analysis/optimization_v0319_report.json)
- [Campagne NTSC et fin](analysis/cold_palace_final_c0046_report.json) · [Rejeu sur le binaire publié](analysis/c0047_palace_final_auto_report.json)
- [Campagne PAL, Hache d’or et générique complet](analysis/palc0046_palace_ending_report.json) · [Rejeu sur le binaire publié](analysis/c0047_pal_ending_report.json)
- [Vraie sauvegarde et Continue NTSC](analysis/c0047_real_save_report.json) · [Sauvegarde et Continue PAL](analysis/c0047_pal_real_save_report.json)
- [Neuvième cristal, ballon et retour PAL](analysis/palc0046_d9_report.json) · [Rejeu publié](analysis/c0047_pal_d9_report.json)
- [Premier gardien D9 PAL](analysis/palc0046_d9_midboss_report.json) · [Rejeu publié](analysis/c0047_pal_d9_midboss_report.json) — combat sans protection.
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


Le relevé PSG initial appelait à tort les valeurs exposées « registres bruts » :
les volumes sont déjà décodés en amplitudes par l’émulateur. L’égalité des
huit états reste exacte ; le comptage corrigé donne 13739 frames actives
en NTSC et 13480 en PAL. Le nouveau relevé observe aussi les octets avant
décodage : quatre frames d’initialisation diffèrent par région, avant le
premier état actif. Ensuite les octets et leur ordre sont exacts, mais
l’espacement entre écritures diffère. Cette mesure confirme un travail
de synchronisation audio restant ; elle ne certifie pas les formes d’onde.
Le rapport historique est conservé, avec cet erratum explicite.

Un [prototype d’émission PSG datée](analysis/v319_buffered_psg_report.json)
réduit l’erreur médiane d’espacement de 6246 à 431 ticks en NTSC et de
6260 à 415 en PAL. Il est écarté : l’attente dans l’IRQ dégrade l’intro,
fortement en NTSC. Les commandes préparées conservent exactement leurs
intervalles source et les états sonores de fin de frame, mais cela ne
suffit pas à valider le jeu entier. Le nouveau point d’entrée avec espace
de travail fourni par l’appelant passe 25644 cas source ; il reste inutilisé
par la ROM publiée. La recompilation des sources conserve exactement V319.
La suite est une émission datée sans attente bloquante dans l’IRQ vidéo.

La [préparation audio avant l’IRQ](analysis/v319_audio_prefetch_report.json)
conserve aussi les états du lecteur et les commandes PSG, mais ses trois
variantes restent écartées après comparaison vidéo. Le [relevé direct des
IRQ et callbacks SMS](analysis/v319_intro_irq_trace_report.json) précise le
problème : la V319 et la SMS exécutent le même nombre total de callbacks
sur deux boucles, avec encore des différences de frame. Le placement de
ces callbacks doit être rendu indépendant du coût du lecteur audio natif
avant d’intégrer le nouvel ordonnanceur sonore.

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

Les parcours complets et les sauvegardes NTSC/PAL sont vérifiés sur ces
octets. La récurrence aléatoire SMS est intégrée, mais le fournisseur du
registre R utilise encore SGDK : la phase globale R/IRQ reste à porter.
[Adaptateur actuel](megadrive/src/source_rng_runtime.c).
Des écarts restent dans des révélations partielles et des fondus.
Les contrôles audio logiques ne certifient pas toutes les formes d’onde PCM,
et les essais sur console réelle ne sont pas déclarés validés.
Le projet reste donc une version de développement.

[Reprise technique](REPRISE_CODEX.md) · [Jalons c0046/c0047](JALONS_C0046_C0047.md)
· [Historique des versions précédentes](HISTORIQUE_PORTAGE.md)
