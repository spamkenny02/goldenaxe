# Livraison du 6 novembre 2026 au soir

Échéance confirmée par l'utilisateur : vendredi 6 novembre 2026 au soir. L'objectif reste le portage
Mega Drive fidèle de Golden Axe Warrior ; la date ne transforme pas une preuve
partielle en validation complète.

État courant : **v314**,2 Mio,SHA c53381c4…,checksum241A.
Le correctif audio de l’intro est intégré : première musique,fondu et titre
alignés sur SMS en PAL/NTSC,12 959 états audio et40 images normalisées.
La production reproduit exactement le candidat testé. Premier cristal et
retour extérieur vérifiés par rejeu RAM/image exact. Menu de démarrage,six
transitions inventaire et compatibilité de la sauvegarde réelle v313 vérifiés
dans les deux régions. Voir intro_audio_integration_v0314_report.json.
La v314 a aussi écrit une vraie sauvegarde dans le premier emplacement :
rejeu exact des592 octets et du fichier SRAM,puis redémarrage,Continuer,
restauration des objets/premier cristal/HUD et déplacement vérifiés.
Voir game_written_save_v0314_report.json,d2_campaign_v0314_report.json
et oil_service_v0314_report.json. Voir aussi d3_campaign_v0314_report.json,
earth_learning_v0314_report.json et d4_progress_v0314_report.json.
Le quatrième cristal et le retour extérieur sont vérifiés :239 prédictions
exactes,sans protection ni dégât pendant le boss. Canoë observé sur99 images
de déplacement aquatique. Feu obtenu contre l’huile,deuxième épée reçue et
entrée D5 vérifiée à62/64 PV et72 PM. Voir d4_campaign_v0314_report.json
et fire_sword_v0314_report.json. D9 et les premiers mécanismes du palais sont terminés ; la suite du palais reste à vérifier sur ce binaire.
Accélération des contrôles :trois points d’un même rejeu froid continu sont
identiques aux rejeux séparés en RAM complète et image,avec62 % d’images
émulées en moins pour cette série. Aucun état de jeu importé ; le noyau reste
en pause entre deux enregistrements. Voir cold_replay_stream_v0314_report.json.

La v313 conserve la campagne complète depuis Nouveau Jeu : neuf cristaux,
ballon,Hache d’or,Death Adder sans protection,générique complet,retour intro.
Fin à l’image379 823 ; coup normal de32 PV pendant le dernier boss,
100→68 PV. Tous les points retenus ont un rejeu indépendant RAM/image exact.
Aucun état,objet,santé ou SRAM n’est importé ; les protections d’approche
sont retirées avant chaque boss. Voir cold_palace_final_v0313_report.json.
Le premier emplacement réellement écrit en jeu et Continuer restent vérifiés
sur v313. Le chargement de ce même enregistrement sur v314 est également
vérifié en PAL/NTSC,avec neuf marqueurs,HUD et déplacement.

Nettoyage :81,7 Mio nets libérés après archivage sans perte et relecture des
captures binaires de six parcours de menu. ROMs,sources,symboles et PNG préservés.
Voir inventory_capture_cleanup_v0313_report.json. Nettoyage supplémentaire :
4 737 sorties de compilation inactives archivées et relues avant suppression,
413 Mio nets d’artefacts,environ400 Mio de place disque mesurée. Les ROMs,
sources,symboles et captures sont préservés. Voir inactive_build_cleanup_v0314_report.json.

Entrée D9 v313 vérifiée : paiement réel 23→13 cornes, tombe ouverte par la
Cloche de glace, entrée à96 PV et72 PM avec huit cristaux. Trois étapes avec
rejeu froid RAM/image exact. Rapport d9_entry_v0313_report.json. Les mécanismes
Terre et le premier gardien sont vérifiés : cinq étapes avec rejeu RAM/image
exact. Deux coups normaux, 96→64 PV ; 72 PM conservés. 174 fenêtres de
prédiction sont exactes. Rapport d9_midboss_v0313_report.json. La suite
vers le second gardien et le ballon est vérifiée : huit étapes avec rejeu
RAM/image exact. Géant vaincu sans protection, coup normal de20 PV,244
prédictions exactes. Ballon reçu à88 PV et72 PM, huit cristaux conservés.
Rapport d9_balloon_v0313_report.json. Le combat principal et le neuvième cristal sont vérifiés : coup normal de20 PV,
240 prédictions exactes, puis guérison à104/104 PV. Retour extérieur sans aide
ni dégât, avec rejeu RAM/image exact. Le contrôleur ne prédit aucun combat
pendant ce retour par les salles vidées ; les ennemis extérieurs restent présents.

