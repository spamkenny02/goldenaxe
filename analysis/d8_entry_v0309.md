# Passage côtier et entrée du huitième donjon sur v0309

Le parcours continue depuis la sortie du septième donjon, sur la même ROM
v0309 et depuis le même Nouveau Jeu. Le bateau et les sept cristaux restent
acquis ; aucun objet, PV, PM, argent ou état SRAM n'est importé.

| Étape | Image finale | Salle | PV | PM | Argent |
| --- | --- | --- | --- | --- | --- |
| Maison du passage côtier 3C | 224027 | 9F | 64/88 | 64 | 38 |
| Passage payé, arrivée en 1A | 224409 | 1A | 64/88 | 64 | 28 |
| Entrée du huitième donjon | 224999 | 1EA | 64/88 | 64 | 28 |

Le paiement dépense exactement dix pièces et le héros traverse par les
commandes normales. Le trajet suivant passe par 2A et rejoint la porte de
29 ; la transition et une marche à l'intérieur de 1EA sont terminées.
Une clé est conservée. La protection d'approche est déclarée et devra être
retirée avant l'adversaire intermédiaire 7A en 1C9, puis avant le boss 6B en 196.
Aucun de ces deux combats n'est couvert par ce rapport.

Les trois points sont relus indépendamment depuis le démarrage avec les
boutons fixés : 65536 octets de RAM et PNG final identiques. La version
courante reste v0309 ; aucun code de jeu n'a changé.

Reproduction : `python tools/summarize_d8_entry_v0309.py`.
Voir le [rapport et ses empreintes](d8_entry_v0309_report.json).
Sources figées : `validation/v0309-d8-entry-sources`.
Commandes exécutées : `validation/run_d8_entry02.py`.
Le premier script entry01 a échoué sur un budget d'images trop court avant
l'émulation ; aucune trace de jeu n'a été créée par cette proposition.

Cette entrée ne prouve ni le huitième cristal ni la fidélité SMS globale.
