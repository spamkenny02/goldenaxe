# v317 — huitième donjon

Le parcours continue sur le binaire publié
`7694654ec85dd6626c0e17ff1834e5893d4eb35481400a4725eac6b6f3503294`.
Aucune modification du programme n'est nécessaire pour les étapes vérifiées
ci-dessous.

## Soin, accès et combat intermédiaire

| Étape | Image finale du parcours | Résultat |
| --- | ---: | --- |
| Arrivée chez le soigneur | 214758 | 26/88 PV, après le trajet depuis le D7 |
| Soin normal et sortie | 215367 | 88/88 PV ; or, magie, objets et cristaux conservés |
| Arrivée au passage payant | 219917 | 88/88 PV, 14 pièces |
| Paiement | 220289 | Prix de 10 pièces, sortie en salle 1A, 4 pièces restantes |
| Entrée du D8 | 220877 | Salle 1EA, 88/88 PV |
| Salle précédant le combat | 223961 | Salle 1CA nettoyée, 88/88 PV |
| Retrait de protection | 223962 | Salle 1CA, protection nulle avant 1C9 |
| Combat intermédiaire terminé | 226609 | Boss 7A vaincu, 70/88 PV, sans mort |

Le boss intermédiaire commence à l'image 224214 avec ses 50 PV source.
Le héros a 88 PV et une protection nulle. Il reçoit un coup de 18 PV à
226419, puis vainc le boss à 226458. Les 279 fenêtres de prédiction
correspondent à la RAM persistante principale. Aucune écriture d'aide n'est
ajoutée pendant le combat.

Les huit points reproduisent les 65536 octets de RAM et le PNG final avec un
lecteur indépendant démarré à froid, alimenté par les commandes enregistrées.
Le soin est celui du jeu ; aucun PV, or, objet, point de magie, état de
progression, SRAM ou état primaire n'est importé. Les empreintes des pilotes
exécutés et de leurs copies sont liées au rapport. Les sept cristaux et le
navire restent présents.

## Mécanismes et clé du voleur

| Étape | Image finale du parcours | Résultat |
| --- | ---: | --- |
| Reprise de l'approche | 226610 | Protection réactivée après la victoire vérifiée |
| Traversée de 1C8 | 227806 | Salle nettoyée, 88/88 PV après les gains ordinaires |
| Premier mécanisme | 228358 | Contact en 1EB, accès de 1C8 ouvert |
| Deuxième mécanisme | 231658 | Contact en 1EC, retour en 1EB |
| Passage Terre | 241710 | Cellule 58 en 1E8, arrivée en 1AA, coût de 8 MP |
| Clé du voleur | 246715 | Objet 15 reçu normalement en 1A9 |
| Dernier mécanisme | 248817 | Contact en 19A, retour en 1AA |
| Salle précédant le boss | 251432 | Salle 1A6 nettoyée, 88/88 PV |

Ces huit points reproduisent également la RAM complète et le PNG final.
La protection d'approche préserve les dégâts du sol ; aucun acteur, mur ou
objet n'est supprimé par le test. Le boss intermédiaire vaincu reste absent
lors du retour par 1C9. Le HUD physique et les sept marqueurs de cristal
correspondent aux données source au dernier point de cette approche.

## Huitième cristal et retour vérifiés

La protection est retirée en 1A6 à l'image 251433. Le combat principal
commence à 251604 : boss source 6B à 80 PV, héros à 88 PV et protection
nulle. Le héros reçoit un coup de 24 PV à 253341. La récompense est terminée
à 256364 avec huit cristaux et 96/96 PV. Le retour extérieur en salle 29 est
vérifié à 257207, toujours à 96/96 PV, sans nouvelle écriture d'aide.

Les 510 fenêtres de prédiction du combat et les 28 du retour correspondent
à la RAM persistante principale. Les 19 nouveaux points reproduisent les
65536 octets de RAM et le PNG final avec deux lecteurs démarrés à froid,
partagés entre étapes. Ils émettent 483816 images au lieu de 4433850 avec
un redémarrage à chaque point : 3950034 répétitions d'images de préfixe sont
évitées pour les seuls lecteurs de preuve. Ce calcul ne mesure pas le temps
total de développement. Le cumul atteint 134 points sélectionnés sur v317.

Le HUD physique et les huit marqueurs de cristal sont contrôlés après la
récompense et à la sortie. Le parcours retenu ne comporte aucune mort.
La ROM n'a pas changé. Le neuvième donjon, le palais, la fin sur ce binaire,
les contenus optionnels, une campagne PAL complète et les écarts globaux
RNG/raster/audio SMS restent ouverts.

- [Soin, paiement, entrée et combat intermédiaire](d8_midboss_v0317_report.json)
- [Mécanismes, Terre, clé du voleur et approche](d8_approach_v0317_report.json)
- [Huitième cristal et retour extérieur](d8_campaign_v0317_report.json)
- [Reproductions partagées](campaign_d8_stream_v0317_report.json)
- [Captures et sources conservées](campaign-d8-v0317/manifest.json)
- [Nettoyage vérifié](campaign_d8_v0317_cleanup_report.json)
