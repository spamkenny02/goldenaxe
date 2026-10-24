# v0280 : conversion de cartes dans la ROM jouable

La v0280 utilise la table et la boucle 68000 de `source_class0_video_map`
dans `draw_map` et dans les copies de fenêtres du titre. La formule conserve
le numéro de tuile, les palettes, les retournements et la priorité de tous
les mots SMS. Le nom du module ne limite pas cette conversion aux extérieurs.
La table de 128 Kio fait franchir la limite de la cartouche précédente :
le binaire, l'en-tête et le script de construction utilisent maintenant 2 Mio.

Le décodeur historique sans horloge s'appelle désormais `source_pattern_unpack`.
Cela résout son conflit de symbole avec le décodeur à horloge, dont l'API reste
inchangée. Ses 515 cas de décodage et de travail passent après ce renommage.

## Publication de l'inventaire

La conversion rapide avançait initialement l'affichage de l'inventaire.
La version retenue prépare les 768 mots avant l'attente, puis transmet une
échéance absolue et un indicateur au propriétaire VBlank. Celui-ci envoie la
carte par DMA avant le lecteur PSG et libère l'indicateur après publication.
Le premier plan reste noir pendant le travail de préparation. Le buffer reste
possédé par cette publication jusqu'à son acquittement.

Les six parcours naturels de l'extérieur et des deux premières maisons,
en NTSC/PAL, vérifient directement contre la SMS :

| Parcours | Région | Noir à l'entrée | Noir à la sortie | Frame de reprise |
|---|---|---:|---:|---:|
| Extérieur | NTSC | 11 | 23 | 3427 |
| Première maison | NTSC | 11 | 17 | 3421 |
| Deuxième maison | NTSC | 11 | 17 | 3421 |
| Extérieur | PAL | 9 | 19 | 3422 |
| Première maison | PAL | 9 | 14 | 3417 |
| Deuxième maison | PAL | 9 | 14 | 3417 |

Les fenêtres noires exactes, le HUD conservé et l'absence de commande sonore
de fermeture passent. Ces échéances reposent encore sur les budgets de travail
et la réserve de reconstruction existants ; tous les inventaires et toutes
les configurations de donjon ne sont pas couverts.

## Gain et vérifications

La mesure des instructions de la ROM jouable, du début de `draw_map` à la fin
de sa préparation, trouve une réduction médiane de 86–87 % sur huit parcours
NTSC/PAL. Ce n'est ni un gain de FPS global ni une accélération de la simulation.
Les champs de progression et de jeu sélectionnés correspondent à la v0275 sur
les 571 frames observées de chacun des huit parcours. L'ordre des commandes
musicales est conservé. Les changements de phase audio et d'animation ainsi
que les différences de VRAM et d'images sont conservés dans le diagnostic :
l'égalité globale image par image avec la v0275 n'est pas revendiquée.

Le titre est comparé séparément à la ROM SMS en cours d'exécution : 33 poses
de cape à six frames, neuf étapes du premier fondu à deux frames, neuf étapes
du fondu du guerrier à six frames et huit lignes du logo à une frame. Les
40 comparaisons d'images normalisées PAL/NTSC passent. Ces tests sautent
l'introduction par les commandes ordinaires ; ils ne prouvent pas l'égalité
du démarrage absolu ou de toute la séquence d'introduction.

Rapports :

- [ROM jouable et coût de conversion](playable_map_conversion_v0280_report.json)
- [Inventaire contre la SMS](inventory_publication_v0280_report.json)
- [Titre NTSC](title_cadence_v0280_report.json), [titre PAL](title_cadence_v0280_pal_report.json)
- [Rendu incrémental séparé : pixels](md_source_room_budget_pixels_report.json)
- [Rendu incrémental séparé : durée](md_source_room_budget_current_report.json)

Le rendu incrémental complet reste séparé du jeu. Ses 268 images maintenues
passent ; la mise à jour réelle `scroll-3051` demande encore environ 437 lignes
en NTSC et 431 en PAL, au-delà d'une frame. Les copies différées des motifs de
stockage des cartes/SAT et le cache de clones réduisent le coût, sans établir
une publication complète aux échéances SMS. L'absence de changement demande
environ quatre lignes, contre 377 dans le diagnostic précédent.

La campagne complète, l'horloge et le hasard SMS globaux, les échéances des
autres chargements et la fidélité physique de l'audio restent à terminer.
Les v0276–v0279 sont conservées comme compilations intermédiaires ; la version
recommandée de cette série est la v0280.
