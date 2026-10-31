# v0305 — Corde, troisième cristal et retour

ROM inchangée : `83dfaf697521ce97597af259835eccae70bde055e70f321176caad34f93a23c7`.
Le parcours poursuit la sortie du deuxième donjon ayant conservé l’huile.
Aucune modification de production n’est nécessaire pour ce jalon.

| Étape | Image finale | Salle | PV | Cristaux |
| --- | --- | --- | --- | --- |
| Entrée D3 | 43740 | 1F8 | 31/48 | 2 |
| Corde | 48913 | 1F4 | 47/48 | 2 |
| Troisième cristal | 53863 | 1C3 | 56/56 | 3 |
| Retour dehors | 55110 | 62 | 56/56 | 3 |

Le héros atteint le troisième donjon en 1F8, récupère normalement la corde
en 1F4 et termine son dialogue. La corde, la hache équipée, l’huile et les
deux premiers cristaux sont conservés jusqu’au troisième boss.

## Passage de 1E3

Le contrôleur essayait de combattre depuis une partie de la salle alors que
des ennemis étaient séparés par les murs. Le script SMS prévoit un mécanisme
stationnaire Haut au point (120,104), coordonnée source 856 : transformation
persistante de la cellule 57 et ouverture du passage supérieur. Le parcours
retenu active ce mécanisme depuis le sud, repart par les couloirs, obtient
la clé en 1D2 puis traverse la couronne extérieure de 1E3 vers le nord.
Les ennemis de 1E3 restent présents ; ce segment ne prétend pas les avoir
tous vaincus. Les portes et transformations sont exécutées par le jeu.

Sept approches antérieures se terminent avant l’entrée du boss et restent
exclues des réussites. Un segment de diagnostic vivant a sa propre relecture
exacte, sans être inclus dans la branche gagnante. Les hypothèses de retour
par une autre entrée et d’attente des animations de mort n’ont pas fourni
le parcours retenu. Les prototypes sont conservés, puis le contrôleur actif
est restauré octet pour octet à celui du commit 0ab6571. La solution utilise
ses options existantes et le véritable mécanisme, sans effacer d’acteur.

## Combat et retour

La dernière écriture de protection est un zéro à l’image 52210. Le premier
combat commence à 52244, à 47 PV avec compteur de protection nul, soit 34
images plus tard. Un coup normal à 53146 fait passer les PV de 47 à 39.
Le boss 69 est vaincu, puis le cristal et son soin terminent à 56/56 PV.
Le retour rejoint l’extérieur 62 à 56/56 PV, sans nouvelle assistance.

Les aides d’approche héritées ne modifient que `hero_hurt` (0 ou 129).
Aucun PV, acteur, objet, progression ou sauvegarde n’est injecté. Le jeu
principal part du démarrage avec ses commandes enregistrées. Le contrôleur
de combat choisit parmi des commandes normales avec un horizon de 96 images
et des fenêtres de 16 images ; les prédictions retenues sont vérifiées sur
la RAM entière. Aucun état secondaire n’est importé dans le jeu principal.
Ce parcours conserve l’assistance d’approche et ne constitue pas une campagne
entièrement sans aide.

Quatre relectures froides indépendantes reproduisent les 65 536 octets de
RAM et le PNG final. Le profil avant chaque instruction normale couvre
55 110 images après l’initialisation à partir de l’image 14. Il observe
450 octets entre le SP minimal et la frontière maximale du tas ; les chaînes
du tas sont valides. Sa RAM et son PNG finaux concordent avec le retour
canonique. Ce profil ne démontre pas la sûreté de tous les chemins.

## Portée

Les trois premiers cristaux et retours sont désormais vérifiés sur v0305.
Les sept cristaux et la clé des voleurs sur v0304 restent des preuves propres
à cette ancienne ROM. La suite de campagne, la fin, les sauvegardes, le
hasard SMS et sa phase globale ainsi que la fidélité vidéo/audio/matériel
complète restent non validés.

[Rapport et empreintes](d3_campaign_v0305_report.json). Reproduction locale :
`tools/summarize_d3_campaign_v0305.py`. `tools/archive_d3_campaign_v0305.py`
archive les captures et prototypes sans perte, vérifie leur relecture avant
le nettoyage, protège les 305 ROMs numérotées et l’original, puis conserve
la RAM finale prête à poursuivre le parcours.
