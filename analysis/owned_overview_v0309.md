# Ballon possédé : carte générale et retour vérifiés sur v0309

Ce test continue directement la campagne aux neuf cristaux, après la sortie
EB. Le ballon a été réellement acquis en 19B. Aucun objet, PV, PM, argent,
acteur, progression ou SRAM n'est importé et aucune nouvelle protection
n'est ajoutée.

| Étape | Image |
| --- | --- |
| Activation par le menu et C | 302468 |
| Carte générale construite | 302964 |
| Retour au jeu, sélection remise à 0 | 303055 |
| Hache rééquipée par le menu normal | 303147 |
| Point final | 303247 |

Le héros reste en EB au même emplacement, avec 102/104 PV, 64 PM, 32 pièces,
deux clés, les neuf cristaux et le ballon. Les ressources sont conservées
pendant l'affichage de la carte. Le retour remet la sélection à l'épée,
comme prévu ; le pilote choisit ensuite la hache par le menu.

Les 5120 octets du fond SMS en mémoire, les 1280 octets de carte, les 160
cellules et les métadonnées de salle sont restaurés. Les 768 mots physiques
Mega Drive de la carte et du HUD correspondent à leur traduction ; les neuf
marqueurs sont présents. La carte affichée et l'écran final ont été inspectés.
Une relecture indépendante depuis le démarrage reproduit les 65536 octets
de RAM et le PNG final, sans lecture de retour pour choisir les boutons.

Reproduction : `python tools/summarize_owned_overview_v0309.py`.
Voir le [rapport et ses empreintes](owned_overview_v0309_report.json).
Pilote : `tools/natural_owned_overview.py` ; trace :
`validation/natural-dungeon-combat/md-auto-v0309-owned-overview01`.
Les tests contrôlés SMS/MD antérieurs restent séparés. Cette vérification
naturelle ne prouve pas tous les timings, le hasard global ou le matériel.
