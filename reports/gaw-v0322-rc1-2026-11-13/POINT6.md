# Point 6 — parcours retenu et vidéos livrés

La V322 devient RC1 pour essais externes sur le parcours sélectionné. Le binaire
reste identique : SHA-256 `1421abe47de95ac104a03e2fb1be7001f70aeca1fbb6a9b35669aa6e98b7d9a4`, 2048 Kio, checksum ECB3.
Le statut RC qualifie les preuves ci-dessous ; il ne certifie pas une fidélité
globale 100 % ni l'absence de tout bogue.

## Parcours effectivement rejoués

- Campagnes MD NTSC et PAL depuis Nouvelle partie jusqu'à la fin et au générique :
  neuf cristaux, Hache d'or, Death Adder, zéro mort et zéro protection pendant
  le combat des boss. La protection autorisée des approches reste déclarée.
- Les 145 objectifs de service/équipement retenus sur SMS ont un résultat MD joué,
  un rejeu indépendant et une vidéo décodée. Les valeurs de progression, de vie,
  de magie et d'argent ne sont pas forcément identiques entre les deux parcours.
- 65 conversations ordinaires connues dans 41 maisons ; 48 refus de service ; 31
  maisons d'argent avec retour sans seconde récompense ; 11 lieux de soin ; 14
  lieux de sauvegarde avec véritable Continuer ; six directions de transport,
  leurs refus et retours ; quatre hôtes de jeu avec gains, pertes, carte chanceuse
  et malchanceuse ; équipements, cheminées, prérequis, indices et corrosion/remède.
- Enseignements 2/2/2/1, capacités 128/128, huit contextes de fées et les retours
  retenus chez les enseignants et fées. Les récompenses sont obtenues dans le jeu.
- Trois emplacements réellement écrits et rechargés, avec écrasement au lieu 2E.
  La limite de 99 clés utilise une branche monétaire assistée clairement annoncée,
  sans injection d'objet, de vie ni de quête. Les autres achats retenus utilisent
  l'argent réellement obtenu.

## Vidéos locales et chapitres

- MD NTSC : `gaw-md-campagne-et-annexes.mp4` — 3 h 22 min 25 s,
  329 annexes annoncées ; SHA-256 `45cae59fc5ff682d970d818fca145851655ce0ce81a7fe67ef7450f7b4e8b290`.
  Dossier : `videos/md/parcours-et-annexes-2026-11-13/`.
- SMS : `gaw-sms-campagne-et-annexes.mp4` — 4 h 26 min 57 s,
  campagne et annexes retenues ; SHA-256 `baf2a1655cacdb1c1cd7317b3139432bf3a87047c21d9b505760735bcf43ba6e`.
  Dossier : `videos/sms/parcours-et-annexes-2026-11-12/`.

Chaque dossier contient `LISEZ-MOI-ET-CHAPITRES.txt`. Les vidéos restent locales,
prêtes pour l'envoi manuel demandé. Les MP4 ne sont pas intégrés à Git.
Les annexes sont des branches distinctes : elles ne sont pas présentées comme
une unique partie continue. Décodage intégral audio/vidéo, nombre d'images,
synchronisation et pixels des frontières de chaque segment vérifiés.

## Portée et limites conservées

Le registre technique conserve 409 enregistrements SMS : il contient des étapes
intermédiaires de contrôleur, des alias et des sous-parcours. Il n'est ni un
compteur de PNJ, ni une liste de 409 objectifs de jeu indépendants. Le nouveau
rapprochement vérifie les 145 objectifs sélectionnés avec des prédicats explicites,
plus les cohortes connues. Il ne transforme pas les étapes techniques non
appariées en preuves réussies. Les écarts de précondition sont indiqués dans
le rapport, notamment le soin testé à vie pleine dans certains lieux, complété
par des soins payants réels sur héros blessé.

Les textes SMS 0xDA58/0xDA7C/0xED3C restent sans déclenchement légitime démontré :
ils ne sont pas déclarés inutilisés. Deux entrées de la table monétaire n'ont
pas d'accès démontré. Le texte de Saylun avec pomme possédée correspond au texte
SMS complet au retour du formateur ; l'attente finale SMS duplique ensuite un
suffixe et son image finale ne correspond pas à l'image MD.
Des différences de raster/fondu du titre demeurent. Les preuves PAL/NTSC
complètes concernent MD ; la vidéo SMS retenue est NTSC. Aucun parcours sur
console physique ou BizHawk ne fait partie de cette qualification, et aucun
test n'affirme des formes d'onde PCM identiques ou une couverture exhaustive
de toutes les permutations de monstres, PNJ et quêtes.

## Preuves reproductibles

- [Publication RC](../../analysis/rc1_release_report.json)
- [145 objectifs et différences de contexte](../../analysis/md_selected_gameplay_goal_closure.json)
- [Registre technique inchangé](../../analysis/md_annex_replay_coverage.json)
- [Collection des extraits MD](../../analysis/md_selected_proof_video_collection.json)
- [Montage MD](../../analysis/md_proof_montage_report.json)
- [Pixels des frontières MD](../../analysis/md_montage_boundary_pixels_report.json)
- [Montage SMS](../../analysis/sms_proof_montage_report.json)
- [ROM V322](../../versions/v0322-1421abe4/gaw-megadrive-v0322.bin)

Les scripts `reconcile_md_selected_goals.py`, `collect_md_proof_videos.py`,
`build_md_proof_montage.py`, `verify_md_montage_boundaries.py` et
`finalize_rc_release.py` échouent si une preuve exigée manque.
