# v317 — troisième et quatrième cristaux

Le parcours du binaire publié `7694654ec85dd6626c0e17ff1834e5893d4eb35481400a4725eac6b6f3503294`
continue depuis les deux premiers cristaux. La ROM et les sources du jeu ne
changent pas : les nouveaux résultats prolongent leur validation.

| Étape | Image finale du parcours | Résultat |
| --- | ---: | --- |
| Cadeau d'huile et escaliers | 40077 | Huile reçue, ressources conservées : 31 PV, 14 pièces, 24 magie |
| Troisième donjon et sortie | 55788 | Corde, mécanisme, clé, troisième cristal ; 56/56 PV |
| Cadeau d'or et achat de Terre | 62156 | Cadeau de 50 pièces, achat à 50 pièces ; Terre niveau 1, magie 48 |
| Quatrième donjon et sortie | 87389 | Deux passages Terre, canoë, clés, quatrième cristal ; 46/64 PV |

Le mécanisme du troisième donjon est ouvert avec des ennemis encore présents.
Les deux passages Terre du quatrième consomment chacun 8 points de magie.
Le canoë est réellement obtenu ; une reproduction indépendante observe 192
images de déplacement sur l'eau, dans deux salles. Aucun objet, or, santé,
progression, SRAM ou état primaire n'est importé dans ce parcours.

La protection de test autorisée reste limitée aux approches. Elle est retirée
dans la salle précédente à l'image 52002 avant le boss 69, puis à 79216 avant
le boss 6A. Les combats commencent aux images 52154 et 79319 avec protection
nulle. Le boss 69 apparaît avec les 32 PV de la source ; le boss 6A avec 30.
Les prédictions du contrôleur sont vérifiées sur 102 fenêtres pour le troisième
boss et 300 pour le quatrième. Les pièges à zéro PV de la salle 190 restent
présents ; l'étape atteint la salle sans prétendre les éliminer.

Le parcours sélectionné ne comporte aucune mort. L'essai de commandes
ordinaires `md-auto-v0317-d4-ordinary02`, qui meurt contre le quatrième boss,
est explicitement rejeté et conservé. Aucun changement du jeu n'est utilisé
pour transformer cet échec en réussite. Les dégâts au retour du quatrième
donjon restent présents : le personnage termine à 46/64 PV.

Avec les étapes antérieures, 47 points de contrôle sélectionnés reproduisent
les 65536 octets de RAM et le PNG final avec des commandes fixes. Les dix
nouveaux points huile/D3 redémarrent chacun à froid. Pour Terre et D4, le
lecteur de preuve existant est partagé entre des points croissants : deux
cœurs démarrés à froid reproduisent quinze points, sans import d'état primaire
ni choix de commandes à partir de la RAM pendant cette reproduction.

Ces deux lecteurs émettent 149545 images, contre 1077190 pour des redémarrages
indépendants à chaque point : 927645 répétitions de préfixe sont évitées.
Cette mesure concerne uniquement les lecteurs de preuve, pas le temps total
de développement. Les comparaisons de RAM complète, de PNG et le contrôle
d'absence de protection pendant les boss sont conservés.

Le HUD physique et les marqueurs des trois puis quatre cristaux sont
contrôlés aux sorties. Cela ne certifie pas chaque image ou son du parcours.
Les donjons suivants, le palais, la fin sur v317, les contenus optionnels, une
campagne PAL complète et la fidélité globale au RNG/raster/audio SMS restent
ouverts. Les résultats des anciennes ROMs ne les remplacent pas.

- [Huile et escaliers](oil_service_v0317_report.json)
- [Corde, mécanisme et clé](d3_progress_v0317_report.json)
- [Troisième cristal et sortie](d3_campaign_v0317_report.json)
- [Or et achat de Terre](earth_learning_v0317_report.json)
- [Canoë et passages Terre](d4_progress_v0317_report.json)
- [Quatrième cristal et sortie](d4_campaign_v0317_report.json)
- [Lecteurs de preuve partagés](campaign_stream_v0317_report.json)
- [Captures et sources conservées](campaign-d3-d4-v0317/manifest.json)
- [Nettoyage vérifié](campaign_d3_d4_v0317_cleanup_report.json)
