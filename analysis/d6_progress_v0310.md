# v0310 : clés, Terre et cloche de glace avant D6

Le [bilan vérifié](d6_progress_v0310_report.json) poursuit la même partie après
le cinquième cristal, sur la ROM v310 inchangée.

| Étape | Image finale | Salle | PV | Clés | PM |
| --- | ---: | --- | ---: | ---: | ---: |
| Hache sélectionnée par le menu | 148007 | Extérieur 49 | 72/72 | 0 | 72 |
| Entrée D6 avec pont débloqué | 149512 | 187 | 72/72 | 0 | 72 |
| Première clé | 152321 | 168 | 72/72 | 1 | 72 |
| Deuxième acquisition ciblée | 154995 | 148 | 68/72 | 2 | 72 |
| Troisième acquisition ciblée | 158263 | 146 | 64/72 | 3 | 72 |
| Quatrième acquisition ciblée | 165047 | 116 | 64/72 | 3 | 72 |
| Cinquième acquisition ciblée | 170857 | 113 | 72/72 | 5 | 48 |
| Cloche et récompense terminée | 173439 | 112 | 72/72 | 3 | 48 |
| Dernier rocher dégagé | 175542 | 125 | 72/72 | 2 | 40 |

Les portes consomment normalement les clés. Une clé supplémentaire est ramassée
en quittant 116. Les ramassages du jeu restaurent aussi des PV et PM. Les six
ouvertures avec Terre utilisent sept lancers, chacun avec un décrément de huit PM.
La cloche passe réellement de 0 à 1 ; la hache reste sélectionnée, avec 30 cornes,
Feu, Terre, épée longue, bottes, canoë, corde et cinq cristaux conservés.

Le trajet utilise la sortie ouverte de 137 puis une réentrée ordinaire dans cette
salle lors du passage vers le mécanisme de 117. Aucun acteur ni élément de carte
n'est remplacé. Le rocher 7B de 125 est dégagé sans entrer dans le boss de 115.

Un arrêt du pilote `earth126-01` révèle une commande manquante : sa séquence Terre
attendait pendant la saisie du héros par un voleur. Le pilote envoie maintenant
les changements de direction prévus par le jeu pour se libérer. Sur `earth126-02`,
le héros est observé saisi à 165300 ; Terre ouvre le rocher à 165317, après la
libération. La ROM n'a pas changé. Les anciennes sources et recettes sont
conservées ; `earth_grab_revision.json` et `executed_recipes_r02.json` lient les
révisions effectivement utilisées dans `validation/v0310-d6-sources`.

Les dix-sept étapes ont une relecture fixe depuis le démarrage : 65 536 octets
de RAM et PNG final identiques. Les 128 mots du HUD physique après la cloche sont
vérifiés et son image finale a été inspectée. L'audit distingue le premier passage
Terre utilisant l'ancien pilote des suivants utilisant sa correction.

Les seules écritures de test restent les protections d'approche déclarées sur
le compteur de blessures. Aucun objet, ressource, acteur, progression, SRAM ou
état principal n'est importé. Ce rapport s'arrête avant le sixième boss ; sa
victoire, la suite de la campagne et la fidélité globale restent ouvertes.
