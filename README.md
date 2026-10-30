# Golden Axe Warrior — portage Mega Drive

Reconstruire Golden Axe Warrior à partir de la ROM Master System fournie,
puis porter sa logique Z80 en code natif 68000 avec SGDK. La fidélité à la
Master System passe avant les améliorations.

<!-- ROM-RELEASE:START -->
**Version courante : v0304 — 2048 Kio.**

[Télécharger la ROM v0304](versions/v0304-b7b4e150/gaw-megadrive-v0304.bin) · [Toutes les versions](versions/README.md)

Contrôles ciblés réussis ; portage complet encore non validé.

SHA-256 : `b7b4e15008a6f0a913c9ad43f15386abcdfbb719e5a575873d92712ba52503a8`
Checksum Mega Drive : `0558`
<!-- ROM-RELEASE:END -->

## État du portage

La **v0304 corrige le ralentissement du cycle de salve contrôlé**, en PAL et
NTSC. Le rendu conserve la limite SMS de huit sprites par ligne : détection
du débordement et masquage partagent désormais une seule passe. Une petite
routine 68000 compte les lignes disponibles ; les copies de tuiles masquées
sont regroupées et une réinitialisation d'allocateur inutilisé est supprimée.

Contrôles de cette ROM :

- 1 512 images de données d'acteurs conformes à la SMS : variantes 6A, 6B et 7C,
  252 images chacune dans les deux régions, avec horloge initiale alignée.
- Aucune image de simulation sautée sur le segment profilé de la variante 7C,
  contre 36 dans chaque région sur la v296.
- 133 120 cas de masquage comparés sur hôte ; 8 192 cas de la routine 68000
  dans chaque région ; 108 images de sprites physiques sans écart.
- Douze images de jeu naturel dont le rendu indépendant VRAM/CRAM est cohérent.
- Sept premiers cristaux et sorties rejoués depuis le démarrage. Le dernier
  retour se termine à l’extérieur en 1B, à 36/88 PV, avec navire, cloche de
  glace, bottes, corde et canoë. RAM de 64 Kio et PNG final identiques aux
  relectures. La protection de test est retirée avant chaque boss principal
  et ne reprend pas pendant son retour. Le dragon intermédiaire de D7 a été
  affronté pendant l’approche assistée. Marge de pile observée jusqu’à la
  septième sortie : 478 octets.

La mesure de pile a été corrigée : les 496 octets des anciennes synthèses
correspondaient aux points instrumentés ; le minimum avant chaque instruction
donne 478 octets sur les parcours D1 à D6. Voir
l’[erratum de mesure](analysis/stack_minimum_v0304_erratum.md).

Ces tests ne prouvent pas encore la cadence de tous les combats, le hasard
ou la phase globale. La suite de campagne, la fin, les sauvegardes et la
fidélité complète vidéo/audio restent à vérifier sur la v304.
Les commandes historiques divergent avant le premier donjon ; les sept
premiers donjons ont été repris avec une conduite adaptative sur v304.
Les six cristaux validés sur v293 restent une preuve propre à cette version.

La suite atteint le quatrième donjon : don de 50 cornes, Terre apprise,
première clé et passage du rocher vérifiés par sept relectures indépendantes.
Une autre séquence de commandes passe ensuite la salle des voleurs : canoë
acquis, téléporteur utilisé et clé de la seconde partie obtenue. Les données
du coffre et du téléporteur concordent avec les captures SMS sur le périmètre
mesuré. Le quatrième boss est vaincu et le retour sans nouvelle protection
est vérifié. Trois relectures RAM/PNG exactes couvrent le combat partiel,
la victoire et la sortie ; la marge de pile observée reste de 478 octets.
Voir les points [Terre/D4](analysis/d4_earth_v0304.md),
[canoë/D4](analysis/d4_canoe_v0304.md) et [quatrième cristal](analysis/d4_campaign_v0304.md).

La progression du cinquième donjon atteint les bottes, obtenues dans leur
coffre. Cinq nouvelles relectures RAM/PNG sont exactes jusqu’à une sortie
de ravitaillement en 49, à 50/64 PV, 22 cornes et zéro clé. Le cinquième
boss est désormais vaincu et sa sortie validée. Le déplacement avec/sans bottes concorde avec la SMS
dans 96 cas contrôlés (3 072 frames), en mode automatique et PAL.
Voir la [progression D5 et les bottes](analysis/d5_progress_v0304.md).

Le ravitaillement D5 est ensuite vérifié : deux dons de 30 cornes, une clé
achetée à 60 et le soin gratuit. Neuf relectures exactes conduisent jusqu’en
172, avant le boss, à 64/64 PV, une clé et 32 de magie. Un recalcul prématuré
dans le contrôleur de parcours est corrigé ; le programme de la ROM ne change
pas. Voir le [ravitaillement et les mécanismes D5](analysis/d5_supplies_v0304.md).

