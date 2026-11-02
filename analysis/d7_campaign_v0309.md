# Septième cristal et retour extérieur sur v0309

La campagne poursuit les 21 points de contrôle du ravitaillement, du combat
intermédiaire, du bateau et de l'approche, sur la même ROM v0309 depuis
Nouveau Jeu. Aucun import de SRAM ni ajout de ressources n'est utilisé.

| Étape | Image finale | Salle | PV | PM | Cristaux |
| --- | --- | --- | --- | --- | --- |
| Retrait de la protection | 215848 | 189 | 80/80 | 64 | 6 |
| Boss vaincu et récompense terminée | 220976 | 179 | 88/88 | 72 | 7 |
| Terre au retour | 222203 | 1B7 | 76/88 | 64 | 7 |
| Sortie extérieure | 222579 | 1B | 76/88 | 64 | 7 |

Le premier combat avec le boss 67 commence à l'image 216012 : héros à 80 PV,
compteur de blessure nul, adversaire à 60 PV. L'épée longue de niveau 2
est sélectionnée par le menu normal. Le héros gagne sans recevoir de dégât.
Les 272 fenêtres de prédiction du combat correspondent sur toute la RAM.
La protection est retirée avant le boss et aucune écriture de test ne suit,
y compris pendant le retour. L'assistance d'approche antérieure reste déclarée.

Un coup normal au retour, en salle 198 à l'image 221546, fait passer les PV
de 88 à 76. Terre détruit la cellule 57 de 1B7 à l'image 222007 pour huit PM ;
le pilote rééquipe ensuite la hache. La sortie emprunte le portail vers 1CB,
puis 1DB et l'extérieur 1B. Ce dernier segment ne rencontre aucun acteur avec
des PV positifs et ne nécessite aucune fenêtre de prédiction de combat.

Les quatre points finaux sont relus indépendamment depuis le démarrage avec
les boutons enregistrés : 65536 octets de RAM et PNG final identiques. Les
128 mots physiques du HUD et les sept marqueurs de cristal sont vérifiés
après la récompense et la sortie. Cela porte le D7 à 25 points canoniques.

La tentative return-earth01 est exclue : la pierre était détruite, mais la
recette attendait à tort un indicateur de passage et relançait le sort jusqu'à
épuisement des PM. La branche validée return-earth02 repart du combat canonique
et emploie une seule activation Terre, sans importer l'état de la tentative.

Reproduction : `python tools/summarize_d7_campaign_v0309.py`.
Voir le [rapport et ses empreintes](d7_campaign_v0309_report.json).
Les sources sont figées dans `validation/v0309-d7-navigation-sources` ;
les commandes exécutées sont dans `validation/run_d7_main01.py` et
`validation/run_d7_return02.py`.

Sept cristaux et leurs retours sont couverts sur la ROM courante. La suite de
la campagne, le hasard et la phase globale SMS, les contenus optionnels, les
sauvegardes et la fidélité audiovisuelle/matérielle restent à vérifier.