Historique des étapes précédentes (périmètres propres à chaque version) :

- ROM courante v312, 2 Mio, SHA0b9aecb4… : transition marchande corrigée,
  neuf images noires et huit étapes du portrait alignées SMS PAL/NTSC.
  43 cas couvrant les 23 villes passent ; le parcours NTSC jusqu'à la sortie
  de D2 conserve les champs de jeu comparés et l'image finale de la v311.
  Le panneau complet reste une image tardif en PAL.
- Campagne v312 : D2 rejoué depuis le démarrage, huile obtenue par le dialogue
  et les escaliers, puis corde, mécanisme, clé et troisième cristal. Retour
  extérieur vérifié à 56/56 PV, sans protection ni dégât pendant le boss D3.
  Chaque point promu a un rejeu indépendant RAM/image exact ; trois marqueurs
  et les 128 mots physiques du HUD sont vérifiés après le boss et la sortie.
- Préparation D4 sur v312 : don de 50 cornes et achat réel de Terre pour 50,
  niveau 1 et capacité de 48 PM. Quatre points avec rejeu RAM/image exact.
  Entrée D4, clés, canoë et deux passages Terre vérifiés par sept relectures
  RAM/image. Boss vaincu sans protection ni dégât, quatrième cristal et retour
  extérieur vérifiés à 62/64 PV. Combat et sortie relus exactement en RAM/image,
  quatre marqueurs et 128 mots physiques du HUD vérifiés. Déplacement réel en
  canoë observé pendant le rejeu ; préparation D5 en cours.
- Préparation D5 v312 terminée : huile échangée contre Feu, épée longue
  réellement reçue et entrée dans D5 à 62/64 PV, 72/72 PM. Sept étapes avec
  rejeu RAM/image exact ; cinquième cristal encore hors de cette preuve.
- D5 v312 : première clé, passage Terre, bottes et sortie de ravitaillement
  vérifiés par quatre relectures RAM/image. Sortie à 58/64 PV, 64 PM ; gain
  de vitesse actif. Préparation du cinquième boss en cours.
- Ravitaillement D5 v312 : dons de 30 + 30 cornes, achat d'une clé pour 60,
  soin gratuit, retour, second passage Terre et mécanisme vérifiés. Treize
  étapes depuis l'entrée avec rejeu RAM/image exact ; point préparatoire à
  64/64 PV et 56 PM avec une clé. Protection retirée en 173 à l'image 127330,
  avant l'entrée du boss 65 en 163.
- D5 v312 terminé : huit satellites et boss vaincus sans protection, coup
  normal de dix PV observé. Cinquième cristal et retour extérieur à 72/72 PV
  et PM ; cinq étapes finales relues exactement en RAM/image et cinq marqueurs
  du HUD vérifiés. Le pilote ciblant les satellites réduit la recherche de
  415 à 60 décisions ; la partie retenue continue sur cette branche.
  Préparation D6 terminée : cinq acquisitions de clés, passages Terre,
  Cloche de glace et accès du boss vérifiés par 17 rejeux RAM/image exacts.
  Point préparatoire à 72/72 PV et 64 PM, sans objet ni ressource injecté.
  Le retrait de l'aide est relu exactement à l'image 156803, avant la salle
  du sixième boss et en conservant les ennemis ordinaires de l'antichambre.
  Sixième boss et cristal vérifiés sans protection ni dégât reçu. Retour
  extérieur à 80/80 PV et 72 PM ; combat et sortie ont un rejeu froid RAM/image
  exact, avec six marqueurs et 128 mots physiques du HUD contrôlés.
  Le premier pilote de retour reste immobile et atteint sa limite d'images ;
  la variante à décisions de huit images réussit en 94 prédictions exactes,
  sans nouvelle écriture d'aide.
