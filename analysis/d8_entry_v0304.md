# v304 : passage payant, navire et entrée du huitième donjon

La ROM reste inchangée : SHA-256 `b7b4e15008a6f0a913c9ad43f15386abcdfbb719e5a575873d92712ba52503a8`. Ce parcours prolonge la [sortie du septième donjon](d7_campaign_v0304.md).

L’escalier du passage payant en 3C est dégagé par de vrais coups de hache. Sa bouche habituelle au sud est bloquée par le relief : le contrôleur possède maintenant une direction d’entrée optionnelle et rejoint cet escalier par le haut. Le comportement distribué du jeu ne change pas.

Le passage intérieur 9F utilise ses vrais dialogues et sa confirmation. Les cornes passent de 41 à 31, puis le héros marche vers la sortie opposée. La destination de la table SMS est 1A, position (232,32). Le héros conserve ses 16/88 PV, deux clés, 40 points de magie, ses objets et sept cristaux. Aucun soin, objet ou argent n’est ajouté par le test.

Depuis la côte, la route compte 73 étapes proposées : 1A, 2A, 29, puis l’entrée du donjon 1EA. Le héros embarque depuis le quai, traverse la mer et rejoint la salle d’entrée avec la hache équipée.

| Étape | Frame finale | Salle | PV | Cornes | Clés |
| --- | ---: | --- | ---: | ---: | ---: |
| Escalier et entrée du passage | 190777 | 9F | 16/88 | 41 | 2 |
| Paiement et sortie côtière | 191130 | 1A | 16/88 | 31 | 2 |
| Entrée du huitième donjon | 191720 | 1EA | 16/88 | 31 | 2 |

Les trois étapes ont une relecture indépendante à commandes fixes depuis le démarrage : 65536 octets de RAM et PNG final identiques. L’approche conserve une huitième séquence de protection de test explicitement journalisée sur hero_hurt ; elle devra être retirée avant le boss 196/type6B. Aucun état secondaire n’est importé dans le jeu.

Deux essais directs vers la mer restent des diagnostics : leur proposition statique se bloquait au pont transformé de 49. L’option de recalcul sur la carte affichée constate ce blocage, puis la route retenue utilise le véritable passage payant.

La proposition des salles du donjon provient de la ROM SMS, avec ses portes et téléporteurs. Elle indique le boss 196/type6B et la clé des voleurs en 1A9, mais ne prouve pas encore ces traversées. Le [rapport reproductible](d8_entry_v0304_report.json) lie les sources, captures et relectures de l’entrée. Le contenu de D8, les donjons suivants, la fin, les sauvegardes et la fidélité globale restent à vérifier.
