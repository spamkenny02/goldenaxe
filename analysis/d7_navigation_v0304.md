# v304 : navigation apres le navire et approche du boss D7

La ROM reste inchangee, SHA-256 `b7b4e15008a6f0a913c9ad43f15386abcdfbb719e5a575873d92712ba52503a8`. Ce point poursuit le [navire de D7](d7_progress_v0304.md).

Le controleur observait le canoe, mais pas encore le navire. Son cache de collision suit maintenant la regle originale2D41 : les deux pieds doivent partager le drapeau d'eau40 avant d'appliquer les changements permis par le navire. L'equipement provient de la RAM de jeu observee ; aucun objet n'est injecte. Les graphes de recherche sont recalcules lorsque cet equipement change.

Un banc isole execute les octets Z80 originaux2D41..2D7A, dans une cartouche de test separee.8192 configurations couvrent les16 combinaisons des drapeaux hauts des deux pieds,256 motifs d'octets et navire absent/present. Les196608 octets de cache compares sont exacts, y compris les octets bas preserves. Ce banc ne prouve pas la cadence du deplacement ni une campagne SMS complete.

Le retour quitte ensuite la salle du navire par sa porte ouverte, en laissant le dernier ennemi hors de portee. En1A8, Terre brise le bloc34 et fait apparaitre le teleporteur vers198. Une cle est consommee sur le trajet suivant.

Le dernier obstacle du controleur etait un ennemi58 encore cache dans189. L'option de parcours --wake-sentinels approche les57/58 dormants a moins de24 pixels sur les deux axes, puis attend leur apparition ordinaire. Les journaux montrent les approches et attentes des emplacements0 et2 avant leurs combats. La routine du jeu ne change pas.

| Etape | Frame finale | Salle | PV /80 | Cles | Magie |
| --- | ---: | --- | ---: | ---: | ---: |
| Retour nord | 176702 | 1B8 | 80 | 3 | 48 |
| Bloc et teleporteur1A8 | 177706 | 198 | 80 | 3 | 40 |
| Salle avant le boss | 181983 | 189 | 80 | 2 | 48 |

Les trois etapes ont chacune une relecture independante a commandes fixes depuis le demarrage :65536 octets de RAM et PNG final identiques. Les aides d'approche sur hero_hurt sont explicites. Le checkpoint final conserve six cristaux, le navire et la hache equipee ; le boss179 n'est pas encore entre a ce point. Les essais bloques restent des diagnostics distincts.

La [correction de mesure de pile](stack_minimum_v0304_erratum.md) etablit478 octets avant chaque instruction sur les parcours D1-D6 ;496 etait la marge aux points instrumentes. Ce checkpoint n'etend pas cette mesure a D7.

Le [rapport reproductible](d7_navigation_v0304_report.json) lie les sources conservees, le banc Z80 et les trois relectures. Le combat principal, le septieme cristal, la fin, les sauvegardes et la fidelite globale restent a verifier.