- D7 v312 préparé : achat réel d'une clé pour 60 cornes, entrée du donjon,
  deux acquisitions de clés et deux ouvertures Terre pour 16 PM. Sept étapes
  avec rejeu froid RAM/image exact ; six cristaux conservés, 64 PV, 56 PM et
  deux clés au point préparatoire.
- Intermédiaire D7 v312 vaincu sans protection. Coup normal de 12 PV observé,
  reprise de l'approche après victoire à 52 PV et 56 PM. Quatre points avec
  rejeu froid RAM/image exact : retrait, passage, combat et reprise.
  Le navire et le boss principal sont validés par la suite ci-dessous.
- D7 v312 terminé : navire, septième cristal et retour extérieur vérifiés à
  68/88 PV et 64 PM, avec une clé. Dix étapes depuis la reprise passent leur
  rejeu froid RAM/image exact ; HUD physique contrôlé après navire, cristal
  et sortie. Aucun soutien pendant les deux boss ou le retour ; les dégâts
  restent enregistrés. Parcours vers D8 lancé depuis cette sortie.
- Entrée et gardien D8 v312 vérifiés : passage réellement payé 10 cornes
  (12→2), puis victoire sur7A/50 PV sans protection ni dégât reçu, à56/88 PV.
  Les six étapes ont un rejeu froid RAM/image exact ;124 prédictions complètes
  sont vérifiées pendant le combat. Le huitième cristal reste à valider.
- Approche D8 v312 vérifiée : reprise après le gardien, mécanismes distants,
  Terre et clé des voleurs, jusqu'à l'antichambre du boss principal. Huit points
  ont leur rejeu froid RAM/image exact, à88/88 PV et72 PM au dernier point.
  L'aide est retirée avant196 ; le combat principal est en cours.
- Menu Nouveau jeu / Continuer v312 : musique active et audible en PAL/NTSC,
  événements des bruitages de curseur et validation alignés SMS. Aucune
  comparaison globale des formes d'onde n'est déduite de ce contrôle.
- Accélération des simulations de commandes : rendu secondaire supprimé,
  audio et format de sauvegarde conservés. Soixante cas D6 conservent la RAM
  et la phase processeur, avec un débit environ 38 % supérieur sur ce benchmark.
  Un retour D5 conserve ses sept prédictions RAM, son image finale et son rejeu
  froid officiel. Aucun changement de ROM ; ce n'est pas un gain global de 38 %
  sur tous les tests. Le combat D6 utilisait le calcul initial ; son retour
  retenu emploie cette option avec les mêmes contrôles.
- v311, 2 Mio, SHA0972465d… : correction d'une image du
  chargement vers le haut en NTSC. Premier donjon, hache, fontaine et clés du
  deuxième donjon vérifiés par rejeu exact. Deuxième cristal et retour extérieur
  vérifiés à 48/48 PV, sans protection ni dégât pendant le boss. La fin de
  campagne v310 ne vaut pas validation complète des versions suivantes.
- ROM de référence v310, 2 Mio, SHA32fe75a6… : récurrence SMS 04E1 raccordée.
  Parcours depuis Nouveau Jeu vérifié jusqu’à la victoire sur Death Adder,
  au générique complet et au retour à l’intro.
- v309 : campagne depuis Nouveau Jeu jusqu'à la fin, générique, retour intro,
  et sauvegarde réelle/Continuer vérifiés. C'est une référence historique,
  pas une preuve de fin v310.
- Sur v310, la reprise après une mort et le soin gratuit en 94 sont vérifiés.
  Le héros franchit le pont du cinquième cristal et entre dans D7, puis
  récupère deux clés et ouvre deux obstacles avec Terre.
- D7 terminé sur v310. Gardien et boss principal vaincus sans protection ni
  dégât reçu, bateau et septième cristal conservés en extérieur. Voir
  `d7_campaign_v0310_report.json`.
