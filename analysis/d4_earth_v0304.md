# v304 : Terre et premier accès du quatrième donjon

La ROM reste la v304, SHA-256
`b7b4e15008a6f0a913c9ad43f15386abcdfbb719e5a575873d92712ba52503a8`.
Le programme du jeu ne change pas à cette étape.

Depuis le retour du troisième donjon, sept nouveaux segments sont exécutés
sur cette ROM, puis rejoués indépendamment depuis le démarrage avec les
boutons enregistrés. Les 65 536 octets de RAM et le PNG final correspondent
pour chacun. Les protections d'approche restent explicitement enregistrées ;
aucune vie, monnaie, clé, possession ou progression n'est injectée.

- Maison F4 ouverte à la hache ; don réel de 50 cornes, de 8 à 58.
- Montée avec la corde acquise ; arbre spécial 4A coupé en A3.
- Dialogue du maître de la Terre : paiement de 50 cornes, niveau 1,
  réserve magique de 24 à 48. Sortie à 46/56 PV et 8 cornes.
- Entrée réelle du quatrième donjon, puis première clé obtenue en 1F1.
- Sélection du sort dans le menu ; Terre détruit le rocher 58 de 1E1,
  consomme 8 unités et ouvre le passage vers 1D1. La hache est rééquipée.
  Le segment finit à 54/56 PV, après du butin normal. La salle 1D1 n'est
  pas déclarée nettoyée.

Le [rapport consolidé](d4_earth_v0304_report.json) lie les états, commandes,
relectures et empreintes aux données exécutées. Le dernier segment validé
se termine à la frame 67 098.

## Capture simultanée avec un coup mortel

L'essai suivant atteint A1 (1A1), mais termine son budget de 76 000 frames
avec une seule clé et le héros dans l'état de capture 12. Il n'est pas compté
comme une salle terminée. Une relecture fixe de diagnostic observe qu'à la
frame 71 822 le voleur qui vient de capturer le héros reçoit un coup mortel.
Son acteur devient une particule de mort ; le héros reste capturé alors
qu'aucun voleur n'est encore attaché. Les directions seules ne le libèrent pas.

Un test isolé initialise ce cas dans une copie de la ROM SMS puis exécute
les routines originales 5043 (voleur) et 2768 (dégâts en attente). Il obtient
aussi le héros en état 12 et le voleur mort, type 1, PV zéro. Cette preuve
porte sur l'ordre des routines dans un cas contrôlé ; elle ne prouve pas
une reproduction pendant une partie normale sur SMS.

La suite doit reprendre depuis le passage validé avec une autre conduite du
combat, en conservant ce diagnostic. Aucun correctif de comportement n'a été
introduit sur la seule hypothèse que le blocage était propre au portage.

Le canoë, le quatrième cristal, la fin, les sauvegardes et la fidélité complète
vidéo/audio ne sont pas validés par cette étape. La marge de pile de 496 octets
publiée auparavant couvre seulement le parcours jusqu'au retour du troisième
donjon ; aucune extension de sa portée n'est revendiquée ici.

Suite validée : [quatrième cristal et retour sur v304](d4_campaign_v0304.md).
