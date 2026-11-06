# Golden Axe Warrior — portage Mega Drive

Reconstruction de Golden Axe Warrior depuis la ROM Master System fournie,
puis portage de sa logique Z80 en code natif 68000 avec SGDK.
La fidélité à la Master System passe avant les améliorations.

<!-- ROM-RELEASE:START -->
**Version courante : v0318 — 2048 Kio.**

[Télécharger la ROM v0318](versions/v0318-b9e1f0a0/gaw-megadrive-v0318.bin) · [Toutes les versions](versions/README.md)

Version de développement ; contrôles ciblés réussis, écarts visuels et validation complète encore ouverts.

SHA-256 : `b9e1f0a0543f191e24ffd6d2740a0d717501e0fcd986f8b8953a37a1b3c416a4`
Checksum Mega Drive : `7863`
<!-- ROM-RELEASE:END -->

La **v318** applique le fondu avant le titre pendant l’interruption vidéo.
Elle ajoute 34 images identiques à la Master System dans chaque région.
Le rejeu de la campagne NTSC retrouve les 393 707 états comparés de la v317
et les quatre captures de fin. La sauvegarde v317 à neuf cristaux se recharge.
[Mesures et limites de la v318](analysis/fade_v0318.md)
· [Premier cristal en PAL et comparaison de l’entrée](analysis/pal_d1_v0318.md)

L’aperçu [c0038](versions/candidates/c0038-e7ee40cb/README.md) est conservé
avec son rejeu divergent. L’ancien aperçu [c0029](versions/candidates/c0029-c3fca1d6/README.md) reste disponible.
L’aperçu [c0039](versions/candidates/c0039-aafa3255/README.md) recale la durée
de la première entrée du donjon 1 en PAL et NTSC. Son rejeu diverge en NTSC.

## État du portage

La **v317** a intégré les correctifs de menus et d’intro repris dans la v318.
Elle rétablit le fondu titre→intro, les attentes
réelles d’interruption, les quatre attentes de chargement, la continuité de
l’horloge et la remise à zéro du compteur du feu. Les publications de sprites
et palettes en attente sont nettoyées à l’entrée et à la sortie de l’intro.

Sur 14000 images sans entrée par région, 13602 images NTSC et 13648 PAL
correspondent à la SMS, contre 9454/9298 sur c0029. Le test couvre deux cycles
complets titre/intro et le début du troisième. Des écarts restent dans les
révélations partielles et les fondus ; ces comptes ne donnent pas un taux de
finition ou de fidélité du jeu entier.

Des images 23 à 14000, les 400 octets du lecteur audio et les huit registres PSG
correspondent à la SMS en PAL/NTSC, avec normalisation des commandes en attente
et conservation des données brutes. Les formes d’onde PCM ne sont pas certifiées.
La saisie du nom (210 cas), 270 images sélectionnées des menus, quatre cas de
bruitages, six retours d’inventaire et deux parties fraîches jusqu’au premier
donjon passent. Le build de production et le build propre sont identiques.
[Correctifs et limites de la v317](analysis/attract_v0317.md)
· [Rapport lié au binaire](analysis/attract_v0317_report.json)
· [Sources et artefacts](analysis/attract_v0317_artifacts_report.json)

Le nouveau parcours de ce même binaire valide les **neuf cristaux
et les retours extérieurs** : hache, première fée, huile, corde, Terre, canoë,
Feu, épée longue, bottes, achat de clé, mécanismes, cloche de glace, navire et
clé du voleur et ballon sont obtenus ou utilisés normalement. Les 155 points de contrôle jusqu'à la sortie du D9
reproduisent la RAM complète et le PNG final avec des commandes fixes. La
protection de test est retirée avant chaque boss ; aucune vie, ressource ou
progression n'est importée. Les huit premiers donjons terminent sans mort.
Une mort et un Continue ordinaires ramènent ensuite le héros en région sud,
avant le soin du jeu et le D9. Le neuvième donjon termine à 74/104 PV, sans
autre mort. Les essais rejetés restent conservés.

Le parcours se poursuit avec l'usage du ballon, l'entrée du palais, ses
mécanismes intérieurs et ses deux gardiens, vaincus sans protection de test.
La Golden Axe est reçue en salle 11D à 88/104 PV. Death Adder est vaincu
sans protection de test. Les neuf gemmes apparaissent dans la scène finale,
le générique défile entièrement et une commande normale ramène à l’intro.
Le parcours principal compte 183 points de contrôle. La comparaison intégrale
avec la Master System reste ouverte.
[Campagne et palais](analysis/campaign_palace_v0317.md)
· [Combat final et générique](analysis/cold_palace_final_v0317_report.json)

La sauvegarde écrite par le jeu après le D9 est reproduite à l'octet près.
Continuer restaure les neuf cristaux et le contrôle du héros en FA.
[Sauvegarde à neuf cristaux et reprise](analysis/game_written_save_v0317_nine_crystals_report.json)

Les vingt-et-un nouveaux points D9 utilisent trois lecteurs démarrés à froid et
partagés entre étapes, sans import d'état primaire : 5030091 répétitions
d'images de préfixe sont évitées dans ces vérifications, avec les mêmes
comparaisons de RAM et de PNG.
[Deux premiers cristaux](analysis/campaign_v0317.md)
· [Troisième et quatrième cristaux](analysis/campaign_d3_d4_v0317.md)
· [Cinquième cristal](analysis/campaign_d5_v0317.md)
· [Sixième cristal, preuves et limites](analysis/campaign_d6_v0317.md)
· [Septième cristal, navire et combats sans protection](analysis/campaign_d7_v0317.md)
· [Huitième cristal, clé du voleur et retour](analysis/campaign_d8_v0317.md)
· [Neuvième cristal, gardiens, ballon et retour](analysis/campaign_d9_v0317.md)

Les essais clos sont archivés et relus avant nettoyage. Toutes les 317 ROMs
publiées, les sources, symboles et captures restent préservés ; les ROMs de
travail sont également conservées dans les archives, et le candidat 37 reste
disponible localement avec son cache de compilation.
[Nettoyage du palais et de la sauvegarde, 101 Mio libérés](analysis/campaign_palace_v0317_cleanup_report.json)
· [Nettoyage D9, 80 Mio libérés](analysis/campaign_d9_v0317_cleanup_report.json)
· [Nettoyage précédent D8 : 63 Mio](analysis/campaign_d8_v0317_cleanup_report.json)
· [Nettoyage précédent D7 : 74 Mio](analysis/campaign_d7_v0317_cleanup_report.json)
· [Nettoyage précédent D6 : 67 Mio](analysis/campaign_d6_v0317_cleanup_report.json)
· [Nettoyage précédent Feu/D5 : environ 92 Mio](analysis/campaign_d5_v0317_cleanup_report.json)
· [Nettoyage précédent D3/D4 : 96 Mio](analysis/campaign_d3_d4_v0317_cleanup_report.json)
· [Nettoyage précédent de la campagne : 81 Mio](analysis/campaign_v0317_cleanup_report.json)
· [Nettoyage précédent des essais d’intro](analysis/attract_v0317_cleanup_report.json)

La **v0316 restaure la sortie du récit et la révélation du premier écran** :
fondu vers le noir, 16 contours et apparition du héros contrôlés sur SMS
et MD en PAL/NTSC, avec deux instants de validation du récit. La musique du
premier écran démarre pendant la révélation. La compilation de production
est identique au candidat testé.

Les flux audio de l’intro avant le titre restent identiques à v315 sur
6500 images par région, ainsi que huit captures du titre. Six retours
d’inventaire et deux reprises de la sauvegarde réelle à neuf cristaux passent.
Deux nouveaux trajets depuis Nouveau Jeu atteignent le premier donjon,
avec déplacement contrôlé et sans écriture de RAM ni import de sauvegarde.
[Correctif initial v316](analysis/initial_world_v0316_report.json)
· [Trajets frais v316](analysis/initial_world_route_v0316_report.json)

**Le parcours complet sur v316 reste à refaire.** L’ancien enregistrement
commence à déplacer le héros à l’image 2501, avant que la SMS et v316 soient
jouables à l’image 2507 en NTSC. Sur la séquence courte rejouée avec ces
commandes, SMS et v316 ont les mêmes positions et états pendant 894 images.
Un décalage de phase audio NTSC déjà présent avant le récit, certains rendus
pendant les écritures de contours et le flux aléatoire restent à traiter.
Les limites sont détaillées dans [l’audit v316](analysis/completion_audit_v0316.md).

