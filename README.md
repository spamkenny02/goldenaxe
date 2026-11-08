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

## Travail natif en cours : statut vidéo des sprites

Le chargeur de scène natif peut maintenant publier les motifs décompressés
avec leurs dates, en plus des effacements et transferts de carte. Les dix
chargements de référence passent sur hôte, puis sur 68000 en NTSC/PAL :
**505040 sorties** et **488 interruptions natives** vérifiées, avec les mêmes
états RAM, audio, VRAM et horloge.
[Scènes avec sorties datées](analysis/v319_scene_ports_report.json).

Les statuts vidéo de ce banc restent des valeurs capturées. Le raccordement
au calcul vivant du miroir, aux paquets vidéo des interruptions et aux sorties
physiques image/son reste à terminer et à mesurer. La ROM reste V319.

Les dates du décodeur sont maintenant confirmées par une capture indépendante
de l’exécution SMS : **65472 écritures** des deux décors en NTSC/PAL, après
séparation du temps réellement passé dans les interruptions. Le décodeur relié
au miroir vidéo passe aussi sur 68000 : 48 cas, 785664 écritures et VRAM finale
exactes. [Dates originales et raccordement compilé](analysis/v319_pattern_dates_report.json).

Le test natif utilise encore une interruption synthétique. Il faut composer
l’intro complète avec les vraies interruptions, puis mesurer le coût des
routines et des sorties vidéo/PSG. Les durées des noyaux diagnostiques ne
constituent pas cette mesure. Aucune nouvelle ROM jouable n’est publiée ici.

Le décodeur natif de motifs publie maintenant chaque écriture de port avec sa
date de fin d’instruction, y compris dans ses chemins optimisés. Les 1054 cas
sur hôte retrouvent les dates, les octets et les états de l’exécution instruction
par instruction. Sur 68000, les deux décors d’intro passent 48 cas et 785664
écritures vérifiées. Le raccordement au miroir vidéo séparé passe aussi sur
hôte : 24 cas, 392832 écritures et comparaison des 16 Kio de VRAM.
[Résultats des sorties du décodeur](analysis/v319_pattern_ports_report.json).

L’ordre de 18528 écritures du premier décor est confirmé par la capture SMS
dans chaque région. Les dates de travail du décodeur sont désormais confirmées par la capture
indépendante ci-dessus ; les dates avec les vraies interruptions natives
restent à vérifier. Le test du décodeur emploie des interruptions
synthétiques ; l’intro complète avec ses sorties vidéo et sonores reste à
composer et à mesurer avant activation. Le binaire public reste V319.

Le miroir `source_intro_vdp.c` possède désormais sa propre VRAM, ses registres,
sa palette et les états des ports. Alimenté uniquement par les instructions
OUT/IN originales, il retrouve **8494239 écritures**, **33707 lectures de statut**
et **5616 lectures VRAM**, avec comparaison intégrale de sa mémoire après les
accès, sur les deux parcours de 14000 images. Les préfixes de démarrage passent
aussi sur 68000 dans les deux régions : 535716 accès et 9856 lectures vérifiés.
[Résultats du miroir des ports](analysis/v319_port_mirror_report.json).

Le producteur des accès de ce banc est encore le Z80 original. Il reste à
raccorder les sorties des routines natives, notamment les motifs décompressés,
puis à optimiser et mesurer le budget complet avec les sorties vidéo/PSG.
Les durées des noyaux de test ne mesurent pas la cadence du jeu. La ROM
publiée reste V319 ; la reconstruction complète demeure identique.

Le calendrier `source_intro_sprite_clock.c` déclenche maintenant lui-même
l’évaluation des sprites et le drapeau VINT à partir des cycles écoulés.
Il retrouve les **33707 lectures complètes de statut** sur les deux parcours
de démarrage de 14000 images, sans recevoir les événements d’évaluation ou
les statuts attendus du moteur de référence. Les **58730 cas** de lignes et
de lectures passent sur 68000 en NTSC et PAL (117460 exécutions), ainsi que
le fournisseur de statut des interruptions. Les états PSG capturés restent
identiques. [Résultats du calendrier](analysis/v319_sprite_clock_report.json).

