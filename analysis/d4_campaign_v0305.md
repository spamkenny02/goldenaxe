# v0305 — Terre, canoë, quatrième cristal et retour

ROM : `83dfaf697521ce97597af259835eccae70bde055e70f321176caad34f93a23c7`.
Le parcours poursuit la sortie du troisième donjon, avec huile et corde.
Le code de production reste inchangé pendant cette validation de progression.

**Limite visuelle connue :** la carte du HUD physique n’est pas restaurée
après les fenêtres d’objet/cristal alors que sa copie RAM l’est. La comparaison
VRAM a révélé le défaut après le canoë. L’égalité des relectures RAM/PNG ne
prouve pas que cette image est correcte face à la SMS. Cette anomalie reste
à corriger ; le rapport ci-dessous valide la progression et les transactions.

| Étape | Image finale | Salle | PV | Magie | Cristaux |
| --- | --- | --- | --- | --- | --- |
| Trajet/entrée | 58296 | 3F | 56/56 | 24 | 3 |
| Don de 50 cornes | 58763 | F4 | 56/56 | 24 | 3 |
| Trajet/entrée | 60503 | BF | 56/56 | 24 | 3 |
| Terre apprise | 61515 | A3 | 56/56 | 48 | 3 |
| Trajet/entrée | 66395 | 1F0 | 56/56 | 48 | 3 |
| Clé | 67128 | 1F1 | 56/56 | 48 | 3 |
| Premier passage Terre | 68217 | 1D1 | 56/56 | 40 | 3 |
| Clé | 73590 | 1A1 | 56/56 | 48 | 3 |
| Canoë | 75406 | 1A2 | 56/56 | 48 | 3 |
| Second passage et téléporteur | 76281 | 192 | 56/56 | 40 | 3 |
| Clé | 77682 | 182 | 56/56 | 40 | 3 |
| Combat partiel | 82357 | 180 | 56/56 | 40 | 3 |
| Quatrième cristal | 83875 | 180 | 64/64 | 48 | 4 |
| Retour dehors | 86364 | 10 | 50/64 | 48 | 4 |

## Transactions et équipement

Le don de F4 fait passer les cornes de 3 à 53. Le trajet emploie la hache
et la corde pour rejoindre le maître A3. L’apprentissage prélève exactement
50 cornes, donne Terre niveau 1 et augmente la réserve de magie de 24 à 48.
Le héros entre normalement dans le quatrième donjon à 56/56 PV.

Après la première clé, un lancement de Terre dégage le rocher de 1E1 et
permet de rejoindre 1D1 : huit points de magie consommés. Le premier trajet
alternatif atteint aussi cette destination mais poursuit plus longtemps
l’attente devant les gardiens cachés ; il n’est pas la branche retenue.
Le trajet suivant emploie leur activation par proximité, le mécanisme de
C0 et laisse le mécanisme facultatif de B0 pour plus tard. Une tentative
bloquée devant ce mécanisme est conservée comme diagnostic.

La clé de 1A1 permet l’accès au canoë de 1A2, obtenu par les commandes normales
et son véritable dialogue. Le premier essai vers 192 est bloqué devant un
second obstacle, puis le lancement de Terre en 1A3 le dégage pour huit points
de magie et permet le passage par le vrai téléporteur. La relecture fixe
relève 33 images de déplacement sur l’eau en 1A2 avec le canoë acquis.
La clé de la seconde partie est obtenue en 182.

## Boss et retour

La dernière écriture de garde est à l’image 79312. Le combat normal
commence à 79357 avec 56 PV et compteur de protection nul,
soit 45 images plus tard. Le premier segment de 3 000 images s’achève
avec le boss à 12/30 PV et le héros à 56 PV ; sa relecture exacte permet de
poursuivre le même combat, sans import de sauvegarde ni remise à zéro des PV.
Le deuxième segment remporte le combat. Le cristal et son soin terminent
à 64/64 PV, puis le héros ressort en 10 à 50/64 PV. Aucun soin ni objet
n’est ajouté par l’outil et aucune protection ne reprend après sa libération.

Les seules écritures de test héritées et d’approche modifient `hero_hurt`
avec les valeurs 0 et 129. Aucun PV, MP, corne, acteur, propriété, progression
ou sauvegarde n’est injecté. Les approches restent explicitement assistées ;
ce parcours n’est pas présenté comme entièrement sans aide.

Quatorze relectures froides indépendantes reproduisent toute la RAM de
65 536 octets et le PNG final. Les fenêtres de prédiction du contrôleur du
boss et du retour correspondent à la RAM entière ; aucun état secondaire
n’entre dans le jeu principal. Le profil de pile avant chaque instruction
normale jusqu’à la sortie observe 450 octets de marge, des chaînes de tas
valides et une RAM/image finale identique au retour canonique. Cette mesure
concerne le parcours enregistré, pas tous les chemins possibles.

## Portée

Les quatre premiers cristaux et retours sont vérifiés sur v0305. La correction
du HUD, les donjons suivants, la fin, les sauvegardes, le hasard SMS et sa
phase globale ainsi que la fidélité complète vidéo/audio/matériel restent
non validés. Les preuves de sept cristaux sur v0304 restent historiques.

[Rapport et empreintes](d4_campaign_v0305_report.json). Les scripts
`tools/summarize_d4_campaign_v0305.py` et `tools/archive_d4_campaign_v0305.py`
vérifient les captures, conservent une archive sans perte avant nettoyage,
protègent l’original et les 305 ROMs numérotées, puis gardent la RAM finale
prête à poursuivre le parcours.
