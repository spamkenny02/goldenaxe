# v304 : cloche de glace et accès au sixième boss

La ROM reste la v304,
`b7b4e15008a6f0a913c9ad43f15386abcdfbb719e5a575873d92712ba52503a8`.
Le programme du jeu reste inchangé. Le parcours repart du
[retour du cinquième donjon](d5_campaign_v0304.md).

Le pont du cinquième cristal est présent dans la carte 49 : cellules 4A/5A
à 0A/6B. Le héros le traverse réellement et entre dans le sixième donjon.
Les mécanismes, portails et passages de Terre conduisent ensuite au coffre
de la cloche de glace. L'objet 10 est acquis et sa salle nettoyée. Le dernier
rocher 7B de 125 est détruit par un tir vers le bas.

Le checkpoint finit à la frame 146 682 dans la salle 125, avant l'entrée
chez le boss 64 de 115 : 72/72 PV, zéro clé, zéro magie, cinq cristaux,
cloche de glace, bottes, corde et canoë conservés.

Seize étapes ont chacune une relecture indépendante depuis le démarrage,
avec les 65 536 octets de RAM et le PNG final identiques. Le
[rapport reproductible](d6_progress_v0304_report.json) contient chaque
étape, son état final et les empreintes des preuves.

Les événements consignent cinq clés obtenues et cinq dépensées, depuis
zéro jusqu'à zéro. Sept baisses de huit unités de magie sont observées
pendant les actions de Terre, soit 56 unités. La réserve commence à 48 et
finit à zéro, avec un bilan net de huit unités regagnées hors de ces baisses.
Ce bilan concerne ce parcours ; il ne compare pas les tirages aléatoires
ou toutes les acquisitions de ressources à une campagne SMS équivalente.
Aucune clé, magie, vie ou possession n'est injectée dans la campagne.

## Gestion des commandes dans l'outil de Terre

Deux essais restaient bloqués dans l'inventaire. Quand l'activité des ennemis
changeait, l'outil de Terre rendait les commandes à celui de combat pendant
la sélection du sort ou le retour à la hache. Celui-ci cherchait alors une
autre sélection depuis une ligne du menu qu'il ne savait pas quitter.

L'outil de Terre conserve désormais les commandes après le début de sa
séquence jusqu'au rééquipement de la hache. La ROM et son inventaire ne
changent pas. Le passage 125 réussit ainsi avec les options habituelles.
Un essai supplémentaire du cas 135, sans l'option de lancement pendant
le combat, retrouve exactement les boutons, écritures d'aide, RAM et PNG
du parcours réussi qui utilisait cette option. Il dispose aussi de sa
propre relecture indépendante. Les deux échecs restent des diagnostics,
sans être présentés comme des défauts établis de la ROM.

Les aides d'approche restent explicitement consignées et ne touchent que
le compteur de blessures. Les actions préparatoires de 135 et 125 prouvent
le dégagement des blocs ; elles ne sont pas des preuves de victoire dans
leurs salles ni chez le boss. Les essais du sixième boss sont distincts
de ce checkpoint. La fin, les sauvegardes, le hasard global et la fidélité
complète vidéo/audio/matériel restent ouverts.
