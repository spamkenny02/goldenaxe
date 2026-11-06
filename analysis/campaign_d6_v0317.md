# v317 — cloche de glace et sixième cristal

Le binaire publié `7694654ec85dd6626c0e17ff1834e5893d4eb35481400a4725eac6b6f3503294`
est vérifié depuis le retour du cinquième donjon jusqu'au sixième cristal et
à la sortie extérieure 8B. Aucun changement du programme ou du binaire n'est
nécessaire pour cette progression.

| Étape | Image finale du parcours | Résultat |
| --- | ---: | --- |
| Sélection de la hache | 130727 | Menu normal, objets et ressources conservés |
| Cloche de glace | 155911 | Cinq récupérations de clés, mécanismes et passages Terre exécutés |
| Préparation devant le boss | 157622 | Cellule 7B de la salle 125 dégagée, boss pas encore entré |
| Retrait de protection | 157623 | Salle 125, 72 PV, protection nulle, ressources conservées |
| Sixième cristal et récompense | 166372 | Boss 64 vaincu, récompense terminée à 80/80 PV |
| Retour extérieur | 168019 | Portails et sortie 8B, 74/80 PV |

Les six étapes de Terre comprennent sept dépenses observées de 8 points de
magie ; le contrôleur lance deux fois le sort pour l'une d'elles. Les
réentrées ordinaires de salles, les consommations de clés et les gains
normaux de ressources restent dans l'enregistrement. Aucun acteur ou mur
n'est supprimé par le test. La cloche est effectivement reçue et son HUD
physique est contrôlé.

La protection de test autorisée reste limitée à l'approche. Elle est retirée
dans la salle précédente à l'image 157623. Le combat commence à 157724 avec
72 PV pour le héros, protection nulle, et le boss source 64 à 60 PV. Le héros
reçoit ensuite un coup de 14 PV. Le boss et le retour n'ajoutent aucune
écriture d'aide. Les objets, PV, magie, or, progression, SRAM et états
primaires ne sont pas importés dans la partie. Le parcours retenu ne comporte
aucune mort.

Les 251 fenêtres de prédiction du combat et les 56 du retour correspondent à
la RAM persistante du jeu principal. Les commandes enregistrées sont ensuite
reproduites indépendamment depuis le démarrage à froid : les 65536 octets de
RAM et le PNG final correspondent à chacun des vingt nouveaux points.
Le lecteur du trajet partage un démarrage entre ses dix-sept points, y
compris le menu de sélection de la hache. Le lecteur du combat et du retour
partage un second démarrage entre trois points.

Ces deux lecteurs émettent 325641 images au lieu de 2928726 avec un
redémarrage indépendant à chaque point : 2603085 répétitions de préfixe sont
évitées. Ce calcul concerne uniquement les lecteurs de preuve, pas le temps
total de développement. Avec les étapes précédentes, 92 points sélectionnés
sont vérifiés sur v317. Les sources natives sont également liées par SHA-256
au rapport du trajet.

Le HUD physique et les six marqueurs de cristal sont contrôlés après la
récompense et à la sortie. Cela ne certifie pas chaque image ou chaque son.
Les donjons suivants, le palais, la fin sur ce binaire, les contenus optionnels,
une campagne PAL complète et la fidélité globale au RNG/raster/audio SMS
restent ouverts.

- [Clés, Terre, mécanismes et cloche](d6_progress_v0317_report.json)
- [Retrait de protection avant le boss](d6_guard_release_v0317_report.json)
- [Sixième cristal et retour](d6_campaign_v0317_report.json)
- [Reproductions partagées](campaign_d6_stream_v0317_report.json)
- [Captures et sources conservées](campaign-d6-v0317/manifest.json)
- [Nettoyage vérifié](campaign_d6_v0317_cleanup_report.json)
