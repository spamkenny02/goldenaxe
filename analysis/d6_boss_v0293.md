# v0293 : sixieme boss et cristal confirmes

Le boss64 de la salle115 est vaincu et le sixieme cristal est acquis sur la ROM v0293 existante. Le soin de recompense est termine : 80/80 PV et 48 points de magie. Aucun changement de code du jeu ni nouveau binaire n'est necessaire pour ce jalon.

Le garde de test de l'approche est retire a145093, avant le debut du combat a145124. Aucune ecriture d'aide ne suit. Le heros subit effectivement un coup a149386, passant de72 a58 PV ; la remontee finale a80 vient de la recompense du cristal. Aucun objet, soin, equipement ou etat sauvegarde n'est injecte. Les aides historiques des approches restent consignees : cette campagne n'est pas entierement sans aide.

Le premier segment de combat finit a148724 sans victoire. Le controleur de navigation poursuit ensuite avec des commandes ordinaires jusqu'a150173. Ses102 predictions de RAM correspondent toutes au coeur principal, sans difference de pile. Chaque segment est rejoue a froid par commandes fixes sur le coeur officiel ; les65536 octets de RAM et le PNG final correspondent exactement. L'essai de commandes laterales qui meurt avec4 PV restant au boss est conserve comme diagnostic et n'est pas utilise dans ce parcours reussi.

[Rapport et empreintes](d6_boss_v0293_report.json). Verification : `tools/summarize_d6_boss_v0293.py`, a partir des captures locales et de leurs relectures.

Ce rapport confirme le combat et le cristal, pas encore la sortie du donjon. La campagne SMS equivalente, toutes les images intermediaires, les ondes audio, le rythme global, le materiel reel, les derniers donjons et la fin du jeu restent a verifier. La marge de pile publiee precedemment ne couvre encore que le parcours jusqu'au cinquieme cristal et au pont.