- D8. Gardien et boss principal vaincus sans invincibilité. Le huitième cristal
  est récupéré à l’image 272 980 et le rejeu du combat est exact en RAM et
  en image. Le retour en extérieur est vérifié à l’image 273 836 avec les
  huit cristaux.
- D9. Deux gardiens et boss principal vaincus sans invincibilité. Sortie
  vérifiée avec les neuf cristaux et le ballon. Le ballon restaure la carte
  et le HUD à la fermeture.
- Palais. La porte des neuf cristaux s’ouvre. Le géant et le gardien de la
  Hache d’or sont vaincus sans invincibilité. La hache est récupérée et
  équipée. Death Adder est vaincu sans invincibilité ni dégât reçu. Le rejeu
  exact de la campagne et de la fin atteint l’image 415 125.
- Sauvegarde v310. Un enregistrement écrit en jeu dans le premier emplacement
  restaure les objets, les neuf cristaux, le HUD et les déplacements après
  redémarrage via Continuer.

Ordre de travail pour la livraison :

Le correctif audio est intégré à la v314. Réutiliser ses preuves liées au
binaire exact ; la campagne complète v313 conserve son périmètre historique.
Poursuivre les contrôles de v314 depuis la préparation de D4 vérifiée, sans attribuer la fin de v313 au nouveau binaire.

1. Poursuivre la validation de la ROM courante et traiter les blocages ou régressions
   réellement rencontrés. Réutiliser les préfixes froids déjà vérifiés ; ne pas
   recommencer les étapes acquises. Les protections restent sur les approches,
   retirées avant chaque boss ; aucun état ou progression n'est importé.
2. Revenir aux contrôles ciblés seulement en cas de changement de code, d'échec
   ou d'incertitude concernant la ROM livrée. Réserver les analyses secondaires
   après ces contrôles critiques ; aucune amélioration de confort supplémentaire.
3. Publier sur main le code, le README et la ROM numérotée effectivement testée,
   avec ses empreintes et des limites explicites. Ne pas créer de numéro pour
   les seuls documents ou preuves. Ne pas annoncer une fin de campagne sur la
   version courante à partir des seules preuves d'une version précédente.

La fidélité R/IRQ globale et les vérifications audiovisuelles, optionnelles
et sur console réelle restent ouvertes. La phase
exacte du fournisseur R demeure provisoire. Ne pas garantir une version finale
sans réserve le 6 novembre tant que ces preuves manquent. La livraison doit
indiquer clairement ce qui a été vérifié et ce qui reste ouvert.

D5 v314 : clé, Terre, bottes et sortie de ravitaillement vérifiés ;58/64 PV,
64 PM,quatre cristaux conservés. Voir d5_progress_v0314_report.json.

Préparation D5 terminée :13 points RAM/image exacts,clé achetée pour60,
soin gratuit et mécanisme d’accès. Point préparatoire à64/64 PV et64 PM,
une clé. Voir d5_supplies_v0314_report.json. Combat D5 terminé.

Cinquième cristal et sortie49 vérifiés sur v314 :protection retirée en173
à128555,premier combat128686,63 prédictions exactes,deux coups normaux
de10 PV. Fin à132527,72/72 PV et72 PM. Quatre prédictions au retour.
L’essai de pilote bloqué à la réentrée reste archivé et exclu. Le correctif
concerne les commandes de test ; aucun changement du binaire.
Voir d5_campaign_v0314_report.json. Préparation D6 en cours.

Préparation D6 v314 terminée :17 étapes,cinq acquisitions de clés,six
étapes Terre et sept consommations réelles de8 PM. Cloche de glace acquise,
HUD physique128 mots exact. Point préparatoire en125 à159782,72/72 PV,
32 PM,aucune clé. Voir d6_progress_v0314_report.json. Boss et retour désormais validés (voir ci-dessous).

Sixième cristal et retour8B vérifiés à172104 sur v314 :307 prédictions
exactes pendant le boss,un coup normal de14 PV,puis guérison du cristal
à80 PV. Un second coup de14 PV au retour donne66/80 PV et72 PM à la sortie.
82 prédictions exactes au retour,six marqueurs et128 mots physiques du HUD.
Voir d6_campaign_v0314_report.json. Préparation D7 en cours.

