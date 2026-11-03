# Premier geant du palais — campagne v0309 depuis Nouveau Jeu

Le premier geant du palais (15E, ennemi7B,60PV) est vaincu dans la partie
v0309 ayant acquis les neuf cristaux et le ballon, sans import SRAM/RAM.
La protection de test est retiree avant la salle du geant et aucune nouvelle
ecriture de test ne survient pendant le trajet restant ou le combat.
La ROM distribuee reste strictement identique.

- Mecanisme ouest16D :314779 ; mecanisme nord16E :321393, checkpoint321493.
- Retrait du garde :321494, en16E a104PV.
- Premiere rencontre :321571, hero102PV,cooldown naturel18,geant60PV.
- Degats naturels :321506 en16E104->102 ;327380 en15E102->82 ;32742862PV.
- Coeur ordinaire :32749662->86PV ; checkpoint de victoire327638,
  86/104PV,72PM,32or,2cles,neuf cristaux conserves.
- 185 predictions sur toute la RAM exactes. Les cinq checkpoints ont une
  relecture independante exacte des65536octets de RAM et du PNG final.
- HUD physique128mots et neuf marqueurs de cristaux exacts apres victoire.

Le premier essai pre-giant01 reste exclu : le pilote pressait la porte nord
fermee pendant qu'un56 etait absent. La correction porte seulement sur le
pilote : patrouille ordinaire lorsque56/59/5A cherchent une case d'apparition,
selon57F8 (terrain00,eloignement minimal sur les deux axes). Le nouvel essai
pre-giant02 repart du checkpoint canonique switch16d01 ; aucun ennemi n'est
modifie. Les sources mesurees avant/apres ce changement restent figees dans
validation/v0309-cold-palace-giant-sources et giant02-sources.

Le rapport JSON et tools/summarize_cold_palace_giant_v0309.py auditent les
sources,la filiation,les ecritures,les ressources,le boss et les relectures.
La capture finale a ete inspectee visuellement. Aucune aide financiere ni
aucun ravitaillement artificiel n'a ete utilise.

Le gardien11E,la vraie Hache d'or et Death Adder14C restent a rejouer dans
cette campagne. Les preuves controlees anterieures du palais restent
separees. Ce jalon ne prouve pas toute la fidelite aleatoire/phase SMS,
les sauvegardes,les contenus optionnels ou le fonctionnement sur console.
