# Golden Axe Warrior — portage Mega Drive

Reconstruction de la ROM Master System fournie, puis portage de sa logique
Z80 en code natif 68000 avec SGDK. La fidélité précède les améliorations.

<!-- ROM-RELEASE:START -->
**Version courante : v0321 — 2048 Kio.**

[Télécharger la ROM v0321](versions/v0321-89c58333/gaw-megadrive-v0321.bin) · [Toutes les versions](versions/README.md)

Version de développement ; contrôles ciblés réussis, écarts visuels et validation complète encore ouverts.

SHA-256 : `89c5833351312ffaa591efb1939161910a298af06437080e2cf84fb3fb8ac86e`
Checksum Mega Drive : `CB3C`
<!-- ROM-RELEASE:END -->

Les scripts et les entrées de campagne sont disponibles dans
[le kit de tests SMS/MD](testkit/README_FR.md). Le lecteur Python/libretro
rejoint la fin sur la V321 en PAL et NTSC avec les parcours enregistrés et
la protection autorisée sur les approches, retirée avant les boss.
Le Lua BizHawk fourni est une adaptation dont le fonctionnement complet
dans BizHawk reste à vérifier. Le kit SMS couvre l’intro et permet de
suivre/enregistrer une partie ; il ne contient pas de campagne SMS complète
validée. [Résultats du kit](testkit/verification.json).

Un nouveau parcours SMS continu est en cours, avec visite des PNJ et
revisites selon les étapes des quêtes. Il a terminé le premier donjon et
validé neuf conversations dans deux villages : texte déclenché, rendu
terminé, fermeture et déplacement, puis relecture indépendante des entrées.
La protection autorisée sur certaines approches est enregistrée et retirée
avant le boss ; aucun état de quête ni sauvegarde n'est importé.
[Relevé des PNJ SMS](analysis/sms_npc_coverage_report.json).
Les 65 contextes statiques des maisons ordinaires ne constituent pas le
nombre total de PNJ ou de variantes. Marchands, donneurs de quêtes,
dialogues conditionnels et autres textes restent à couvrir. Ce parcours
partiel n'est pas encore livré dans l'archive du kit de tests.

La **V321** corrige le retard d’une image des portions de carte du titre :
cape, apparition du logo et clignotement de l’invite. Les 198 images des
33 poses de cape correspondent à la source, avec six images par pose, en
PAL et NTSC après conversion des niveaux de couleur matériels connus.
L’apparition initiale du guerrier et la durée totale du cycle sont conservées.
Le correctif natif 68000 de 60 octets conserve la disposition du jeu et
le correctif des crédits V320. Les huit parcours ciblés conservent les états
de contrôle, l’image finale, les registres PSG et l’état du lecteur sonore.
Le PCM diffère : ces tests ne certifient pas une identité audio bit à bit.
[Mesures et limites V321](analysis/title_publication_v0321_report.json).

**Graphismes et animations restent la priorité ; ils ne sont pas certifiés à
100 %.** Il reste notamment une différence de 262 pixels sur une image NTSC
pendant la première ligne du logo, des révélations partielles de scènes et
la préparation du récit suivant. Héros, transitions, PNJ, ennemis, boss et
générique nécessitent encore une couverture visuelle complète.
Les trois textes signalés aux offsets SMS `DA58`, `DA7C` et `ED3C` sont absents
des données MD ; leur déclenchement sur SMS reste à établir. Aucune condition
de dialogue n’a été inventée pour les afficher.
[Audit des textes signalés](analysis/reported_missing_texts_v0320_report.json).

Pour reconstruire la V321 depuis la V320 exacte :
`python tools/build_title_publication_overlay.py --out validation/title-build-local`.
Une V320 reconstruite peut être fournie avec `--base chemin/rom-v320.bin` ;
son SHA est vérifié avant toute modification. Le script retrouve aussi la
base dans l’historique Git si la copie locale a été nettoyée.
Les archives de passation dans `handoff` restent les instantanés **V320**
demandés ; elles ne contiennent pas ce correctif V321.

La recherche sur la première ligne du logo a ensuite mesuré les écritures
réelles SMS : un octet toutes les 32 périodes Z80. Un candidat privé réduit
l’écart NTSC de 262 à **20 pixels**, sans différence dans la plage du titre
PAL comparée. Son délai initial est encore calibré et son modèle de phase
d’interruption est incomplet : **ce candidat n’est pas publié**, la ROM
courante reste la V321. La correction finale doit aussi traiter la différence
entre les écritures SMS par octet et les écritures MD par mot.
[Mesures raster et travail restant](analysis/title_logo_raster_v0321_research_report.json).

La cause de l’échec d’un simple modèle d’attente a été identifiée : le titre
SMS active aussi une interruption horizontale à la ligne 187, avec le callback
`0280` de 691 périodes Z80. Le nouveau module natif `source_title_wait`
reproduit exactement les échéances et les états IRQ/audio de **158 attentes**
PAL/NTSC enregistrées, puis prédit le début de la première écriture du logo.
Il compile pour le 68000 et ne contient pas le délai calibré du candidat.
Il reste à le raccorder aux écritures physiques du VDP ; il n’est pas encore
sélectionné dans la ROM V321. Le modèle ordinaire `source_wait` est conservé.
[Validation du modèle d’attente avec interruption horizontale](analysis/title_hint_phase_v0321_report.json).

