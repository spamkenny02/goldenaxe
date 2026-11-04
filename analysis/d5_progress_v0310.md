# v0310 : première clé de D5, Terre et bottes

Le [bilan vérifié](d5_progress_v0310_report.json) poursuit l'entrée D5 après
[Feu et l'épée longue](fire_sword_v0310.md), sur la même ROM v310.

| Étape | Image finale | Salle | PV | PM | Clés |
| --- | ---: | --- | ---: | ---: | ---: |
| Première clé | 119290 | 176 | 62/64 | 72 | 1 |
| Passage Terre | 119735 | 166 | 62/64 | 64 | 1 |
| Bottes et récompense terminée | 122822 | 157 | 56/64 | 64 | 0 |
| Sortie pour ravitaillement | 123488 | Extérieur 49 | 56/64 | 64 | 0 |

Terre détruit le rocher 4A de 176, pour huit PM. Le jeu dépense la clé sur
le trajet ; les bottes passent réellement de 0 à 1 et `hero_attack_speed`
est actif. Feu, Terre, épée longue niveau 2, canoë, corde et quatre cristaux
sont conservés. La hache reste sélectionnée, avec 19 cornes à la sortie.

Les quatre étapes sont relues depuis le démarrage, par commandes fixes,
avec 65 536 octets de RAM et PNG final identiques. Les 128 mots du HUD physique
sont vérifiés après les bottes et la sortie ; l'image après les bottes a été
inspectée. Les sources sont figées avec `progress_source_index.json` dans
`validation/v0310-d5-sources`, sans remplacer l'index de préparation.

La protection autorisée reste limitée à l'approche, avec les dégâts normaux
du terrain possibles. Aucun objet, ressource, acteur, progression, SRAM ou
état principal n'est importé. Cette sortie de ravitaillement ne termine pas
D5 : le cinquième boss n'est pas entré et son cristal reste absent.
