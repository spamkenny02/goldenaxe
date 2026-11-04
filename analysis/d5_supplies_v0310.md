# v0310 : ravitaillement et mécanisme avant le cinquième boss

Le [bilan vérifié](d5_supplies_v0310_report.json) poursuit la sortie après
[les bottes](d5_progress_v0310.md), sans changement de ROM.

| Étape | Image finale | Résultat |
| --- | ---: | --- |
| Don A1 | 126433 | 19 → 49 cornes |
| Don B4 | 127873 | 49 → 79 cornes |
| Achat et soin en 94 | 129247 | Une clé à 60 ; 19 cornes ; 56 → 64 PV |
| Retour dans D5 | 132028 | Salle 186, clé conservée |
| Terre et portail | 140118 | Rocher 44 de 153 ouvert ; arrivée en 162 |
| Mécanisme et passage | 141133 | Haut à 72,40 ; traversée vers 172 |

Le second passage Terre consomme huit PM, de 64 à 56. Le mécanisme s'active
alors que les ennemis sont encore présents. Le héros atteint 172 à 64/64 PV,
avec une clé, 20 cornes, bottes, épée longue, Feu, Terre, canoë et corde ; la
hache reste sélectionnée. Les quatre cristaux sont conservés.

Le premier pilote `warp01` épuise ses trois réentrées autorisées sans franchir
le tronçon. `warp02` repart du préfixe canonique, autorise jusqu'à douze
réentrées et en utilise huit, sans modifier la ROM ni les acteurs. La révision
de l'auditeur conserve l'index et le script initiaux dans les sources figées ;
le rapport final utilise `supplies2_source_index.json` et le tronçon réellement
réussi. Cet arrêt du pilote n'établit pas un bug natif.

Les treize étapes depuis l'entrée initiale de D5 ont une relecture fixe depuis
le démarrage : RAM complète de 65 536 octets et PNG final identiques. Les seules
écritures de test restent les protections d'approche déclarées. Aucun argent,
objet, soin, acteur, progression, SRAM ou état principal n'est importé.
Le cinquième boss et son cristal ne sont pas validés par ce rapport ; la suite
de la campagne et la fidélité globale restent ouvertes.
