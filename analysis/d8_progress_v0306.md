# Entree et combat intermediaire du huitieme donjon sur v0306

La ROM reste v0306, SHA-256 `3a12380b86c193148d1cbd29d68a880901860cfb1c276aa96d61d2da16ac2c01`. Aucun changement de code natif ni nouvelle version n'est revendique pour ces preuves.

Le parcours conserve les **sept cristaux** et atteint **1C9** apres **203594 images**, avec **46/88 PV, 64/72 PM, 1 cle et 20 pieces**. Le combat intermediaire est vaincu. L'epee longue2 est selectionnee ; le boss principal196/type6B, la cle des voleurs et le huitieme cristal ne sont pas encore atteints.

Depuis la sortie du septieme donjon, les boutons ordinaires rejoignent le passeur3C/9F par sa porte orientee vers le bas. Les sols dangereux coutent20PV, avec leur delai naturel conserve :84 deviennent64. Le passage est paye10 pieces,29 deviennent19, et le heros arrive en1A. Le bateau deja obtenu permet l'entree1EA.

Les scripts originaux placent le combat intermediaire en1C9, avec50PV,18 de degats et4 d'armure (type7A,flags20h). L'approche s'arrete donc en1CA. La premiere tentative reste bloquee en1DA avec un ennemi hors de portee ; elle finit au budget d'images sans capture terminale et est exclue. Une sortie/rentree normale, declenchee une seule fois dans la seconde tentative, renouvelle la salle et permet de la traverser. Aucun acteur n'est supprime ou modifie par le test.

La protection est retiree a201458, puis son retrait est relu a l'identique. Le combat debute a201711, avec64PV, hurt0 et50PV ennemis. L'epee longue est choisie par le menu ; force native6, armure ennemie4. L'ennemi est vaincu a l'issue du checkpoint203594, sans protection. Un seul coup, a202722, fait passer les PV de64 a46. Aucun soin,MP,argent,objet,acteur,progression ou SRAM n'est injecte.

Les **six nouveaux checkpoints positifs** ont chacun une relecture froide independante :65536 octets de RAM et PNG final identiques. Les215 fenetres de prediction du combat correspondent sur toute la RAM ; seul le coeur secondaire jetable restaure ses propres snapshots. Le coeur principal n'importe aucun etat. Les ecritures de test apres le retrait sont exactement celles du prefixe ferme :aucun garde n'est ajoute durant le combat.

Ces preuves ne valident pas encore le boss principal du huitieme donjon, son cristal, le neuvieme donjon, la fin, les sauvegardes, le hasard global SMS, les timings/audiovisuel globaux ou le materiel. La marge de pile442 concerne toujours le checkpoint precedent du septieme donjon a196280 images ; elle n'est pas etendue par ces controles.

Reproduction : `python tools/summarize_d8_entry_v0306.py`, puis `python tools/summarize_d8_midboss_v0306.py`. Rapports : `analysis/d8_entry_v0306_report.json`, `analysis/d8_midboss_v0306_report.json`. Archive locale sans perte : `analysis/d8-progress-v0306`.
