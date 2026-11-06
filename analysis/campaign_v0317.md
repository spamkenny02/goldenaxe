# v317 — nouveau parcours jusqu'au deuxième cristal

Le binaire publié `7694654ec85dd6626c0e17ff1834e5893d4eb35481400a4725eac6b6f3503294`
a été joué depuis Nouveau jeu jusqu'au retour extérieur après le deuxième
donjon. La ROM reste v317 : cette étape ajoute des preuves de progression,
sans changement du code du jeu ni du binaire.

| Étape | Image finale du parcours | Résultat |
| --- | ---: | --- |
| Premier donjon et retour extérieur | 16178 | Premier cristal, 28/32 PV |
| Hache, première fée et entrée du deuxième donjon | 26351 | Hache acquise et équipée, 40/40 PV |
| Deuxième donjon et retour extérieur | 37814 | Deux cristaux, 31/48 PV |

Les 22 points de contrôle sélectionnés ont chacun été reproduits depuis un
démarrage à froid avec les commandes enregistrées : les 65536 octets de RAM
et le PNG final sont identiques. Aucune mort ni commande audio native non
prise en charge n'a été observée sur les étapes sélectionnées.

La protection de test autorisée par l'utilisateur ne concerne que les
approches. Elle est retirée dans la salle précédente, à l'image 13569 avant
le premier boss et 33950 avant le second. Les combats commencent aux images
13779 et 34073 avec une valeur de protection nulle. Aucun ajout de vie,
d'argent, d'objet, de progression, de SRAM ou d'état primaire n'est utilisé.
Le premier boss apparaît avec le type source 68 et 12 PV ; le deuxième avec
le type 63 et 30 PV. Le deuxième combat inflige effectivement des dégâts au
héros ; son résultat accepté n'est pas un essai invincible.

Les prédictions du contrôleur secondaire sont contrôlées contre la RAM du
jeu principal : 33 fenêtres pour le premier boss et 99 pour le second.
Le jeu principal conserve un démarrage à froid ; seuls les cœurs secondaires
de recherche chargent des instantanés. La reproduction indépendante avec
commandes fixes vérifie ensuite les points de contrôle complets.

L'essai `md-auto-v0317-d2-boss01` est rejeté : le pilote évite les attaques
mais laisse le boss à 20 PV à la limite de 43950 images. Il reste archivé.
L'essai sélectionné `boss02` utilise une recherche prudente et gagne le combat.
Le diagnostic de décalage de l'ancien parcours est aussi conservé : un simple
décalage de sept images ne reproduit pas les rencontres et ne constitue pas
une preuve de régression du jeu.

Au retour du deuxième donjon, les 128 mots physiques du HUD correspondent à
la traduction de la VRAM logicielle et les deux marqueurs de cristal à la ROM
source. Cela ne certifie pas chaque framebuffer du parcours.

Les donjons suivants, la fin sur ce binaire, les contenus optionnels, un
parcours PAL complet, la fidélité globale du RNG, du raster et des formes
d'onde audio restent à vérifier. Les preuves de campagne des anciennes ROMs
ne sont pas reprises comme preuves de la v317.

- [Premier cristal et sortie](d1_campaign_v0317_report.json)
- [Hache, fée et entrée du deuxième donjon](d2_approach_v0317_report.json)
- [Deuxième cristal et sortie](d2_campaign_v0317_report.json)
- [Captures et essais conservés](campaign-v0317-progress/manifest.json)
- [Nettoyage des captures intermédiaires](campaign_v0317_cleanup_report.json)
