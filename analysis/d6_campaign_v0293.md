# v0293 : sixieme donjon termine dans la campagne native

Le sixieme cristal est conserve jusqu'au retour a l'exterieur8B. Le heros termine a74/80 PV, avec une cle,48 points de magie et la cloche de glace. La ROM distribuee reste v0293 ; ce jalon concerne les commandes de parcours, les preuves et la documentation.

Apres le [boss et le cristal](d6_boss_v0293.md), le retour traverse115,125,124,123,113,114, puis utilise les portails114 vers138 et138 vers169. Il rejoint168,178,177,187 et ressort en8B. La sortie est observee a151825 ; le trace se termine a151975. Les six octets de progression des cristaux sont verifies directement dans la sauvegarde en RAM.

Le garde de l'approche reste retire depuis145093, avant le combat du boss a145124. La sortie n'ajoute aucune ecriture d'aide. Une perte ordinaire de6 PV est observee pendant le retour. Aucun soin, objet ou etat n'est importe. Les aides historiques des approches restent presentes dans les manifestes ; ce parcours n'est pas une campagne entierement sans aide.

Le controleur de sortie predit92 fenetres de RAM, toutes identiques a l'execution principale. La relecture independante a froid par commandes fixes retrouve les65536 octets de RAM et le PNG final exacts. Seul le coeur secondaire utilise des instantanes pour chercher des commandes.

Une correction de l'outil de navigation permet de quitter puis reentrer sur la case de contact d'un portail apres une arrivee sur place. Le script source exige un changement de coordonnee alignee ; attendre immobile ne le declenche pas. Cette correction ne change aucun code du jeu. Le premier essai bloque et l'erreur d'initialisation de l'essai suivant restent des diagnostics distincts.

[Rapport reproductible](d6_campaign_v0293_report.json). Commande : `tools/summarize_d6_campaign_v0293.py`, a partir des preuves locales. Le [jalon de l'approche](d6_progress_v0293.md) couvre quinze autres etapes et la cloche de glace.

Un [rapport complementaire](d7_entry_v0293_report.json) etend le controle de pile a151975 : minimumF798, limite du tasF600, soit408 octets de marge observee, sans en-tete invalide et avec RAM/image finales exactes. Il confirme aussi le trajet exterieur sans nouvelle aide vers l'entree1DB du septieme donjon, ou le heros arrive a16/80 PV. Ce n'est pas une victoire dans le septieme donjon.

Limites : campagne native NTSC en detection automatique. La campagne SMS equivalente, toutes les images intermediaires, les ondes audio, le rythme global et le materiel reel restent a comparer. Les donjons7 a10 et la fin du jeu ne sont pas encore valides. La marge de pile observee sur ce parcours ne constitue pas une borne pour les chemins suivants.
