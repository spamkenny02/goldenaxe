# Gardien du palais et Hache d'or — campagne froide v0309

La partie v0309 commencee depuis Nouveau Jeu a vaincu le gardien11E/7C
(60PV) et recu la vraie Hache d'or en11D. Aucun import SRAM/RAM et aucune
recharge artificielle de ressources. La ROM distribuee reste inchangee.

| Etape | Image finale | Salle | PV | PM | Or | Cles |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| switch | 347516 | 12C | 104 | 72 | 33 | 2 |
| approach | 354193 | 12E | 104 | 72 | 34 | 2 |
| release | 354194 | 12E | 104 | 72 | 34 | 2 |
| guardian | 365263 | 11E | 104 | 72 | 34 | 2 |
| resume | 365264 | 11E | 104 | 72 | 34 | 2 |
| axe | 367133 | 11D | 104 | 72 | 35 | 2 |

Le levier12C est utilise avant de contourner la separation interieure par
11C,11B,12B,12C,12D,12E. Les ennemis de12C restent presents au levier :la
salle n'est pas declaree nettoyee. La salle12E est vide sur les16slots
avant retrait de la protection.

Retrait du garde354194 en12E ;premier combat354248 en11E,hero104PV/hurt0,
gardien60PV. Victoire effective365112,checkpoint365263. Aucun degat ni
aucune ecriture de test entre retrait et victoire. Les339predictions du
pilote concordent sur toute la RAM,sans difference reservee a la pile.
La reprise du garde365264 intervient seulement apres victoire canonique ;
les ressources sont conservees et l'episode suivant vise toujours14C.

Le cadeau11D fait passer la hache1->2 a366733 ;dialogue termine367033,
checkpoint367133 a104PV/72PM,35or,2cles,hache selectionnee. Le code original
5DC3 ecrit bien02 enC0E1 ;le catalogue du cadeau,son appel original et son
libelle sont lies a la ROM SMS fournie,et les relectures executent les
boutons normaux du jeu. Aucun objet ni ennemi n'est ecrit par le test.

Les six checkpoints disposent chacun d'une relecture independante exacte
des65536octets de RAM et du PNG final. Le HUD physique128mots et les neuf
marqueurs sont exacts apres acquisition. Les images de victoire et de la
Hache d'or ont ete inspectees visuellement. Voir le rapport JSON et
tools/summarize_cold_palace_guardian_v0309.py ;sources mesurees dans
validation/v0309-cold-palace-guardian01-sources.

La derniere portion du palais,Death Adder et le generique restent a rejouer
sur cette campagne. Les anciennes preuves SRAM controlees demeurent
separees. Ce bilan ne prouve pas toute la fidelite RNG/phase SMS,les
sauvegardes,les contenus optionnels ou les essais sur console.
