# Sixième cristal et retour dehors sur v0306

La ROM reste la v0306, SHA-256 `3a12380b86c193148d1cbd29d68a880901860cfb1c276aa96d61d2da16ac2c01`.
Le code du jeu n’a pas changé. Les nouveaux outils ajoutent une sélection d’arme par
le menu ordinaire et contrôlent la progression du sixième donjon sur cette ROM.

La hache possédée est sélectionnée avec Start, déplacement du curseur et C, sans
changer les objets ni les ressources. Le trajet extérieur utilise la carte réelle
du pont de 49 débloqué après le cinquième cristal. L’entrée 187 est atteinte à 127 170.

Les dix-sept étapes de préparation valident cinq acquisitions de clé, les mécanismes
de contact, six ouvertures par Terre, la cloche de glace et le rocher précédant le boss.
Sept lancers de Terre, chacun avec un décrément observé de 8 PM, sont nécessaires
pour ces six ouvertures. Les objets ramassés normalement restaurent de la magie.
La cloche est acquise à 150 183 ; le rocher 7B de 125 est dégagé à 152 382,
avec 48/72 PV, 56 PM et aucune clé. Le boss n’est pas encore entré à ce point.

Un ennemi isolé de 137 bloquait le premier contrôleur. Le passage sud, déjà ouvert,
permet de prendre la troisième clé sans devoir le tuer immédiatement. Au retour vers
le nord, un aller-retour réel 137→147→137 suffit à permettre son élimination normale.
Aucun acteur ni élément de carte n’est remplacé par un état de test. Les tentatives
qui n’ont pas abouti sont conservées sans être promues comme parcours validés.

| Étape du parcours retenu | Image finale | Résultat |
| --- | ---: | --- |
| Premier segment du boss | 156 084 | Héros 48 PV, boss 40 PV |
| Deuxième segment | 158 484 | Héros 48 PV, boss 16 PV |
| Victoire et sixième cristal | 160 884 | 80/80 PV, 72/72 PM |
| Retour dehors en 8B | 162 574 | 80/80 PV, 72/72 PM, 27 pièces, aucune clé |

Le boss 64 commence avec 60 PV. La protection d’approche est retirée à 152 453,
31 images avant le premier état de combat 152 484, dont le compteur de blessure
est nul. Aucun dégât n’est subi sur le parcours retenu ; aucune protection n’est
réactivée après cette entrée. L’autre essai de stratégie, qui a perdu le combat,
est conservé séparément. La vie passe normalement de 48 à 80 lors du cristal,
acquis à 160 753. La hache reste sélectionnée, l’épée longue est possédée et l’armure
reste au niveau 1.

Les trois segments du combat vérifient respectivement 450, 300 et 220 fenêtres
sur les 65 536 octets de RAM ; le retour en vérifie 53. Les 21 étapes retenues ont
chacune une relecture froide indépendante exacte sur toute la RAM et le PNG final.
Leur primaire ne charge aucun état ou SRAM. Les seules écritures de test sont les
protections d’approche journalisées ; aucun PV, PM, argent, objet, acteur ou progression
n’est injecté. Cela ne constitue pas une campagne sans aide sur les approches.

Le profil de chaque instruction normale couvre 162 574 images : SP minimum 63 418,
limite du tas 62 976, marge observée 442 octets et tas valide. La RAM et le PNG finaux
du profil correspondent à la relecture canonique. Les 128 mots physiques du HUD
après la cloche et au retour, ainsi que les six indicateurs de cristal finaux,
respectent les données SMS et leur conversion native. Le PNG final est inspecté.

La suite du jeu, la fin, les sauvegardes complètes, le hasard et le phasage source
global ainsi que la fidélité audiovisuelle complète restent à valider.

Rapports : [progression](d6_progress_v0306_report.json), [sixième cristal](d6_campaign_v0306_report.json).
Audits : `python tools/summarize_d6_progress_v0306.py` puis `python tools/summarize_d6_campaign_v0306.py`.
Les captures volumineuses sont archivées localement et vérifiées avant nettoyage ;
les ROMs numérotées sont conservées.
