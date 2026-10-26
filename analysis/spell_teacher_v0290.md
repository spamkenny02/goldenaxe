# v0290 : apprentissage des quatre magies

ROM : `63cb9dcc37b965291c5b54ba85420ad22edebfcc02b6fa24f1bd112ade83ab61`,
2 Mio, checksum `F1B7`.

Le service 3 du script 669D (maison BF, point 136,56) n'était pas raccordé
au répartiteur Mega Drive. Les dialogues SMS 79DA–7B30 identifient quatre
maîtres : Foudre en E6, Terre en A3, Feu en 2C et Eau en AA.
La nouvelle routine native reprend leurs conditions et effets. Les quatre
portraits et 22 textes sont extraits directement de la ROM d'origine.

- Foudre : première présentation, demande de Pomme d'Or (inventaire 8),
  consommation de l'objet, puis amélioration à partir de 72 PV de capacité.
- Terre : proposition et confirmation ; 50 cornes pour le premier niveau,
  100 pour le second, qui demande aussi 72 PV. Refus et manque d'or conservent
  les effets originaux, notamment le drapeau de présentation.
- Feu : premier niveau à 72 PV, second lorsque les neuf cristaux sont réunis.
- Eau : premier apprentissage et dialogue après acquisition.

Le premier apprentissage augmente la capacité de magie de 24 avec le calcul
sur huit bits et le seuil original. Le remplissage des réserves dépend de
la branche : certaines réponses anticipées ne passent pas par 7B2A.
Les états de présentation restent dans les octets persistants 43–45 de la
sauvegarde. Les paiements sont animés avec les routines normales.

## Preuves

Le [rapport consolidé](spell_teacher_v0290_report.json) lie les essais au
binaire. Les étiquettes internes historiques `fire`/`wind` des fixtures
correspondent respectivement aux premier et second projectiles : les textes
originaux les nomment Foudre et Terre.

1. 3 081 cas exécutent les décisions originales 7A09–7B30 et la fonction C
   compilée. Seules les sorties d'affichage, le choix explicite de réponse
   et le rafraîchissement du HUD d'or sont interceptés ; la boucle réelle de
   décrémentation et les conditions restent exécutées.
2. La v0289 reproduit l'absence du service dans 24 interactions contrôlées.
   La v0290 passe 26 interactions PAL/NTSC : présentation, objet manquant,
   apprentissage, améliorations, manque d'or, refus et conditions finales.
   Les entrées de porte et dialogues s'exécutent dans les deux vrais jeux.
3. Dans 24 cas, les 64 mots de carte du portrait et tous les indices de couleur
   des tuiles référencées correspondent entre les VDP SMS et MD. L'affichage
   a aussi été inspecté visuellement.
4. Le premier donjon passe depuis le démarrage à partir des commandes
   enregistrées : hache, cristal, sortie B9 à 32/32 PV, sans injection ni aide.
   Une seconde exécution reproduit les 65 536 octets de RAM et le PNG finals.
5. L'observation de pile à chaque instruction donne une marge de 412 octets
   sur ce parcours de 16 569 frames. L'amélioration Terre contrôlée donne
   612 octets en PAL et NTSC ; la chaîne du tas reste valide. Deux exécutions
   isolées, cœur officiel et cœur instrumenté, reproduisent toute la RAM et
   l'image finales. Une comparaison avec l'essai au milieu de la matrice
   différait sur 22 octets de pile inactive en NTSC, avec PNG identique ;
   elle n'est pas présentée comme une relecture RAM exacte.

## Campagne historique et limites

Sur la v0289, le deuxième donjon est terminé sans décès : aide limitée à
l'approche, retirée à la frame 28 208 avant le combat à 28 265, compteur nul.
Le boss est vaincu sans perte de PV, puis le cristal et la sortie à 48/48 PV
sont acquis. Les quatre segments assistés ont leur relecture RAM/PNG exacte.
Boss01 s'arrêtait vivant à sa limite de diagnostic ; boss02 continue et gagne.
Exit01 a atteint la sortie mais n'a pas enregistré les métadonnées héritées ;
le nouvel essai propre exit02 est la preuve retenue. Voir le
[rapport v0289](d2_campaign_v0289_report.json).

L'itinéraire extérieur statique vers E6 ne trouve pas de chemin depuis B9.
Il omet les transports et transformations de quête : ce résultat ne prouve
pas le maître inaccessible dans le jeu. Aucun apprentissage naturel complet
n'est encore annoncé sur cette version.

Le blocage de la référence SMS dans le quatrième donjon a une piste précise :
E1 possède la cellule spéciale 58 (0B), dont la transformation enlève quatre
cellules à partir de 36. Le second sort transforme 0B en 00 dans les donjons.
Il faut maintenant acquérir la Terre par le parcours normal et utiliser cette
transformation ; ni ce passage naturel, ni le canoë ni le quatrième boss ne
sont validés par les fixtures de cette version.

La chronologie complète des portraits et dialogues, la quantification des
palettes, les formes d'onde audio, les donjons suivants, le flux RNG/R/IRQ et
le matériel réel restent à vérifier. Ces preuves ne constituent pas un
portage complet. Captures archivées sans perte avant nettoyage :
[manifeste](spell-teacher-v0290/manifest.json).