D7 :neuf étapes préparatoires vérifiées jusqu’à191702. Don B5 réel de10,
clé94 achetée pour60,soin gratuit66→80,entrée,clés et deux actions Terre.
Point préparatoire à80/80 PV,56 PM,deux clés. Le trajet direct vers A5
n’avait pas nettoyé la carte avant son entrée cachée ; il est conservé
et exclu. Aucun succès A5 ni septième cristal n’est revendiqué.
Voir d7_prep_v0314_report.json. Gardien intermédiaire en cours.

Gardien78 de D7 vaincu sans protection ni dégât :87 prédictions exactes,
80 PV et56 PM. Quatre points jusqu’à192855 :retrait191703,contact,combat,
reprise après mort vers179. Voir d7_midboss_v0314_report.json. Bateau en cours.

D7 terminé jusqu’à212039 :bateau réel,boss67 sans protection ni dégât,
154 prédictions exactes,septième cristal. Retour1B à88/88 PV,64 PM,
une clé et11 cornes. Dix points RAM/image exacts. Voir d7_campaign_v0314_report.json.
D8 :trajet vers le passage payant3C en cours ; paiement attendu10 cornes.

D8 :paiement réel11→1,entrée,gardien7A50 PV vaincu sans protection.
Un coup normal de18 PV (84→66),243 prédictions exactes ; six points
RAM/image jusqu’à219770. Voir d8_midboss_v0314_report.json.
Approche principale et clé du voleur en cours.

Approche D8 et clé du voleur terminées :huit points froids RAM/image exacts,
mécanismes distants et solC8 franchis,gardien7A absent après sa mort.
Voir d8_approach_v0314_report.json. Combat principal6B en cours,sans protection.

Huitième cristal v314 : boss6B/80 PV sans protection ni dégât,423 prédictions
exactes ; retour extérieur à80/96 PV,72 PM,28 prédictions, RAM/image exactes.
Voir d8_campaign_v0314_report.json.

Nettoyage D1–D7 clos :18 064 captures intermédiaires archivées et relues,
536 fichiers des points finaux conservés et hachages inchangés. Gain net
442 077 835 octets, toutes les ROMs numérotées préservées.
Voir closed_capture_cleanup_v0314_report.json.

Branche D9 : mort normale puis Continuer et soin gratuit vérifiés sur trois
rejeux RAM/image exacts. Huit cristaux et tous les objets conservés ;96/96 PV,
24 PM,6 cornes. Aucun argent ni état injecté. Le trajet direct vers la Cloche
et D9 est lancé ; ce donjon n’est pas encore validé.
Voir d9_recovery_v0314_report.json.

Entrée D9 atteinte et vérifiée à l’image264263 : passage CB ouvert avec la
Cloche réelle,603 points de trajet et16 décisions de coupe normales,96 PV,
24 PM,6 cornes. Rejeu RAM/image exact. Gardiens et neuvième cristal ouverts.
Voir d9_entry_v0314_report.json.

Dix essais clos du contrôleur de collecte ont été archivés et relus :
7 328 captures intermédiaires supprimées,40 derniers fichiers binaires
conservés,187 273 763 octets libérés nets. Avec le nettoyage D1–D7,
le gain net de ces deux opérations dépasse600 Mio. Toutes les ROMs gardées.
Voir failed_d9_toll_cleanup_v0314_report.json.

Premier gardien D9/79 vaincu à279232 :221 prédictions exactes, un seul
dégât normal de20 PV,76/96 PV et72 PM à la fin. Cinq points supplémentaires
relus en RAM complète/image, protection retirée avant le combat.
Voir d9_midboss_v0314_report.json. Deuxième gardien/Ballon en cours.

Deuxième gardien D9/7B vaincu sans protection :292 prédictions exactes,
deux dégâts normaux de20 PV,56/96 PV à la fin. Ballon acquis normalement
à290406 ; fin de l’étape76 PV/72 PM. Huit rejeux RAM/image exacts.
Voir d9_balloon_v0314_report.json. Boss principal D9 encore ouvert.

