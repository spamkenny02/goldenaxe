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
- Premier cristal et sortie du premier donjon rejoués depuis le démarrage :
  retour en B9 à 28/32 PV. RAM de 64 Kio et PNG final identiques aux relectures.
  La protection de test est retirée 72 images avant le boss et ne reprend pas
  au retour. Marge de pile observée jusqu'à cette sortie : 496 octets.

Ces tests ne prouvent pas encore la cadence de tous les combats, le hasard
ou la phase globale. La suite de campagne, la fin, les sauvegardes et la
fidélité complète vidéo/audio restent à vérifier sur la v304.
Les commandes historiques divergent avant le premier donjon ; le parcours
ci-dessus a été repris avec une conduite adaptative. Les deux cristaux et
la corde validés sur v296, ainsi que les six cristaux sur v293, restent des
preuves propres à ces versions.

Voir le [bilan v0304](analysis/burst_cadence_v0304.md),
le [rapport vérifié](analysis/burst_cadence_v0304_report.json) et
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
