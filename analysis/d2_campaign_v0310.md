# v0310 : deuxième cristal et retour vérifiés

Le [bilan lié aux captures](d2_campaign_v0310_report.json) poursuit la même
partie démarrée depuis Nouveau Jeu : premier cristal, [hache et fée de vie](d2_approach_v0310.md),
clés D2, boss en 144, deuxième cristal, puis retour en D6 à **31/48 PV**.
La hache reste équipée et les deux cristaux sont conservés.

| Étape | Image finale | Résultat |
| --- | --- | --- |
| Clé en 160 | 27110 | 40 PV, une clé |
| Clé en 152 | 28562 | 40 PV, deux clés |
| Clé en 131 | 32362 | 40 PV, deux clés après ouverture du passage |
| Boss et cristal | 42327 | 48/48 PV, second cristal |
| Sortie en D6 | 44790 | 31/48 PV, deux cristaux, une clé |

La dernière écriture de protection est un zéro à **33960**. Le combat commence
à **34017**, avec 40 PV et compteur de blessures nul. Le boss réellement
observé est **type63, 30 PV**, et non le type65 à satellites. Un coup ordinaire
retire 16 PV au héros à 41640, de 40 à 24. Le cristal donne ensuite son soin
normal à 48/48 PV. Aucun garde ne reprend pendant le combat ni le retour.

Les 479 fenêtres de prédiction du combat et les 15 du retour correspondent à
la RAM principale. Les cinq étapes ont chacune une relecture froide par
commandes fixes, sans lecture de retour du contrôleur : RAM complète de
65 536 octets et PNG final exacts. Les 128 mots physiques du HUD et les deux
marqueurs de cristal sont vérifiés après acquisition et après sortie. Les
deux images finales ont été inspectées.

L'approche est assistée par les seules écritures de compteur de blessures
consignées. Aucun PV, argent, objet, clé, acteur ou progression n'est injecté ;
aucun import SRAM ou état dans le jeu principal. Les instantanés de recherche
restent limités au cœur secondaire. Le retour n'ajoute aucune écriture d'aide.

Le premier essai de clé D2 visait par erreur la salle 151, qui ne contenait
pas la clé demandée : il finit bloqué dans le pilote, sans mort. Il est conservé
comme diagnostic et exclu de ce bilan. Les points promus utilisent 160, 152
et 131. Le boss est terminé dans l'essai borné initial, sans reprise de combat.

ROM inchangée : v310 `32fe75a6…`, 2 Mio. Il n'y a donc pas de nouveau numéro.
Ce parcours NTSC ne prouve pas toute la campagne v310, les probabilités ou la
phase R/IRQ exactes de la SMS, tous les pixels/audio ou le matériel. La campagne
complète v309 reste historique ; le vrai combat du type65 doit être distingué
des tests contrôlés de sa branche déjà réalisés.