Déplacement v314 comparé à la SMS :96 cas terrain/bottes/direction,
3 072 états identiques en NTSC/PAL. Cadences des deux systèmes identiques
pour chaque région ; contrôle préparé, sans revendication de charge combat.
Voir terrain_walk_v0314_game_report.json.

Les neuf cristaux v314 et le retour EB sont vérifiés à303753 : boss6C/90 PV
sans protection,291 prédictions exactes,un dégât normal20 PV,cristal puis
retour104/104 PV et72 PM avec67 prédictions. Quatre points RAM/image exacts.
Voir d9_campaign_v0314_report.json. Le palais final est lancé.

Ballon utilisé et retour carte/HUD768 mots vérifiés à304687. Porte réelle
aux neuf cristaux ouverte, entrée palais18D à307886,104 PV/72 PM,7 cornes.
Deux rejeux froids RAM/image exacts. Gardiens,Hache d’or et fin en cours.
Voir owned_overview_v0314_report.json et cold_palace_entry_v0314_report.json.

Premier gardien du palais15E/7B vaincu à322922 :165 prédictions exactes,
5 points RAM/image.2 PV perdus avant combat,20 en combat,puis soin normal
type11 de82 à104 PV. Aucune protection pendant le combat.
Voir cold_palace_giant_v0314_report.json et palace_giant_health_v0314_report.json.
Mécanismes intérieurs puis gardien de la Hache d’or en cours.

Mécanismes intérieurs v314 validés : portails, deux passages Terre et
mécanisme distant, cinq points froids RAM/image exacts, fin339379.
Voir cold_palace_inner_v0314_report.json. Gardien11E en combat sans protection.

Scrolling extérieur v314 : huit cas direction/région validés sur les tables
matérielles de sprites. Aucun ancien monstre/objet durant le scroll ;
persistance et reprise préservées. Des écarts de fin d’état subsistent ;
ce test ne conclut pas à une cadence ou à un décor identiques.
Voir scroll_objects_v0314_report.json.

Gardien11E/7C vaincu sans protection :405 prédictions exactes,trois coups
de24 PV,fin32 PV. Hache d’or acquise en11D à363747,fin364147 à56 PV/72 PM.
Six points RAM/image exacts. Dernière portion du palais lancée.
Voir cold_palace_guardian_v0314_report.json et palace_guardian_health_v0314_report.json.

Campagne v314 terminée :Death Adder sans protection,100 prédictions exactes,
trois pertes20+20+32 PV,fin20 PV. Victoire396040,générique397055→404478,
retour intro404508,fin404608. Onze derniers points RAM/image exacts.
Sauvegarde réelle à neuf cristaux en cours ; correctif marchand candidat03
validé PAL/NTSC,43 transactions,six menus,intro/audio conservés,non intégré
tant que les processus v314 restent actifs. Voir cold_palace_final_v0314_report.json
et merchant_panel_candidate03_v0314_report.json.

Sauvegarde réelle v314 à neuf cristaux vérifiée :592 octets et SRAM exacts,
Continuer restaure neuf marqueurs/HUD/objets et le déplacement à1343.
Le premier essai de service ne joue pas :collision du dossier du test D1,
reprise limitée au service/rechargement sous un nom neuf. Aucun bug ROM.
Voir game_written_save_v0314_nine_crystals_report.json.

ROM courante désormais v315,SHA004b593b…,checksumDFA4,2 Mio. Production
identique au candidat03. Panneau marchand aligné PAL/NTSC,43 transactions,
six retours d’inventaire,intro/audio conservés. Campagne complète rejouée
sur315 :401609 états sémantiques identiques à314,image finale exacte.
Sauvegarde réelle314 à neuf cristaux compatible315 PAL/NTSC.
Voir merchant_panel_v0315_report.json,campaign_v0315_report.json
et save_compatibility_v0315_report.json. Fidélité globale encore distincte.

Nettoyage des essais marchands clos :16607 fichiers générés retirés après
archive complète et relecture,gain net d’artefacts381213957 octets (~364 Mio).
Les315 ROMs numérotées restent présentes ;sources,symboles et PNG préservés.
Récupération des données supprimées testée depuis les archives,y compris
le binaire candidat identique à la production315.
