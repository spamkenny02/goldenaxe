# Bateau acquis après le combat intermédiaire sur v0309

Le parcours poursuit la [victoire intermédiaire](d7_midboss_v0309.md),
toujours depuis le même Nouveau Jeu sans import de SRAM. La ROM reste v0309,
SHA-256 `7270576d6eeb2aee641776a3e364f2f3f320711d70bb91a566d7578161261049`.

| Étape | Image finale | Salle | PV | PM | Clés |
| --- | --- | --- | --- | --- | --- |
| Reprise déclarée de l'aide d'approche | 200067 | 1B8 | 54/80 | 56 | 2 |
| Trajet sud terminé | 205966 | 1D6 | 80/80 | 72 | 2 |
| Mécanisme de 1E6 activé et retour | 207552 | 1D6 | 80/80 | 72 | 2 |
| Bateau obtenu, fenêtre fermée | 208659 | 1D5 | 80/80 | 72 | 2 |

La protection reprend uniquement après la victoire intermédiaire vérifiée,
à 200067. Une relecture froide vérifie l'entrée et le combat 1B8 sans
protection, la victoire, puis cette reprise. L'épisode fermé est attribué
au combat 1B8 réellement observé ; un nouvel épisode vise le boss principal
179, encore non entré. Les PV, objets et autres ressources restent inchangés
sur la seule image ajoutant cette protection.

Les PV et la magie sont restaurés ensuite par les ramassages normaux du jeu
pendant le trajet sud. Le mécanisme de 1E6, UP en (72,40), ouvre le passage
ouest de 1D6 et l'accès à 1D5. Le bateau est accordé par le véritable coffre
et sa fenêtre de récompense est fermée par les commandes ordinaires.

Quatre pièges 5E à zéro PV sont conservés, ainsi qu'un ennemi 44 vivant
à 10 PV dans le slot 4 sur ce parcours. La salle n'est pas déclarée nettoyée.
Aucun acteur n'est supprimé ni remplacé par un état de test.

Les quatre points de contrôle ont une relecture fixe depuis le démarrage,
identique sur les 65536 octets de RAM et le PNG final. Après la fenêtre du
bateau, les 128 mots physiques du HUD correspondent au miroir SMS traduit
et les six marqueurs de cristal suivent la table originale 1EDC.

Seul `hero_hurt` sert à l'aide d'approche déclarée. Aucun argent, objet,
PV, PM, acteur, progression ou SRAM n'est importé. La protection devra
être retirée avant le boss principal. Le septième cristal et le retour
extérieur ne sont pas validés par cette étape.

Voir le [rapport et les empreintes](d7_ship_v0309_report.json) et
l'[audit reproductible](../tools/summarize_d7_ship_v0309.py).
Les sources exactes sont figées dans `validation/v0309-d7-ship-sources`.
La branche sud sans protection historiquement perdue sur v0306 n'a pas
été rejouée sur v0309 et aucune défaite correspondante n'est revendiquée ici.
