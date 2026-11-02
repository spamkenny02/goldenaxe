# Neuvième cristal et retour extérieur sur v0309

Le parcours poursuit le géant et le ballon réellement acquis, sur la même
v0309 depuis Nouveau Jeu. Il n'utilise aucun import de SRAM ni ajout de
ressources. L'assistance d'approche reste déclarée et se termine avant le boss.

| Étape | Image finale | Salle | PV | PM | Cristaux |
| --- | --- | --- | --- | --- | --- | --- |
| approach | 295159 | 1BC | 36/96 | 72 | 8 |
| release | 295160 | 1BC | 36/96 | 72 | 8 |
| boss | 300396 | 1AC | 104/104 | 72 | 9 |
| exit | 302306 | 0EB | 102/104 | 64 | 9 |

Le trajet depuis 19B revient par 19C, 19D et 19E, traverse le portail vers
1CC, puis active le puzzle de BC et le mécanisme de BD. Il s'arrête en 1BC,
avant le boss. Le ballon et les deux clés sont conservés.

La protection est retirée à l'image 295160. Le combat commence à 295276 :
héros à 36 PV, compteur de blessure nul, boss original 6C à 90 PV. L'épée
longue de niveau 2 fournit une force de 6. Le héros reçoit un coup à 297383,
de 36 vers 16 PV, puis gagne. Le neuvième cristal est réellement ramassé,
sa fenêtre se ferme et les PV/PM sont restaurés à 104/104 et 72.
Les 270 fenêtres de prédiction du combat correspondent sur toute la RAM.
Aucune écriture de test ne suit le retrait, y compris durant le retour.

La sortie emprunte 1AC, 1BC, 1CC, 19E, 1AE, 1BE, 1CE, 1DE, 1EE, 1FE,
1FD et 1FC, puis rejoint l'extérieur EB. Un coup normal en 1EE à 301743
fait passer les PV de 104 à 102 et les PM de 72 à 64. Quinze fenêtres de
prédiction supplémentaires sont vérifiées pendant ce retour.

Les quatre points finaux sont relus indépendamment depuis le démarrage :
65536 octets de RAM et PNG final identiques. Les 128 mots physiques du HUD
et les neuf marqueurs de cristal sont vérifiés après la récompense et la
sortie. L'image extérieure finale a aussi été inspectée. Le D9 totalise
20 points canoniques avec son entrée, ses deux gardiens et le ballon.

Reproduction : `python tools/summarize_d9_campaign_v0309.py`.
Voir le [rapport et ses empreintes](d9_campaign_v0309_report.json).
Sources figées : `validation/v0309-d9-main-sources`.
Commandes exécutées : `validation/run_d9_main01.py`.

Les neuf cristaux et leurs retours sont maintenant vérifiés sur la campagne
courante. Le palais et la fin doivent encore être rejoués depuis cette partie,
sans les confondre avec le scénario contrôlé déjà terminé. La fidélité globale
SMS, le hasard et la phase source, les autres contenus optionnels, les
sauvegardes et le matériel restent à vérifier.
