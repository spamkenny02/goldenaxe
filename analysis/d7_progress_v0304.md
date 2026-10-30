# v304 : navire et passage distant du septieme donjon

ROM inchangee : `b7b4e15008a6f0a913c9ad43f15386abcdfbb719e5a575873d92712ba52503a8`. Suite du [ravitaillement D7](d7_supplies_v0304.md).

La salle1B9 fournit sa cle. Terre degage ensuite les cellules36 et2B, avec deux depenses normales de8 points de magie. La commande de cette salle ouvre la suite vers1B8. Le dragon intermediaire de type78 est actif puis vaincu pendant cette approche assistee ; ce combat ne constitue pas une preuve sans protection.

Une autre cle, provenant du butin d'un ennemi, reste encore presente apres le ramassage de la cle de salle. Elle est recoltee en allant lancer Terre : le compteur passe de2 a3. Les tables originales autorisent cette cle pour la classe de butin5 du type5A. La sequence globale du hasard SMS reste a reproduire ; ce constat ne prouve pas le meme butin au meme moment sur SMS.

| Etape | Frame finale | Salle | PV /80 | Cles | Magie |
| --- | ---: | --- | ---: | ---: | ---: |
| Seconde cle1B9 | 165712 | 1B9 | 60 | 2 | 48 |
| Terre cellule36 | 166022 | 1B9 | 60 | 3 | 40 |
| Terre cellule2B | 166362 | 1B9 | 60 | 3 | 32 |
| Commande1B9 vers1B8 | 166648 | 1B8 | 60 | 3 | 32 |
| Branche sud vers1D6 | 172733 | 1D6 | 80 | 3 | 48 |
| Commande distante1E6 et retour | 174724 | 1D6 | 80 | 3 | 48 |
| Navire1D5 | 175880 | 1D5 | 80 | 3 | 48 |

Le trajet direct1D6 vers1D5 est ferme. Le script original de1E6 contient une commande HAUT a la coordonnee332, avec D=4 et E=D6. Elle ouvre a distance l'ouest de1D6 et l'est de1D5. Le parcours descend en1E6, actionne cette commande, evite le teleporteur de retour, puis remonte en1D6 et rejoint le navire. L'essai direct echoue reste un diagnostic separe, sans reutiliser un etat importe.

Le navire est acquis dans son coffre : emplacement16 a1, recompense fermee, jeu normal et hache equipee. Les quatre pieges persistants5E a zero PV et un ennemi44 a10 PV sont encore presents. La salle n'est donc pas declaree nettoyee. Le nouvel outil de prise d'objet termine sur l'acquisition reelle et la fin de sa recompense, sans exiger la disparition de tous les acteurs. Il ne modifie aucune memoire du jeu.

Sept nouvelles relectures independantes depuis le demarrage reproduisent les65536 octets de RAM et le PNG final. Le [rapport reproductible](d7_progress_v0304_report.json) lie ces preuves, les commandes, les aides, les tables originales et les sources conservees des controleurs. La protection d'approche ne touche que hero_hurt ; les soins et recharges observes dans les salles proviennent du jeu.

Six cristaux sont conserves. Le boss principal179 n'est pas encore entre ; sa protection doit etre retiree avant le combat. Le septieme cristal, les donjons suivants, la fin, les sauvegardes et la fidelite globale restent a verifier. La marge de pile de496 octets precedente s'arrete au retour D6 et ne constitue pas une mesure de ce nouveau parcours. Aucune nouvelle ROM numerotee pour ces changements d'outils de test.