La V320 corrige le débordement du générique dans les 16 pixels supplémentaires
au bas de l’écran Mega Drive. Les 192 lignes SMS conservent leur image et leur
cadence. La correction est un ajout natif 68000 de 124 octets sur la V319 :
les deux entrées du générique et sa sortie partagée sont redirigées ; le reste
du binaire de jeu garde sa disposition et ses instructions.
[Validation PAL/NTSC et parcours complet](analysis/v320_credits_report.json) ·
[Comparaison visuelle](analysis/v320-credits-preview/before-after.png).

Les parcours enregistrés complets **NTSC et PAL** atteignent le retour à
l’introduction sur la V320, avec protection sur les approches retirée avant les
boss. Le retour du générique vers une nouvelle partie est également testé dans
les deux régions : progression réinitialisée, jeu contrôlable et masque retiré.
[Contrôles supplémentaires V320](analysis/v320_followup_tests_report.json).


Pour reconstruire cette correction à partir de la V319 auditée et de son code
assembleur versionné, depuis la racine du dépôt :
`python tools/build_credits_border_overlay.py --out validation/credits-build-local`.
Le dossier de sortie doit être nouveau ; SGDK est recherché dans `../../work/sgdk`.
Une compilation SGDK générale produit la base V319 ; cette étape applique ensuite
le correctif natif après vérification du SHA et des instructions remplacées.

La V319 reprend exactement le binaire testé de l’aperçu c0047. Les sources
principales intègrent maintenant l’atlas RAM des motifs d’ennemis et les
écritures directes des trois plans du héros. La préparation d’une nouvelle
pose passe de 123060 à 67942 cycles maîtres médians, soit −44,79 % pour
cette routine ; la cadence de jeu visée reste celle de la Master System.
[Mesures et captures](analysis/c0046-hero-three-plane/manifest.json).

## Espace disque et paquet de reprise V320

Le poste de travail garde seulement la dernière ROM numérotée. Les anciennes
restent dans Git ; `python tools/prune_local_roms.py --apply` retire les copies
locales inchangées, après vérification de leur présence dans Git.
Le correctif V320 récupère automatiquement sa base V319 depuis Git au besoin.

Les anciennes sorties de validation sont compactées dans le cache local ignoré
`analysis/local-validation-cache/`. Pour restaurer un fichier précis :
`python tools/restore_validation_cache.py --path validation/chemin/du/fichier`.
Les objets de compilation régénérables ne sont pas conservés. Les fixtures
actives restent déployées. [Bilan du nettoyage](analysis/output_storage_cleanup_report.json).

Les ZIP de livraison locaux sont dans `handoff/` : un paquet Windows autonome
avec SGDK/Java, et une version légère des sources pour un autre LLM. Les deux
contiennent les sources V320 ; le paquet autonome extrait a été recompilé avec
le SHA exact attendu. [Instructions](handoff/README_BUILD_FR.md) ·
[Note pour le LLM](handoff/PASSATION_LLM.md) · [Vérification](handoff/package-verification.json).
Les gros ZIP et le cache local restent hors Git.

## Vidéo complète de la V319

Une capture NTSC de **1 h 54 min 06 s**, en 720p avec son stéréo, est prête en
local : introduction/titre complets, puis parcours continu de nouvelle partie
jusqu’au générique. Protection de test uniquement sur les approches, retirée
avant les combats de boss ; aucun import de progression, vie ou sauvegarde.
[Informations et aperçu](videos/v0319/README.md).

Le MP4 volumineux reste hors Git. L’envoi vers `@KennYMcCormick-m2b` reste à
faire par l’utilisateur, en visibilité **privée**, selon son choix.
Cette capture V319 conserve le défaut de bordure du générique signalé ensuite.
[Rapport de capture](analysis/v319_gameplay_video_report.json).

## Travail natif en cours : statut vidéo des sprites

Les interruptions qui travaillent déjà sur une copie privée n’en font plus
une seconde pour pouvoir revenir en arrière : en cas d’échec, la copie privée
est simplement jetée. La routine sur RAM réelle conserve sa restauration.
Cette étape supprime un tampon de secours de 336 octets par appel concerné ;
le gain de temps mesuré reste modeste, proche de 1 %.

46000 cas compilés 68000 conservent les états et rejets attendus ; 133 cas de
trames par région retrouvent aussi les états et dates de ports SMS en simulation
native sur ordinateur. Le helper reste à **69..77 images MD en NTSC** et
**58..64 en PAL**, au-dessus du budget source. La V320 reste identique.
[Preuves et limites](analysis/v320_irq_workspace_report.json).


