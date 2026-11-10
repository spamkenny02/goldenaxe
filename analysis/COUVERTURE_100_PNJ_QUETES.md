# Tous les PNJ et toutes les quêtes secondaires — SMS et Mega Drive

La fin du jeu seule ne valide pas cette demande. Chaque PNJ, service, quête
secondaire et variante de dialogue accessible doit être parcouru sur les deux
systèmes. Les nouvelles vidéos 100 % utiliseront nos parcours maison achevés.
La vidéo MD V321 déjà livrée reste une vidéo de campagne jusqu'au générique,
sans couverture exhaustive des PNJ.

## Référence de parcours

[Guide Lord Paddle sur Méga Force Magazine](https://megaforcemagazine.com/2021/06/gameplay-100-golden-axe-warrior-master-system-lord-paddle/).
Les huit liens intégrés sont relevés dans `lord_paddle_guide_reference.json`.
L'accès au navigateur fonctionne désormais. Des passages du premier épisode
ont été observés entre 2:45 et 3:24 : premiers habitants, service et sauvegarde.
Les observations sont conservées dans `lord_paddle_observations.json`.
Des salles de labyrinthe du premier épisode et un passage extérieur du deuxième épisode
ont également été relevés comme simples repères de route, sans nouvelle
conversation attestée par ces images. Aucun épisode n'est encore visionné
intégralement. La vidéo présente des textes
anglais, tandis que la ROM fournie contient des textes français ; les repères
visuels ne prouvent donc pas une identité de ROM ou de synchronisation.

| Partie | Repère dans l'article | Vidéo |
|---|---|---|
| 1 | Labyrinthes 1 et 2 | https://www.youtube.com/watch?v=EwDYM1NL_Eo |
| 2 | Bouclier magique et labyrinthe 3 | https://www.youtube.com/watch?v=wcaW3w6lG_M |
| 3 | Montagnes, labyrinthe 4 | https://www.youtube.com/watch?v=XlRjuP9VKJc |
| 4 | Marais, labyrinthe 5 | https://www.youtube.com/watch?v=TFC47cr2hYE |
| 5 | Nendoria, labyrinthe 6 | https://www.youtube.com/watch?v=SJ4WZOuH2TI |
| 6 | Volcans, labyrinthes 7 et 8 | https://www.youtube.com/watch?v=LFSFvDt5GQI |
| 7 | Altorulia, labyrinthe 9 | https://www.youtube.com/watch?v=rtaBkzAEPIg |
| 8 | Death Adder, fin | https://www.youtube.com/watch?v=thtMuiTIjoc |

## Liste ouverte des obligations

`full_completion_checklist.json` contient actuellement 173 entrées :

| Catégorie | Entrées |
|---|---:|
| Contextes des maisons ordinaires | 65 |
| PNJ à dialogues conditionnels | 4 |
| Récompenses et indices d'équipement | 10 |
| Quêtes de dons d'objets dans les maisons | 3 |
| Maisons de gains/pertes d'argent | 33 |
| Fées | 8 |
| Marchands | 23 |
| Auberges et soins | 11 |
| Enseignants de magie | 4 |
| Passages payants | 6 |
| Mini-jeu, sauvegardes, intérieurs cachés, objets optionnels, malédictions, textes signalés : audits | 6 |

Ces entrées ne sont pas 173 PNJ distincts et ne prouvent pas un recensement
exhaustif. Les audits des intérieurs conditionnels et objets optionnels restent
ouverts. Toute découverte ajoute une entrée ; aucun pourcentage global ne se
déduit de ce total provisoire.

Prévoir, selon les conditions réelles : première visite, refus, argent insuffisant,
échange/récompense, objet déjà possédé, capacité pleine, amélioration, retour
après récompense, après un cristal ou après une autre quête. Les issues
irréversibles alternatives peuvent nécessiter une autre branche de commandes
rejouée depuis le démarrage. Ne pas fabriquer leurs états par import de progression.

Pour valider complètement : conserver toutes les pages réellement affichées,
conditions d'inventaire/quête, choix et effets, fermeture, restauration du décor
et reprise des déplacements ; comparer rendu, animation et audio en PAL/NTSC.
Une sélection de texte correcte ou le seul bitmap final ne suffit pas.

## Résultats actuels et anomalie trouvée

Le deuxième boss SMS est vaincu sans assistance au combat ; la récompense du
cristal a été réellement acquittée, avec capacité de vie 48, puis le héros est
sorti du donjon. Le drapeau du cristal précède la fin de sa fenêtre de récompense :
le contrôleur exige maintenant la capacité attendue pour accepter cette étape.
Un don de 50 pièces en F4 finance un achat réel de clé à 60 pièces en C7.
La corde du troisième donjon et son mécanisme sont ensuite obtenus/activés.
Son boss est vaincu, le troisième cristal acquitté et la capacité portée à 56 ;
le retour à l'extérieur est également rejoué.
Voir `sms_npc_campaign_progress_report.json` : chaque étape sélectionnée est
rejouée depuis le démarrage. Les retours/variantes de ces nouveaux services,
le reste de la campagne et les comparaisons MD restent à faire.

Le don de 30 pièces en B4 finance ensuite l'achat de la magie de la Terre chez
Battler pour 50 pièces : offre B06F et réponse B35D observées. Le canoë est
réellement obtenu, le quatrième boss vaincu et sa récompense terminée, avec
capacité de vie 64, puis retour extérieur. L'armure de l'étang (27) et l'épée
longue (50) sont acquises. Le premier escalier est révélé par la défaite des
monstres de son écran ; leur combat et l'entrée réelle sont rejoués.
La branche sélectionnée entre ensuite dans le cinquième donjon.
L'armure supérieure B1 reste en attente de l'accès maritime ; elle n'est pas
comptée comme acquise. Les indices et retours des deux premières récompenses,
les autres réponses de Battler et la comparaison MD restent ouverts.

Le parcours SMS a acquis et équipé la hache, coupé l'arbre qui révèle Gillian,
puis observé son introduction, l'échange de la pomme d'or contre la magie de
la Foudre et son dialogue de retour avant la capacité de vie de 72.
La pomme est réellement consommée et la capacité magique passe de 24 à 48.
Chaque étape sélectionnée réussit la relecture indépendante depuis le démarrage.
Voir `gillian_quest_campaign_report.json`. L'échange chez Gillian reste à jouer
sur MD, ainsi que les autres variantes de cet enseignant sur SMS.

Le don initial de la pomme d'or en C7 est vérifié sur SMS et MD.
Les anciens chemins `oil`/`oil_stairs` désignent cette pomme (inventaire 8),
pas l'huile magique (inventaire 2). De même, les chemins historiques
`fire-teacher` correspondent à Gillian/Foudre, pas à la magie du Feu.

La fée de vie en C9 a été visitée puis revisitée sur les deux systèmes :
capacité augmentée de 8, vie restaurée, sortie normale, puis absence de second
don après un nouvel essai de contact. Les huit étapes d'entrée/service/retour
réussissent leur relecture indépendante. Voir `npc_fairy_campaign_report.json`.
La branche SMS possède le premier cristal, contrairement à cette branche MD ;
ce résultat compare l'effet du don, pas des états de campagne identiques.
Les textes, images, vitesses et sons restent à comparer sur ces services.

La maison d'argent cachée D4 a également été visitée puis revisitée sur SMS :
gain réel de 10 pièces, texte 8E30 observé, puis aucun nouveau texte ou don
lors du retour. Les quatre étapes sont relues indépendamment ; la branche
sélectionnée finit dehors, en état de jeu normal. La visite MD et les limites
de monnaie restent ouvertes. Voir `npc_gold_campaign_report.json`.

Neuf conversations SMS sont observées. Huit ont désormais une visite MD V321
avec sélection correcte, bitmap final de 1040 octets identique à la SMS,
acquittement, déplacement et relecture indépendante. Les pages intermédiaires,
le rendu physique complet, la restauration, la synchronisation et l'audio
restent à valider séparément. Voir `paired_npc_coverage_report.json`.

La neuvième conversation, indice sur le mur en C7/maison 1F, échoue sur V321 :
une ligne vide supplémentaire fait défiler la première phrase. Le contrôle Z80
05B2..05D0 traite les espaces/contrôles avant la largeur ; le natif teste aussi
les séquences vides et ajoute un retour avant FF. Voir `npc_c7_empty_width_report.json`.
Un candidat privé limité à la pièce 1F retrouve le bitmap SMS et réussit la
relecture indépendante, sans import de progression. La correction générale
et la validation PAL restent ouvertes. La V321 publiée, son ZIP et sa vidéo
n'ont pas été remplacés par ce candidat.

Les textes SMS DA58, DA7C et ED3C restent présents en ROM mais sans déclenchement
en jeu établi. Ils ne sont pas comptés comme visités ou déclarés inutilisés.

## Dernier jalon SMS : cinquième cristal

Le parcours sélectionné se termine à la frame 176515, à l'extérieur 49,
avec cinq cristaux, 44/72 points de vie et 41 pièces. Les bottes, les achats
et le soin gratuit en 94 sont suivis du véritable combat du cinquième boss,
satellites compris, puis du mécanisme de retour et de la sortie du donjon.
Les 55 étapes sélectionnées du relevé ont une relecture indépendante exacte
de la RAM entière et de l'image finale. Ce jalon ne prouve pas toutes les
pages, les timings, le son ni la couverture exhaustive des PNJ.

## Dernier jalon SMS : sixième cristal

Le parcours sélectionné rejoint maintenant l'extérieur 8B à la frame 225679,
avec six cristaux, 70/80 points de vie, la cloche de glace et 31 pièces.
Gillian a amélioré la Foudre au niveau 2 ; Battler a amélioré la Terre au
niveau 2 contre 100 pièces possédées. Les dons de 7D et E7 sont observés.
Les 82 étapes sélectionnées passent leur relecture indépendante. La relecture
continue SMS avance depuis un seul démarrage entre les nouveaux checkpoints,
sans importer d'état, et vérifie les 8192 octets de RAM et l'image finale.
L'essai lent à l'épée et la sortie mortelle ne sont pas sélectionnés. Le combat
réussi emploie la hache avec des positions de frappe prévues dans un cœur
secondaire ; aucune protection ne couvre le boss. La sortie traverse les
salles déjà ouvertes et subit les dommages normaux, sans aide ajoutée.

## Dernier jalon SMS : septième cristal

Le parcours rejoint l'extérieur 1B à la frame 270823 avec sept cristaux,
88/88 points de vie, 22 pièces, une clé et le bateau réellement acquis.
Le don d'AC finance une clé achetée en 94 ; le soigneur remonte la vie à 80.
Le gardien intermédiaire, le bateau, les mécanismes du nord, le boss principal
et la sortie sont joués, puis rejoués exactement. Les 105 étapes sélectionnées
sont vérifiées. La reprise de la protection d'approche après le gardien ne
modifie ni ses dégâts déjà subis, ni les ressources, ni les quêtes ; elle est
retirée avant le boss principal. L'accès raté au marchand A5 est exclu.

## Dernier jalon SMS : huitième cristal

Le parcours rejoint l'extérieur 29 à la frame 327106, avec huit cristaux,
90/96 points de vie, 32 pièces et une clé. Les dons de l'armure de dragon en B1
et de l'épée de feu en 6A sont obtenus par les trajets maritimes. Le passage
3C vers 1A est payé avec dix pièces réelles. Le gardien intermédiaire, la clé
du voleur, les mécanismes, le boss principal et la sortie sont rejoués.
Les 126 étapes sélectionnées sont vérifiées. L'essai du passage sans
confirmation C et l'essai bloqué parmi les voleurs en 19A sont exclus ; le
trajet retenu active le mécanisme avant le combat. Les refus, variantes de
texte, revisites et comparaisons MD restent ouverts.
