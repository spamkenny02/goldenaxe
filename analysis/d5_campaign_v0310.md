# v0310 : cinquième cristal et retour extérieur

Le [bilan vérifié](d5_campaign_v0310_report.json) poursuit le
[ravitaillement et le mécanisme de D5](d5_supplies_v0310.md), depuis la même
partie démarrée à froid. La ROM v310 reste inchangée.

| Étape | Image finale | Salle | PV |
| --- | ---: | --- | ---: |
| Antichambre dégagée, épée longue sélectionnée | 142820 | 173 | 64/64 |
| Protection retirée | 142821 | 173 | 64/64 |
| Cinquième cristal, récompense terminée | 146636 | 163 | 72/72 |
| Mécanisme du retour traversé | 146985 | 174 | 72/72 |
| Retour extérieur | 147802 | 49 | 72/72 |

Le combat commence à 142904 avec 64 PV et compteur de blessures nul,
contre le boss original **65 à 72 PV**. Les huit satellites 66 sont observés ;
ils sont détruits avant les premiers dégâts au noyau, à 145022. Aucun dégât
n'est reçu pendant le combat ou le retour. Le soin du cristal et sa restauration
de magie sont obtenus normalement : 72/72 PV et PM à la sortie.

La dernière écriture de protection est 142821, avant l'entrée du boss.
Aucune nouvelle aide pendant le combat, le mécanisme du retour ou la sortie.
Aucun objet, ressource, acteur, progression, SRAM ou état principal n'est importé.
L'épée longue niveau 2 reste sélectionnée ; Feu, Terre, bottes, canoë, corde
et cinq cristaux sont conservés.

Les cinq étapes ont une relecture fixe depuis le démarrage, exacte sur les
65 536 octets de RAM et le PNG final. Les 96 fenêtres de prédiction du combat
et les onze du retour correspondent à toute la RAM. Après le cristal et la
sortie, les 128 mots du HUD physique et les cinq marqueurs de cristal sont
vérifiés ; les deux images finales ont été inspectées. Les sources sont figées
dans `validation/v0310-d5-boss-sources`.

Ce combat teste réellement le boss à satellites avec le générateur raccordé
en v310 ; il complète les cas contrôlés de sa routine. Il ne prouve pas la
phase R/IRQ originale. Un parcours NTSC jusqu'à cinq cristaux est couvert ;
la suite de la campagne v310, les contenus optionnels et la fidélité globale
temporelle, audiovisuelle et matérielle restent ouverts.
