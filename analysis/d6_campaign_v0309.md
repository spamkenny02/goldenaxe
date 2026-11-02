# Sixième cristal et retour extérieur sur v0309

Le parcours poursuit la [préparation D6](d6_progress_v0309.md), depuis le même
Nouveau Jeu sans import de SRAM. La ROM reste v0309, SHA-256
`7270576d6eeb2aee641776a3e364f2f3f320711d70bb91a566d7578161261049`.
Le programme du jeu n'a pas changé pendant cette validation.

| Étape | Image finale | Salle | PV | PM |
| --- | --- | --- | --- | --- |
| Retrait de la protection avant le boss | 171343 | 125 | 72/72 | 32 |
| Sixième cristal, récompense terminée | 179816 | 115 | 80/80 | 72 |
| Retour extérieur | 182351 | 8B | 70/80 | 72 |

Le combat commence à 171445 avec le héros à 72 PV, compteur de protection
nul, contre le boss original 64 à 60 PV. Le héros gagne sans subir de dégât.
Le cristal et son soin portent normalement ses PV à 80 et restaurent sa magie.
La dernière écriture de test est le retrait de la protection à 171343,
avant l'entrée chez le boss ; aucune nouvelle écriture n'a lieu ensuite.

Le retour traverse 125, 124, 123, 113, 114, 138, 169, 168, 178, 177 et 187,
puis sort en 8B. Un dégât normal est observé à 181376 en 169 : 80 vers 70 PV.
Le héros conserve les six cristaux, la cloche de glace, les bottes, le canoë,
la corde, Feu, Terre et l'épée longue. La hache reste sélectionnée ; il
dispose de 27 cornes, d'aucune clé et de l'armure de niveau 1.

Les trois points de contrôle finaux ont chacun une relecture fixe depuis le
démarrage, exacte sur les 65536 octets de RAM et le PNG final. Les 969 fenêtres
de prédiction du combat et les 42 du retour correspondent à toute la RAM.
Les dix-sept étapes de préparation disposent aussi de leurs relectures exactes.
Les 128 mots de la carte physique du HUD et les six marqueurs de cristal sont
vérifiés après la récompense et la sortie. L'image de sortie a été inspectée.

Le premier essai du pilote, avec des décisions par séquences de 32 images,
était inefficace : après 287 fenêtres vérifiées, le boss n'avait perdu que
2 PV. Cet essai a été arrêté volontairement ; son diagnostic est conservé
dans `validation/v0309-d6-coarse32-diagnostic`. Son enregistrement incomplet
est exclu des préfixes acceptés. L'essai gagnant `boss02` repart du même
retrait de protection vérifié, avec des décisions par séquences de huit images
et une entrée UP ordinaire. Le retour utilise des séquences de 32 images.

Les approches précédentes restent explicitement assistées par `hero_hurt`.
Aucun argent, objet, PV, PM, acteur ou état de progression n'est importé.
L'autorisation supplémentaire d'argent de test pour acheter des potions
n'a pas été utilisée ici ; le boss et le retour sont sans protection de test.

Voir le [rapport et les empreintes des preuves](d6_campaign_v0309_report.json)
et l'[audit reproductible](../tools/summarize_d6_campaign_v0309.py).
Les sources exactes des pilotes sont figées localement dans
`validation/v0309-d6-boss-sources`. Les donjons suivants et la fin depuis ce
parcours froid restent à valider. Les [limites de fidélité relevées dans les sources](native_remaining_v0309.md)
restent distinctes de cette preuve de progression.
