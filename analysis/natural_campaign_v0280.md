# Parcours naturel de la v0280

La ROM jouable et le code du jeu restent inchangés. Le parcours fixe de la
v0274 ne peut pas être simplement réutilisé : son rejeu sur la v0280 échoue
avant la hache. Le préfixe jusqu'à la première entrée de donjon, lui, atteint
la bonne salle, vivant et avec la progression attendue, à la frame 4258.
Tous ces essais utilisent les commandes ordinaires depuis le démarrage,
sans injection de RAM, de sauvegarde ou de point de reprise.

Le pilote a été amélioré avec les rectangles d'attaque des descripteurs de
la ROM SMS. Il choisit une position et une direction capables de toucher,
plutôt qu'une simple distance entre les centres. Cette stratégie est un outil
de contrôle extérieur au jeu ; elle ne modifie ni les collisions ni les dégâts.

Le nouveau parcours MD accomplit les étapes suivantes sans décès :

| Étape | Frame atteinte | État |
|---|---:|---|
| Hache | 9006 | Arme possédée, capacité de vie 24 |
| Premier boss et cristal | 13775 | Hache équipée, cristal 128, capacité 32 |
| Sortie du premier donjon | 16003 | Retour en B9, vivant |

Le parcours est conservé jusqu'à la frame 16153. Une seconde exécution depuis
le démarrage, avec les commandes fixes enregistrées et sans décisions fondées
sur la RAM, reproduit les 65 536 octets de RAM finale et le PNG final.
Les 256 indicateurs persistants et les 1 280 octets de carte de la sortie
correspondent exactement à la trace SMS originale déjà archivée. Les rencontres,
la vie restante, les commandes et les durées ne sont pas déclarées identiques.

Le pilote SMS renouvelé récupère aussi la hache sans décès, mais son essai
suivant meurt au premier boss. Il n'est pas présenté comme un parcours SMS
réussi. La comparaison de progression ci-dessus utilise la trace SMS historique
réussie, dont le SHA de ROM et les preuves d'absence d'injection sont vérifiés.

## Deuxième donjon encore ouvert

Le trajet MD renouvelé atteint la deuxième entrée sans décès. Sept essais
supplémentaires, quatre MD et trois SMS, échouent avant le deuxième cristal.
Le meilleur nouveau trajet MD atteint le boss 63 en salle 144, avec un seul
point de vie ; le minimum de vie du boss observé est 28. Les essais source
échouent eux aussi. Ce sont des résultats du pilote, sans preuve suffisante
pour attribuer ces échecs à un défaut du portage.

Une variante prudente prédisant huit frames de contact et attendant la fin
des déplacements avant l'attaque a dégradé le trajet. Son code et ses essais
sont conservés séparément. La politique actuelle garde la visée par rectangles,
utilise la géométrie présente pour les pièges et rend l'attente de fin de pas
optionnelle. Le pilote exact du premier parcours réussi est également conservé.

Reproduction : `tools/summarize_natural_campaign_v0280.py` vérifie et rassemble
les preuves. Son [rapport](natural_campaign_v0280_report.json) conserve les
SHA et les résultats négatifs, sans les transformer en validation de campagne.
La suite doit préserver davantage de vie ou obtenir des ressources sur le
trajet, puis terminer le deuxième cristal et la sortie sur les deux systèmes.
La campagne complète, la campagne PAL, le flux R/IRQ et l'audio physique restent
à terminer ou vérifier.
