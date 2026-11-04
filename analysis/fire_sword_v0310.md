# v0310 : Feu, épée longue et entrée du cinquième donjon

Le [bilan vérifié](fire_sword_v0310_report.json) poursuit la même partie depuis
la sortie de D4. La ROM reste v310, SHA-256
`32fe75a653d7152f7cbf873a32f2ffef14234ea190885ae8a8235f2ccd10e071`.

| Étape | Image finale | Résultat |
| --- | ---: | --- |
| Entrée chez le maître du Feu | 108364 | Maison BF de E6 |
| Présentation et sortie | 108915 | Huile conservée, Feu absent |
| Seconde entrée | 109123 | Maison BF |
| Échange et sortie | 109796 | Feu 1, huile consommée, magie 72/72 |
| Entrée chez le donateur | 112806 | Maison 4F de 50 |
| Épée longue et sortie | 113309 | Niveau 1 vers 2, récompense terminée |
| Entrée D5 | 117807 | Salle 186, 62/64 PV, 72/72 PM |

Les deux services utilisent les dialogues normaux et conservent les 19 cornes.
Le don d'épée pose le drapeau de maison 50 par le jeu. La hache reste sélectionnée ;
l'épée longue est possédée. Terre, canoë, corde et quatre cristaux sont conservés.

Chacune des sept étapes est relue depuis le démarrage, par commandes fixes :
65 536 octets de RAM et PNG final identiques. Les 128 mots du HUD physique sont
vérifiés après Feu et après l'épée ; ces deux images finales ont été inspectées.
Les sources des pilotes sont conservées dans `validation/v0310-d5-sources`.

La protection d'approche autorisée reste déclarée dans le cinquième épisode,
qui attend le boss de 163. Aucun objet, ressource, acteur, progression, SRAM ou
état principal n'est importé. Le cinquième boss et son cristal ne sont pas encore
validés par ce rapport. La fidélité globale R/IRQ, audiovisuelle et matérielle
ainsi que la suite de la campagne v310 restent ouvertes.
