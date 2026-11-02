# v0309 - Palais,phase controlee1

Ce scenario charge un enregistrement SRAM synthetique construit avec les
valeurs reelles du checkpoint v0306 neuf cristaux. Ce n'est pas une sauvegarde
ecrite par le jeu,ni une preuve de parcours v0309 depuis Nouveau Jeu. Les
imports initiaux sont declares :1. Apres le demarrage,seul le compteur de
protection d'approche est ecrit ; aucun PV,PM,objet,acteur ou avancement n'est
modifie par le controleur.

Le scenario valide l'ouverture8B en289 images,le trajet jusqu'a89 et l'entree
18D. Il active les mecanismes16D et16E,retire la protection en14646,puis bat
le geant7B en15E. Le premier combat a102PV et un delai naturel de blessure18
vient d'un contact avec le danger61 avant la salle ; aucune valeur129 ne
subsiste apres la fermeture de l'approche. La victoire est en21579,104PV apres
les ramassages normaux,avec209 predictions RAM exactes.

La protection d'approche reprend apres cette victoire verifiee. Le chemin
traverse les deux premiers portails,emploie Terre en14E puis11A,et actionne
le mecanisme129 qui ouvre le teleporter12A. La phase1 s'arrete en48495 en12A.
Quinze relectures independantes comparent65536octets RAM et le PNG entier.
Les checkpoints vivants interrompus restent identifies comme tels.

Le controle de fin de combat ne doit pas ignorer les enfants de monstres
alloues dans les slots8..15. Le premier arret14E conservait un enfant4C a6PV ;
il est tue trois images apres la reprise. L'etape clear14e01 verifie bien
l'absence d'acteurs dans les seize slots. Les dangers persistants a0PV sont
traites par les objectifs de mecanisme ou de traversee,et non comme des
monstres vaincus.

Le trajet est aide par le [guide Any% de Quarbit](https://www.speedrun.com/golden_axe_warrior/guides/yfxxr),
puis controle dans le jeu et dans les tables de la ROM. La carte du guide
reste locale ; elle n'est pas distribuee comme ressource du portage.

Un premier essai controle demarrait apres la mort du heros et a ete ecarte.
Ses captures redondantes ont ete archivees avec relecture et SHA-256 avant
suppression : environ1,79Go nets liberes. L'original,les309ROMs numerotees et
les deux alias sont verifies inchanges. Voir les rapports de nettoyage.

La hache doree,le gardien7C,Death Adder,la fin,le parcours froid courant complet
et la fidelite globale restent ouverts. Le rapport de cette phase est fige :
[phase1 et empreintes](controlled_palace_phase1_v0309_report.json).
