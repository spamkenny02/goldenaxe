# État de livraison — v316, 6 novembre 2026

Le but reste le portage fidèle complet de Golden Axe Warrior SMS en 68000
natif sur Mega Drive. La v316 est une étape de ce portage, pas une finale.

La ROM de production et le candidat contrôlé ont le même SHA-256 :
`8b94f2e022d1027b5bc3cefd18ffd9f79a8895fba7622defc400c10d6fdfff7b`.
La ROM numérotée, les deux alias et le binaire compilé sont identiques.

| Exigence | Preuve actuelle | Limite restante |
| --- | --- | --- |
| Port natif Z80 vers 68000 | Sources `megadrive/src`, SGDK, désassemblage `analysis/bank_00.asm` à `bank_0f.asm`, compilation reproductible du candidat | La couverture de fidélité de toutes les situations reste ouverte. Le lecteur audio est natif ; les données originales sont conservées. |
| Intro, cape, logo, titre | Validation v314/v315 et régression v316 : 6500 images audio par région, cartes et huit PNG identiques à v315 | Ce contrôle couvre le démarrage sans boutons, pas les transitions de tous les menus. |
| Récit puis premier écran | `initial_world_v0316_report.json` : quatre cas naturels, 19 images de fermeture normalisées par cas, 16 contours aux mêmes images, héros à la même image matérielle | Certains pixels pendant les écritures en cours de balayage diffèrent ; le compteur global source n’est pas reproduit entièrement. |
| Jeu et progression | Parcours complet jusqu’au générique sur v314, rejoué sur v315 ; deux nouveaux trajets v316 jusqu’au premier donjon sans import ni écriture RAM | Le parcours complet n’est pas encore établi sur v316. Le rejeu de l’ancien calendrier de boutons diverge dès le départ. La même séquence courte sur SMS et v316 donne cependant 894 images de positions/états identiques. |
| Marchands et inventaire | Correctif de panneau v315, six retours d’inventaire contrôlés sur le candidat devenu v316 | Pas de nouvelle revendication de couverture de tous les services sur v316. |
| Sauvegarde / Continuer | Deux reprises PAL/NTSC sur v316 d’une sauvegarde réelle v314 à neuf cristaux ; inventaire, HUD, marqueurs et déplacement vérifiés | Autres emplacements et écriture d’une nouvelle sauvegarde sur v316 non établis par ce test. Le critère de disponibilité exclut désormais le chargement et la révélation en cours. |
| Musique et bruitages | Lecteur natif, régression d’intro, thème initial sélectionné avant la révélation | Un écart de phase audio NTSC est observé avant le récit. La phase modulo six change aux images 950 et 1201 dans le trajet diagnostiqué ; sa cause exacte reste à traduire. Pas de preuve que chaque bruitage de chaque scène est identique. |
| Aléatoire et acteurs | Nombreuses comparaisons source ciblées, campagnes précédentes et contrôles de boss | Le fournisseur de rafraîchissement utilise encore SGDK ; ne pas revendiquer le flux Z80 R ou des trajectoires globalement identiques. |
| Versions, README et Git | ROM v316 et rapports distincts ; README actualisé ; publication sur `main` à vérifier à la livraison | Aucun statut de finale ne doit être déduit du numéro de version. |
| Nettoyage | Archives avec hachage et relecture avant retrait des artefacts générés ; rapport de nettoyage v316 à la clôture | Conserver les 316 ROMs, l’original, les sources, les symboles et les captures PNG. |

Suite prioritaire : corriger la phase audio des transitions de menu depuis les
routines source, reprendre un parcours complet avec un contrôleur adapté à la
disponibilité réelle, puis fermer les écarts de fidélité restants. Les essais
émulés ne constituent pas une validation sur console physique.