La VRAM et les registres du banc viennent encore de la référence. Il reste à
les alimenter depuis les écritures du portage et à dater les sorties du décodeur
de motifs, puis à mesurer le coût du calendrier avec les sorties vidéo/PSG.
Le budget CPU précédent de 19..22 images ne comprend pas ce nouveau calcul.
La ROM publique reste V319 ; la reconstruction complète est identique.

Le contexte des interruptions de l’intro accepte maintenant un fournisseur
optionnel du statut vidéo. Sa lecture précède les sorties vidéo/PSG et alimente
`C01B`, y compris pour les interruptions audio seules. Les quatre variantes
d’interruption passent 384 cas au total sur hôte, puis les mêmes
384 cas en NTSC et en PAL sur 68000 (768 exécutions compilées).
Sans fournisseur, le comportement et les dates PSG du banc sont conservés ;
un refus du fournisseur arrête l’interruption avant publication.
[Contrats de raccordement](analysis/v319_irq_status_binding_report.json).
La reconstruction complète reste identique à la V319 publiée, octet pour octet.
[Reconstruction](analysis/v319_irq_status_rebuild_report.json).

Le nouveau module `source_intro_sprite_status.c` calcule les collisions et le
débordement des sprites à partir de la VRAM, des registres et des événements
vidéo. Il conserve les caches et les drapeaux entre les lignes et les lectures.
Sur deux parcours de démarrage de 14000 images, il retrouve les 33707 lectures
de statut et les 27986 statuts sauvegardés par les interruptions, sans écart.
Les 33179 transitions distinctes passent aussi sur 68000 en NTSC et PAL,
soit 66358 exécutions. [Résultats](analysis/v319_chip_temporal_report.json).

Le calendrier reste à raccorder aux écritures VRAM et à l’horloge du portage ;
les événements de ces tests viennent encore du moteur de référence. La ROM
publiée reste V319. Les lectures juste avant le pixel de collision ne sont
pas couvertes par ce parcours naturel, et le rendu physique/PCM reste à vérifier.

Correction des anciennes notes : la différence `9F/BF` indique une **collision**
(bit `20`), et le débordement utilise le bit `40`. Les valeurs capturées et les
comparaisons antérieures sont inchangées.
[Erratum](analysis/v319_sprite_status_erratum.json).

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

Les [essais d’acquittement explicite de l’IRQ](analysis/v319_intro_irq_ack_report.json)
confirment aussi que déplacer le callback dans l’IRQ ne reproduit pas la
continuation SMS. Son exécution au premier plan préserve les cinq champs
d’état d’intro contrôlés et les 420 octets d’état audio suivis, mais laisse
des régressions de pixels. Ces cinq variantes restent privées et écartées.
L’étape suivante est l’ordonnancement continu avec `SourceClock` et le coût
réel du lecteur, en réutilisant le modèle existant de l’attente SMS `0B95`.

