# v0310 : sixième cristal et retour extérieur

Le [bilan vérifié](d6_campaign_v0310_report.json) poursuit la préparation de D6,
depuis la même partie démarrée à froid. La ROM v310 reste inchangée.

| Étape | Image finale | Salle | PV | PM |
| --- | ---: | --- | ---: | ---: |
| Protection retirée | 175543 | 125 | 72/72 | 40 |
| Sixième cristal, récompense terminée | 185904 | 115 | 80/80 | 72 |
| Retour extérieur | 190773 | 8B | 2/80 | 72 |

Le combat contre le boss original **64 à 60 PV** commence à 175645 avec
72 PV et compteur de blessures nul. Un coup à 185239 retire quatorze PV,
de 72 à 58. Le cristal donne ensuite son soin normal à 80 PV et restaure
la magie. La dernière écriture de protection est 175543 ; aucune nouvelle
aide pendant le combat ou le retour.

Trois conduites ordinaires ont été essayées. `boss01`, avec décisions espacées
de 32 images, atteint sa limite sans infliger de dégâts. `boss03`, à 16 images,
s'arrête avec le boss encore à 24 PV. `boss02`, à huit images, remporte le combat.
Les deux essais incomplets ne sont pas comptés comme des victoires. Le fichier
`selected_boss_trial.json` lie explicitement l'audit à l'empreinte du rapport
réussi ; les sources initiales restent conservées.

Le retour traverse 125, 124, 123, 113, 114, 138, 169, 168, 178, 177 et 187,
puis ressort en 8B. Le héros perd beaucoup de vie sur ce trajet et termine
vivant à **2/80 PV**, avec deux clés, la cloche de glace, Feu, Terre, épée longue,
bottes, canoë et corde. La hache reste sélectionnée. Un soin normal est donc
prioritaire pour la suite ; aucun PV n'a été ajouté par le test.

Les trois étapes ont une relecture fixe depuis le démarrage : 65 536 octets
de RAM et PNG final identiques. Les 1 202 fenêtres de prédiction du combat
et les 121 du retour correspondent à toute la RAM, sans différence de pile
réservée. Le HUD physique de 128 mots et les six marqueurs de cristal sont
vérifiés après récompense et après sortie ; les deux images ont été inspectées.

Les seules écritures de test restent les protections d'approche déclarées.
Aucun objet, ressource, acteur, progression, SRAM ou état principal n'est
importé. Six cristaux sont couverts sur ce parcours NTSC v310 ; la suite
de la campagne, les contenus optionnels et la fidélité globale R/IRQ,
temporelle, audiovisuelle et matérielle restent ouverts.
