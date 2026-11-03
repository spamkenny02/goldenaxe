# Mini-jeu v0310 : comparaison des frontends SMS/MD

Les douze cas passent : six scénarios en NTSC et PAL, chacun avec une exécution
SMS et une MD de 6 600 images. Le [bilan](minigame_rng_v0310_report.json) et
l'[audit lié aux captures](minigame_rng_v0310_audit_report.json) couvrent les
cartes ordinaires, chance/inversion, récompense, nouvelle partie avec paiement,
fonds insuffisants et refus d'entrée. Le cas ordinaire ouvre puis ferme aussi
l'inventaire après le premier tirage.

Chaque modification unitaire de l'argent correspond à la SMS. Les cases du
jeu, les cases statiques au retour, les 1 040 octets du bitmap de dialogue,
les quatre glyphes et les 48 octets du cadre de confirmation correspondent.
Les écarts d'animation de la maison sont explicitement conservés dans le bilan.
Les images MD de récompense et de retour ont été inspectées.

Le vieux pilote supposait que SGDK fournissait directement les cinq bits du
tirage ; depuis v310, il doit tenir compte de la graine SMS et du XOR. Ce nouveau
pilote réinitialise explicitement la graine native avant les choix contrôlés,
puis règle le fournisseur SGDK pour obtenir les cinq bits demandés. Les 28
échantillons après tirage ont effectivement la graine 733C : l'adaptateur de
production s'exécute. Le côté SMS utilise une ROM de test avec tirage forcé,
et la routine d'origine déplacée intacte. Les fichiers sources sont figés.
Les écritures de préparation et de contrôle sont déclarées dans les captures.

Ce test vérifie le fonctionnement du mini-jeu avec des tirages donnés. Il ne
prouve ni les probabilités naturelles, ni la phase exacte R/IRQ, ni la fidélité
temporelle globale, ni une arrivée naturelle jusqu'à cette maison. La ROM
publique reste strictement la v310 `32fe75a6…` ; aucune aide ou modification
native n'a été ajoutée et aucun nouveau numéro de ROM n'est créé.