Cette étape commence avec [la nouvelle attente vidéo native](analysis/v319_native_intro_poll_report.json) :
172 attentes `0F21..0F2B` de la ROM SMS sont reproduites exactement, soit
172770 lectures de compteur. Les vecteurs passent aussi sur le 68000 compilé.
Le regroupement des lectures sans changement de condition ni IRQ ramène
le banc NTSC de 2453 à 105 frames d’émulation, sans changer les résultats.
5948 contextes supplémentaires vérifient ce regroupement aux frontières
d’IRQ, DI/EI et compteur. Les [continuations `F09/F32/F1E` avec callback vide](analysis/v319_intro_empty_report.json)
passent maintenant 2052 captures naturelles SMS, toutes avec IRQ pendant
l’attente, puis 4104 exécutions compilées 68000 dans les deux régions.
Le [callback du feu avec son compteur et sa palette](analysis/v319_intro_fire_report.json)
est aussi traduit : 7159 vecteurs source passent, puis 14318 exécutions
compilées 68000 dans les deux régions. Les [callbacks des personnages animés](analysis/v319_intro_actors_report.json)
passent également 14704 vecteurs source et 29408 exécutions compilées 68000,
avec les listes de sprites et les palettes. Le banc de la troisième scène
fournit explicitement le statut VDP capturé à chaque IRQ ; sa production
à partir des sprites vivants reste à intégrer. L’[initialisation des acteurs F51/F54](analysis/v319_intro_init_report.json)
reproduit aussi les 12 vecteurs d’entrée naturels capturés, puis leurs
24 exécutions compilées : remise à zéro, neuf/six acteurs et temps source
identiques. Ces appels ne traversent aucune IRQ ; ce cas reste à couvrir.
Le [passage de dévoilement E8B..E9D](analysis/v319_intro_reveal_report.json)
reproduit désormais 112 entrées SMS et 774144 écritures vidéo : valeurs,
ordre et temps de fin d’instruction identiques. Tous les vecteurs passent
également en 68000 compilé sur les deux régions. Le regroupement des
boucles sans interruption préserve ces résultats. La [composition complète E79..EA2](analysis/v319_intro_sequence_report.json)
passe maintenant aussi : 14 séquences naturelles SMS, avec leurs attentes,
callbacks actifs et 40 IRQ par séquence, puis 28 exécutions compilées.
La boucle comporte huit passages, dont un dernier au masque zéro.
La [sortie anticipée pendant le dévoilement](analysis/v319_intro_skip_report.json)
passe également 84 scénarios de manette (deux boutons, trois callbacks,
sept étapes, PAL/NTSC), avec rejeu indépendant des états audio source.
Les 88 vecteurs conservés, préfixes complets compris, passent 176 exécutions
68000. Cette preuve s’arrête à l’entrée D0B, avant le retour à l’écran titre.
La [préparation de la carte et son transfert vidéo EA5/EFA](analysis/v319_intro_transfer_report.json)
sont également traduits : 42 vecteurs d’entrée source et 84 exécutions
68000 passent, avec 32340 écritures vidéo vérifiées. Cela inclut la carte
vide, les quatre couleurs du bandeau de données et les deux attentes avec
callbacks autour du transfert. Le [décodage de carte BD3/BFE et son placement par lignes](analysis/v319_intro_map_report.json)
sont aussi traduits : 28 vecteurs source et 56 exécutions compilées passent,
avec les banques ROM 6/7, les tampons mémoire et les temps correspondants.
L’[effacement du quatrième plan graphique E2B](analysis/v319_intro_clear_report.json)
est aussi traduit et vérifié : 96768 écritures source, puis 28 exécutions
compilées en PAL/NTSC. Son regroupement des boucles sans interruption
préserve chaque écriture et son timing. Le [chargement complet E50..E72](analysis/v319_intro_scene_report.json)
est maintenant composé et vérifié : graphismes et carte en mémoire vidéo,
états suivis et horloge source correspondent sur les dix chargements capturés,
puis vingt exécutions 68000. Le décodeur optimisé conserve aussi les cas de
la banque ROM 7. Les [optimisations des transferts, copies et plans ROM](analysis/v319_intro_runs_report.json)
font désormais tenir le helper dans la durée des cas SMS correspondants :

| Région | Helper MD avant | Helper MD après | Durée SMS |
| --- | ---: | ---: | ---: |
| NTSC | 98–99 frames | 19–22 frames | 24–27 frames |
| PAL | 81–83 frames | 15–18 frames | 21–23 frames |

Ces mesures ont une résolution d’une frame, désactivent les comparaisons de
chaque écriture et excluent la livraison vidéo/PSG sur le matériel. Tous les
états finaux restent contrôlés ; les écritures sont vérifiées séparément.
L’intégration à l’intro publiée, le statut VDP vivant et les délais réels
sur Mega Drive restent à finaliser.
Aucune de ces nouvelles routines ne pilote encore l’intro publiée.
La recompilation complète conserve exactement la V319.

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
