# Palais v0309 — teleporteur,Terre et levier depuis la campagne froide

La suite du premier geant est parcourue dans la partie v0309 commencant a
Nouveau Jeu. Les neuf cristaux,le ballon et les objets de progression sont
conserves. Aucun import SRAM/RAM ni recharge artificielle de ressources.
Le seul garde de test est celui de l'approche,reactive apres la victoire
canonique contre le geant. La ROM distribuee est inchangee.

| Etape | Image finale | Salle | PV | PM | Or | Cles |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| resume | 327639 | 15E | 86 | 72 | 32 | 2 |
| portal | 336921 | 14E | 94 | 72 | 33 | 2 |
| earth14e | 337338 | 119 | 94 | 56 | 33 | 2 |
| earth11a | 342640 | 12A | 102 | 64 | 33 | 2 |
| switch | 344707 | 12A | 104 | 64 | 33 | 2 |

Le trajet du teleporteur est15E,15D,16D,16C,14D,14E. Une sortie/reentree
ordinaire16C a ete necessaire pour les ennemis separes. Le mecanisme16C est
reporte au retour ulterieur ;le teleporteur lui-meme reste utilise. Les16
emplacements d'acteurs de14E sont vides avant la premiere action Terre.

Terre14E cellule58 :ouverture337119,passage119 termine337238 ;72->56PM
observes pendant cette action (deux depenses de8). Terre11A cellule35 :
ouverture339547,passage12A termine342540 ;56->48PM a l'ouverture,puis
ramassages normaux jusqu'a64PM. Le levier129 est presse a343395,ouvrant le
flag distant12A ;retour12A termine344607,checkpoint344707 a104PV/64PM.

Chaque etape a une relecture independante exacte des65536octets de RAM et
du PNG final. Les128mots physiques du HUD et les neuf marqueurs sont aussi
verifies au dernier checkpoint. L'image finale a ete inspectee visuellement.
Voir le rapport JSON et tools/summarize_cold_palace_inner_v0309.py.
Sources mesurees :validation/v0309-cold-palace-inner01-sources ;les pilotes
sont identiques pendant les essais acceptes,les itineraires sont dans les
rapports et relectures de chaque etape.

Branches exclues :portal14e01 echoue sur la proposition16E->16D,sortie
inexistante ;portal14e02 a ete arrete volontairement apres verification du
processus possede,car le report du mecanisme16C manquait. Portal14e03 repart
du resume canonique327639 et corrige les deux points. Aucune de ces branches
exclues n'est un jalon de progression valide.

Le gardien11E,la vraie Hache d'or et Death Adder restent a parcourir ici.
Les preuves controlees du palais restent separees. Ces tests de progression
ne prouvent pas la fidelite globale RNG/phase SMS,les sauvegardes,le contenu
optionnel ou les essais sur console.
