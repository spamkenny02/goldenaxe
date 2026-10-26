# Progression native dans le cinquième donjon, v0292

La cartouche reste inchangée : v0292, SHA-256
`6eeb56086a81c230c75b154f51cafab72167a1eec42c691aed9bf317fd19dd82`.

Depuis la sortie validée du quatrième donjon, le contrôleur utilise le
canoë réellement acquis pour calculer les collisions. La RAM entière du
préfixe est comparée avant sa prolongation. Le chemin dérivé des cartes
SMS parcourt 365 étapes jusqu'à l'entrée extérieure 49, puis la salle186.
Le déplacement d'essai confirme que le héros est contrôlable à62/64PV.
Une tentative sans nouvelle assistance meurt dans l'écran48 ; la route
retenue consigne l'assistance du compteur de blessures, sans recharge de
vie ni import d'état dans le jeu principal. Cette aide ne protège pas
nécessairement contre toutes les attaques spéciales : le jalon se termine
vivant à30/64PV. Elle n'est jamais intégrée dans la ROM distribuée.

Étapes et preuves indépendantes depuis le démarrage :

| Étape | Salle | Fin | Résultat |
| --- | --- | --- | --- |
| Approche | 186 | 88153 | 62/64PV, canoë présent, héros contrôlable |
| Clé | 176 | 88953 | Salle nettoyée, clé0→1 |
| Terre | 176→166 | 89397 | Rocher4A:0B→00, porte ouverte, magie48→40 |
| Bottes | 166→156→157 | 92303 | Bottes acquises (inventaire14), clé consommée, 30/64PV |

Chaque étape a sa relecture officielle par commandes fixes :65 536 octets
de RAM et PNG final exactement identiques au parcours avec contrôleur.
Les quatre premiers cristaux et le canoë sont conservés.
La magie finale vaut48 après les ramassages en jeu.

Deux corrections de l'outil accélèrent la relecture : indexer les écritures
historiques par image et différer la lecture des cartes jusqu'à la fin du
préfixe. Les routes03/04 donnent les mêmes commandes, RAM entière et PNG.
Les captures et sources du contrôleur exécuté avant cette accélération
sont conservées. Les essais de diagnostic ne prouvent pas un défaut du
portage : boots02 essayait la porte sans détruire le rocher ; earth01
ouvrait l'inventaire avant l'apparition complète des ennemis. La séquence
retenue nettoie la salle et prend la clé avant de lancer Terre.

Le boss de ce donjon, en163 et accessible depuis173, n'est pas encore
atteint par cette campagne. Ni sa victoire, ni la sortie du donjon5,
ni la vitesse des bottes face à la SMS ne sont revendiquées. La campagne
source équivalente, les donjons6–10, la fin et la fidélité globale restent
ouverts. L'aide sera retirée avant le combat du boss, comme précédemment.

Rapports : `d5_approach_v0292_report.json` et
`d5_progress_v0292_report.json`. Reproduction par
`tools/summarize_d5_approach_v0292.py` puis
`tools/summarize_d5_progress_v0292.py` ; leurs références SHA-256 lient les
rapports aux contrôles, assistance, captures et preuves indépendantes.
