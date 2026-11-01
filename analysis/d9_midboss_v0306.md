# Premier boss intermediaire du neuvieme donjon sur v0306

La ROM reste v0306, SHA-256 `3a12380b86c193148d1cbd29d68a880901860cfb1c276aa96d61d2da16ac2c01`. Ce jalon n'ajoute aucun changement natif et ne cree pas de nouvelle ROM.

Le checkpoint courant est en **1BE**, a **252171 images**, avec **48/96 PV, 72/72 PM, 1 cle, 27 pieces et huit cristaux**. Le boss intermediaire79 est vaincu sans protection. L'epee longue2 est selectionnee par le vrai menu ; hache1, armure1, cloche de glace, cle des voleurs et bateau sont conserves.

Le trajet part de l'entree1FC a239841. Il nettoie1FD,1FE,1EE et1DE. Le premier essai se bloque ensuite : le point de contact de la torche est inaccessible tant que le bloc34 n'est pas casse. Cet essai negatif est conserve separement, sans relecture terminale revendiquee.

Le controleur combine utilise Terre normalement au point72,80 vers le haut. Le bloc34 de1DE passe de0B a0 et coute8PM. Le heros peut alors atteindre72,40 et presser UP (coord332), ouvrant le passage nord. Le checkpoint246418 atteint1CE a84PV,64PM et27pieces. Cette ouverture combine deux actions ; la magie seule n'actionne pas la torche.

Un deuxieme lancer de Terre en1CE, cellule56, point104,112 vers le haut, coute8PM et applique la transformation originale qui retire les quatre obstacles36..39. Le checkpoint246742 conserve84PV et56PM. Le nettoyage ordinaire de1CE s'acheve a250495 ; des ramassages normaux ont remonte les PM a72, sans changement des84PV.

La protection est retiree dans la salle vide1CE a250496, par une unique ecriture finale zero dans hero_hurt. Les ressources, objets et cristaux restent identiques. Le premier combat en1BE apparait a250692 :84PV, hurt0, acteur79 a60PV. Ses statistiques originales sont60PV,20degats,4armure,flag20. L'epee longue2 donne force6. Aucun acteur ni parametre du boss n'est modifie.

Le combat observe deux pertes :84->64PV a250835 et64->48PV a251525. Il se termine avec une salle vide et le passage nord ouvert. Les164 fenetres de prediction selectionnees reproduisent toute la RAM, sans import dans le processus principal ni ecart limite a la pile. La liste des ecritures reste exactement celle du prefixe clos ; aucune protection ne reprend pendant le combat.

Les cinq checkpoints positifs possedent une relecture froide independante depuis la nouvelle partie :65536 octets de RAM et PNG terminal identiques. Le nouvel audit compare aussi les objets, les huit cristaux, les donnees originales du boss et les empreintes des controleurs figes.

Le geant19C/type7B, le boss principal1AC/type6C, le neuvieme cristal, la Hache d'or, la fin et les sauvegardes restent a verifier. Le dernier profil de pile reste celui du huitieme donjon a235211 images (402octets observes), pas de ce nouveau parcours. Le hasard global SMS, les timings/audiovisuel globaux et le materiel ne sont pas prouves par ces relectures MD.

Reproduction : `python tools/summarize_d9_midboss_v0306.py`. Rapport : `analysis/d9_midboss_v0306_report.json`. Archive locale sans perte : `analysis/d9-midboss-v0306`. Les RAM du retrait250496 et de la victoire252171 sont conservees en clair pour la reprise.
