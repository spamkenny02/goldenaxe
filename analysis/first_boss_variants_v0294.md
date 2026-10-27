# v0294 : variantes78/79 du premier comportement de boss

La v0294 corrige les ennemis78 et79, presents respectivement dans les salles1B8 et1BE. Leur table originale2B63 appelle506B, comme les types63 et64. Le wrapper506B appelle A754. Le portage possedait cette routine mais ne la distribuait qu'a63/64 ;78 restait donc au repos, invisible, avec30 PV et sans boite de collision. Le parcours naturel de la v0293 reste bloque devant la sortie fermee de1B8.

La correction native se limite a deux conditions de actors.c : distribution de78/79 vers first_boss_behavior et publication de leurs boites de collision apres la simulation. Leurs statistiques et leur absence de drapeau de boss sont conservees. Aucun autre fichier de jeu ne change. La ROM reste de2 Mio, checksum7F10, SHA-256 `508642dc6a7f27883746b1bbb5b208045205644205be325a3d3a317ecca87098`.

Les1824 cas de logique pour63,64,78,79 correspondent aux768 octets d'entites calcules par les instructions Z80 originales. Deux lectures du registre de rafraichissement sont remplacees par des valeurs explicites dans cette seule fixture. Vingt-quatre segments des vrais jeux, en PAL et NTSC, comparent1232 images de donnees d'entites, incluant initialisation,mouvement,animation,projectiles et boites de collision. Les acteurs et la position du heros sont controles dans ces segments ; ils ne prouvent pas un combat naturel ou une equivalence de tous les pixels et sons.

La relecture froide des anciennes commandes de campagne s'arrete a13489 dans le premier donjon, heros mort avant toute nouvelle aide. La cause de cette divergence de trajectoire n'est pas encore identifiee. La campagne complete de cette compilation n'est donc pas validee ; les six cristaux et l'approche du septieme precedemment publies restent des preuves de la v0293. Une reprise adaptative sur la nouvelle compilation est necessaire.

Le jalon historique v0293 jusqu'a1B8 est conserve dans [ce rapport](d7_passage_v0293_report.json) : deux cles, soins par objets jusqu'a74 PV, deux tirs de Terre sur36 puis2B, mecanisme actionne et passage traverse. L'outil de Terre attend maintenant la fin de son action au lieu de s'arreter apres150 images d'une salle deja vide. Les erreurs et limites de test ne sont pas presentees comme des corrections du jeu.

[Rapport consolide](first_boss_variants_v0294_report.json), [cas Z80/68000](first_boss_alias_v0294_report.json), [segments PAL/NTSC](first_boss_alias_game_v0294_report.json).

Reproduction : `tools/validate_first_boss.py --aliases --generate`, puis `tools/build_first_boss_harness.ps1`, `tools/validate_first_boss.py --aliases`, `tools/validate_first_boss_gameplay.py --aliases` et `tools/summarize_first_boss_variants_v0294.py`. Les rapports lient les sources et captures par empreintes. Ni la campagne SMS complete, ni le septieme cristal, les derniers donjons, la fin ou la fidelite globale ne sont acquis par ces tests cibles.
