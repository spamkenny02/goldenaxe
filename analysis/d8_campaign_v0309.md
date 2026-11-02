# Huitième cristal et retour extérieur sur v0309

Le parcours poursuit la quête vérifiée de la clé des voleurs sur la même
ROM v0309 depuis Nouveau Jeu, sans import de SRAM ni ajout de ressources.

| Étape | Image finale | Salle | PV | PM | Cristaux |
| --- | --- | --- | --- | --- | --- |
| Retrait de la protection | 256795 | 1A6 | 88/88 | 64 | 7 |
| Boss vaincu et récompense terminée | 260756 | 196 | 96/96 | 72 | 8 |
| Sortie extérieure | 261634 | 29 | 94/96 | 64 | 8 |

Le premier combat commence à l'image 256980 : héros à 88 PV, compteur de
blessure nul, boss original 6B à 80 PV. L'épée longue de niveau 2 est choisie
par le menu normal. Le héros gagne sans recevoir de dégât. Les 396 fenêtres
de prédiction du combat correspondent sur toute la RAM. Aucune écriture de
test ne suit le retrait de la protection, y compris pendant le retour.

La sortie suit 196, 1A6, 1A7, 1EB et 1EA, puis l'extérieur 29. À l'image
261240 en 1A7, un coup normal fait passer les PV de 96 à 94 et les PM de 72
à 64. Neuf fenêtres de prédiction supplémentaires sont vérifiées au retour.
La hache est rééquipée, la clé des voleurs et le bateau conservés.

Les trois points finaux ont des relectures indépendantes depuis le démarrage :
65536 octets de RAM et PNG final identiques. Les 128 mots physiques du HUD
et les huit marqueurs de cristal sont vérifiés après la récompense et la
sortie. Avec l'entrée, le gardien et la quête, le D8 compte 17 points canoniques.
L'image finale a aussi été inspectée visuellement.

Le premier lancement de l'audit final s'arrêtait sur une empreinte mal
recopiée dans le vérificateur. La valeur a été corrigée pour correspondre
à la ROM v0309 inchangée et aux captures ; les tests de jeu n'ont pas été relancés.

Reproduction : `python tools/summarize_d8_campaign_v0309.py`.
Voir le [rapport et ses empreintes](d8_campaign_v0309_report.json).
Sources figées : `validation/v0309-d8-main-sources`.
Commandes exécutées : `validation/run_d8_main01.py`.

Huit cristaux et leurs retours sont couverts sur la ROM courante. Le neuvième
donjon, la fin dans cette campagne, le hasard et la phase globale SMS, les
contenus optionnels, les sauvegardes et le matériel restent à vérifier.
