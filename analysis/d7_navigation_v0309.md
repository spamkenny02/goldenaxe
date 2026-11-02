# Du bateau à l'antichambre du boss sur v0309

Le parcours poursuit [l'acquisition du bateau](d7_ship_v0309.md), sur la même
ROM v0309 inchangée et depuis le même Nouveau Jeu sans import de SRAM.

| Étape | Image finale | Salle | PV | PM | Clés |
| --- | --- | --- | --- | --- | --- |
| Retour nord | 210300 | 1B8 | 80/80 | 72 | 2 |
| Terre en 1A8 et portail | 211386 | 198 | 80/80 | 64 | 2 |
| Sentinelles et antichambre | 215847 | 189 | 80/80 | 64 | 1 |

Terre détruit la cellule 34 de 1A8 pour huit PM, puis le portail conduit à
198. Le trajet suivant réveille les sentinelles par les commandes normales,
les combat et dépense une clé pour atteindre l'antichambre 189. Le bateau,
la cloche et les six cristaux précédents sont conservés.

Chaque étape a une relecture fixe depuis le démarrage, exacte sur les
65536 octets de RAM et le PNG final. Aucun PV, PM, argent, objet, acteur,
progression ou SRAM n'est importé. La protection d'approche est toujours
déclarée dans ce rapport et devra être retirée avant le boss 179.

Voir le [rapport et les empreintes](d7_navigation_v0309_report.json) et
l'[audit reproductible](../tools/summarize_d7_navigation_v0309.py).
Les sources et recettes exécutées sont figées dans
`validation/v0309-d7-navigation-sources`. Le septième cristal et le retour
ne sont pas validés par ce rapport.
