# v317 — septième donjon

Le parcours continue sur le binaire publié
`7694654ec85dd6626c0e17ff1834e5893d4eb35481400a4725eac6b6f3503294`.
Les résultats ci-dessous ne nécessitent aucune modification du programme.

## Préparation vérifiée

| Étape | Image finale | Résultat |
| --- | ---: | --- |
| Don ordinaire B5 | 172354 | Or : 58 → 68 |
| Achat de la clé | 173966 | Prix : 60 pièces ; soin normal : 74 → 80 PV |
| Entrée du donjon | 178922 | Salle 1DB, 64/80 PV après le trajet extérieur |
| Première clé intérieure | 179670 | Salle 1CB, récompense terminée |
| Deuxième clé intérieure | 186148 | Salle 1B9, deux clés en possession |
| Premier passage Terre | 186462 | Cellule 36 ; magie : 72 → 64 |
| Deuxième passage Terre | 186802 | Cellule 2B ; magie : 64 → 56 |

Les neuf points de contrôle de cette préparation reproduisent les 65536
octets de RAM et le PNG final avec un lecteur indépendant démarré à froid,
alimenté par les commandes enregistrées. Les achats, récompenses et sorts
emploient les commandes normales du jeu. Aucun objet, PV, or, point de magie,
état de progression, sauvegarde ou état primaire n'est importé.

## Combat intermédiaire vérifié

La protection d'approche est retirée en salle 1B9 à l'image 186803. Le
contact normal ouvre le passage vers 1B8. Le combat commence à l'image
186988 : boss source 78 à 30 PV, héros à 80 PV et protection nulle.
Le boss est vaincu à 188067 ; la capture finale à 188218 conserve 80/80 PV,
sans mort et sans perte de PV pendant le combat. Les 120 fenêtres de
prédiction correspondent à la RAM persistante du jeu principal.

Les quatre points de cette séquence reproduisent également la RAM complète
et le PNG final depuis un démarrage à froid. Une protection d'approche est
réactivée à 188219, après la victoire vérifiée, pour le trajet vers le boss
principal 179. Elle devra être retirée avant ce combat.

## Navire, septième cristal et retour vérifiés

| Étape | Image finale | Résultat |
| --- | ---: | --- |
| Mécanisme à distance | 195646 | Contact en 1E6, accès du navire ouvert |
| Navire | 196889 | Objet 16 obtenu normalement en 1D5 |
| Passage Terre vers le nord | 198680 | Cellule 34 en 1A8, arrivée en 198 |
| Retrait de protection | 204516 | Salle 189, 72/80 PV, protection nulle |
| Septième cristal | 207642 | Boss source 67 vaincu, récompense terminée à 88/88 PV |
| Passage Terre du retour | 210043 | Cellule 57 en 1B7, 30/88 PV |
| Retour extérieur | 210419 | Salle 1B, 30/88 PV, sept cristaux et navire conservés |

Le boss principal commence à l'image 204685 avec ses 60 PV source. Le héros
conserve ses 72 PV pendant le combat ; la récompense normale augmente ensuite
son maximum à 88 et le soigne. Les 145 fenêtres de prédiction correspondent
à la RAM persistante principale. Les dégâts du trajet de retour restent dans
l'enregistrement : aucun soin n'est ajouté par le test. Le dernier tronçon
ne demande aucune fenêtre de prédiction supplémentaire. Aucun nouveau garde
n'est activé après le retrait en 189 et le parcours retenu ne comporte aucune
mort.

Les 23 nouveaux points reproduisent la RAM complète et le PNG final avec
trois lecteurs indépendants démarrés à froid, partagés entre étapes. Ils
émettent 585440 images au lieu de 4379714 avec un redémarrage à chaque point,
soit 3794274 répétitions d'images de préfixe évitées pour les seuls lecteurs
de preuve. Cela ne mesure pas le temps total de développement. Le cumul
avec les étapes précédentes atteint 115 points sélectionnés sur v317.

Le HUD physique et les marqueurs de cristal sont également contrôlés à la
récupération du navire, après la récompense et à la sortie. Cette preuve de
parcours ne certifie pas toutes les images ou tous les sons. Les donjons 8
et 9, le palais et la fin sur ce binaire, les contenus optionnels, une campagne
PAL complète et les écarts globaux au RNG/raster/audio SMS restent ouverts.
Les pilotes D8 sont adaptés au binaire courant mais n'ont pas encore été
exécutés ; ils ne constituent pas une validation du huitième donjon.

- [Préparation, clés et Terre](d7_prep_v0317_report.json)
- [Combat intermédiaire sans protection](d7_midboss_v0317_report.json)
- [Navire, septième cristal et sortie](d7_campaign_v0317_report.json)
- [Reproductions partagées](campaign_d7_stream_v0317_report.json)
- [Captures et sources conservées](campaign-d7-v0317/manifest.json)
- [Nettoyage vérifié](campaign_d7_v0317_cleanup_report.json)
