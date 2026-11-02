# Cloche et entrée du neuvième donjon sur v0309

La campagne poursuit la sortie vérifiée du huitième donjon sur la même
v0309 depuis Nouveau Jeu. Les huit cristaux et l'équipement acquis sont
conservés, sans import de SRAM ni ajout de ressources.

| Étape | Image finale | Salle | PV | PM | Argent |
| --- | --- | --- | --- | --- | --- |
| Maison du passage côtier 1A | 262214 | 9F | 94/96 | 64 | 40 |
| Passage payé, arrivée en 3C | 262569 | 3C | 94/96 | 64 | 30 |
| Entrée du neuvième donjon | 266242 | 1FC | 94/96 | 64 | 30 |

Le passage coûte exactement dix pièces. La route suivante emploie la cloche
de glace déjà possédée : sélection par le menu, activation normale en CB,
puis changement réel de la cellule 86 de 2F vers 39 et du drapeau persistant.
L'ouverture est observée à l'image 265080, sans écriture de terrain, de
ressources ou de progression. La hache est ensuite rééquipée. Le héros
rejoint la porte du neuvième donjon et marche à l'intérieur ; une clé est conservée.

Les trois points sont relus indépendamment depuis le démarrage avec les
boutons enregistrés : 65536 octets de RAM et PNG final identiques. La
protection d'approche reste déclarée et devra être retirée avant les combats.
L'entrée ne prouve pas encore le neuvième cristal, le premier gardien 1BE/79
ni le gardien optionnel 19C/7B et son ballon.

Reproduction : `python tools/summarize_d9_entry_v0309.py`.
Voir le [rapport et ses empreintes](d9_entry_v0309_report.json).
Sources figées : `validation/v0309-d9-entry-sources`.
Commandes exécutées : `validation/run_d9_entry01.py`.

La fidélité globale SMS, les contenus optionnels, les sauvegardes et les
essais matériels restent à vérifier.