Les écritures de sprites des interruptions sont maintenant regroupées entre
les frontières de ligne, en conservant l’ordre des mutations observables.
Le helper composé passe de 88..96 à **70..78 images MD en NTSC**, et de
74..80 à **58..65 en PAL**, soit environ 20 % de temps en moins sur ces cas.
Il s’agit de durées de diagnostic du helper, pas de la cadence du jeu.

48300 cas sur ordinateur et **96600 cas compilés 68000** comparent le nouvel
envoi aux OUTI individuels : caches, collisions, débordements, phases de ligne,
VRAM et lecture du statut. Les vingt scènes compilées gardent leurs états
attendus. Les reconstructions de la base V319 et du correctif V320 restent
identiques aux ROMs publiées. Le budget source est encore dépassé : cette
composition reste désactivée dans la V320.
[Mesures, preuves et limites](analysis/v320_sat_runs_report.json).


Le calendrier vidéo évite maintenant de parcourir les lignes quand la liste
native de sprites est vide et que cet intervalle ne peut modifier aucun statut.
Les drapeaux déjà présents, les coordonnées de collision et le déclenchement
VINT restent identiques. Les appels qui ne franchissent aucune ligne prennent
également un chemin direct.

Sur les dix scènes mesurées, le helper composé passe de 144..162 à
**88..96 images MD en NTSC**, et de 120..136 à **74..80 en PAL**.
Ce sont des durées d’exécution du helper de diagnostic, pas la cadence du jeu.
172500 comparaisons complètes sur ordinateur et **345000 sur 68000**
retrouvent exactement le calendrier précédent. Les relectures des ports SMS
sur 14000 images par région et les scènes natives restent sans écart.
[Mesures, limites et preuves](analysis/v319_empty_sprite_clock_report.json).

Le budget source reste dépassé : cette composition n’est pas activée dans
la ROM distribuée. La reconstruction de production reste identique à la V319.
Les prochaines réductions concernent les attentes/IRQ, le calendrier avec
sprites actifs et les motifs. La livraison physique vidéo/audio, les dates IRQ
indépendantes et le démarrage continu restent à valider.

À l’étape précédente, le profil avait identifié le coût de l’effacement.
Les blocs datés ajoutés pour l’effacement et les copies
de carte avaient fait passer le helper de 316..335 à **144..162 images MD en NTSC**, et
de 265..281 à **120..136 en PAL**. L’effacement seul passe d’environ 165 à
22..24 images dans ces mesures NTSC.
[Profil par étape et équivalence vidéo](analysis/v319_map_runs_report.json).

576 cas par région MD comparent les blocs aux écritures individuelles sur
l’ensemble de la VRAM, des caches et des drapeaux, avec des sprites actifs et
les statuts effacés avant chaque séquence. Les scènes conservent leurs états
attendus. Le budget source n’est toujours pas atteint : la V319 reste inchangée.

Les motifs décompressés peuvent maintenant être livrés sous forme de blocs
datés : les dates exactes de chaque écriture restent disponibles, avec moins
d’appels. Le modèle conserve l’ordre de chaque écriture pouvant affecter les
sprites ; seules les zones sans effet sur ceux-ci sont regroupées davantage.
392832 écritures retrouvent leurs dates et octets audités ; 1728 cas par région
MD retrouvent aussi tout l’état vidéo intermédiaire et les 16 Kio de VRAM.

Le helper de scène passe de 606..711 à **316..335 images MD en NTSC**, et de
507..595 à **265..281 en PAL**, dans le même périmètre de mesure.
[Blocs datés et mesures](analysis/v319_pattern_runs_report.json).
Ce coût reste trop élevé : ce chemin expérimental reste désactivé dans la V319.

Le coût du raccordement vidéo vivant est désormais mesuré : en retirant les
comparaisons par écriture et les copies de préparation du banc, le helper
initial demandait 1406..1684 images MD dans les exécutions NTSC. Une première
optimisation des divisions/modulos le ramène à **606..711 images** (507..595
sur les exécutions PAL), soit environ **57 % de coût en moins**.
[Profil CPU et contrôles](analysis/v319_video_math_report.json).

Ce coût reste très supérieur au budget source : **ce chemin ne peut pas être
activé en l’état**. Il faut réduire le traitement par écriture en conservant
les dates et les observations vidéo. Ce gain concerne le module expérimental,
pas la cadence de la ROM V319 publiée, qui reste identique.

Les dix scènes calculent maintenant leur statut vidéo depuis le miroir natif
et l’utilisent pour piloter les interruptions. Les valeurs capturées servent
uniquement de contrôle après exécution. Le raccordement passe sur 68000 en
NTSC/PAL : **488 lectures de statut** et **80 publications vidéo d’interruption**,
avec les états RAM/audio, l’horloge et la VRAM suivie identiques.
[Scènes pilotées par le statut vivant](analysis/v319_scene_live_vdp_report.json).

Le miroir reçoit les écritures natives de motifs, carte, registres, sprites et
palette. Les états initiaux restent des instantanés de scène ; le démarrage
continu complet, les dates des sorties IRQ et le budget avec la restitution
physique image/son restent à vérifier. La ROM publiée reste V319.

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
