# v0293 : approche corrigee et premiere cle du septieme donjon

La campagne atteint l'entree1DB du septieme donjon a58/80 PV, puis nettoie la salle1CB et recupere sa cle, toujours a58 PV. Une cle a ete utilisee pour la premiere porte, puis une cle a ete gagnee normalement. Les six cristaux et la cloche de glace restent acquis. La ROM v0293 ne change pas.

La correction concerne uniquement le garde de blessures de l'outil de test. Auparavant, hors presence d'ennemis actifs, il ecrivait zero a chaque image. Cela effacait aussi le delai de48 images que le jeu applique apres un degat de sol. Le nouveau mode `--preserve-floor-hurt` retire uniquement le garde129 lorsqu'il est encore present ; il laisse le compteur ordinaire0..128 evoluer normalement. Les degats de sol continuent donc de se produire, sans soin ni remise a niveau de la vie.

Les deux approches comparees utilisent exactement les memes commandes, les memes pressions initiales, le meme nombre d'images et les memes ecritures de garde129. La seule difference executee est la suppression de867 ecritures de zero redondantes. Une868e ecriture figurait dans l'ancien journal pour l'image suivant la fin du test et n'a pas ete executee. L'ancien essai arrive a2 PV ; le nouvel essai arrive a58 PV. Les deux parcours et la premiere cle ont chacun une relecture froide independante par commandes fixes, avec65536 octets de RAM et PNG final exacts. Le premier essai n'est pas presente comme une erreur de la ROM.

Cette approche est assistee, avec toutes les ecritures consignees. Elle n'importe aucun etat et n'injecte ni vie, ni objet, ni argent. Le boss179 n'est pas encore atteint ; la protection doit etre retiree avant son combat. L'entree precedente a16 PV sans nouvelle aide exterieure reste conservee comme preuve distincte.

[Rapport reproductible](d7_approach_v0293_report.json), outil `tools/summarize_d7_approach_v0293.py`. Le [releve des donnees SMS](d7_source_route_proposal.json) propose les passages vers le navire de1D5 et le boss67 de179. Ce graphe repose sur les bords des cartes et les portails ; il ne prouve pas que les portes, collisions interieures et scripts autorisent encore tous ces trajets.

Le navire, le boss, le septieme cristal et la sortie restent a verifier, ainsi que les derniers donjons, la fin, la campagne SMS complete et la fidelite globale du rythme, de l'audio, des images et du materiel.
