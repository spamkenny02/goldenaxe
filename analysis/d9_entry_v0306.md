# Acces au neuvieme donjon sur v0306

La ROM reste v0306, SHA-256 `3a12380b86c193148d1cbd29d68a880901860cfb1c276aa96d61d2da16ac2c01`. Aucun changement natif ni nouvelle version pour ce parcours.

Le checkpoint courant est en **1FC**, entree du neuvieme donjon, a **239841 images**, avec **84/96 PV, 72/72 PM, 1 cle, 21 pieces et huit cristaux**. La hache1 est selectionnee ; epee longue2, armure1, cloche de glace, cle des voleurs et bateau sont conserves.

Le trajet repart du huitieme donjon, dehors en29 a235211. L'acces au transport1A/9F s'acheve a235791. La traversee normale coute10 pieces (31 vers21), conserve les ressources et rejoint3C a236169, position24,144. Aucun argent, objet, acteur, PV ou etat SRAM n'est importe.

La carte de base proposait initialement un raccourci maritime par49. L'essai01 s'arrete a235432 devant le pont deja transforme du cinquieme donjon ; il est exclu des preuves positives et ne dispose pas d'une relecture terminale. Une seconde recherche statique tenant compte du pont ne trouve aucun trajet direct. Le trajet retenu utilise le transport, puis les transformations persistantes effectives du monde.

En CB, la cloche deja obtenue est choisie par le menu et actionnee normalement. La table originale `CB,86,39,01` donne l'index86, la valeur39 et la transformation de type1. La cellule originale2F devient39, le drapeau24 devient25 et ice_bell_state devient1 a238680. L'index86 n'est pas le type initial de la cellule. Aucun metatile ni drapeau n'est injecte par le controleur. La hache est ensuite re-selectionnee par le menu.

Le trajet comporte533 propositions de pas et onze decisions de coupe ordinaires. L'entree1FC est publiee a239655, le personnage devient controlable a239741 ; le test directionnel confirme16 pixels de deplacement avec les bottes. Le checkpoint final est239841. Les trois etapes positives possedent une relecture froide independante : les65536 octets de RAM et le PNG terminal sont identiques.

L'assistance d'approche declaree utilise exclusivement hero_hurt et conserve le delai naturel des degats de terrain. Le nouvel episode11 cible le boss principal1AC/type6C mais ne l'a jamais atteint. Les combats intermediaires1BE/type79 et19C/type7B restent a faire : la protection doit etre retiree avant chacun. Aucun combat de boss du neuvieme donjon n'est encore valide.

Cette entree ne prouve ni le neuvieme cristal, ni la Hache d'or, ni la fin ou les sauvegardes. Le dernier profil de pile reste celui de la sortie du huitieme donjon, pas de ce nouveau trajet. La fidelite globale du hasard SMS, des timings, de l'audiovisuel et du materiel reste a verifier.

Reproduction : `python tools/summarize_d9_entry_v0306.py`. Rapport : `analysis/d9_entry_v0306_report.json`. Archive locale sans perte : `analysis/d9-entry-v0306`.