Le cinquième boss et son cristal sont obtenus, puis le héros ressort en 49
à 72/72 PV. Quatre relectures RAM/PNG couvrent le combat partiel, la victoire,
le mécanisme de sortie et le retour ; aucune nouvelle protection ne reprend
après le boss. Le contrôleur cible aussi ses satellites attaquables ;
les règles du jeu restent identiques. La marge de pile observée jusqu’à
cette sortie reste de 478 octets. Voir le [cinquième cristal](analysis/d5_campaign_v0304.md).

Le sixième donjon est parcouru jusqu’à la cloche de glace et au dernier
rocher avant le boss : seize étapes rejouées exactement, 72/72 PV et cinq
cristaux conservés. Cinq clés sont obtenues puis dépensées ; les ressources
proviennent du jeu. L’outil de Terre conserve désormais une séquence de
commandes commencée jusqu’au rééquipement, ce qui corrige deux blocages
du contrôleur dans le menu. Voir la [progression D6](analysis/d6_progress_v0304.md).

Le sixième boss est vaincu et son cristal obtenu. Trois relectures exactes
couvrent le combat partiel, la victoire et le retour en 8B à 80/80 PV.
La branche gagnante repart du segment vérifié ; l’essai perdu reste un
diagnostic distinct. Aucune aide ne reprend après le début du combat.
Voir le [sixième cristal et le retour](analysis/d6_campaign_v0304.md).

Le septième donjon est engagé après ravitaillement : deux dons de 30 cornes,
une clé achetée à 60, porte d’entrée ouverte et première clé du donjon
obtenue. Huit relectures RAM/PNG exactes conduisent en 1CB à 60/80 PV et
une clé à ce point de reprise. Voir le
[ravitaillement D7](analysis/d7_supplies_v0304.md).

Le navire de D7 est maintenant obtenu, à 80/80 PV et trois clés. Sept
nouvelles relectures exactes couvrent la seconde clé, Terre, le dragon
intermédiaire pendant l’approche assistée et la commande de 1E6 qui ouvre
la porte distante de 1D6. Quatre pièges et un ennemi restent présents
après la prise du navire ; le contrôleur valide l’objet, sans déclarer la
salle nettoyée. Voir le
[navire et les passages D7](analysis/d7_progress_v0304.md).

Le contrôleur tient désormais compte du navire : 8 192 cas de collision
comparés à l’exécution Z80. Trois relectures exactes reprennent la route
vers le boss, avec le bloc de Terre en 1A8 et l’approche des ennemis cachés.
Le point de reprise en 189 conserve 80/80 PV et deux clés. Voir l’[approche D7](analysis/d7_navigation_v0304.md).

Le septième boss est ensuite vaincu avec les dégâts ordinaires : le héros
descend à 42 PV avant que le cristal ne porte sa capacité et sa vie à 88.
Le retour utilise Terre pour dégager le téléporteur de 1B7, puis atteint
l’extérieur à 36/88 PV et deux clés. Quatre nouvelles relectures sont exactes,
et la mesure de pile avant chaque instruction conserve 478 octets de marge.
Voir le [septième cristal et le retour](analysis/d7_campaign_v0304.md).

L’entrée du huitième donjon est atteinte : escalier dégagé à la hache en
3C, passage payé dix cornes vers la côte de 1A, puis traversée en navire
jusqu’à 1EA. Trois relectures RAM/PNG exactes conservent les sept cristaux,
le navire et deux clés. Le contrôleur sait entrer dans cet escalier depuis
le haut. Le huitième boss reste à atteindre ; voir l’[entrée D8](analysis/d8_entry_v0304.md).

Le parcours de D8 atteint ensuite sa partie ouest et active les deux
mécanismes distants : transformation de 1C8, puis ouverture de la sortie
ouest de 1EB. Trois autres relectures sont exactes ; le héros revient en
1EB à 40/88 PV et deux clés. Le combat intermédiaire contre le type 7A
reste une approche assistée. Voir les [passages de D8](analysis/d8_passages_v0304.md).

Voir le [bilan v0304](analysis/burst_cadence_v0304.md),
les [sept cristaux vérifiés](analysis/d7_campaign_v0304_report.json) et
l'[historique conservé du README](analysis/readme_history_through_v0296.md).
Les v297/v298 sont des essais écartés ; v299 à v303 sont des étapes
intermédiaires conservées. La version courante à tester est **v304**.

## Fichiers utiles

