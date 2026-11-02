# Ravitaillement et entrée du septième donjon sur v0309

Le parcours poursuit le [retour D6](d6_campaign_v0309.md), depuis le même
Nouveau Jeu sans import de SRAM. La ROM reste v0309, SHA-256
`7270576d6eeb2aee641776a3e364f2f3f320711d70bb91a566d7578161261049`.
Le programme du jeu n'a pas changé pendant ces tests.

| Étape | Image finale | Salle | PV | Cornes | Clés |
| --- | --- | --- | --- | --- | --- |
| Don de 30 cornes | 183474 | 7D | 70/80 | 57 | 0 |
| Second don, après coupe AC/1C | 184554 | AC | 70/80 | 87 | 0 |
| Entrée chez le marchand | 186325 | Maison 0 de 2E | 66/80 | 87 | 0 |
| Achat normal d'une clé | 186934 | 2E | 66/80 | 27 | 1 |
| Entrée D7 | 187840 | 1DB | 50/80 | 27 | 1 |
| Porte franchie et première clé récupérée | 188960 | 1CB | 58/80 | 27 | 1 |

Les dons font réellement passer l'argent de 27 à 57 puis 87 cornes. Le
marchand prélève exactement 60 cornes pour la clé. Le trajet coupe l'obstacle
AC/1C avec la hache, ouvre la porte verrouillée de 1DB, puis obtient la clé
de 1CB par le jeu. Les PV évoluent normalement pendant le trajet et les
ramassages ; aucun soin n'est injecté.

Une visite au marchand de 94 avait été envisagée pour son soin gratuit.
Le planificateur n'a trouvé de chemin ni avec la carte de base ni avec la
carte courante du préfixe. Ces propositions échouent avant l'émulation et
ne constituent pas des points de contrôle. L'itinéraire retenu utilise le
marchand de 2E, déjà étudié. Aucun soin n'est revendiqué sur cette étape.

Les huit étapes, trajets compris, ont chacune une relecture fixe depuis le
démarrage, identique sur les 65536 octets de RAM et le PNG final. Les six
cristaux, la cloche de glace, Feu, Terre, épée longue, bottes, canoë et corde
sont conservés. La hache reste sélectionnée ; le bateau est encore absent.

Seules les protections d'approche déclarées utilisent `hero_hurt`, avec
préservation du délai naturel des dégâts de terrain. Aucun argent, objet,
PV, PM, acteur, progression ou SRAM n'est importé. L'autorisation d'argent
de test pour acheter des potions n'a pas été utilisée.

Ce rapport s'arrête avant le combat intermédiaire 1B8/type78 et le boss
principal 179/type67. La protection doit être retirée avant chacun de ces
combats. Le bateau, le septième cristal et le retour restent à valider.

Voir le [rapport et les empreintes des preuves](d7_supplies_v0309_report.json)
et l'[audit reproductible](../tools/summarize_d7_supplies_v0309.py).
Les sources des pilotes sont figées dans `validation/v0309-d7-sources`.
