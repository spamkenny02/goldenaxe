# Neuvieme cristal et retour exterieur sur v0306

La ROM reste v0306, SHA-256 `3a12380b86c193148d1cbd29d68a880901860cfb1c276aa96d61d2da16ac2c01`. Ce jalon n'ajoute aucun changement natif et ne cree pas de nouvelle ROM.

Le parcours courant est revenu dehors en **EB** a **270242 images**, avec **neuf cristaux,104/104 PV,72/72 PM,1 cle et37 pieces**. Hache1 selectionnee,epee longue2,armure1,cloche de glace,cle des voleurs et bateau conserves. Le ballon reste absent et le geant optionnel19C/7B n'est pas encore valide dans ce parcours.

La reprise252172 revalide depuis le demarrage la victoire sans protection contre1BE/79, puis reprend uniquement l'approche du principal1AC. L'ancien episode est retague vers le boss intermediaire reel, et l'episode12 reste cible sur1AC. Les ressources ne changent pas lors de cette reprise. Le masque BE est enregistre a0 en quittant la salle, et non au moment de la mort.

La torche AD,action UP au point72,40/coord332,ouvre19D ouest et19C est. Le checkpoint258545 est en1AD a72PV. Le nettoyage de19E s'acheve a259929,a68PV,avec son vrai portail ouvert. Un essai optionnel s'arrete en19D devant quatre acteurs62 a0PV : ce sont des dangers persistants, pas des ennemis a tuer ; cet essai est exclu des preuves positives et n'a pas de preuve terminale revendiquee.

Pour accelerer les controles, le trajet suivant regroupe le portail19E->1CC,le nettoyage deCC,la torche BC qui ouvre l'est et la torche droite BD qui ouvre BC nord. Il s'arrete en BC avant1AC a264600,96/96PV grace aux ramassages ordinaires. Une seule relecture froide couvre cette sequence complete.

Le premier essai du principal choisissait un deplacement lateral depuis le seuil bas et ressortait dansBC. Il ne fait aucun progres sur les90PV du boss et est exclu. Le nouveau controleur ajoute huit commandes UP ordinaires pour finir d'entrer avant le calcul des attaques. Aucun acteur,PV ou parametre de jeu n'est modifie.

Dans l'essai retenu,boss02,la protection est retiree avant le premier etat de combat12,en bonne sante et hurt0. Le boss original6C a90PV,30degats,6armure et le flag40. L'epee longue2 est equipee par le menu,force6. Les200 fenetres de prediction retenues sont identiques sur toute la RAM,sans import dans le processus principal ni ecart limite a la pile. L'entree UP et les decisions de16 images sont uniquement des choix de boutons.

Le checkpoint268635 prouve la victoire,le neuvieme cristal et sa fenetre fermee,104/104PV,72PM. La sortie suit AC,BC,CC,19E,AE,BE,CE,DE,EE,FE,FD,FC et revient enEB a270242. Aucune protection ne reprend pendant le combat ou le retour ; la liste des ecritures demeure close. La sortie n'a pas necessite de recherche secondaire.

Les six nouveaux checkpoints positifs possedent une relecture froide independante :65536 octets de RAM et PNG final identiques. Les128 mots physiques du HUD et les neuf indicateurs de cristal sont verifies au cristal et dehors. Le dernier profil complet de pile reste celui deD8 (402octets observes jusqu'a235211),pas ce nouveau trajet ; le prochain profil large sera fait au jalon final plutot qu'a chaque salle.

Les neuf cristaux ne prouvent pas un portage termine. Restent l'acces a la derniere partie,la Hache d'or,le boss final,la fin,les sauvegardes,le contenu optionnel restant et la fidelite globale du hasard,timings,audiovisuel. Le materiel reel n'a pas ete teste.

Piste de progression a verifier contre la ROM SMS : le guide [Any% de Quarbit](https://www.speedrun.com/golden_axe_warrior/guides/yfxxr) indique une cinematique en L8 (8B,l'ancienne entreeD6),puis l'acces final en J8 (89). La recherche statique ne trouve pas actuellement de marche directe vers89 ; cela seul ne prouve pas un defaut natif. Tracer l'evenement SMS avant de modifier le jeu.

Rapports : `analysis/d9_navigation_v0306_report.json`,`analysis/d9_boss_v0306_report.json`,`analysis/d9_campaign_v0306_report.json`. Reproduction : leurs trois outils summarize homonymes. Archive locale sans perte : `analysis/d9-campaign-v0306`. RAM de l'approche264600 et du retour270242 conservees en clair pour la suite.