Les essais clos sont archivés et relus avant nettoyage : 21136 fichiers
générés retirés, environ 478 Mio nets libérés. Les 316 ROMs sont conservées.
[Nettoyage v316](analysis/initial_world_cleanup_v0316_report.json)

La **v0315 corrige le dernier décalage du panneau marchand** : il apparaît
à la même image que sur SMS en PAL et NTSC. Les huit étapes du portrait et la durée de la fenêtre noire
sont conservées ;43 transactions dans23 villes
et six retours d’inventaire passent. L’intro, ses flux audio et les images
du titre contrôlées restent identiques à la v314.

Le **parcours complet est également rejoué sur ce nouveau binaire** jusqu’au
générique et au retour intro :401609 images de champs de jeu comparées à
v314, sans différence, et image finale identique. Les protections de trajet
sont retirées avant les boss ; aucun objet, santé ou progression n’est importé.
La sauvegarde réelle v314 à neuf cristaux se charge normalement sur v315
en PAL/NTSC, avec objets, HUD, marqueurs et déplacement restaurés.
[Correctif marchand v315](analysis/merchant_panel_v0315_report.json)
· [Parcours v315](analysis/campaign_v0315_report.json)
· [Sauvegarde compatible](analysis/save_compatibility_v0315_report.json)
Les essais clos ont été nettoyés après archivage et relecture :16607
fichiers générés retirés, environ364 Mio nets d’artefacts libérés. Les315
ROMs numérotées, les sources, symboles et captures PNG sont préservés.
[Nettoyage des essais v315](analysis/merchant_experiment_cleanup_v0315_report.json)

Ces contrôles établissent le parcours et les scènes décrites ; ils ne
revendiquent pas une identité matérielle globale avec la SMS ni une
validation sur console physique.

La **campagne v0314 est terminée depuis Nouveau Jeu** : neuf cristaux,
Ballon, Hache d’or, Death Adder, générique complet et retour à l’intro.
Le dernier boss est vaincu sans protection avec100 prédictions exactes :
dégâts normaux20+20+32 PV, fin à20 PV. Le générique dure7423 images ;
le parcours se termine à404608. Chaque point retenu est reproduit en
RAM complète/image exacte. Une mort normale puis Continuer fait partie du
parcours ; les protections de trajet sont retirées avant chaque boss.
La sauvegarde réelle à neuf cristaux est également vérifiée ; la fidélité globale reste à auditer.
[Campagne et fin v314](analysis/cold_palace_final_v0314_report.json)
· [PV du dernier combat](analysis/palace_final_health_v0314_report.json)
La **sauvegarde à neuf cristaux** est également écrite en jeu et reproduite
exactement :592 octets du contenu et fichier SRAM identiques. Après
redémarrage, Continuer restaure les objets, les neuf marqueurs, le HUD et
le déplacement normal. Le test au premier cristal reste conservé séparément.
[Sauvegarde réelle à neuf cristaux v314](analysis/game_written_save_v0314_nine_crystals_report.json)

La **v0314** corrige le démarrage et le fondu sonore de l’intro. La première
musique, le fondu vers le titre et ses animations s’alignent sur la SMS en
PAL/NTSC : **12 959 états audio IRQ** et **40 images normalisées du titre**
comparés. Les commandes audio sont publiées ensemble pendant une section
protégée contre les interruptions. La compilation de production reproduit
exactement le binaire testé.
[Correctif intégré et preuves v314](analysis/intro_audio_integration_v0314_report.json)

Le huitième cristal et le retour extérieur sont maintenant vérifiés sur la
v314. Le boss6B/80 PV est vaincu sans protection et sans dégât pendant le
combat, avec423 prédictions exactes. Le retour compte28 prédictions et un
dégât normal de16 PV : sortie à **80/96 PV et72 PM**. Les trois points
finaux reproduisent les65 536 octets de RAM et l’image finale lors du
rejeu froid indépendant. La campagne complète reste à terminer.
[Huitième cristal et retour v314](analysis/d8_campaign_v0314_report.json)

La branche de poursuite vers D9 passe maintenant par une **mort normale,
puis Continuer et le soigneur gratuit**. Les huit cristaux et tous les objets
sont conservés. Le jeu ramène le héros en95 à24 PV/24 PM et applique sa
pénalité de8 à6 cornes ; le soigneur restaure ensuite96/96 PV. Les trois
points reproduisent toute la RAM et l’image finale, sans nouvelle écriture
de test ni import de ressources. L’accès direct à D9 et le passage CB ouvert
avec la Cloche sont maintenant vérifiés, à96 PV/24 PM. Le premier gardien est aussi vaincu ;
le deuxième gardien et le Ballon sont aussi vérifiés. Le boss principal, le neuvième cristal
et le retour extérieur sont désormais vérifiés. L’entrée, le premier gardien et les mécanismes intérieurs du palais sont validés ; la suite et la fin restent à terminer.
[Continuer et soin gratuit v314](analysis/d9_recovery_v0314_report.json)
[Entrée D9 et passage de la Cloche v314](analysis/d9_entry_v0314_report.json)

Le **premier gardien de D9** est vaincu sans protection pendant le combat :
**221 prédictions exactes**, une perte normale de20 PV, fin à76/96 PV et
72 PM. Les deux actions Terre, le mécanisme associé, la préparation et
la fermeture de la protection sont couverts par cinq rejeux RAM/image exacts.
[Premier gardien D9 v314](analysis/d9_midboss_v0314_report.json)

Le **deuxième gardien de D9** est également vaincu sans protection pendant
le combat : **292 prédictions exactes**, deux dégâts normaux de20 PV, fin
à56/96 PV. Le **Ballon est ensuite acquis normalement** ; la fin de cette
étape se termine à76 PV/72 PM. Huit points sont relus en RAM complète et
image exacte, avec les quatre dangers persistants62 conservés sur le trajet.
[Deuxième gardien et Ballon v314](analysis/d9_balloon_v0314_report.json)

Le déplacement du héros est aussi comparé directement à la SMS sur la v314 :
**96 cas** couvrent six terrains, les bottes et les quatre directions en
NTSC/PAL. **3 072 états de mouvement** sont identiques : positions, direction,
animation, compteur, vitesses et contexte de terrain. Les deux systèmes ont
la même cadence émulée dans chaque région. Ce contrôle utilise des cartes
et des acteurs préparés ; il ne couvre pas la charge complète d’un combat.
[Cadence de déplacement v314](analysis/terrain_walk_v0314_game_report.json)

Les **neuf cristaux et le retour extérieur de D9** sont maintenant vérifiés.
Le boss6C/90 PV est vaincu sans protection : **291 prédictions exactes**, un
seul dégât normal de20 PV avant le soin du cristal. Le retour compte67
prédictions et se termine à **104/104 PV et72 PM**, enEB. Les quatre derniers
points sont relus avec RAM complète et image exacte. Le test du palais
final, de la Hache d’or et de la fin est lancé sur cette même ROM.
[Neuvième cristal et retour v314](analysis/d9_campaign_v0314_report.json)

Le **Ballon est utilisé normalement**, puis la carte du monde se referme
avec restitution du décor/HUD vérifiée sur768 mots physiques. La **porte
aux neuf cristaux** s’ouvre réellement et l’entrée du palais18D est relue en
RAM/image exacte, à104 PV/72 PM. Les deux gardiens et la Hache d’or sont vérifiés.
Death Adder et le générique sont vérifiés ; la sauvegarde à neuf cristaux est également vérifiée.
[Ballon et retour de carte v314](analysis/owned_overview_v0314_report.json)
· [Porte et entrée du palais v314](analysis/cold_palace_entry_v0314_report.json)

Le **premier gardien du palais** est vaincu avec **165 prédictions exactes**
et cinq points de rejeu RAM/image. La protection est retirée avant sa salle :
2 PV sont perdus sur le trajet, puis20 pendant le combat. Un butin de soin
normal ramène ensuite les PV de82 à104 ; le bilan ne revendique donc pas
un combat sans dégât. Le compte précis des pertes/récupérations est conservé.
[Premier gardien du palais v314](analysis/cold_palace_giant_v0314_report.json)
· [Bilan des PV](analysis/palace_giant_health_v0314_report.json)

Les portails, les deux passages Terre et le mécanisme intérieur du palais
sont également vérifiés : cinq points reproduisent la RAM complète et
l’image finale. Le parcours atteint339379 images depuis Nouveau Jeu ;
le gardien suivant, la Hache d’or et la fin restent en test.
[Mécanismes intérieurs v314](analysis/cold_palace_inner_v0314_report.json)

