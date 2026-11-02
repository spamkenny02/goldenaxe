# Premier gardien du neuvième donjon sur v0309

La campagne poursuit l'entrée vérifiée sur la même v0309 depuis Nouveau Jeu,
sans import de SRAM ni ajout de ressources. Les huit cristaux sont conservés.

| Étape | Image finale | Salle | PV | PM | Clés |
| --- | --- | --- | --- | --- | --- |
| earth_contact | 272518 | 1CE | 94/96 | 64 | 1 |
| earth | 272862 | 1CE | 94/96 | 56 | 1 |
| ready | 276463 | 1CE | 94/96 | 72 | 2 |
| close | 276464 | 1CE | 94/96 | 72 | 2 |
| combat | 278275 | 1BE | 78/96 | 72 | 2 |

Terre détruit la pierre 34 en 1DE, puis la commande UP active le mécanisme
et ouvre le passage vers 1CE. Le sort consomme huit PM. Une seconde
activation normale détruit la pierre 56 de 1CE pour huit PM supplémentaires.
Les ennemis de l'antichambre sont combattus normalement avec la protection
d'approche déclarée ; les ramassages rendent les PM et donnent une seconde clé.

La protection est retirée à l'image 276464 avant 1BE. Le premier combat
commence à 276636 : héros à 94 PV, compteur de blessure nul, gardien original
79 à 60 PV. L'épée longue de niveau 2 est sélectionnée par le menu normal.
Le héros reçoit un coup de 16 dégâts à l'image 278023 et gagne à 78/96 PV.
Aucune écriture de test ne suit le retrait pendant cet affrontement.

Les 184 fenêtres de prédiction du combat correspondent sur toute la RAM.
Les cinq points finaux sont relus indépendamment depuis le démarrage :
65536 octets de RAM et PNG final identiques. L'image finale a été inspectée.
Avec l'entrée, huit points de contrôle D9 sont couverts jusqu'ici.
Le géant optionnel 19C, le ballon et le boss principal 1AC restent à vérifier.

Reproduction : `python tools/summarize_d9_midboss_v0309.py`.
Voir le [rapport et ses empreintes](d9_midboss_v0309_report.json).
Sources figées : `validation/v0309-d9-first-mini-sources`.
Commandes exécutées : `validation/run_d9_midboss01.py`.

La fidélité globale SMS, le hasard, les contenus optionnels, la fin de cette
campagne, les sauvegardes et le matériel restent ouverts.
