# Gardien intermédiaire du huitième donjon sur v0309

La campagne poursuit l'entrée vérifiée en 1EA sur la même v0309 depuis
Nouveau Jeu. Les sept cristaux, le bateau, l'épée longue et les ressources
acquis normalement sont conservés.

| Étape | Image finale | Salle | PV | PM | Argent | Clés |
| --- | --- | --- | --- | --- | --- | --- |
| Antichambre et sentinelles vaincues | 229029 | 1CA | 64/88 | 64 | 33 | 1 |
| Retrait de la protection | 229030 | 1CA | 64/88 | 64 | 33 | 1 |
| Gardien vaincu | 231568 | 1C9 | 28/88 | 64 | 33 | 1 |

L'approche emploie deux sorties/rentrées normales et réveille les sentinelles
par proximité. La première recette ready01, qui omettait cette activation,
s'arrêtait devant deux acteurs 58 endormis et reste exclue du parcours validé.
La recette ready02 reprend l'entrée canonique, sans importer cet état arrêté.

La protection est retirée avant 1C9. Le premier combat commence à l'image
229267 : héros à 64 PV, compteur de blessure nul, gardien original 7A à 50 PV.
L'épée longue de niveau 2 est choisie par le menu normal, avec une force de 6.
Deux coups sont reçus : 64 vers 46 PV à l'image 231214, puis 46 vers 28 à
231348. Chacun inflige les 18 dégâts de la table source. Aucun soin ni ajout
de ressources n'intervient, et aucune écriture de test ne suit le retrait.

Le combat vérifie 267 fenêtres de prédiction sur toute la RAM. Les trois
points finaux sont relus indépendamment depuis le démarrage : 65536 octets
de RAM et PNG final identiques. Le gardien ne conserve aucun PV positif.
Le boss principal 196 n'a pas été visité et le huitième cristal reste à obtenir.

Reproduction : `python tools/summarize_d8_midboss_v0309.py`.
Voir le [rapport et ses empreintes](d8_midboss_v0309_report.json).
Sources figées : `validation/v0309-d8-midboss-sources`.
Commandes exécutées : `validation/run_d8_midboss02.py`.

Cette victoire vérifie la progression et les dégâts sur ce parcours. La
fidélité globale SMS, le hasard, les sauvegardes, les contenus optionnels et
les essais matériels restent ouverts.
