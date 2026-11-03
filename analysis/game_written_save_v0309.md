# Sauvegarde reelle et Continuer — v0309

Une branche separee du vrai parcours Nouveau Jeu apres le neuvieme cristal
rejointFA,ouvre l'arbre83 en5D avec la hache1,puis entre chez le sauvegardeur
6F. Aucun fichier SRAM initial et aucun nouveau garde ni ecriture de PV,
objets,or,cles,ennemis ou progression. Les anciennes aides d'approche du
parcours sont seulement relues ;aucune aide n'est ajoutee pendant ce test.
Cette branche ne remplace pas la campagne complete jusqu'aFIN.

Le trajet EB/FB/FA puis l'entree6F ont une relecture canonique exacte.
Le joueur confirme normalement Oui,puis l'emplacement0 :ecriture302961,
retour au jeu303022,checkpoint303172 a82/104PV,64/72PM,32or et2cles.
Le fichier SRAM reel fait3224octets dans cet export du coeur ;les quatre
derniers octets logiques FF du record sont absents de la fin du fichier.
Apres restitution de ces FF,les592octets correspondent exactement au bloc
serialise dans la RAM du jeu ;la metadonnee du dernier emplacement vaut1.

Une seconde execution depuis le demarrage,rejouant seulement les boutons
fixes et les anciens gardes autorises,reproduit exactement les65536octets
RAM,l'image finale et les3224octets SRAM. Un coeur NEUF importe ensuite
ce fichier ecrit par le jeu,choisit Continuer et rechargeFA normalement.
Aucune ecriture de RAM ni suppression d'ennemis n'est appliquee au reload.

Les statistiques et les17objets sont compares au payload reel,ainsi que les
neuf cristaux :premier controle possible1321,mouvement ordinaire confirme
1343,checkpoint1443. Le personnage reste a82PV/64PM. Le HUD physique128mots
et les neuf marqueurs sont exacts. L'arbreFA:5D est bien restaure sous sa
forme ouverte4,identique a la capture apres la coupe,avec son flag persistant.
Les images apres fermeture du dialogue et apres Continuer sont inspectees.

Le chargement importe necessairement UNE SRAM ECRITE PAR LE JEU ;il n'est
pas presente comme une campagne froide Nouveau Jeu ni comme l'ancienne
fixture synthetique du palais. Sources mesurees :
validation/v0309-game-written-save04-sources et04b-sources. Audits :
analysis/game_written_save_v0309_report.json,
analysis/game_written_save_audit_v0309_report.json et
tools/summarize_game_written_save_v0309.py.

Essais exclus :route01 n'avait pas coupe l'arbre ;save02 et03 ecrivaient
correctement mais le pilote appuyait de nouveau sur Haut a la restauration
hero0 et relancait le dialogue. Le pilote corrige attend neutre avant de
confirmer le retour hero1. Le premier appel du validateur04 etait refuse
avant emulation car il demandait circulairement sa propre future preuve ;
04b verifie d'abord le parent canonique,puis produit la relecture complete.
Aucun correctif du jeu ni nouvelle ROM n'a ete necessaire pour ces points.

Ce cas couvre l'ecriture normale de l'emplacement0 et son vrai chargement.
Les autres emplacements/refus/annulation,les comparaisons temporelles SMS
completes,les contenus optionnels et les essais materiels restent distincts.
La recurrence/phase aleatoire de production reste egalement a raccorder ;
ce test ne termine pas l'objectif complet du portage.
