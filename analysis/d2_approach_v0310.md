# v0310 : hache, fée de vie et entrée D2

Le [bilan vérifié](d2_approach_v0310_report.json) prolonge le parcours v310
ayant obtenu le premier cristal. Retour dans D1 pour la clé 1C5, ouverture du
passage vers 1B6, acquisition réelle de la hache puis équipement via l'inventaire.
Le héros ressort en B9 à 32/32 PV, avec le premier cristal conservé.

Trois actions de coupe avec la hache sont consignées sur la route de la première fée de vie.
Le dialogue donne le cœur supplémentaire et le soin normal : capacité 32 -> 40,
puis 40/40 PV. Le drapeau du don C9 est positionné. Après une autre coupe sur
le chemin suivant, le héros entre en 171 dans le deuxième donjon, hache équipée.

| Étape | Image finale | Résultat |
| --- | --- | --- |
| Retour D1 | 16450 | 1E4, 28 PV |
| Clé du passage | 19585 | 1C5, 32 PV, une clé |
| Hache | 21176 | 1B6, hache acquise, clé consommée |
| Sortie équipée | 22295 | B9, hache équipée, 32/32 PV |
| Entrée chez la fée | 23350 | AF, trois actions de coupe sur le trajet |
| Don et sortie | 23872 | C9, drapeau du don, 40/40 PV |
| Entrée D2 | 26033 | 171, hache équipée, 40/40 PV |

Les sept étapes ont chacune leur relecture froide indépendante par commandes
fixes : RAM complète de 65 536 octets et PNG final exacts. Les seules écritures
de test sont les compteurs de blessures consignés pour l'approche. Aucun PV,
objet, argent, clé, acteur ou progression n'est injecté ; aucun import SRAM ou
instantané dans le jeu principal. Le service de fée n'ajoute aucune écriture.

La seconde protection d'approche commence après la sortie D1 vérifiée à 16254.
Elle cible le futur boss en 144 et doit cesser avant ce combat. Le premier
boss D1 garde son épisode distinct, déjà terminé sans protection au combat.
Les images de la hache acquise et de l'entrée D2 ont été inspectées.

Ce rapport ne prouve pas la victoire D2, la suite ou la fidélité globale du
registre R et des interruptions. Le boss D2 observé ensuite est de type63,
pas le type65 à satellites : ces validations restent distinctes. La campagne
complète v309 demeure historique. La ROM publique v310 reste inchangée.
