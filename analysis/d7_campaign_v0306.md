# Septieme cristal et retour exterieur sur v0306

La ROM reste v0306, SHA-256 `3a12380b86c193148d1cbd29d68a880901860cfb1c276aa96d61d2da16ac2c01`. Aucun changement de code natif ni nouvelle version pour ces preuves.

Le parcours courant termine le septieme donjon et revient en **1B**, apres **196280 images**, avec **84/88 PV, 64/72 PM, 1 cle et 29 pieces**. Les sept cristaux, le bateau, la cloche de glace, le canoe, la corde, les bottes, Feu, Terre et l'epee longue sont conserves. La hache1 est selectionnee pour le retour ; l'armure reste1.

Trois checkpoints de navigation depuis le bateau valident le retour nord, Terre1A8/cellule34 et son portail, puis le reveil ordinaire des sentinelles et l'ouverture de la porte vers189. Aucun etat v0304 n'est importe : les anciens rapports proposent seulement des destinations et parametres.

Le garde d'approche se termine a191693, soit28 images avant le combat179/type67 a191721. L'entree se fait a76PV, hurt0. Les4PV ont ete perdus avant le combat, pas contre le boss. L'epee longue2 est selectionnee avec le menu normal ; sa force native est6, face aux60PV et a l'armure2 originaux du boss. Les147 fenetres de prediction correspondent sur toute la RAM, sans import d'etat principal. Le heros conserve76PV durant le combat.

Le checkpoint194121 s'arrete apres la defaite, pendant l'animation : le progres vaut1, le cristal n'est pas collecte. Le checkpoint suivant194673 prouve son ramassage, la fermeture de la fenetre, sept marqueurs128,88/88PV et72/72PM. Cette distinction est verifiee explicitement.

Le retour utilise une selection ordinaire de la hache, puis Terre1B7/cellule57 pour8PM. La sortie se termine a196280 en1B,84/88PV et64/72PM. Aucun garde n'est reactive apres191693, y compris pendant le retour. Les dix predictions supplementaires de sortie correspondent sur toute la RAM.

Les sept nouveaux checkpoints positifs (trois de navigation, quatre de combat/cristal/retour) ont chacun une relecture froide independante :65536 octets de RAM et PNG final identiques. Seul hero_hurt est utilise pour l'assistance d'approche declaree. Aucun PV,PM,argent,objet,acteur,progression ou SRAM n'est injecte.

Le profil avant chaque instruction normale jusqu'a196280 images observe **442 octets de marge de pile**, tas valide, RAM et PNG finaux identiques au checkpoint. Le profil commence apres l'initialisation materielle, a l'image14 ; il couvre ce parcours, pas tous les chemins possibles. Les128 mots physiques du HUD final et les sept indicateurs de cristal sont verifies contre le miroir traduit et la table originale1EDC.

Le portage complet n'est pas declare termine : huitieme et neuvieme donjons, fin, sauvegardes, hasard global SMS, timings et fidelite audiovisuelle globale restent a verifier. Les preuves de partie MD et de pile ne constituent pas une comparaison de campagne complete avec la SMS ni une validation materielle.

Reproduction : `python tools/summarize_d7_navigation_v0306.py` puis `python tools/summarize_d7_campaign_v0306.py`. Rapports : `analysis/d7_navigation_v0306_report.json`, `analysis/d7_campaign_v0306_report.json`. Archive locale sans perte : `analysis/d7-campaign-v0306`.