Les anciens monstres et objets restent masqués pendant les changements de
carte extérieurs : quatre directions en PAL/NTSC, tables matérielles de
sprites contrôlées, persistance et reprise du jeu conservées. Ce test préparé
ne prouve pas chaque pixel du décor ni une durée identique de transition.
[Objets pendant le scrolling v314](analysis/scroll_objects_v0314_report.json)
Le contrôle du **flash d’ancienne carte** passe également sur dix fins de
scroll naturelles : fond stable sur trois images après publication, en
PAL/NTSC, hors rectangles des sprites. Aucune comparaison de cadence
SMS globale n’est déduite de ce contrôle.
[Publication du décor v314](analysis/scroll_publish_v0314_report.json)

Le **gardien11E/7C** est vaincu sans protection : **405 prédictions exactes**,
trois coups normaux de24 PV, fin à32 PV. La **Hache d’or est acquise réellement**
en11D, avec une fin d’étape à56 PV/72 PM. Six points supplémentaires
reproduisent RAM et image. Death Adder et le générique sont maintenant
vérifiés ; la sauvegarde finale reste en cours de vérification.
[Gardien et Hache d’or v314](analysis/cold_palace_guardian_v0314_report.json)
· [Bilan des PV](analysis/palace_guardian_health_v0314_report.json)

Sur ce binaire, le parcours depuis Nouveau Jeu atteint **neuf cristaux**,
avec la hache et la première fée de vie obtenues normalement. Le boss de D2
est vaincu sans protection ni dégât :89 prédictions conformes, puis cristal
et retour extérieur à **48/48 PV et24 PM**. Un dégât normal de4 PV sur le
retour est compensé pendant le trajet. Les huit étapes retenues de D2 ont
un rejeu indépendant exact de toute la RAM et de l’image finale ; les deux
essais de contrôleur infructueux sont conservés et exclus de cette preuve.
[Parcours D1 publié](analysis/d1_campaign_v0314_report.json)
· [Hache et fée de vie](analysis/d2_approach_v0314_report.json)
· [Deuxième cristal et retour](analysis/d2_campaign_v0314_report.json)

Le quatrième boss est vaincu sans protection et sans dégât pendant le combat,
avec **239 prédictions exactes**. Le retour extérieur se termine à62/64 PV ;
les dégâts de sol avant et après le boss restent comptabilisés. Le canoë est
également vérifié sur99 images de déplacement dans l’eau.
La magie de feu est obtenue contre l’huile, puis la deuxième épée est offerte
normalement. Le parcours atteint ensuite l’entrée de D5, avec72 PM maximum.
[Quatrième cristal](analysis/d4_campaign_v0314_report.json)
· [Feu, deuxième épée et D5](analysis/fire_sword_v0314_report.json)

Le **don d’huile**, les deux escaliers de la maison C7 et le retour extérieur
sont vérifiés, sans nouvelle écriture de test ni modification des ressources
pendant le dialogue. Le parcours passe par1F→0F→1F→C7.
[Huile et escaliers v314](analysis/oil_service_v0314_report.json)

La v314 a **réellement écrit une sauvegarde** dans le premier emplacement.
Son rejeu reproduit les592 octets du contenu et le fichier SRAM, puis un
redémarrage et **Continuer** restaurent les objets, le premier cristal,
le HUD physique et le déplacement. Aucun état SRAM synthétique n’est utilisé.
La sauvegarde à neuf cristaux écrite sur v313 reste également compatible avec
v314 en PAL/NTSC. Le palais final et la sauvegarde à neuf cristaux restent à terminer sur ce binaire.
[Sauvegarde écrite et Continuer au premier cristal](analysis/game_written_save_v0314_first_crystal_report.json)
· [Compatibilité de sauvegarde v313](analysis/save_compatibility_candidate11_v0313_report.json)

La musique et les bruitages de Nouveau Jeu/Continuer sont vérifiés dans les
deux régions. Six parcours de menu, dont les deux premières boutiques,
conservent les mêmes fenêtres noires et reprises de jeu que la SMS, le HUD
et une fermeture silencieuse.
[Menu de démarrage](analysis/start_menu_candidate11_v0313_report.json)
· [Menu en jeu](analysis/inventory_candidate11_v0313_report.json)

La **v0313** conserve la preuve d’une campagne complète depuis Nouveau Jeu :
neuf cristaux, ballon, vraie Hache d’or, **Death Adder vaincu sans protection**,
générique complet et retour à l’intro. Le dernier combat commence à100 PV,
inflige un coup normal de32 PV et se termine à68 PV. Le point final atteint
l’image **379 823**, avec rejeu indépendant exact RAM/image. Les protections
d’approche sont retirées avant chaque boss ; aucun état de progression,
objet, santé ou SRAM n’est importé dans cette campagne. Cette preuve reste
liée au binaire v313 ; la fidélité globale R/IRQ, audiovisuelle et matérielle
reste ouverte.
[Campagne et fin v313](analysis/cold_palace_final_v0313_report.json)
· [Neuvième cristal](analysis/d9_campaign_v0313_report.json)
· [Sauvegarde écrite en jeu](analysis/game_written_save_v0313_report.json)

Les étapes v312/v313 ci-dessous conservent leurs périmètres historiques.

Les étapes v312 ci-dessous documentent la préparation du parcours et les
corrections précédentes.

La **v0312** corrige la vitesse de la transition marchande : neuf images
noires et les huit étapes du portrait s’alignent sur SMS en PAL et NTSC.
Les 43 cas contrôlés couvrant les 23 villes passent. Le parcours NTSC jusqu’à
la sortie de D2 conserve les champs de jeu comparés à la v311 sur 35 782
images, et son image finale. Le panneau complet reste une image tardif en PAL.
[Correction marchande et restauration du menu v312](analysis/merchant_inventory_v0312_report.json)

La musique et les bruitages du menu Nouveau jeu / Continuer sont contrôlés
sur v312 en PAL/NTSC : musique active et audible, événements de sélection et
de validation aux mêmes images que sur SMS, pression sur le choix déjà actif
silencieuse. [Contrôle du menu de démarrage](analysis/start_menu_v0312_report.json)

La campagne v312 reprend depuis le démarrage avec les deux premiers boss
sans protection, puis récupère l’huile par le dialogue et les deux escaliers.
Le héros ressort avec **48 PV, 24 PM et 8 cornes**, sans nouvelle écriture
d’aide pendant le service. Approche et visite ont chacune un rejeu RAM/image
exact. [Rapport de l’huile v312](analysis/oil_service_v0312_report.json)

La v312 récupère ensuite la corde, active le mécanisme avec les ennemis
présents, obtient la clé et le troisième cristal, puis ressort à **56/56 PV**.
Le boss type69 est vaincu sans protection ni dégât reçu. Combat et retour
ont leur rejeu froid RAM/image exact, avec les trois marqueurs du HUD vérifiés.
[Corde, mécanisme et clé](analysis/d3_progress_v0312_report.json)
· [Troisième cristal et sortie](analysis/d3_campaign_v0312_report.json)

La préparation de D4 sur v312 vérifie le don de 50 cornes et l’achat de Terre
pour 50 : argent **18→68→18**, niveau **0→1**, magie **24→48**. Les quatre
étapes passent leur rejeu RAM/image ; aucun objet ni argent n’est injecté.
[Apprentissage de Terre v312](analysis/earth_learning_v0312_report.json)

Dans D4, la v312 récupère le canoë, franchit deux passages avec Terre et
obtient la clé d’accès au boss. Les sept étapes passent leur rejeu RAM/image,
avec **56 PV et 40 PM** au dernier point avant le combat. Le quatrième
cristal et le retour en extérieur sont vérifiés à **62/64 PV**, sans protection
ni dégât pendant le boss. Combat et sortie ont un rejeu RAM/image exact ; le
déplacement en canoë et les quatre marqueurs du HUD sont contrôlés.
[Progression D4 v312](analysis/d4_progress_v0312_report.json)
· [Quatrième cristal et sortie](analysis/d4_campaign_v0312_report.json)

La suite v312 échange l’huile contre Feu, reçoit l’épée longue et entre dans
D5 à **62/64 PV et 72/72 PM**. Les sept étapes passent le rejeu RAM/image ;
la hache reste équipée et les quatre cristaux sont conservés.
[Feu, épée longue et entrée D5](analysis/fire_sword_v0312_report.json)

