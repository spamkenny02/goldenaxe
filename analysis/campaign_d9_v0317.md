# v317 — neuvième donjon

Le parcours continue sur le binaire publié
`7694654ec85dd6626c0e17ff1834e5893d4eb35481400a4725eac6b6f3503294`.
Aucune modification du programme n'est nécessaire pour les étapes vérifiées
ci-dessous.

## Retour sud et entrée vérifiés

Le parcours des huit premiers donjons termine sans mort à 96/96 PV.
Pour la suite, une branche utilise une mort et un Continue ordinaires pour
revenir au point de reprise sud. Le test d'or extérieur préalable n'a pas
obtenu de pièces avant sa limite de durée ; il est conservé comme échec et
ses écritures d'approche ne sont pas importées dans la branche retenue.
Deux propositions directes d'accès ont également été rejetées avant tout
nouveau parcours : mauvais prérequis du pilote, puis absence de chemin
piéton entre les régions. Ces diagnostics ne prouvent pas un bug de la ROM.

| Étape | Image finale du parcours | Résultat |
| --- | ---: | --- |
| Mort et Continue | 259652 | Région 95, 24 PV, 24 MP, 3 pièces |
| Arrivée chez le soigneur | 260012 | Maison 0 en région 94, 24 PV |
| Soin normal et sortie | 260609 | 96/96 PV ; 24 MP, 3 pièces, objets et huit cristaux conservés |
| Entrée du D9 | 264983 | Cloche utilisée au passage CB, arrivée en salle 1FC à 96/96 PV |

La mort est observée à 259453, le menu à 259545 et la reprise à 259650.
La pénalité d'or est celle du jeu : 6 → 3. Tous les objets et les huit
cristaux restent présents. Aucun PV, MP, or, objet, état de progression,
SRAM ou état primaire n'est importé. Le trajet et le soin après Continue
n'ajoutent aucune écriture d'aide.

Les trois points de récupération et l'entrée reproduisent les 65536 octets
de RAM et le PNG final avec des lecteurs indépendants démarrés à froid.
L'export initial du rapport de récupération a échoué sur un import Python
manquant, après la fin des trois reproductions. Le rapport a été reconstruit
par un audit des preuves existantes ; les parcours n'ont pas été relancés.

L'approche du D9 utilise ensuite la protection de test déclarée, limitée au
compteur de blessure. La cloche est sélectionnée et utilisée par les boutons
normaux : le drapeau CB et la cellule du passage changent réellement dans le
jeu. La protection devra être retirée avant chacun des gardiens.

## Premier gardien vérifié

| Étape | Image finale du parcours | Résultat |
| --- | ---: | --- |
| Terre et mécanisme en 1DE | 272439 | Passage vers 1CE franchi |
| Terre en 1CE | 272782 | Cellule 56 ouverte ; magie : 56 → 48 |
| Préparation | 275100 | Salle 1CE nettoyée, deux clés, 96 PV |
| Retrait de protection | 275101 | Protection nulle avant 1BE |
| Premier gardien vaincu | 276808 | Boss 79 absent, 96/96 PV, sans mort |

Le combat commence à 275292 : boss 79 à 60 PV, héros à 96 PV, protection
nulle. La victoire est observée à 276657. Les 169 fenêtres de prédiction
correspondent à la RAM persistante principale ; aucune différence de pile
réservée n'est écartée et aucune écriture d'aide n'est ajoutée au combat.
Les cinq points reproduisent également la RAM complète et le PNG final.

## Second gardien et ballon vérifiés

Le mécanisme de 1AD est franchi à 281120, puis la salle 19E à 282277.
La position d'approche en 19D est atteinte à 282514. Ses quatre pièges 62
restent présents et actifs malgré leurs PV nuls ; cette salle est franchie,
pas déclarée nettoyée. La protection est retirée à 282515 avant 19C.

Le second gardien 7B commence à 282566 avec 60 PV. Le héros a 96 PV et une
protection nulle. Le gardien est vaincu à 285731, sans dommage au héros ni
nouvelle écriture d'aide. Les 394 fenêtres de prédiction correspondent à la
RAM persistante principale et la reproduction finale RAM/PNG passe.

La protection d'approche reprend à 285883 après la victoire vérifiée. Le
ballon, objet 11, est reçu normalement en 19B ; sa récompense est terminée
au point 287629, avec 92/96 PV après les dégâts du trajet. Les huit points
de cette séquence passent la reproduction indépendante. Le HUD physique et
les huit marqueurs de cristal sont contrôlés avec l'objet acquis.

## Neuvième cristal et retour vérifiés

Le mécanisme final est franchi au point 293303, en salle 1BC, avec 96 PV.
La protection est retirée à 293304 avant 1AC. Le combat commence à 293421 :
boss source 6C à 90 PV, héros à 96 PV et protection nulle. Le héros reçoit
un coup de 20 PV à 296304. La récompense du neuvième cristal est terminée
au point 298786, avec 104/104 PV. Le retour extérieur en EB est vérifié à
300598, avec 74/104 PV, deux clés et 72 MP. Aucun garde n'est réactivé après
le retrait en 1BC. Les dégâts du retour restent dans l'enregistrement.

Les 288 fenêtres de prédiction du combat et les 48 du retour correspondent
à la RAM persistante principale. Le HUD physique et les neuf marqueurs de
cristal sont contrôlés après la récompense et à la sortie. Le D9 retenu ne
comporte aucune mort ; la mort normale pour revenir au sud reste explicitement
comptée dans la branche de préparation.

Les 21 nouveaux points, récupération comprise, reproduisent les 65536 octets
de RAM et le PNG final avec trois lecteurs démarrés à froid, partagés entre
étapes. Ils émettent 838015 images au lieu de 5868106 avec un redémarrage
à chaque point, soit 5030091 répétitions d'images de préfixe évitées pour les
seuls lecteurs de preuve. Cela ne mesure pas le temps total de développement.
Le cumul atteint 155 points sélectionnés sur v317. Aucune nouvelle ROM n'est
créée pour ces validations : le programme publié est inchangé.

L'activation du ballon, le palais et la fin sur ce binaire, les sauvegardes
de cette partie, les contenus optionnels, une campagne PAL complète et les
écarts globaux RNG/raster/audio SMS restent ouverts. Les pilotes du palais
et de sauvegarde sont préparés, pas encore exécutés.

- [Continue et soin](d9_recovery_v0317_report.json)
- [Cloche et entrée du donjon](d9_entry_v0317_report.json)
- [Passages Terre et premier gardien](d9_midboss_v0317_report.json)
- [Second gardien et ballon](d9_balloon_v0317_report.json)
- [Neuvième cristal et retour](d9_campaign_v0317_report.json)
- [Reproductions partagées](campaign_d9_stream_v0317_report.json)
- [Captures et sources conservées](campaign-d9-v0317/manifest.json)
- [Nettoyage vérifié](campaign_d9_v0317_cleanup_report.json)
