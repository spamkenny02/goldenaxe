# v317 — Feu, épée longue, bottes et cinquième cristal

Le même binaire publié `7694654ec85dd6626c0e17ff1834e5893d4eb35481400a4725eac6b6f3503294`
est vérifié depuis le retour du quatrième donjon jusqu'au cinquième cristal
et à la sortie extérieure 49. La ROM et les sources du jeu restent celles de
v317 ; cette étape prolonge les preuves de progression.

| Étape | Image finale du parcours | Résultat |
| --- | ---: | --- |
| Feu, épée longue et entrée D5 | 101806 | Huile échangée, Feu niveau 1, magie maximale 72, épée niveau 2 |
| Bottes, ravitaillement et mécanisme | 124747 | Bottes reçues, deux cadeaux de 30 pièces, clé achetée à 60, soin de 42 à 64 PV |
| Cinquième boss et récompense | 129416 | Huit satellites observés, cœur à 72 PV vaincu, cinquième cristal, 72/72 PV |
| Retour extérieur | 130535 | Mécanisme de retour, sortie 49, 72/72 PV |

Les cadeaux, achats, sorts, mécanismes et récompenses sont exécutés avec les
commandes ordinaires. L'or, les PV, la magie, les objets, la progression, la
SRAM et les états primaires ne sont pas importés. Les écritures de protection
autorisées pour l'approche restent déclarées dans les enregistrements.

La protection est retirée à l'image 126804, dans la salle 173. Le boss 65 est
observé en combat à 126892 avec 64 PV pour le héros et une protection nulle.
Le héros perd effectivement 30 PV pendant le combat, puis la récompense
normale termine à 72/72. Aucun ajout d'aide n'a lieu pendant le boss ou le
retour. Le contrôleur inclut les satellites dans ses cibles et termine
l'arrivée physique avant les esquives ; il ne modifie pas les acteurs ou le
programme. Les 56 fenêtres de prédiction du boss et les quatre du retour
correspondent à la RAM persistante du jeu principal. Les points de contrôle
sont ensuite reproduits avec des commandes fixes et comparés sur la RAM
complète de 65536 octets et le PNG final.

Les 25 nouveaux points utilisent trois lecteurs démarrés à froid, partagés
entre points croissants : 357088 images sont émises au lieu des 2762605
nécessaires avec un redémarrage indépendant à chaque point. Les 2405517
répétitions de préfixe évitées concernent uniquement les lecteurs de preuve,
pas le temps total de développement. Avec les étapes précédentes, 72 points
sélectionnés sont vérifiés sur ce binaire. Le parcours retenu ne comporte
aucune mort.

Le HUD physique est contrôlé après les récompenses et les cinq marqueurs de
cristal sont comparés à la ROM source. Ces vérifications ne couvrent pas
chaque framebuffer ou chaque son. Les donjons suivants, le palais, la fin sur
v317, les contenus optionnels, une campagne PAL complète et la fidélité
globale au RNG/raster/audio de la SMS restent ouverts.

- [Huile, Feu, épée et entrée D5](fire_sword_v0317_report.json)
- [Bottes et sortie de ravitaillement](d5_progress_v0317_report.json)
- [Ravitaillement et mécanisme](d5_supplies_v0317_report.json)
- [Cinquième cristal et retour](d5_campaign_v0317_report.json)
- [Reproductions partagées](campaign_d5_stream_v0317_report.json)
- [Captures et sources conservées](campaign-d5-v0317/manifest.json)
- [Nettoyage vérifié](campaign_d5_v0317_cleanup_report.json)
