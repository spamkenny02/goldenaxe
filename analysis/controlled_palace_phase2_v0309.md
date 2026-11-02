# v0309 : gardien du palais et hache doree

La phase2 prolonge la [phase1](controlled_palace_phase1_v0309.md) avec la meme
SRAM **synthetique**, derivee du parcours v0306 a neuf cristaux. Une seule
initialisation SRAM ; ce scenario ne prouve pas une campagne v0309 depuis
Nouveau Jeu. Le binaire v0309 est inchange.

Le contournement 12C -> 11C -> 11B -> 12B -> 12C -> 12D -> 12E permet de
rejoindre le gardien 7C en 11E. La protection de test est retiree avant la
salle, a l'image76953. Le premier combat commence a77054 avec104PV et hurt0.
Le controleur predictif verifie404 fenetres sur toute la RAM sans ecart de
pile, puis s'arrete sur un checkpoint vivant : le gardien a encore8PV.

Le controleur simple finit ce meme combat. Salle vide a90564, checkpoint
90715 :56PV,72PM,aucun deces,aucune ecriture d'assistance depuis76953. La
relecture fixe reproduit les65536 octets de RAM et le PNG. Le checkpoint a8PV
est une etape incomplete, pas une victoire supplementaire.

La protection d'approche reprend seulement apres cette victoire verifiee.
Le nouveau boss cible14C est absent de tout le prefixe controle. En11D,la
recompense normale donne la hache doree : inventaire1 passe de1 a2,l'animation
et le texte de recompense finissent,la hache2 est selectionnee. Checkpoint
93233 :80PV,72PM,2cles ; les PV recuperes viennent des ramassages normaux.
Aucune ecriture de PV,d'objet,de monstre ou de progression n'est ajoutee.

Neuf relectures fixes RAM/PNG couvrent les etapes de cette phase. Les premiers
points de navigation atteignant leur limite sont conserves comme etapes
incompletes. Voir le [rapport et les empreintes](controlled_palace_phase2_v0309_report.json)
et le script `tools/summarize_controlled_palace_phase2_v0309.py`.

Restent a prouver : combat final et fin sans injection apres l'approche,
campagne complete sur la ROM courante,fidelite globale SMS et essais materiels.
