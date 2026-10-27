# v0294 : hache, fee de vie et entree du deuxieme donjon

Depuis la [premiere victoire](d1_campaign_v0294.md), le heros revient dans le premier donjon pour la cle1C5 puis la hache1B6. Il utilise cette cle pour ouvrir le passage, acquiert la hache par la fenetre de recompense, l'equipe par le menu et ressort enB9 a32/32 PV. Il conserve le premier cristal ; ce retour n'est pas une deuxieme victoire.

Le trajet suivant coupe normalement trois obstacles avec la hache et entre chez la fee de vie enC9. Le dialogue donne le premier coeur supplementaire et son soin :32 devient40 PV maximum et la vie atteint40/40. Le heros ressort normalement, drapeau du don deC9 positionne, puis rejoint la salle171 du deuxieme donjon, toujours a40 PV et hache equipee.

| Etape | Trace | Fin |
| --- | --- | --- |
| Retour pour la hache | md-v0294-d1-return-axe01 |15221|
| Cle1C5 | md-auto-v0294-d1-axe-key03 |18698|
| Acquisition de la hache | md-auto-v0294-d1-axe02 |20872|
| Sortie et hache equipee | md-auto-v0294-d1-axe-exit02 |21995|
| Entree chez la fee | md-v0294-fairy-route01 |23055|
| Don et soin termines | md-v0294-fairy-service01 |23572|
| Entree du deuxieme donjon | md-v0294-d2-entry01 |25735|

Les sept etapes ont chacune une relecture froide independante par commandes fixes :65536 octets de RAM et PNG final identiques. Aucun instantane n'est importe dans le coeur principal. Les seuls changements de RAM de test sont les compteurs de blessures consignes ; aucune vie,cle,hache,monnaie ou progression n'est injectee.

L'aide de la deuxieme approche commence apres la sortie deja verifiee du premier donjon, a15025. Elle couvre cette excursion et le trajet vers le prochain boss144. Celui-ci n'est pas encore entre : sa protection devra etre retiree avant son combat. Le premier boss175 conserve sa preuve distincte de combat ordinaire, avec le garde retire a12338. Le service de fee n'ajoute aucune ecriture d'aide ; il rejoue seulement celles heritees de l'approche. L'outil accepte maintenant explicitement ces prefixes assistes et conserve leur manifeste, en filtrant une eventuelle ecriture encore programmee apres la fin du prefixe.

[Rapport et empreintes](d2_approach_v0294_report.json). Reproduction : `tools/summarize_d2_approach_v0294.py`.

Limites : la ROM reste v0294. Le deuxieme boss, son cristal, la suite, la fin et la campagne SMS complete ne sont pas prouves par ce jalon. Les relectures finales ne comparent pas toutes les images intermediaires, les ondes audio ou la cadence physique du materiel.
