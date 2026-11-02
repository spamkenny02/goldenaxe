# Géant optionnel et ballon acquis sur v0309

La campagne poursuit le premier gardien vérifié, sur la même v0309 depuis
Nouveau Jeu. Les huit cristaux restent acquis. Aucun PV, PM, argent, objet,
acteur, progression ou état SRAM n'est importé. La protection d'approche
reprend seulement après chaque victoire canonique et se termine avant le géant.

| Étape | Image finale | Salle | PV | PM | Clés |
| --- | --- | --- | --- | --- | --- |
| resume | 278276 | 1BE | 78/96 | 72 | 2 |
| contact | 282557 | 1AD | 96/96 | 72 | 2 |
| portal | 283730 | 19E | 96/96 | 72 | 2 |
| reach | 283935 | 19D | 96/96 | 72 | 2 |
| release | 283936 | 19D | 96/96 | 72 | 2 |
| giant | 287675 | 19C | 16/96 | 72 | 2 |
| resume2 | 287676 | 19C | 16/96 | 72 | 2 |
| item | 289111 | 19B | 36/96 | 72 | 2 |

Le mécanisme de 1AD et le passage en 19E sont réellement parcourus. La salle
19D contient quatre acteurs 62 de zéro PV : ce sont des pièges persistants,
qui restent présents. Le héros traverse jusqu'au point 24,88 sans dégât et
sans prétendre nettoyer la salle. Cela résout l'arrêt de l'ancien test qui
attendait à tort leur mort.

La protection est retirée à l'image 283936 avant 19C. Le premier combat
commence à 283988 : héros à 96 PV, compteur de blessure nul, géant original
7B à 60 PV, 20 de dégâts de base et 6 d'armure. L'épée longue de niveau 2
est choisie par le menu normal. Quatre coups de 20 PV sont reçus à 284303,
284513, 284561 et 285205. Le héros gagne à 16/96 PV. Aucune écriture de test
ne suit le retrait pendant le combat ; 440 fenêtres de prédiction sont
exactes sur toute la RAM. La longue charge à rebonds explique le palier de
PV observé pendant l'affrontement ; le processus continuait normalement.

Après la victoire canonique, le trajet reprend vers 19B. Un ramassage normal
fait passer les PV de 16 à 40 à l'image 287771. Le ballon est réellement acquis
par la récompense stationnaire originale, avec l'inventaire 11 passant de 0 à 1.
Sa fenêtre se ferme et la hache est rééquipée. Un coup normal en 19B fait
passer les PV de 40 à 36 à l'image 289102. Le point final conserve 72 PM,
32 pièces et deux clés ; le géant vaincu ne réapparaît pas vivant.

Les huit points sont relus indépendamment depuis le démarrage : 65536 octets
de RAM et PNG final identiques. Les 128 mots physiques du HUD et les huit
marqueurs de cristal finaux sont vérifiés. Les images du combat et du point
final ont aussi été inspectées. Avec l'entrée et le premier gardien, 16 points
D9 sont couverts jusqu'ici. Le neuvième cristal reste à obtenir.

Le ballon ouvre la carte générale depuis l'extérieur ; ce rapport couvre
son acquisition, pas encore son activation et son retour dans cette campagne.
Les anciens tests contrôlés de la carte restent des preuves distinctes.

Reproduction : `python tools/summarize_d9_balloon_v0309.py`.
Voir le [rapport et ses empreintes](d9_balloon_v0309_report.json).
Sources figées : `validation/v0309-d9-balloon-sources`.
Commandes exécutées : `validation/run_d9_balloon01.py`.
La fidélité globale SMS, le hasard, la fin, les sauvegardes et le matériel
restent à vérifier.
