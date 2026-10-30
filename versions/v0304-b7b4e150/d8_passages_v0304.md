# v304 : partie ouest et mécanismes distants de D8

La ROM reste inchangée : SHA-256 `b7b4e15008a6f0a913c9ad43f15386abcdfbb719e5a575873d92712ba52503a8`. Ce point continue l’[entrée D8](d8_entry_v0304.md).

Le parcours traverse 1EA, 1DA, 1CA, 1C9 puis 1C8. Les ennemis cachés apparaissent par leur proximité normale et le héros ramasse de vrais soins : il passe de 16 à 40/88 PV, sans écriture sur sa vie. Le type7A de 1C9 est affronté pendant l’approche protégée ; sa victoire ne constitue pas un combat validé sans aide. Des projectiles demeurent en 1C8 après la défaite des ennemis des huit premiers emplacements.

Le téléporteur de 1C8 mène ensuite en 1EB. Après son combat, une commande UP en (72,40), coordonnée source332, active le mécanisme : le drapeau de 1C8 passe de144 à148. Le contrôleur attend le drapeau distant, après le redessin, pour constater l’ouverture.

La salle 1EC possède un second mécanisme. Une commande UP en (184,40), coordonnée source360, ouvre la sortie ouest de 1EB et l’entrée est de 1EA. Le héros revient réellement dans 1EB ; le checkpoint se termine à 40/88 PV, deux clés et 48 points de magie. La hache, le navire et sept cristaux sont conservés.

| Étape | Frame finale | Salle | PV | Clés | Magie |
| --- | ---: | --- | ---: | ---: | ---: |
| Partie ouest | 200078 | 1C8 | 40/88 | 2 | 48 |
| Mécanisme distant de 1EB | 201255 | 1EB | 40/88 | 2 | 48 |
| Mécanisme de 1EC et retour | 203862 | 1EB | 40/88 | 2 | 48 |

Trois relectures indépendantes à commandes fixes depuis le démarrage donnent 65536 octets de RAM et PNG final identiques. Aucun état secondaire n’est importé dans le jeu. Les aides d’approche portent uniquement sur hero_hurt et sont déclarées dans les journaux.

Deux essais restent des diagnostics du contrôleur : key01 attendait une clé dans une salle dont la récompense transforme la carte ; switch1ec-01 avait déjà atteint sa salle cible avant de poursuivre vers le mécanisme. Ils sont exclus de la chaîne retenue.

Le [rapport reproductible](d8_passages_v0304_report.json) lie sources, interactions et relectures. Le passage transformé de 1C8 n’est pas encore traversé dans ce checkpoint. La clé des voleurs, le boss principal 196/type6B, le huitième cristal et le retour restent à vérifier, ainsi que les donjons suivants, la fin, les sauvegardes et la fidélité globale.
