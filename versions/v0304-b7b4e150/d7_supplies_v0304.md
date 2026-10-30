# v304 : ravitaillement et premiere cle du septieme donjon

La ROM reste v304, SHA-256 `b7b4e15008a6f0a913c9ad43f15386abcdfbb719e5a575873d92712ba52503a8`. Cette etape poursuit le [sixieme cristal et son retour](d6_campaign_v0304.md).

La premiere approche de D7 atteint bien la salle1DB, mais sans cle. Le controleur ne trouve pas de trajet a travers sa porte superieure verrouillee. Ce diagnostic reste distinct du parcours retenu, qui repart de la sortie D6 verifiee.

Le ravitaillement obtient les dons normaux de30 cornes en7D et de30 enAC. EnAC, la hache coupe le vrai arbre1C et ouvre la maison. Les cornes passent de29 a59 puis89. Le marchand2E vend une cle a60 : il reste29 cornes. Aucun montant, objet ou drapeau de progression n'est injecte.

| Etape | Frame finale | Salle | PV /80 | Cles | Cornes |
| --- | ---: | --- | ---: | ---: | ---: |
| Approche7D | 154615 | 3F | 80 | 0 | 29 |
| Don7D | 154993 | 7D | 80 | 0 | 59 |
| ArbreAC et approche | 155700 | 3F | 80 | 0 | 59 |
| DonAC | 156073 | AC | 80 | 0 | 89 |
| Approche2E | 157845 | 0 | 76 | 0 | 89 |
| Achat de cle2E | 158455 | 2E | 76 | 1 | 29 |
| RetourD7 | 159361 | 1DB | 60 | 1 | 29 |
| Cle de la salle1CB | 160556 | 1CB | 60 | 1 | 29 |

La cle achetee est depensee a la porte1DB a la frame159409. Le drapeau20 de la porte est ensuite conserve. Le heros entre en1CB sans cle, termine le combat, puis ramasse la cle de cette salle :60/80 PV et une cle a160556. Les six cristaux, la cloche de glace, les bottes, la corde et le canoe restent acquis.

Les huit etapes du parcours retenu ont chacune une relecture a commandes fixes depuis le demarrage, avec65536 octets de RAM et le PNG final identiques. L'approche initiale sans cle possede aussi sa propre relecture exacte. Les essais de planification sans trajet et l'essai5D devant une entree fermee restent des diagnostics, sans revendication de defaut de la ROM.

Les aides d'approche sur hero_hurt sont explicitement consignees. Les six episodes precedents ont relache leur garde avant leurs boss ; le septieme boss179 n'est pas encore entre. Les visites et l'achat ajoutent zero ecriture d'aide. Ce parcours ne prouve pas une campagne entierement sans assistance.

Le [rapport reproductible](d7_supplies_v0304_report.json) relie les commandes, relectures, aides, sources conservees, tarifs et dons originaux. Le septieme boss et son cristal restent a verifier, ainsi que la suite, la fin, les sauvegardes et la fidelite complete SMS. Aucune nouvelle ROM numerotee n'est creee pour ces validations du programme inchange.
