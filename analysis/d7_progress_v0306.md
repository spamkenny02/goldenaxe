# Septieme donjon : combat intermediaire et bateau sur v0306

La ROM reste v0306, SHA-256 `3a12380b86c193148d1cbd29d68a880901860cfb1c276aa96d61d2da16ac2c01`. Le code natif n'a pas change pendant ces validations.

Le parcours courant atteint la salle 1D5 apres **184383 images**, avec **80/80 PV, 72/72 PM, deux cles, 27 pieces et le bateau**. Les six cristaux precedents sont conserves ; le boss principal179 et le septieme cristal ne sont pas encore atteints.

Dix nouveaux checkpoints positifs sont relus depuis une nouvelle partie : 65536 octets de RAM et PNG final identiques. Ils couvrent une cle supplementaire, deux lancers de Terre a8PM, le retrait du garde, le passage vers le combat intermediaire, sa victoire, la reprise declaree du garde d'approche, le trajet sud, le mecanisme1E6 et le bateau.

Le garde est retire a174623. Le combat intermediaire1B8/type78 commence a174808, avec80PV, hurt0 et30PV ennemis. Il est gagne a176005 sans perte de PV. Les135 fenetres de prediction correspondent sur toute la RAM ; aucun etat principal n'est importe. Le checkpoint retenu finit a176109.

La premiere recherche n'avait pas capture son image/RAM terminale. Une repetition des memes boutons, sans recherche ni import d'etat, reproduit les18 captures RAM/PNG deja conservees et verifie les valeurs finales observees. Ce nouvel enregistrement complet est ensuite relu independamment avec le coeur officiel ; RAM et PNG terminal sont identiques. Le premier enregistrement reste conserve et n'est pas presente comme une relecture complete.

L'essai suivant sans garde meurt en1B7. Son resultat negatif est egalement reproduit en RAM/PNG et exclu du parcours retenu. La protection autorisee d'approche reprend seulement apres la victoire intermediaire verifiee, a176110. Une relecture froide verifie l'entree et le combat intermediaires sans protection, leur victoire et l'absence de rencontre du boss principal avant cette reprise. Les anciens episodes sont conserves ; l'episode ferme est attribue au combat intermediaire effectivement observe. Le nouveau garde vise179 et devra etre retire avant son combat.

Le mecanisme1E6, UP en72,40, ouvre1D6 ouest/1D5 est. L'objet bateau est accorde par le jeu, sa fenetre est fermee par les boutons ordinaires. Quatre pieges type5E a0PV et un acteur vivant44 a10PV sont conserves. Le slot de cet acteur vivant est5 sur ce parcours ; aucun slot historique v0304 n'est impose a l'etat courant. La salle n'est pas declaree entierement nettoyee.

Apres la fenetre du bateau, les128 mots physiques du HUD correspondent au miroir SMS traduit et les six indicateurs de cristal correspondent a la table originale1EDC. La capture finale est inspectee visuellement.

Seul hero_hurt est utilise pour le garde de test. Aucun PV, PM, argent, objet, acteur, progression ni SRAM n'est injecte. Ces preuves ne valident pas encore le hasard global SMS, les timings et l'audiovisuel globaux, le septieme cristal, les derniers donjons, la fin, les sauvegardes ou le materiel. La marge de pile442 reste celle du parcours precedent jusqu'a162574 images.

Reproduction : `python tools/summarize_d7_midboss_v0306.py` puis `python tools/summarize_d7_ship_v0306.py`. Rapports : `analysis/d7_midboss_v0306_report.json`, `analysis/d7_ship_v0306_report.json`. Archive locale sans perte : `analysis/d7-progress-v0306`.
