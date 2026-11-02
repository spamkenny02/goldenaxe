# v0309 : corde,troisieme cristal et retour

Le parcours depuis Nouveau Jeu sur la ROM courante valide maintenant trois
cristaux. Il prolonge la [sortie du deuxieme donjon](d2_campaign_v0309.md),
sans SRAM ni import d'etat. Les protections autorisees sur les approches sont
retirees avant les boss. Le retour du troisieme donjon reste sans protection.
Le binaire v0309 ne change pas.

| Etape | Image finale | Salle | PV |
| --- | ---: | --- | ---: |
| Entree D3 | 50436 | 1F8 | 33/48 |
| Corde et recompense terminee | 54658 | 1F4 | 48/48 |
| Mecanisme pendant le combat | 55144 | 1E3 | 48/48 |
| Cle obtenue normalement | 56605 | 1D2 | 48/48 |
| Antichambre degagee | 57766 | 1D3 | 48/48 |
| Retrait de la protection | 57767 | 1D3 | 48/48 |
| Troisieme cristal | 63012 | 1C3 | 56/56 |
| Retour dehors | 64422 | 62 | 48/56 |

Le mecanisme1E3 est active par Haut au point120,104,pendant que les ennemis
sont encore presents. Le heros repart par les couloirs pour obtenir la cle
en1D2,puis revient par la couronne exterieure de1E3. Le premier essai avait
quitte la salle de la cle avant sa collecte : sa tentative de boss bloquee
est exclue de la branche gagnante.

Le premier combat contre69 commence a57859,48PV,hurt0,boss32PV. Les139 fenetres
de prediction sont exactes sur toute la RAM,sans ecart de pile. Un coup normal
a62251 fait passer les PV48->40 ; le cristal donne ensuite son soin normal.
Aucune ecriture d'assistance ne survient apres57767,ni pendant le retour.

Huit relectures fixes reproduisent les65536 octets de RAM et le PNG final.
Les128 mots du HUD physique et les trois marqueurs de cristal sont verifies
apres la recompense et apres la sortie. La corde et l'huile sont conservees.
Voir le [rapport et les empreintes](d3_campaign_v0309_report.json).

Le controleur de sortie utilise maintenant le vrai itineraire pour ses
calculs ; les pas32 permettent de sortir avec neuf fenetres verifiees.
Un premier essai reste un checkpoint incomplet en1E3 et n'est pas une sortie.
Les metadonnees de l'episode sont completees par observation de toute l'entree
et du combat relus,ce qui permettra de commencer la prochaine approche apres
le retour dehors,avec les memes ecritures et aucune protection supplementaire.

Ce parcours reste aide sur les approches ; il ne constitue pas une campagne
entierement sans invincibilite. Il reste distinct du
[palais et de la fin en SRAM synthetique](controlled_palace_ending_v0309.md).
La campagne froide D4 et suivantes,les contenus optionnels et la fidelite
globale restent ouverts. La marge de pile402 octets mesuree sur l'ancien D8
v0306 n'est pas une mesure globale sur cette nouvelle campagne.
