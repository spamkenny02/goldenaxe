# v0309 : Death Adder et fin complete

Le scenario controle du palais atteint maintenant la fin du jeu. Il utilise
toujours **une SRAM synthetique derivee du parcours v0306 a neuf cristaux**.
Ce resultat ne remplace pas une campagne v0309 depuis Nouveau Jeu et ne
termine pas l'objectif de fidelite globale. Le binaire v0309 est inchange.

Apres la [phase3](controlled_palace_phase3_v0309.md),la protection est retiree
a151245 dans15C. Le vrai combat contre6D commence a151328 :100PV pour le
heros,hurt0 et90PV pour Death Adder. La hache doree est selectionnee.
Les114 fenetres de prediction reproduisent toute la RAM sans ecart de pile.
Aucune ecriture d'assistance,de PV,d'objet,de monstre ou de progression ne
survient apres151245.

Le jeu enregistre la defaite du donjon10 et declenche son vrai game14 a155151.
Le heros a48PV. Le point de reprise155152 est relu depuis le demarrage avec
les65536 octets de RAM et le PNG exacts.

La continuation execute les routines de fin de la ROM produite :

| Evenement observe | Image |
| --- | ---: |
| Neuf cristaux visibles autour du heros | 155477 |
| Debut du generique | 156170 |
| Generique termine | 163593 |
| Nouvelle pressionC,retour au flux titre | 163623 |
| Capture finale,pendant la nouvelle introduction | 163723 |

Les commandes musicales8D et88 sont observees a155433 et155838. Les captures
de la scene des cristaux et du generique ont aussi ete inspectees visuellement.
La continuation conserve exactement les ecritures du prefixe : aucune nouvelle
injection. Sa relecture fixe reproduit toute la RAM et le PNG final.

Le premier essai de retour donnaitC pendant le dernier tick du generique,
avant l'attente d'une nouvelle pression. Il est conserve comme essai incomplet.
Le controleur attend maintenant30 images apres la fin du texte ; le jeu natif
ne change pas. Le retour passe par l'introduction du flux titre : ce rapport
ne pretend pas comparer chaque image du titre a la Master System.

Voir le [rapport et les empreintes](controlled_palace_ending_v0309_report.json)
et le script `tools/summarize_controlled_palace_ending_v0309.py`.

Restent ouverts : campagne froide complete sur la version courante,contenus
optionnels,fidelite globale des images/sons/cadences et essais materiels.
Les neuf cristaux froids restent prouves sur v0306 ; le parcours froid v0309
est actuellement verifie jusqu'au retour du deuxieme donjon.
