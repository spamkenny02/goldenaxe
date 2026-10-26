# Cinquieme donjon : ravitaillement, mecanismes et bottes, v0292

La ROM reste v0292 (SHA-256 6eeb56086a81c230c75b154f51cafab72167a1eec42c691aed9bf317fd19dd82). Aucun code du jeu ni binaire de production ne change dans ce jalon.

Apres les bottes, le heros sort volontairement sans cristal a 30/64 PV. Cette sortie est etiquetee comme ravitaillement, jamais comme donjon termine. Quatre cadeaux reels aux maisons 54, A1, B5 et B4 donnent 10, 30, 10 et 30 cornes. Le heros achete deux cles a 60 cornes dans la maison 94 (128 vers 8), puis utilise son soin gratuit (30 vers 64 PV). Aucun ajout artificiel de monnaie, cle, objet ou vie n'est utilise.

Le retour au donjon suit les passages reels. Le mecanisme de 154 exige d'arriver par le bas pour atteindre sa partie gauche. Terre en 153, cellule44, transforme le rocher0B en portail0C et consomme huit points de magie. Le portail conduit en162 ; une commande HAUT au mecanisme de162 ouvre le passage vers172. Le checkpoint finit avant le boss, avec deux cles et64/64 PV.

Les14 etapes canoniques ont chacune une relecture independante depuis le demarrage, par commandes fixes : les65536 octets de RAM et le PNG final correspondent exactement. Le compteur de blessures est assiste pendant l'approche, comme consigne dans les manifestes ; cette aide n'est pas dans la ROM. Aucun etat de sauvegarde n'est importe dans l'execution principale. Cette preuve concerne la campagne native ; elle ne demontre pas une campagne complete equivalente sur SMS ni l'egalite de toutes les images intermediaires.

Les bottes reellement acquises activent le selecteur de vitesse1. Un banc distinct, avec situations controlees, compare les six terrains, quatre directions et bottes presentes/absentes en PAL/NTSC. Les96 cas et3072 frames correspondent pour positions8.8, vitesses, direction, animation, compteur de marche et terrain. Ce banc ne prouve ni la vitesse globale, ni les transitions, ni l'audio, ni l'accumulation des degats de terrain.

Rapports : [ravitaillement](d5_supplies_v0292_report.json), [bottes](boots_timing_v0292_report.json), [banc de marche](terrain_walk_v0292_game_report.json). Reproduction : tools/summarize_boots_timing_v0292.py puis tools/summarize_d5_supplies_v0292.py. Les essais alternatifs bloques par des murs ou meubles ne constituent pas des defauts etablis du portage.