- [Sources 68000/SGDK](megadrive/src/main.c) et [moteur des acteurs](megadrive/src/actors.c).
- [Journal des ROMs numérotées](versions/README.md) et [index des versions](versions/index.json).
- [Corrections v0180](analysis/reveal_wait_milestone.md).
- [Correction audio v0181](analysis/raw_note_duration_milestone.md).
- [Correction du partage audio v0182](analysis/audio_ownership_milestone.md).
- [Correction du silence du bruit emprunté v0183](analysis/noise_note_milestone.md).
- [Mesures des interruptions audio](analysis/audio_irq_milestone.md).
- [Calcul du traitement des musiques et bruitages](analysis/audio_dispatch_milestone.md).
- [Calcul des enveloppes de volume](analysis/audio_envelope_milestone.md).
- [Calcul de la hauteur des notes et du vibrato](analysis/audio_pitch_milestone.md).
- [Calcul des notes et du contrôle des séquences](analysis/audio_note_sequence_milestone.md).
- [Calcul du canal de bruit](analysis/audio_noise_channel_milestone.md).
- [Calcul des canaux de tonalité](analysis/audio_tone_channel_milestone.md).
- [Composition du lecteur audio](analysis/audio_reader_milestone.md).
- [Attentes VBlank et budget de chargement](analysis/save_wait_milestone.md).
- [Interruptions vidéo et budget conditionnel complet](analysis/full_irq_milestone.md).
- [Phase vidéo et prédiction des boucles de palette](analysis/irq_raster_milestone.md).
- [Prédiction des attentes VBlank](analysis/wait_raster_milestone.md).
- [Prédiction de la révélation depuis un seul état](analysis/reveal_phase_milestone.md).
- [Phase du début de chargement graphique](analysis/graphics_prefix_phase_milestone.md).
- [Phase de la routine graphique complète](analysis/graphics_load_phase_milestone.md).
- [Phase graphique et chargement de carte](analysis/world_map_phase_milestone.md).
- [Phase graphique, carte, HUD et attente vidéo](analysis/map_hud_phase_milestone.md).
- [Sortie du hasard original et registre R](analysis/rng_refresh_milestone.md).
- [Lectures d’opcodes des préfixes audio](analysis/audio_prefix_refresh_milestone.md).
- [Lectures d’opcodes du dispatch et des effets prioritaires](analysis/audio_control_refresh_milestone.md).
- [Lectures d’opcodes des enveloppes audio](analysis/audio_envelope_refresh_milestone.md).
- [Lectures d’opcodes des hauteurs et du vibrato](analysis/audio_pitch_refresh_milestone.md).
- [Lectures d’opcodes des notes et commandes de séquence](analysis/audio_note_sequence_refresh_milestone.md).
- [Composition des lectures d’opcodes des canaux de tonalité](analysis/audio_tone_channel_refresh_milestone.md).
- [Composition des lectures d’opcodes du canal de bruit](analysis/audio_noise_channel_refresh_milestone.md).
- [Composition des lectures d’opcodes du lecteur audio complet](analysis/audio_reader_refresh_milestone.md).
- [Lectures d’opcodes du vecteur et des interruptions audio seules](analysis/audio_irq_refresh_milestone.md).
- [Travail restant et notes techniques](analysis/world_next.md).
- [Ancien README conservé comme historique](analysis/README_historique_avant_v0180.md).

`gaw-megadrive.bin` est le binaire courant. `gaw-title-megadrive.bin` est
un alias du même binaire pour les anciens liens. Les anciennes ROMs
numérotées sont conservées sans écrasement dans `versions/`.

## Compilation et Git

Depuis ce dossier, dans PowerShell :

```powershell
.\build.ps1
python tools/verify_git_roms.py
```

La compilation utilise SGDK et Java ; leurs chemins peuvent être fournis
avec les paramètres `-Sgdk` et `-Java` de [build.ps1](build.ps1).
Chaque nouveau binaire reçoit un numéro de version. La version et le lien
affichés en tête de ce README sont actualisés par `tools/version_rom.py`.

Git conserve les sources, outils, rapports principaux et ROMs numérotées.
Les captures et fichiers temporaires volumineux restent disponibles localement.
Le dépôt distant est [spamkenny02-commits/goldenaxe](https://github.com/spamkenny02-commits/goldenaxe).
Les livraisons demandées sont publiées sur sa branche `main`, avec les ROMs
numérotées et ce README. Les captures volumineuses archivées restent locales.

- [Lectures d’opcodes des interruptions vidéo complètes](analysis/full_irq_refresh_milestone.md).

- [Registre R pendant le chargement des motifs](analysis/graphics_prefix_refresh_milestone.md).

- [Registre R sur la routine graphique complète](analysis/graphics_load_refresh_milestone.md).

- [Registre R jusqu’au chargement de la carte](analysis/world_map_refresh_milestone.md).

- [Registre R pendant les attentes VBlank](analysis/wait_refresh_milestone.md).

- [Registre R jusqu’à la sortie du HUD](analysis/map_hud_refresh_milestone.md).

- [Tirages de l’historique depuis le début du chargement](analysis/history_refresh_phase_milestone.md).

- [Initialisation des acteurs et registre R](analysis/actor_prefix_refresh_milestone.md).

- [Graphismes des acteurs et registre R](analysis/actor_graphics_refresh_milestone.md).

- [Phases et registre R de l’initialisation du héros](analysis/hero_refresh_phase_milestone.md).

- [Chargement raccordé jusqu’au héros](analysis/loader_hero_refresh_milestone.md).

- [Chargement jusqu’à la réactivation de l’écran](analysis/loader_tail_refresh_milestone.md).

- [Routines aléatoires traduites en C 68000](analysis/native_source_rng_milestone.md).

- [Horloge d’instructions en C 68000](analysis/native_source_clock_milestone.md).
