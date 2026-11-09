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
Aucun épisode n'est encore visionné intégralement. La vidéo présente des textes
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
