# Huitieme cristal, cle des voleurs et retour exterieur sur v0306

La ROM reste v0306, SHA-256 `3a12380b86c193148d1cbd29d68a880901860cfb1c276aa96d61d2da16ac2c01`. Aucun changement natif ni nouvelle version pour ces preuves.

Le parcours courant revient dehors en **29**, apres **235211 images**, avec **huit cristaux, 84/96 PV, 72/72 PM, 1 cle et 31 pieces**. La cle des voleurs et le bateau sont conserves. La hache1 est selectionnee, l'epee longue2 reste disponible et l'armure reste1.

Apres la victoire intermediaire sans assistance en1C9, la reprise declaree du garde est relue depuis une nouvelle partie. Elle verifie a nouveau l'entree et le combat intermediaires, le coup18PV et sa defaite, puis l'absence de rencontre du boss principal. Le garde reprend a203595 ; aucun PV,PM,argent,objet,acteur,progression ou SRAM n'est importe. Le soin ramasse normalement fait passer46PV a70PV.

Les mecanismes1EB et1EC sont actionnes avec UP, leurs drapeaux et passages sont verifies. Le sol transforme de1C8 est effectivement traverse. Terre ouvre1E8/cellule58 pour8PM et son portail rejoint1AA. L'interaction reelle en1A9 accorde l'objet15 (cle des voleurs), sa fenetre se ferme, puis le mecanisme19A ouvre1D8 ouest/1D7 est. Le trajet atteint1A6 avant le boss. Le masque de persistance de1C9 reste nul : aucun7A vivant ne reapparait sous le garde lors du retour. Posseder la cle ne prouve pas a lui seul tous ses usages sur les portes.

Le garde se termine a230425, soit31 images avant le combat196/type6B a230456,70PV et hurt0. Le boss original a80PV,16 de degats et2 d'armure. L'epee longue2 est choisie par le menu ; force6. Le premier checkpoint233456 laisse16PV au boss, le heros conserve70PV. Le checkpoint234391 prouve la victoire, le huitieme cristal, la fenetre fermee et96/96PV avec72/72PM. Aucun coup n'est encaisse pendant le combat.

La sortie emprunte196,1A6,1A7,1EB,1EA et rejoint29 a235211 images,84/96PV. Le garde n'est jamais reactive apres le retrait initial, y compris durant le retour. Les deux combats selectionnes verifient406 fenetres sur toute la RAM ; la sortie en ajoute19, soit425 au total.

Les onze nouveaux checkpoints positifs (huit de quete/approche, trois de combat/cristal/sortie) sont relus independamment depuis une nouvelle partie :65536 octets de RAM et PNG final identiques. Seul hero_hurt sert a l'assistance d'approche declaree.

Le profil avant chaque instruction normale jusqu'a235211 images observe **402 octets de marge de pile**, tas valide, RAM et PNG finaux identiques au checkpoint. Il commence apres l'initialisation materielle, a l'image14, et couvre ce parcours, pas tous les chemins possibles. Les128 mots physiques du HUD final et les huit indicateurs de cristal sont verifies.

Le neuvieme donjon, la fin, les sauvegardes, le hasard global SMS, les timings/audiovisuel globaux et le materiel restent a verifier. Le code final6D exige la hache2 ; la table originale place cette amelioration en11D (objet5,valeur2,index inventaire1). Sa collecte devra prouver le passage reel1 vers2, pas seulement une valeur deja non nulle.

Reproduction : `python tools/summarize_d8_thief_v0306.py`, puis `python tools/summarize_d8_campaign_v0306.py`. Rapports : `analysis/d8_thief_v0306_report.json`, `analysis/d8_campaign_v0306_report.json`. Archive locale sans perte : `analysis/d8-campaign-v0306`.
