# Quatrième cristal et retour dehors sur v0309

La campagne poursuit le retour du troisième donjon depuis Nouveau Jeu, sans
import de SRAM. La ROM reste la v0309 :
`7270576d6eeb2aee641776a3e364f2f3f320711d70bb91a566d7578161261049`.
Le code du jeu n'a pas changé pendant ces tests.

| Étape | Image finale | Salle | PV |
| --- | --- | --- | --- |
| Don de 50 cornes | 68044 | F4 | 48/56 |
| Apprentissage de Terre | 70796 | A3 | 48/56 |
| Entrée D4 | 75677 | 1F0 | 48/56 |
| Première clé | 76334 | 1F1 | 48/56 |
| Premier passage Terre | 77718 | 1D1 | 56/56 |
| Deuxième clé | 84182 | 1A1 | 52/56 |
| Canoë | 86814 | 1A2 | 52/56 |
| Second passage Terre et portail | 87752 | 192 | 56/56 |
| Dernière clé | 89762 | 182 | 56/56 |
| Antichambre, avant retrait de l'aide | 91327 | 190 | 56/56 |
| Protection retirée | 91328 | 190 | 56/56 |
| Quatrième cristal, récompense terminée | 99296 | 180 | 64/64 |
| Retour extérieur | 101777 | 10 | 62/64 |

Le don fait passer l'argent de 12 à 62 cornes. L'achat de Terre coûte
50 cornes, donne le niveau 1 et porte la réserve de magie à 48.
Les deux obstacles sont détruits par de vrais lancements de Terre,
consommant chacun 8 PM. Les clés et le canoë viennent des récompenses du jeu.
La relecture relève 33 images de déplacement effectif sur l'eau avec le canoë.

Les approches utilisent la protection de test autorisée. Ses seules écritures
concernent `hero_hurt` ; aucun PV, PM, argent, objet, acteur ou drapeau de
progression n'est injecté. La dernière écriture, à 91328, retire la protection
dans le couloir de l'antichambre. Le combat commence à 91391 avec le héros à
56 PV, compteur de protection nul, contre le boss original 6A à 30 PV.
Le héros gagne sans subir de dégât. Aucune nouvelle écriture n'a lieu pendant
le combat ni le retour ; un piège enlève normalement 2 PV sur le trajet retour.

Les quinze étapes ont chacune une relecture fixe depuis le démarrage,
identique sur les 65536 octets de RAM et le PNG final. Les 228 fenêtres de
prédiction du combat et les quatre du retour correspondent à toute la RAM.
Après le canoë, le cristal et la sortie, les 128 mots de la carte physique du
HUD correspondent à la conversion SMS ; les marqueurs des cristaux acquis
suivent aussi la table de la ROM originale. L'image de sortie a été inspectée.

Le pilote de test réveille désormais les ennemis 52 en marchant sur les
motifs de sol nuls qui déclenchent leur apparition dans le jeu original.
Le mécanisme facultatif de B0 est différé. Les essais `a1-key01` à `04`,
`approach01`, `approach02` et `release01` sont exclus de cette branche :
attente devant des acteurs cachés, recherche du mécanisme facultatif ou arrêt
trop près d'un piège. `approach03` atteint (128,40) avant le retrait de l'aide.
Il ne prétend pas avoir détruit les pièges permanents de l'antichambre.

L'audit reproductible est [summarize_d4_campaign_v0309.py](../tools/summarize_d4_campaign_v0309.py),
avec son [rapport et les empreintes des preuves](d4_campaign_v0309_report.json).
Les sources exactes des pilotes sont conservées localement dans
`validation/v0309-d4-sources`. La copie complète de l'espace de travail reste
nécessaire pour transférer les captures et archives ignorées par Git.

Cette validation couvre les quatre premiers cristaux et leurs retours sur
v0309. Le palais et la fin ont une preuve contrôlée distincte. La suite de la
campagne courante, les contenus optionnels, le hasard SMS et la fidélité
globale vidéo/audio/matériel restent ouverts. Le portage complet n'est pas déclaré terminé.
