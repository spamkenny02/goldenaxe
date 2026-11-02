# v0309 : derniers mecanismes et entree du boss final

Cette phase prolonge le [gardien et la hache doree](controlled_palace_phase2_v0309.md)
dans le meme scenario **SRAM synthetique controle**. Il reste distinct d'une
campagne depuis Nouveau Jeu. Une seule initialisation SRAM ; aucun PV,objet,
monstre ou flag de progression n'est injecte apres le demarrage. Le binaire
v0309 ne change pas.

Le vrai trajet execute les mecanismes suivants :

- Retour par les portails11C/12A et119/14E, puis magie Terre en13E pour
  reveler le portail vers16A. Un vrai lancement consomme8PM.
- Elimination des ennemis16A : le script de salle libere sa barriere.
  Ce n'est pas une cible de magie Terre. L'essai contraire s'est arrete sur
  l'assertion du type de bloc, avant toute nouvelle action.
- Interrupteur17C,qui active le flag4 de17B. Le detour par18B/18A/17A permet
  d'atteindre son portail depuis le bon compartiment et d'arriver en13C.
- Flamme14B,puis boucle13B/13A/14A et portail vers15A.
- Magie Terre en15B sur le bloc48,puis16B et16C.
- Interrupteur nord16C,qui donne acces a15C. Les ennemis caches sont reveilles
  et vaincus normalement ; la porte nord de15C donne sur Death Adder en14C.

Les checkpoints de navigation incomplets restent identifies comme tels.
La verification des collisions du terrain sert a choisir un trajet, puis
les commandes sont executees dans le jeu. L'inspecteur
`tools/inspect_recorded_dungeon_room.py` ne modifie aucun etat et ne remplace
pas la preuve d'un deplacement reel.

L'antichambre15C est vide a l'issue de cette phase :100/104PV,72PM,2cles et
hache doree selectionnee. Une image neutre retire la protection avant le
boss. Quinze relectures fixes reproduisent les65536 octets de RAM et le PNG.
Voir le [rapport et ses empreintes](controlled_palace_phase3_v0309_report.json).

Le combat final,la fin,la campagne froide complete sur la ROM courante et la
fidelite globale SMS ne sont pas prouves par ce rapport.