Dans D5, la v312 obtient la première clé, ouvre le passage Terre, récupère les
bottes et ressort pour se ravitailler à **58/64 PV et 64 PM**. Les quatre
étapes ont un rejeu RAM/image exact, avec le gain de vitesse actif et les
quatre cristaux conservés. Ce ravitaillement précède le cinquième boss.
[Bottes et sortie de ravitaillement v312](analysis/d5_progress_v0312_report.json)

Le ravitaillement v312 vérifie deux dons de 30 cornes, l’achat d’une clé pour
60 et le soin gratuit. Le héros revient dans D5, ouvre le second passage Terre
et franchit le mécanisme à **64/64 PV et 56 PM**, avec une clé. Les treize
étapes depuis l’entrée initiale ont un rejeu RAM/image exact.
[Ravitaillement et mécanisme D5 v312](analysis/d5_supplies_v0312_report.json)

Le cinquième cristal et le retour en extérieur sont vérifiés sur v312 à
**72/72 PV et PM**. Les huit satellites et le boss 65 sont vaincus sans
protection ; un coup normal retire dix PV pendant le combat. Les cinq étapes
finales passent leur rejeu RAM/image, avec les cinq marqueurs du HUD vérifiés.
Le pilote de test cible désormais les satellites : sa recherche passe de
415 à 60 décisions sur ce combat. [Cinquième cristal et sortie v312](analysis/d5_campaign_v0312_report.json)

La préparation de D6 sur v312 vérifie cinq acquisitions de clés, les passages
Terre et la Cloche de glace. Les 17 étapes ont un rejeu RAM/image exact ;
le héros rejoint l’accès du boss à **72/72 PV et 64 PM**. L’aide reste limitée
aux approches ; aucun objet ni ressource n’est injecté. Le retrait de l’aide avant
la salle du boss est relu exactement à l’image 156803, sans modifier les
ressources ni supprimer les ennemis ordinaires restants de l’antichambre.
[Clés, Terre et Cloche de glace v312](analysis/d6_progress_v0312_report.json)
· [Retrait de l’aide avant le boss](analysis/d6_guard_release_v0312_report.json)

Le sixième boss et son cristal sont ensuite vérifiés sur v312, sans protection
ni dégât reçu. Le retour en extérieur conserve **80/80 PV et 72 PM**. Combat
et sortie passent chacun leur rejeu froid RAM/image exact ; les six marqueurs
et les 128 mots physiques du HUD sont contrôlés. Le retour utilise des décisions
plus fines après l’immobilisation du premier pilote dans une salle, sans changer
la ROM ni réactiver l’aide. [Sixième cristal et sortie v312](analysis/d6_campaign_v0312_report.json)

La préparation de D7 vérifie l’achat d’une clé pour 60 cornes, l’entrée du
donjon, deux acquisitions de clés et deux ouvertures Terre coûtant 16 PM.
Les sept étapes passent leur rejeu RAM/image exact. Le point préparatoire
conserve six cristaux, **64 PV, 56 PM et deux clés**. Le septième cristal
reste à valider.
[Ravitaillement, clés et Terre D7 v312](analysis/d7_prep_v0312_report.json)

Le combat intermédiaire de D7 est ensuite gagné sans protection. Un coup
normal retire 12 PV ; l’approche suivante reprend à **52 PV et 56 PM** après
la victoire. Le retrait de l’aide, le passage, le combat et la reprise ont
chacun un rejeu froid RAM/image exact. Le boss principal n’est pas encore
validé dans cette étape. [Combat intermédiaire D7 v312](analysis/d7_midboss_v0312_report.json)

Le navire, le septième cristal et le retour en extérieur sont ensuite vérifiés
sur v312. Les deux combats de D7 et le retour se déroulent sans protection ;
les dégâts reçus restent enregistrés. Les dix étapes depuis la reprise passent
leur rejeu froid RAM/image exact, avec les 128 mots physiques du HUD contrôlés
après le navire, le cristal et la sortie. Le héros ressort à **68/88 PV et 64 PM**,
avec sept cristaux, une clé et le navire.
[Navire D7 v312](analysis/d7_ship_v0312_report.json)
· [Septième cristal et sortie v312](analysis/d7_campaign_v0312_report.json)

Le passage vers D8 coûte réellement dix cornes, **12→2**, puis le gardien
intermédiaire est vaincu sans protection ni dégât reçu, à **56/88 PV**.
Les six étapes depuis la sortie de D7 passent leur rejeu froid RAM/image exact.
Le huitième cristal reste à vérifier.
[Passage, entrée et gardien D8 v312](analysis/d8_midboss_v0312_report.json)

La clé des voleurs, les mécanismes distants et le passage Terre de D8 sont
ensuite vérifiés par huit points avec rejeu RAM/image exact. L’accès au boss
principal est atteint à **88/88 PV et 72 PM**, avec la clé spéciale et le navire.
[Clé des voleurs et approche D8 v312](analysis/d8_approach_v0312_report.json)

La **v0311** ajoute une image au chargement lors des défilements de donjon
vers le haut en NTSC. Sur trois trajets comparés à la Master System, la
reprise du jeu s’aligne. Le premier déplacement s’aligne aussi dans les deux
salles où le bouton testé permet de bouger. Le premier donjon, son cristal
et la sortie ont passé le rejeu sur cette ROM. La v0310 est la version
vérifiée de Nouveau Jeu au générique.
[Comparaison des défilements](analysis/upward_ntsc_candidate_report.json)
· [Validation du premier donjon v311](analysis/upward_ntsc_d1_report.json)

La clé supplémentaire, le coffre et le retour en extérieur avec la hache équipée sont vérifiés sur v311.
[Rapport du parcours de la hache](analysis/axe_route_v0311_report.json)

La fée, l’entrée de D2 et ses trois clés ont passé le rejeu sur v311.
Le deuxième cristal et le retour en extérieur sont vérifiés à **48/48 PV**,
sans protection ni dégât pendant le boss. Combat et retour ont chacun une
relecture froide RAM/image exacte.
[Approche de D2](analysis/d2_approach_v0311_report.json)
· [Boss, cristal et sortie](analysis/d2_campaign_v0311_report.json)

Le premier [candidat marchand](analysis/merchant_candidate_v0311_report.json)
reste conservé comme diagnostic. La v312 utilise une routine marchande
distincte et conserve les chargements PAL/NTSC contrôlés de la v311.

La **[v0310 raccorde la récurrence du hasard SMS](analysis/rng_integration_v0310.md)**
aux routines du jeu : ennemis, butin, historique des salles et mini-jeu.
Les lectures directes de R sont séparées des appels 04E1. Le fournisseur de R
reste provisoire ; sa phase exacte avec les interruptions reste à porter.
Tests PC et 68000 PAL/NTSC réussis, démarrage/déplacement relus exactement,
et vraie sauvegarde v309 rechargeable avec objets, cristaux, arbre et HUD.
La campagne v310 est vérifiée depuis Nouveau Jeu jusqu’au générique et au
retour à l’intro. [Rapport de la campagne](analysis/cold_palace_final_v0310_report.json)

Un [nouveau parcours v310 termine le premier donjon](analysis/d1_campaign_v0310.md)
et ressort avec le premier cristal à **28/32 PV**. Première clé sans aide,
approche ensuite assistée, boss et retour sans protection. Les quatre étapes
ont une relecture RAM/image exacte ; HUD et marqueur de cristal sont contrôlés.

La suite récupère [la hache et le don de vie](analysis/d2_approach_v0310.md),
puis [le deuxième cristal et ressort de D2](analysis/d2_campaign_v0310.md)
à **31/48 PV**. Le boss type63 est combattu sans protection ; les cinq étapes
D2 ont une relecture RAM/image exacte, avec les deux marqueurs vérifiés.
La protection reste limitée aux approches et aucune ressource n'est injectée.

