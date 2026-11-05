# Audit de livraison — v314

État de travail du 5 novembre 2026. Cet audit ne déclare pas le portage terminé.
ROM : `c53381c459a1e6254a8c9f1cfad1b8cda482cc0614697ad566133b28335e07a7`.
Échéance demandée : 6 novembre au soir. La priorité reste une version fidèle.

## Exigences et preuves disponibles

| Exigence | Preuve actuelle | Conclusion et travail restant |
|---|---|---|
| Traduction SMS vers 68000, SGDK autorisé | `analysis/bank_00.asm` à `bank_0f.asm`, sources `megadrive/src`, `build.ps1`, ROM numérotée v314 | Reconstruction et port natif présents. Le lecteur de musique s'exécute aussi en 68000 ; lire les données originales ne constitue pas une émulation du CPU Z80. La couverture fonctionnelle complète reste à établir. |
| Séquence avant le titre, guerrier, cape, logo | `intro_audio_integration_v0314_report.json`, `intro_audio_candidate11_v0313_report.json` ; candidat et production identiques | Comparaisons PAL/NTSC ciblées : 12 959 états audio IRQ, 40 images normalisées du titre. Ne prouve pas toutes les images transitoires ni le cycle matériel global. |
| Musique Nouveau Jeu/Continuer, choix sonores | `start_menu_candidate11_v0313_report.json`, référencé par l'intégration v314 | Musique, curseur et confirmation comparés à la source dans les deux régions sur le même binaire. |
| Entrée/sortie du menu et décor après retour chez les marchands | `inventory_candidate11_v0313_report.json`, référencé par l'intégration v314 | Six parcours naturels, extérieur et deux premières boutiques, PAL/NTSC. Fenêtres noires, restauration et fermeture silencieuse vérifiées ; ne couvre pas chaque pièce du jeu. |
| Transition marchande fluide | `merchant_v0312_report.json`, code actuel `merchant.inc` | Portrait et fenêtre noire comparés ; le panneau complet avait encore une image de retard en PAL. Ce rapport reste lié à v312 : Mesure v314 actuelle : PAL+1 et NTSC−1. Le candidat03 corrige les deux, avec43 transactions et intro/audio conservés ; intégration après clôture des tests actifs. |
| Vitesse du héros | `terrain_walk_v0314_game_report.json` | 96 cas, 3 072 états source/MD identiques pour terrain, bottes et direction. Carte/acteurs préparés ; charge complète de combat exclue. |
| Vitesse des monstres | Routines et validations individuelles des acteurs ; campagne courante | Le déplacement du héros ne prouve pas celui de tous les monstres. Consolider les comparaisons source par famille et distinguer logique de mouvement, calendrier des images et aléatoire. |
| Anciens monstres/objets pendant le scrolling | `scroll_objects_v0314_report.json` | Huit cas direction/région, tables matérielles des sprites contrôlées, persistance et reprise conservées. La disparition est vérifiée ; la durée exacte du scrolling et chaque pixel du décor ne le sont pas par ce test. |
| Flash d'ancienne carte d'une image | `scroll_publish_v0314_report.json` | Dix fins de scroll naturelles PAL/NTSC, fond stable sur trois images après publication hors rectangles des sprites. Contrôle actuel sans comparaison héritée à v202 ; cadence source et autres transitions non prouvées. |
| Musiques et bruitages du jeu | Lecteur natif `sound.inc`, validations individuelles du lecteur et de ses enveloppes ; erreurs audio nulles aux points de campagne retenus | Une erreur nulle ne prouve pas que chaque effet a été déclenché ni que chaque événement sonore est à l'instant source. Consolider la couverture des commandes et des scènes ; ne pas déclarer tous les sons identiques à partir du seul test d'intro. |
| Jeu complet, objets et boss | Rapports v314 D1 à D9, Ballon, porte du palais, premier géant et mécanismes intérieurs | Neuf cristaux et retour extérieur vérifiés. Gardien 11E vaincu à362186, 405 prédictions exactes, trois coups de24 PV ; Hache d'or, Death Adder et générique complet vérifiés : `cold_palace_final_v0314_report.json`, fin404608. Sauvegarde à neuf cristaux en cours. Les gardes d'approche sont retirées avant les boss. Aucun objet, santé ou progression importé. Une mort normale puis Continuer fait partie du parcours. |
| Sauvegarde et Continuer | `game_written_save_v0314_report.json`, `save_compatibility_candidate11_v0313_report.json` | Écriture réelle au premier cristal et reprise prouvées ; ancienne sauvegarde à neuf cristaux compatible PAL/NTSC. L'écriture réelle à neuf cristaux sur v314 reste à terminer. |
| ROMs numérotées, README et Git main | `versions/index.json`, `versions/README.md`, ROM v314 et rapports joints ; commits sur `main` | Numérotation conservée. Un nouveau numéro exige un nouveau binaire, pas uniquement de nouveaux tests. Publier les prochaines étapes et actualiser la description courante. |
| Nettoyage sans perte | Rapports `closed_capture_cleanup_v0314` et `failed_d9_toll_cleanup_v0314`, archives et manifestes | Captures closes archivées, hachées et relues avant suppression. ROMs numérotées, original et sources préservés. Ne pas supprimer les fichiers utilisés par les tests actifs. |

## Limites de fidélité à traiter explicitement

- Le fournisseur de rafraîchissement dans `actors.c` utilise encore l'aléatoire
  SGDK sur sept bits. La récurrence de graine source est traduite ; le flux R
  issu des instructions/interruptions SMS n'est pas reproduit par ce fournisseur.
  Ne pas confondre ces deux affirmations ni promettre des trajectoires identiques.
- Les cas de pool de projectiles plein et IY ont des observations source bornées
  (`iy_item_context_target_v0314_report.json`). Elles ne démontrent ni un défaut
  naturellement atteint ni un invariant universel. Aucun correctif de production
  n'est justifié uniquement par ces observations.
- Un rejeu de la même ROM en RAM/image exactes prouve la reproductibilité du
  parcours et ses contraintes d'aide. Il ne remplace pas une comparaison avec la
  Master System pour le rendu, l'audio ou la cadence.
- Les tests émulés ne constituent pas une validation sur Mega Drive physique.

La victoire, le générique et la reprise de sauvegarde doivent être vérifiés sur
la v314 avant de qualifier cette ROM de candidate complète. La fidélité finale
demande aussi de résoudre ou de caractériser les écarts concrets ci-dessus.
