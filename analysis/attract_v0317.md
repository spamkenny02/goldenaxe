# v0317 de développement — retours titre et intro

La ROM numérotée v317, les deux alias locaux et les sources utilisées par défaut
contiennent les mêmes correctifs que le candidat 37 testé. Le build privé sans
cache et le build de production donnent le même binaire :
`7694654ec85dd6626c0e17ff1834e5893d4eb35481400a4725eac6b6f3503294`,
checksum 7D56, 2 Mio. Toutes les versions précédentes et l’aperçu c0029 sont conservés.

## Erreurs de traduction corrigées

La SMS conserve DCE2 entre deux intros. Le natif le remettait à zéro ; après
la conservation de sa valeur, une autre erreur apparaît : INC/CP6/JR C/XOR
ramène à zéro toute valeur qui dépasse 5 après incrément, ce qui n’est pas un
modulo 6. Avec 225 en NTSC, le modulo donnait 4 ; avec 227 en PAL, il donnait 0
par coïncidence. Le clamp est désormais identique au branchement source.

Les publications SAT/palette encore en attente sont supprimées à l’entrée et
à la sortie de l’intro. Le retour depuis le titre rétablit le fondu 0B48,
la préparation des polices et les 19 attentes complètes de la palette 0AA4.
Le travail des polices, 691749/691750 T hors IRQ selon le parcours, est mesuré
sur la ROM et cadencé avec le coût audio courant. Les quatre attentes 0EFA
sont rétablies, y compris leurs callbacks avant le nouveau chargement de
couleurs ; le raccourci du seed 22 n’est plus utilisé à chaque retour.

Le titre avance l’horloge source seulement pour ses attentes B95 explicites.
Les attentes SGDK avec écran désactivé peuvent revenir dans le même VBlank ;
une attente complète exige désormais une nouvelle interruption réelle.
Le délai audio 81 qui compensait auparavant cette attente manquante est retiré.

Lors de la révélation, la requête d’interruption précède la préparation du
premier morceau de données sur 68k. Si l’interruption arrive pendant cette
préparation, elle est prise en compte, sans en demander une seconde.

Le premier 024F active une interruption de ligne avec un compteur encore à
zéro. Les appels suivants retrouvent le compteur déjà configuré. Le natif
conserve cet état, également installé par l’initialisation du monde 0240,
afin de ne pas ajouter une attente au chargement des titres suivants.
Les traces montrent le surcoût IRQ du premier appel, absent au second.

Les candidats 30 à 36 restent archivés : conservation d’état, fade, continuité
d’horloge, attente réelle, callbacks complets, requête avant préparation,
clamp du compteur puis suppression du délai 81. Le candidat 37 ajoute la
continuité de configuration du compteur de ligne. La publication est explicitement
de développement ; le contrôle d’absence de régression de pixels reste ouvert.

## Mesures du binaire v317

| Sur 14000 images sans entrée par région | NTSC | PAL |
| --- | ---: | ---: |
| Images identiques à la SMS sur c0029 | 9454 | 9298 |
| Images identiques sur v317 | 13602 | 13648 |
| Pixels différents de la SMS sur v317 | 538303 | 515308 |
| Pixels devenus moins fidèles que c0029 | 73686 | 76424 |

Ce contrôle porte sur le viewport 192 lignes après normalisation des niveaux
DAC. Il couvre deux cycles complets et le début du troisième, sans donner
un pourcentage de finition du jeu. Les régressions, notamment partielles,
restent enregistrées et ne sont pas masquées par la baisse des totaux.

Les entrées dans la deuxième et la troisième intro ont les mêmes images et
horloges que la source : NTSC 6725/C52 et 13457/C121 ; PAL 6711/C70 et 13430/C157.
Les valeurs source sont relevées à C98 avant le fondu ; le reset de ligne
source à CE0, plus tardif, n’est pas confondu avec cette entrée.

Sur les images 23..14000, les 400 octets du lecteur audio et les huit registres
PSG correspondent dans les deux régions. Les requêtes natives en attente sont
comparées aux octets source DE06/DE08, avec données brutes conservées. Le début
silencieux, les formes d’onde PCM et le matériel physique ne sont pas certifiés.

Les 210 saisies initiales de nom, 270 images sélectionnées des menus et quatre
cas de sélection/confirmation sonore passent sur v317. Les six contrôles
extérieurs/maisons restaurent le décor fixe après l’inventaire ; les quatre
motifs animés identifiés par la source sont distingués du décor fixe.

Deux parties fraîches atteignent le premier donjon et déplacent ensuite le
héros : 12 PV en NTSC, 8 en PAL, sans mort, modification de RAM ou SRAM importée.
Cela ne remplace pas un nouveau parcours complet sur ce binaire.

## Limites conservées

Les révélations partielles et les fondus du titre gardent des différences.
Le chargement initial froid, les entrées arbitraires, les retours depuis une
partie, les palettes dépendant de la sauvegarde et tous les contextes de phase
ne sont pas certifiés par les boucles sans entrée. La fidélité globale du
rafraîchissement/RNG, un parcours complet et le matériel physique restent ouverts.

[Rapport lié au binaire](attract_v0317_report.json) ·
[Sources et artefacts](attract_v0317_artifacts_report.json) ·
[Patch depuis le précédent main](attract_candidate37_v0317_crlf.patch) ·
[Archive des essais](attract-v0317/manifest.json) ·
[Nettoyage vérifié](attract_v0317_cleanup_report.json)