Le parcours v310 reçoit ensuite [l'huile par son dialogue et ses escaliers](analysis/oil_service_v0310.md),
puis [la corde et le troisième cristal](analysis/d3_campaign_v0310.md).
Retour en extérieur à **46/56 PV**, trois cristaux conservés. Les huit étapes
D3 ont une relecture RAM/image exacte ; le boss type69 est combattu sans garde.

La préparation D4 valide [le don de 50 cornes et l'achat de Terre](analysis/earth_learning_v0310.md) :
argent 2→52→2, Terre niveau 1 et réserve de 48 PM, avec quatre relectures exactes.

La suite valide [le canoë, le quatrième cristal et la sortie de D4](analysis/d4_campaign_v0310.md)
à **62/64 PV**. Les quinze étapes ont une relecture RAM/image exacte ; le boss
type6A est vaincu sans protection. Deux passages Terre et le déplacement sur
l'eau avec le canoë sont vérifiés. Le mécanisme facultatif B0 reste hors parcours.

Le même parcours [échange l'huile contre Feu et reçoit l'épée longue](analysis/fire_sword_v0310.md),
puis entre dans D5 à **62/64 PV et 72/72 PM**. Sept relectures RAM/image exactes.
La suite [récupère les bottes et ressort pour se ravitailler](analysis/d5_progress_v0310.md)
à **56/64 PV**, avec quatre relectures exactes. Cette sortie précède le cinquième boss.

Le [ravitaillement et le mécanisme de D5](analysis/d5_supplies_v0310.md) passent,
puis le [cinquième cristal et le retour extérieur](analysis/d5_campaign_v0310.md)
sont validés à **72/72 PV et PM**. Le boss 65 et ses huit satellites sont vaincus
sans protection, avec 96 fenêtres de prédiction exactes pour le combat et onze
pour le retour.

La [préparation de D6](analysis/d6_progress_v0310.md) valide ensuite les clés,
sept lancers de Terre, les mécanismes et la cloche de glace. Ses dix-sept étapes
sont relues exactement ; le dernier point avant le boss est à **72/72 PV et 40 PM**.

Le [sixième cristal et le retour de D6](analysis/d6_campaign_v0310.md) sont aussi
validés, avec 1 202 prédictions exactes pour le combat et 121 pour le retour.
Le héros ressort vivant à **2/80 PV et 72 PM**, sans protection pendant le boss
ou la sortie.

La suite valide [une mort normale, Continuer et le soin gratuit de 94](analysis/death_heal_v0310.md).
Les six cristaux et l'inventaire sont conservés : reprise à 24 PV/PM, puis nuit
restaurant **80/80 PV**, avec **24/72 PM, 21 cornes et deux clés**.
Trois relectures RAM/image exactes ; aucune nouvelle écriture d'aide ni ressource
injectée depuis le retour de D6.

La campagne v310 franchit le pont du cinquième cristal puis entre dans D7 à
**68/80 PV, 24/72 PM et deux clés**. Le pilote lit désormais l'état persistant
qui ouvre ce pont. Le trajet est relu depuis le démarrage avec une RAM et une
image finales identiques. [Rapport d'entrée D7](analysis/d7_entry_v0310_report.json)

Deux clés supplémentaires sont ramassées dans D7 et deux obstacles sont détruits
avec Terre dans la salle 1B9. Le héros arrive avant le boss intermédiaire à
**80/80 PV, 24/72 PM et trois clés**. Les quatre étapes ont une relecture
exacte de la RAM et de l’image finale. [Rapport de préparation D7](analysis/d7_prep_v0310_report.json)

Le gardien de D7, en 1B8, est vaincu à la hache avec **80/80 PV**. La
protection est retirée avant la salle. Le combat et sa relecture aboutissent
avec la même RAM et la même image finale.
[Rapport du gardien de D7](analysis/d7_midboss_v0310_report.json)

Le levier de 1E6 ouvre la salle du coffre de 1D5. Le bateau est récupéré par
les commandes du jeu et la fenêtre de récompense se ferme. Le héros conserve
**80/80 PV, 40/72 PM et trois clés**. Le HUD et les six marqueurs de cristal
sont contrôlés après le coffre. [Rapport du bateau](analysis/d7_ship_v0310_report.json)

Le boss principal de D7 est vaincu sans protection ni dégât reçu. Le septième
cristal est obtenu et le héros ressort avec le bateau, **88/88 PV, 64/72 PM et
deux clés**. La sortie et les étapes qui y mènent sont rejouées depuis le
démarrage avec la même RAM et la même image finale. [Rapport de D7](analysis/d7_campaign_v0310_report.json)

Le passage côtier vers D8 coûte dix cornes. Après l’entrée dans D8, le gardien
de 1C9 est vaincu sans protection et le héros termine à **22/88 PV**. Les
six étapes depuis la sortie de D7 ont une relecture exacte. [Rapport du gardien de D8](analysis/d8_midboss_v0310_report.json)

Après le gardien, les mécanismes de 1EB et 1EC, le passage de Terre et le
coffre de la clé des voleurs ont été rejoués exactement. Le héros conserve
sept cristaux et termine cette étape avec **62/88 PV et 72/72 PM**.
[Rapport de la clé des voleurs](analysis/d8_thief_key_v0310_report.json)

Le boss principal de D8 est vaincu sans invincibilité ni dégât reçu. Le
huitième cristal est récupéré à l’image **272 980** avec **96/96 PV**.
Un rejeu depuis le démarrage reproduit les 65 536 octets de RAM et l’image
finale. Le retour en extérieur est vérifié à l’image **273 836**. Le héros
conserve ses huit cristaux, **96/96 PV, 72/72 PM et deux clés**.
[Rapport du huitième donjon](analysis/d8_campaign_v0310_report.json)

Vers D9, le passeur débite dix cornes et la cloche de glace ouvre le
passage en CB. Le héros entre avec huit cristaux, **96/96 PV, 72/72 PM,
deux clés et dix cornes**. Les trois étapes sont rejouées exactement.
[Rapport de l’entrée de D9](analysis/d9_entry_v0310_report.json)

Deux sorts Terre ouvrent le chemin vers le premier gardien de D9. Il est
vaincu sans invincibilité et le héros conserve **44/96 PV, 72/72 PM et
deux clés**. Le rejeu reproduit exactement la RAM et l’image finale.
[Rapport du premier gardien de D9](analysis/d9_midboss_v0310_report.json)

Le second gardien est vaincu sans invincibilité. Le ballon est récupéré dans
le coffre et son acquisition est confirmée par un rejeu exact. Le héros
conserve ses huit cristaux, **52/96 PV, 72/72 PM et deux clés**.
[Rapport du second gardien et du ballon](analysis/d9_balloon_v0310_report.json)

Le boss principal de D9 est vaincu sans invincibilité et le neuvième cristal
est récupéré. Le héros ressort à l’image **315 457** avec **102/104 PV,
64/72 PM et deux clés**. Le rejeu de la sortie reproduit exactement la RAM
et l’image finale. [Rapport du neuvième donjon](analysis/d9_campaign_v0310_report.json)

Le ballon affiche la vue d’ensemble et restaure la carte et le HUD à la
fermeture. Les neuf cristaux ouvrent ensuite la porte du palais. Le héros
reprend le contrôle dans le palais avec **102/104 PV et 64/72 PM**.
[Rapport du ballon en extérieur](analysis/owned_overview_v0310_report.json)
· [Rapport de l’entrée du palais](analysis/cold_palace_entry_v0310_report.json)

Les deux premiers mécanismes du palais sont activés et le géant est vaincu
sans invincibilité. Le héros termine avec **84/104 PV, 72/72 PM et deux clés**.
Cinq étapes sont reproduites exactement en RAM et en image.
[Rapport du géant du palais](analysis/cold_palace_giant_v0310_report.json)

Le portail intérieur, deux passages de Terre et le levier distant sont
vérifiés par des rejeux exacts. Le héros termine cette étape avec
**104/104 PV, 72/72 PM et deux clés**.
[Rapport des mécanismes intérieurs](analysis/cold_palace_inner_v0310_report.json)

Le gardien de la Hache d’or est vaincu sans invincibilité. La hache est
récupérée dans le coffre et équipée avec **104/104 PV et 72/72 PM**.
[Rapport du gardien et de la Hache d’or](analysis/cold_palace_guardian_v0310_report.json)

**La campagne v310 est vérifiée depuis Nouveau Jeu jusqu’au générique.**
Death Adder est vaincu avec la Hache d’or, sans invincibilité ni dégât reçu.
La fin affiche les neuf cristaux, déroule le générique et revient à l’intro.
Le rejeu depuis le démarrage atteint l’image **415 125** avec la même RAM et
la même image finale. Les approches ont utilisé une protection de test
retirée avant chaque boss. [Rapport de la campagne v310](analysis/cold_palace_final_v0310_report.json)

Une sauvegarde écrite en jeu dans le premier emplacement a été rechargée
après redémarrage via **Continuer**. Le jeu restaure le point de reprise,
les statistiques, les objets et les neuf cristaux. Le HUD et le déplacement
ont été vérifiés après la reprise.
[Rapport de la sauvegarde v310](analysis/game_written_save_v0310_report.json)

Les défilements des premières cartes ont été vérifiés en NTSC et PAL.
Les pixels du décor restent stables dès l’affichage de la nouvelle carte,
et les anciens monstres et objets disparaissent dans les quatre directions
testées. [Rapport des défilements](analysis/scroll_v0310_report.json)

La musique et les bruitages de Nouveau Jeu / Continuer sont vérifiés en NTSC
et PAL. En jeu, les essais d’inventaire en extérieur et dans deux boutiques
confirment la fermeture silencieuse, le HUD visible, la restauration du décor
fixe et les mêmes durées d’écran noir que sur SMS. [Rapport des menus](analysis/menu_v0310_report.json)

Chez le premier marchand, les écrans stabilisés, les achats et les refus
comparés correspondent à la SMS. L’ouverture reste trop rapide. La zone de
jeu reste noire 5 images en NTSC et 4 en PAL sur Mega Drive, contre 9 sur
Master System dans les deux régions. Le HUD reste visible. [Rapport du marchand](analysis/merchant_v0310_report.json)

Le [mini-jeu est aussi comparé sur v310](analysis/minigame_rng_v0310.md) :
douze cas SMS/MD en PAL/NTSC, cartes, paiements, récompenses, nouvelle partie,
refus et retour depuis l'inventaire. Les tirages sont contrôlés pour ce test ;
les probabilités et la phase naturelle du hasard restent à vérifier.

La [branche de production du boss à satellites](analysis/second_boss_rng_v0310.md)
passe aussi 732 cas par région : état des acteurs, graine finale et nombre de
tirages correspondent aux instructions SMS avec des entrées contrôlées.

Le titre v310 a été comparé à la SMS après l’intro complète, en NTSC et PAL.
La cape garde ses poses de six images, le guerrier ses paliers de six images,
et le logo avance d’une ligne par image. Les quarante images comparées sont
identiques après normalisation des palettes. La séquence démarre 21 images
plus tôt en NTSC et 22 en PAL. L’avance est déjà présente au premier
dévoilement de l’intro. Les 65 lignes du récit correspondent dans les deux
régions et leur décalage ne s’accumule pas. [Mesures de l’intro](analysis/intro_timing_v0310_report.json) · [Mesures du titre](analysis/title_cadence_v0310_report.json)

La [campagne v0309 depuis Nouveau Jeu atteint la fin](analysis/cold_palace_final_v0309.md) :
neuf cristaux, palais, Hache d’or, Death Adder, générique complet et retour
au cycle intro/titre. Les approches utilisent les protections de test
autorisées ; les combats de boss se déroulent sans protection. Aucun import
SRAM/RAM ni écriture de ressources ou de progression. Le combat final se
termine à 100 PV, avec 180 prédictions et une relecture RAM/image exactes.
Les onze nouveaux points de contrôle du dernier palais sont vérifiés.
Le [cycle réel Sauvegarder/Continuer](analysis/game_written_save_v0309.md) est
aussi vérifié : 592 octets sérialisés, relecture RAM/image/SRAM exacte,
rechargement normal sans retrait d’ennemis, objets et neuf cristaux restaurés,
arbre coupé persistant et déplacement possible. La fidélité globale SMS, les
autres cas de sauvegarde, les contenus optionnels et les essais matériels
restent ouverts.

La **v0309 regroupe les transferts du palais dans la file VBlank existante**.
Le test SMS/MD conserve les 289 images et tous les décalages de la secousse.
Le parcours v0309 depuis Nouveau Jeu valide maintenant **les neuf cristaux et
le retour du neuvième donjon**, à 102/104 PV et 64 PM en extérieur EB.
Le géant optionnel et le ballon sont aussi couverts. Les trois gardiens D9
sont vaincus sans protection pendant les combats ; aucune aide ne reprend
pendant le retour du boss principal. Les 20 points de contrôle D9 ont des
relectures exactes sur toute la RAM et le PNG final. Le HUD physique et les
neuf marqueurs sont vérifiés après le dernier cristal et la sortie.
Voir [le neuvième cristal et le retour](analysis/d9_campaign_v0309.md),
[le géant et le ballon](analysis/d9_balloon_v0309.md),
[le premier gardien](analysis/d9_midboss_v0309.md),
[l'entrée avec la cloche](analysis/d9_entry_v0309.md)
et [le huitième donjon](analysis/d8_campaign_v0309.md).

L'[usage réel du ballon](analysis/owned_overview_v0309.md) est aussi vérifié :
carte générale, fermeture, restauration de la salle et des 768 mots physiques
carte/HUD, avec relecture RAM/image exacte et ressources conservées.
L'[entrée du palais depuis cette partie](analysis/cold_palace_entry_v0309.md)
est validée après l'ouverture réelle par les neuf cristaux, à 102/104 PV.
Le [premier géant du palais](analysis/cold_palace_giant_v0309.md) est désormais
vaincu sans protection pendant le combat, à 86/104 PV. Les cinq points de
contrôle ont une relecture RAM/image exacte ; 185 prédictions sont vérifiées.
Les [passages Terre et le levier suivant](analysis/cold_palace_inner_v0309.md)
sont aussi vérifiés : cinq relectures exactes, retour en 12A à 104 PV/64 PM.
Le [gardien et la vraie Hache d’or](analysis/cold_palace_guardian_v0309.md)
sont vérifiés : combat sans protection ni dégât reçu, six relectures exactes,
hache acquise en 11D, héros à 104 PV/72 PM. La dernière portion du palais
et la fin sont maintenant vérifiées dans le bilan lié ci-dessus. Les preuves
contrôlées antérieures restent séparées.

La progression ne prouve pas toute la fidélité SMS : le [relevé des sources](analysis/native_remaining_v0309.md)
distingue les appels aléatoires SGDK encore provisoires, les estimations de
phase et les anciens commentaires devenus obsolètes.

Le **scénario contrôlé antérieur du palais atteint aussi la fin du jeu** :
géant et gardien sans protection,hache dorée,Death Adder,générique complet
et retour au flux titre. Le combat final commence à100PV contre90PV pour
le boss ; le héros gagne à48PV. Aucune écriture de test après le retrait de
l'invincibilité avant le boss. Les relectures du combat et de la fin
reproduisent les65536 octets de RAM et le PNG final.
Voir [Death Adder et la fin](analysis/controlled_palace_ending_v0309.md),
ainsi que les [mécanismes du palais](analysis/controlled_palace_phase3_v0309.md).

Ce scénario démarre avec **une SRAM synthétique dérivée du parcours neuf
cristaux v0306**. Il reste séparé de la campagne depuis Nouveau Jeu. La
campagne froide complète sur v0309 est désormais vérifiée séparément ; les
contenus optionnels, la fidélité globale SMS et les essais matériels restent ouverts.

La **v0308 restaure l'ouverture du passage vers le palais apres les neuf
cristaux**. Le test controle SMS/MD reproduit les289 images,les neuf amplitudes
de secousse et chaque changement de decalage. Avec huit cristaux,le passage
reste ferme. Voir [le correctif du palais](analysis/palace_gate_v0308.md).
Ce controle utilise un scenario isole ; le parcours complet v0309 est maintenant verifie separement.

La **v0306 restaure le HUD après les fenêtres d’objet et de cristal** et
affiche les neuf indicateurs de cristal selon la table SMS. Les comparaisons
PAL/NTSC couvrent 22 scénarios, 44 images après fermeture et les fenêtres
avant fermeture : carte physique du HUD et tuiles utilisées conformes.

Le parcours v0306 valide les **neuf cristaux et le retour dehors en EB**,
a **104/104 PV et72/72 PM**, avec une cle,37 pieces,la cle des voleurs,
Feu,Terre,canoe,corde,bottes,cloche de glace,bateau et epee longue.
La hache1 est selectionnee ; l'epee longue reste2 et l'armure1.
Les objets,les cles,l'argent et les soins proviennent des actions du jeu.

Le **neuvieme boss et le retour sont valides sans protection**. Le trajet
regroupe le portail et les deux mecanismes avant le principal6C. L'epee longue2
est choisie par le menu ; une entree UP ordinaire corrige le controleur de test.
Six nouveaux checkpoints reproduisent toute la RAM et l'image finale ;200
fenetres de prediction sont identiques. Les128 mots du HUD et les neuf
indicateurs sont verifies. Voir [le neuvieme cristal](analysis/d9_campaign_v0306.md),
[l'acces au donjon](analysis/d9_entry_v0306.md) et [son premier boss intermediaire](analysis/d9_midboss_v0306.md).
La fin est validee separement dans le scenario controle v0309 decrit plus haut.
Les sauvegardes et la fidelite globale restent a valider.
La note [REPRISE_CODEX.md](REPRISE_CODEX.md) contient le point de reprise courant.

Les **21 étapes validées du sixième donjon** comprennent la sélection de la
hache par le menu, les clés, les mécanismes, sept lancers de Terre, la cloche,
le combat et le retour. Chaque étape possède une relecture froide indépendante
identique sur les 65 536 octets de RAM et le PNG final.
Les protections d’approche sont retirées avant les boss principaux et ne sont
pas réactivées pendant le retour. Aucun PV ni objet n’est injecté.
Les 128 mots du HUD final et les six indicateurs de cristal sont vérifiés.

Le dernier profil, jusqu’à la sortie du huitième donjon à **235 211 images**, observe
**402 octets de marge de pile**, sans corruption du tas. Cette mesure concerne
ce parcours v0306 ; elle ne couvre pas tout le palais v0309. Le portage complet
et la fidélité audiovisuelle globale restent à valider.
Voir le [huitième cristal](analysis/d8_campaign_v0306.md),
le [septième cristal](analysis/d7_campaign_v0306.md),
le [sixième cristal](analysis/d6_campaign_v0306.md),
le [cinquième cristal](analysis/d5_campaign_v0306.md),
le [parcours Feu et épée](analysis/fire_sword_v0306.md) et le
[correctif du HUD v0306](analysis/reward_hud_v0306.md).

L'approvisionnement du **septième donjon est aussi validé** : deux dons de
30 pièces, achat réel d'une clé pour 60, ouverture de la porte et première clé
récupérée en 1CB. Huit relectures indépendantes reproduisent la RAM et l'image
finales. Cette étape conserve les six cristaux et s'achève à **72/80 PV**.
Une première branche de test qui effaçait le délai des dégâts de terrain est
exclue ; le trajet retenu préserve ce délai. Aucun changement de ROM.
Voir [l'entrée du septième donjon](analysis/d7_supplies_v0306.md).

La suite valide le **combat intermédiaire du septième donjon sans protection**,
vaincu avec **80/80 PV**, puis la **récupération du bateau**. Ce jalon
s’achève en 1D5, à **80/80 PV, 72/72 PM et deux clés**, avec six cristaux. Dix nouveaux
checkpoints reproduisent toute la RAM et l'image finale. Les 128 mots du HUD
après la fenêtre du bateau et les six indicateurs de cristal sont vérifiés.
La protection d'approche avait repris après le combat intermédiaire ; son
retrait avant le boss principal est vérifié dans la phase suivante. L'essai
sud sans protection mort en 1B7 est conservé séparément. Voir [le combat intermédiaire et le bateau](analysis/d7_progress_v0306.md).

Le **septième cristal et le retour extérieur sont validés**. Le boss principal
est vaincu à l'épée longue sans perte de PV pendant le combat. La protection
est retirée 28 images avant son début et reste désactivée pendant le retour.
Sept nouveaux checkpoints reproduisent toute la RAM et l'image finale ;
157 séquences prédites sont vérifiées. Le HUD final affiche les sept indicateurs
de cristal. Les deux derniers donjons, la fin et la fidélité globale restent
à valider. Voir [le septième cristal et la sortie](analysis/d7_campaign_v0306.md).

L’**entrée du huitième donjon et son combat intermédiaire sont validés**.
Le passeur prélève réellement 10 pièces ; une sortie/rentrée ordinaire permet
de résoudre un ennemi hors de portée sur l’approche. La protection est retirée
avant l’entrée en 1C9. L’ennemi de 50 PV est vaincu à l’épée longue, avec un seul
coup encaissé. Six checkpoints reproduisent toute la RAM et l’image finale ;
215 séquences de combat sont vérifiées. Le boss principal et le huitième
cristal sont validés dans la phase suivante. Voir [l’entrée et le combat intermédiaire du huitième
donjon](analysis/d8_progress_v0306.md).

La **clé des voleurs, le huitième cristal et la sortie sont validés**. Les
mécanismes et le passage avec Terre sont actionnés par les boutons du jeu.
Le boss principal est vaincu à l’épée longue sans coup encaissé. Le garde
est retiré31 images avant le combat et reste désactivé pendant le retour.
Onze nouveaux checkpoints reproduisent toute la RAM et l’image finale ;
425 séquences prédites sont vérifiées. Les 128 mots du HUD et les huit
indicateurs de cristal sont contrôlés. Le neuvième donjon, la fin et la fidélité
globale restent à valider. Voir [le huitième cristal et la sortie](analysis/d8_campaign_v0306.md).

La **v0305 corrige le blocage des escaliers entre pièces intérieures**.
Chez les marchands de C7, il est maintenant possible de monter de la pièce
1F vers la pièce 0F, de récupérer l’huile, de redescendre et de ressortir.
Une exclusion du défilement de toutes les pièces intérieures bloquait ce
passage ; le gestionnaire de bordure SMS ne comporte pas cette exclusion.

Validation de cette correction :

- Le blocage est reproduit sur v0304 et absent sur v0305. Les comparaisons
  SMS/MD en PAL et NTSC retrouvent le parcours 1F â†’ 0F â†’ 1F â†’ C7,
  l’huile, 17 valeurs sémantiques d’inventaire et les 160 cellules finales.
  Ces comparaisons utilisent une position intérieure de test explicite.
- Un parcours séparé depuis une nouvelle partie récupère l’huile et revient
  dehors sans modification de RAM ni import de sauvegarde. Les deux étapes
  sont rejouées : les 64 Kio de RAM et le PNG final sont identiques.
- Le profil de pile avant chaque instruction couvre les 4 677 images de ce
  parcours. La marge observée est de 666 octets ; cette mesure ne couvre pas
  encore la campagne entière sur v0305.

Détails et limites : [rapport de la v0305](analysis/indoor_stairs_v0305.md)
et [résultats vérifiables](analysis/indoor_stairs_v0305_report.json).

La suite sur v0305 confirme maintenant le **premier cristal et le retour
à l’extérieur en B9, à 28/32 PV**, avec l’huile conservée. La protection
d’approche est retirée 72 images avant le premier combat du boss et ne reprend
pas pendant le retour. Quatre relectures froides reproduisent toute la RAM
et le PNG final. Le profil de pile de cette branche, jusqu’à 17 482 images,
observe 466 octets de marge. Voir le [rapport du premier donjon](analysis/d1_oil_v0305.md).
Cette vérification ne valide pas encore les donjons suivants sur v0305.

La **hache, la première fée de vie, le deuxième cristal et sa sortie** sont
également vérifiés sur v0305. Le retour finit en D6 à 31/48 PV, avec une clé,
la hache équipée et l’huile conservée. Douze étapes disposent de relectures
RAM/PNG exactes. La protection d’approche se termine 57 images avant le
combat du deuxième boss et ne reprend pas au retour. Le profil de pile
jusqu’à 40 562 images observe 450 octets de marge. Voir le
[rapport du deuxième donjon](analysis/d2_campaign_v0305.md).

Le **troisième cristal et le retour en extérieur 62** sont maintenant
vérifiés sur v0305, à 56/56 PV, avec la corde obtenue dans son donjon.
Le mécanisme original de la salle 1E3 ouvre le passage avant le boss ; cette
salle est traversée avec ses ennemis encore présents. Quatre relectures
RAM/PNG sont exactes, et aucune protection ne reprend après le début du
combat. Le profil de pile jusqu’à 55 110 images observe 450 octets de marge.
Voir le [rapport du troisième donjon](analysis/d3_campaign_v0305.md).

Le **quatrième cristal et le retour en extérieur 10** sont également
vérifiés sur v0305, à 50/64 PV. Le parcours obtient normalement 50 cornes,
achète Terre, dégage deux passages, récupère le canoë et utilise le
téléporteur. Quatorze relectures RAM/PNG sont exactes ; la protection cesse
avant le boss et ne reprend pas au retour. Voir le
[rapport du quatrième donjon](analysis/d4_campaign_v0305.md).

Le défaut visuel du HUD documenté sur v0305 est corrigé dans la v0306.
Les rapports v0305 ci-dessus conservent leur périmètre historique.

## Campagne et travail restant

Sur la ROM courante **v0313**, neuf cristaux et le retour en extérieur sont
vérifiés depuis le démarrage. Le navire, la clé des voleurs et le ballon sont
acquis en jeu. Le premier emplacement de sauvegarde et Continuer sont vérifiés ;
le palais et la fin restent à valider.
La protection de test est déclarée et limitée aux approches, puis retirée
avant les combats de boss. Aucun objet, ressource ou progression n’est importé.

La **v0310** dispose d’un parcours froid de Nouveau jeu à la fin, ainsi que
d’une sauvegarde écrite en jeu et rechargée par Continuer. Ces preuves restent
propres à cette version ; elles ne valident pas la campagne entière de v313.
[Parcours jusqu’à la fin v310](analysis/cold_palace_final_v0310_report.json)
· [Sauvegarde et rechargement v310](analysis/game_written_save_v0310_report.json)

Les routines d’acteurs utilisent encore le générateur aléatoire SGDK.
Le raccordement au hasard SMS et à sa phase globale reste à faire.
La campagne complète et la sauvegarde sur la ROM courante, ainsi que la
fidélité globale vidéo/audio et les contrôles sur console réelle restent ouverts.

L’[historique du README jusqu’à v0304](analysis/readme_history_through_v0304.md)
conserve les étapes et leurs liens de preuve. Le [journal de recherche](analysis/world_next.md)
conserve les observations détaillées ; certaines entrées anciennes sont
supplantées par les rapports de versions plus récentes.

## ROMs et compilation

Chaque ROM différente conserve son numéro et son SHA-256 dans
[l’index des versions](versions/index.json). Les fichiers racine
`gaw-megadrive.bin` et `gaw-title-megadrive.bin` pointent sur les mêmes octets
que la version courante. Les anciennes ROMs numérotées sont conservées.

Depuis ce répertoire, avec SGDK, Java et Python disponibles :

```powershell
.\build.ps1
python tools/verify_git_roms.py
```

Le [module de démarrage SGDK](megadrive/src/gaw_sgdk_sys.c) conserve
l’[attribution MIT](megadrive/SGDK-license.txt). Seule la largeur des écritures
d’effacement initial de la RAM change :32 bits pour les mêmes64 Kio.

Les outils de validation mettent en cache les manifestes d'archives pendant
un processus et les rechargent si leur signature de fichier change. Les hashes
et la decompression restent controles a chaque lecture. Les trois auditsD9
produisent des rapports strictement identiques : voir [le controle du cache](analysis/evidence_manifest_cache_v0306_report.json).

Le candidat audio11 est maintenant intégré dans la **v0314**, avec un binaire
strictement identique. Ses rapports historiques conservent leur état de
candidat au moment des mesures ; le
[rapport d’intégration v314](analysis/intro_audio_integration_v0314_report.json)
relie leurs empreintes à la ROM publiée.

Les captures binaires de ces six parcours sont archivées sans perte, puis
supprimées après relecture et contrôle des empreintes : **81,7 Mio nets libérés**.
Les ROMs numérotées, les sources, symboles et captures PNG sont conservés.
[Manifeste du nettoyage](analysis/inventory_capture_cleanup_v0313_report.json)

Un nettoyage supplémentaire archive sans perte **4 737 fichiers de compilation
générés** devenus inactifs. Après relecture complète et contrôle des empreintes,
ils sont retirés :413 Mio nets d’artefacts, environ400 Mio de place disque
mesurée pendant les tests. Les314 ROMs, sources, symboles et captures de jeu
sont conservés ; les archives d’objets compilés restent locales.
[Rapport du nettoyage des compilations](analysis/inactive_build_cleanup_v0314_report.json)


La correction du chargement initial avait été intégrée à la v313. Son binaire
est identique au candidat vérifié jusqu’aux huit cristaux et à la sortie de D8.
Les détails PAL/NTSC et les limites figurent dans le
[rapport de livraison v313](analysis/startup_v0313_report.json).

Une option supprime le rendu vidéo des seules simulations secondaires qui
choisissent les commandes. Sur le petit benchmark D6, le débit augmente
d’environ 38 % ; le retour D5 conserve les sept prédictions RAM complètes,
l’image finale et son rejeu froid officiel. Ce gain ne mesure ni la vitesse
du jeu ni celle de l’ensemble des tests. Les vérifications RAM et le rejeu
restent obligatoires. [Accélération des prédictions](analysis/prediction_video_skip_v0312_report.json)

`build.ps1` accepte `-Sgdk` et `-Java` pour sélectionner leurs emplacements.
Le vérificateur compare les ROMs locales avec les objets du dernier commit
Git : il s’exécute après l’enregistrement de la livraison.

Code natif : [boucle et transitions](megadrive/src/main.c),
[acteurs](megadrive/src/actors.c). Les preuves volumineuses sont archivées
sans perte et vérifiées avant le nettoyage des fichiers générés.

D5 v314 : première clé, passage Terre, bottes et sortie de ravitaillement
vérifiés en RAM complète et image. Sortie à58/64 PV et64 PM ; quatre cristaux
conservés. Les quatre points sont relus dans un même noyau démarré à froid,
sans import d’état. Le ravitaillement est terminé :deux dons de30 cornes,clé achetée pour60,
soin gratuit et retour par le second passage Terre puis le mécanisme. Treize
points concordent en RAM complète et image dans un même rejeu froid continu.
Le point préparatoire est à64/64 PV et64 PM,avec une clé.
[Préparation complète de D5](analysis/d5_supplies_v0314_report.json)
Le cinquième boss et ses huit satellites sont vaincus sans protection. Deux
coups normaux coûtent20 PV,avant le cristal qui restaure72/72 PV et PM.
Le retour extérieur est vérifié sans nouvelle aide :63 fenêtres de prédiction
exactes pendant le boss,quatre pendant le retour. L’essai du pilote bloqué
sur une réentrée est conservé et exclu ; le pilote corrigé termine le parcours.
[Cinquième cristal et retour](analysis/d5_campaign_v0314_report.json)
Préparation D6 terminée :cinq acquisitions de clés,six étapes Terre,Cloche
de glace et son HUD physique vérifiés en17 points. Les sept consommations
de8 PM observées restent celles du jeu ; aucune ressource n’est ajoutée.
Point préparatoire à72/72 PV et32 PM,devant le boss.
[Clés, Terre et Cloche de glace](analysis/d6_progress_v0314_report.json)
[Preuve des bottes et de la sortie](analysis/d5_progress_v0314_report.json)

D6 :boss vaincu sans protection,307 prédictions exactes et un coup normal
de14 PV (72→58). Le cristal restaure80 PV,puis un autre coup de14 PV
au retour laisse66/80 PV à la sortie,avec72 PM. Les82 prédictions du retour,
les six marqueurs et les 128 mots physiques du HUD concordent.
[Sixième cristal et retour](analysis/d6_campaign_v0314_report.json)
La suite depuis D8 reste à valider.

Préparation D7 :don réel de10 cornes (55→65),clé achetée pour60 et soin
gratuit (66→80 PV),puis entrée,clés et deux mécanismes Terre. Neuf points
RAM/image exacts ; état préparatoire à80/80 PV,56 PM et deux clés.
Le gardien intermédiaire, le septième cristal et le retour sont désormais validés (voir ci-dessous).
[Préparation D7](analysis/d7_prep_v0314_report.json)

Le gardien78 de D7 est vaincu sans protection ni dégât reçu :87 prédictions
exactes,80 PV et56 PM conservés. L’approche ne reprend qu’après sa mort,
vers le bateau et le boss principal179. Quatre points RAM/image exacts.
[Gardien intermédiaire D7](analysis/d7_midboss_v0314_report.json)

D7 terminé :bateau obtenu normalement,boss67 vaincu sans protection ni
dégât,154 prédictions exactes. Septième cristal et retour extérieur à
88/88 PV et64 PM,une clé et11 cornes. Dix points relus en RAM complète
et image ; le passage Terre du retour consomme ses8 PM normalement.
[Septième cristal, bateau et retour](analysis/d7_campaign_v0314_report.json)

D8 :passage3C payé10 cornes (11→1),entrée et gardien7A vérifiés.
La protection est retirée avant le combat ; un coup normal de18 PV
(84→66) et243 prédictions exactes. Six points RAM/image exacts.
Le huitième cristal reste à valider.
[Entrée et gardien D8](analysis/d8_midboss_v0314_report.json)

D8 :clé du voleur obtenue par le jeu,mécanismes distants et passage Terre
franchis,approche du boss principal vérifiée en huit points RAM/image.
Le gardien vaincu ne réapparaît pas. Le boss6B et son cristal restent à valider.
[Clé du voleur et approche D8](analysis/d8_approach_v0314_report.json)
