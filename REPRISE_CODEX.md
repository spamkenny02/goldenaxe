# Reprise du portage dans un autre compte Codex

État courant au 7 novembre 2026. Les notes historiques conservées
plus bas décrivent des versions antérieures. Lire d’abord cette section,
le README et les rapports cités.

## Suivi courant au 7 novembre 2026

La V318 a terminé les parcours NTSC et PAL jusqu’à la victoire, au générique
et au retour à l’intro. Le pipeline PAL est fermé et son audit final passe.
Ne pas reprendre ses anciens pilotes mentionnés dans l’historique ci-dessous.

L’aperçu recommandé pour poursuivre l’optimisation est c0047-d3ea2a83,
2 Mio, checksum DA29. Il reprend le programme de c0046 avec un complément
correct de fichier. Cinq cristaux et retours sont rejoués en NTSC avec
RAM entière/image finale identiques, ainsi que la corde, le don de 50
pièces et l’achat de Terre. Dernier point Terre : 81636, 48 PV, 12 pièces,
48 PM, Terre niveau 1. Dernier retour D4 : 107105, 62/64 PV, canoë acquis.
Le premier donjon est aussi rejoué en PAL.
La campagne complète de cet aperçu demeure ouverte.

Feu, le don de l’épée longue et l’entrée D5 sont terminés et rejoués sur
c0047 à 121528 : 62/64 PV, 72 PM, huile consommée, épée niveau 2 possédée,
hache toujours sélectionnée. Rapports : analysis/fire_sword_c0046_report.json
et analysis/c0047_d5_fire_sword_auto_report.json. Archive : c0046-fire-sword,
sept points d’un même rejeu froid ; c0047-d5-fire-sword-auto pour l’image complétée.

La préparation D5 est terminée : treize étapes, bottes, deux dons de 30,
clé achetée à 60, soin normal, Terre et mécanisme 162 vers 172. Rapport :
analysis/d5_supplies_c0046_report.json ; archive analysis/c0046-d5-supplies.
Point de préparation 144659, salle 172, 64 PV et une clé.

Le cinquième cristal et le retour sont également terminés : 150525, extérieur
49, 72/72 PV, 72 PM, cinq cristaux et épée longue sélectionnée. La protection
est retirée à 146597 ; premier combat à 146688, héros 64 PV/hurt0 et boss65
72 PV. Huit satellites observés, 63 prédictions de combat et 10 au retour,
sans mort ni nouvelle aide. Cinq points froids vérifiés. Rapports :
analysis/d5_campaign_c0046_report.json et analysis/c0047_d5_auto_report.json.
Archives : c0046-d5-campaign et c0047-d5-auto. Le rejeu c0047 passe aussi
sur toute la RAM et l’image finale. Tous les pilotes D5 sont terminés.

Le processus courant joue continue_d6_c0046.py dans
validation/c0046-campaign01/isolated/project. Cette branche continue sur
c0046 puis chaque jalon est rejoué sur c0047. Journaux et sources :
validation/c0046-d6-sources02 dans ce projet, preuves indépendantes partagées
dans son sous-dossier cold-stream. Le pilote D6 réutilise quinze propositions
d’actions historiques, toutes rejouées de nouveau sur le candidat. Adapter
summarize_d6_progress_v0317.py pour c0046 après les dix-sept étapes (sélection
hache, entrée et quinze recettes) : les chemins du rapport D5 sont préfixés
par validation/c0046-campaign01/isolated/project, à ramener au projet pour
les lectures internes. Ne pas lancer l’ancien audit V317 tel quel.
Les sources natives réelles c0046 sont liées en lecture seule dans
megadrive/src ; native_sources_setup.json enregistre leurs empreintes.
Ne pas modifier ces liens ni les outils partagés. prepare_d6.py documente
la préparation ; le seul changement par rapport aux sources V318 est main.c.
D4 est terminé : dix points froids
dans c0046-d4-cold-stream, sortie corrigée dans c0046-d4-exit-cold-stream03.
Les pilotes de sortie01 (énigme facultative) et sortie02 (mort) ont échoué ;
exit03 passe sans mort ni nouvelle aide. Vérifier le processus réel avant
reprise ; ne pas relancer les pilotes dans les sorties existantes.

Preuves actuelles : analysis/c0046_d4_report.json, analysis/c0047_d4_auto_report.json,
analysis/c0046_d3_report.json,
analysis/c0047_d3_auto_report.json, analysis/earth_learning_c0046_report.json,
analysis/c0047_d4_earth_auto_report.json. Archive du don et achat :
analysis/c0046-earth-learning, quatre points d’un même rejeu froid.

## Historique des étapes précédentes

La version de référence est V318, 2 Mio, checksum 7863, SHA-256
b9e1f0a0543f191e24ffd6d2740a0d717501e0fcd986f8b8953a37a1b3c416a4.
La ROM SMS du dossier input correspond exactement au fichier fourni par
l’utilisateur sur D:/Cartmod/GoldenAxeWarrior/chat. Une compilation propre
a reproduit le binaire publié et ses symboles. Le dépôt est sur main,
avec le remote https://github.com/spamkenny02/goldenaxe.git.

Le parcours NTSC V318 atteint la victoire, le générique et le retour à
l’intro par rejeu de la campagne V317. La campagne PAL V318 possède
désormais neuf cristaux et a rejoint le palais après utilisation du ballon.
Le premier géant du palais est vaincu en salle 15E à l’image 326281.
Le héros conserve 82/104 PV, 72 PM et ses neuf cristaux. La protection
d’approche est retirée à 323223. Le premier combat à 323299 conserve
un délai naturel après dégât de 18. Les 351 fenêtres de prédiction et
le rejeu RAM/image depuis le démarrage passent. Consulter le processus
et les fichiers actuels pour connaître les étapes jouées après ce point. Le pilote validation/pal318-palace01/run.py est suivi du pilote
validation/pal318-palace-inner01/run.py dans une même chaîne de commandes.
Ne pas relancer ces pilotes sur leurs répertoires existants.

Les points d’entrée pour reprendre le suivi sont les commandes exécutées
et les checkpoints, avec vérification de l’état réel des processus avant
toute nouvelle exécution.

Dernier jalon PAL audité : gardien 7C en 11E vaincu à 352326,
checkpoint à 352477 avec 76/104 PV, 72 PM et neuf cristaux. Les 387
fenêtres de prédiction et le rejeu RAM/image depuis Nouvelle partie
passent. Protection retirée à 346001 ; premier combat à 346117 avec
100 PV et hurt=0, gardien à ses 60 PV source. Le pilote poursuit vers
la vraie Golden Axe, puis Death Adder et la fin. Voir
analysis/pal_palace_guardian_v0318_report.json.
La vraie Golden Axe est ensuite obtenue en 11D, checkpoint 355012,
100/104 PV et 72 PM. Le rejeu indépendant RAM/image passe et l’inventaire
contient la valeur 2. Voir analysis/pal_palace_golden_axe_v0318_report.json.
Le parcours atteint ensuite 15C avant Death Adder : checkpoint 381582,
100/104 PV, 64 PM, Golden Axe et neuf cristaux. Les dix-neuf étapes
intérieures sont auditées avec rejeu RAM/image exact ; le HUD matériel
est vérifié à ce point. Voir analysis/pal_palace_pre_final_v0318_report.json.

- validation/pal318-palace01/commands.jsonl
- validation/pal318-palace01/cold-stream/checkpoints.json
- validation/pal318-palace-inner01/commands.jsonl
- validation/pal318-palace-inner01/cold-stream/checkpoints.json
- analysis/pal_d9_exit_v0318_report.json
- analysis/pal_palace_entry_v0318_report.json
- analysis/pal_palace_mechanisms_v0318_report.json

Le pilote audit.py de chaque répertoire de campagne vérifie les points
courants et archive les preuves. Les audits du géant, du gardien, de la
Golden Axe et de la fin doivent suivre leurs victoires réelles. La chaîne
de jeu ne les remplace pas. Les écritures de test sont limitées au compteur
de protection des approches. Tous les boss doivent être affrontés après
retrait de cette protection. Aucun objet, cristal, PV ou état de progression
ne doit être importé dans le parcours depuis Nouvelle partie.

Une sauvegarde écrite normalement par V318 PAL avec neuf cristaux a été
rejouée, comparée octet par octet puis rechargée par Continuer. Les
défilements des premières cartes et la disparition des anciens sprites
passent les contrôles ciblés des deux régions. Ces résultats figurent dans
le README et leurs archives.

Les aperçus c0042 et c0043 sont des essais numérotés avec limites documentées.
c0042 récupère une mise à jour PAL pendant une salve mais introduit un saut
NTSC à 7697. c0043 recale les 7424 étapes du générique PAL dans le test
contrôlé mais ses rejeux de campagne divergent avant la fin. Aucun de ces
aperçus ne remplace la V318. La fidélité globale des timings, du hasard,
de l’image et du son, les chemins optionnels et le matériel restent ouverts.

c0044 utilise l’atlas RAM des ennemis du donjon. Il récupère la mise à jour
PAL 80003 ; celle de 80001 manque toujours. La première divergence NTSC
à 44801 correspond à une mise à jour d’acteurs supplémentaire : un essai
SMS contrôlé en 1E2 retrouve ses 768 octets d’acteurs à la phase 73.
Cela ne valide pas une chronologie SMS naturelle complète.

c0045 est un aperçu numéroté de copie des huit lignes, avec 108 images
de sprites contrôlés identiques et le début NTSC comparé jusqu’à 7710.
Il ne récupère aucune mise à jour PAL supplémentaire par rapport à c0044.
La combinaison distincte atlas RAM + cache à sentinelle a aussi été testée,
sans mise à jour PAL supplémentaire ; elle n’est pas intégrée. Son archive
analysis/dungeon-atlas-sentinel-v0318 conserve les preuves et le binaire
compressé. Le nettoyage vérifié y libère 7144211 octets nets.
La suite de l’optimisation doit examiner la préparation précédant le
masquage, plutôt que répéter ces deux variantes déjà mesurées.

Le profil détaillé c0044 est désormais archivé dans
analysis/c0044-burst-stages : à 80000, préparer les motifs d’une pose
changée du héros coûte 241332 cycles maîtres, contre 230146 pour toute
la simulation. Le témoin est un processus neuf, RAM/image entière identique.

c0046 remplace les copies de trois octets de cette préparation par trois
écritures directes, sur la base c0044. La médiane des poses mesurées passe
de 123060 à 67942 cycles maîtres, soit -44,79 %, avec 561 états de pose
et de pixels identiques par région. Les 16 essais de marche face à SMS
passent, ainsi que 108 images de sprites physiques. Les mises à jour PAL
80001 et 80003 sont exécutées ; les anciennes trajectoires divergent dès
23709 en PAL et 3396 en NTSC, où une mise à jour supplémentaire est observée.
Le parcours complet de cet aperçu n’est pas validé.

Un nouveau parcours c0046 est lancé dans
validation/c0046-campaign01/isolated/project. Ses outils sont liés par
liens physiques en lecture ; ne pas les modifier dans cette copie.
ROM et symboles publics sont aussi liés. Les sorties de validation sont
séparées. Les pilotes run_d1.py et resume_d1_key.py, à la racine de ce
laboratoire, enregistrent les commandes. Le premier parcours laissait
la seconde clé en 193 et n’entrait pas chez le boss ; sa reprise retourne
la ramasser normalement avant de retirer la protection. Ne pas annoncer
le cristal avant victoire, acquisition et rejeu depuis Nouvelle partie.

Le Python actuellement invoqué par python est C:/Python315/python.exe.
SGDK est dans ../../work/sgdk depuis outputs/gaw-md. Le script
tools/build_private_candidate.ps1 compile les essais dans validation et
conserve la ROM de référence. Les programmes de test en cours utilisent
cette ROM et ses symboles. Préserver les fichiers qu’ils lisent.

## Historique conservé

Etat de cette note : 4 novembre 2026. Lire aussi README.md et les rapports plus recents eventuellement ajoutes depuis cette note. Le changement de compte ne termine pas l'objectif du portage.

## Priorite utilisateur : livraison vendredi6novembre au soir

Lire analysis/livraison_2026-11-06.md. User demande etatdeslieux et rappelle
DEADLINE REPORTEE par utilisateur au6novembre au soir (message du4novembre). Priorite aux blocages/regressions/validation
ROMlivree,finparcours310,paquetnumerote+README+main. Pasdegarantie100%sanspreuves.
Ne pas confondre campagnev309complete et courante310jusqueD6.
Pointcourant: md-auto-v0310-d6-exit01 fin190773 salle8B,HP2/80,MP72/72,
keys2,gold30,6cristaux,cloche1,Feu1,Terre1,bottes/canoe/corde1,epee2,hache1
selectionnee1. SOIN NORMAL PRIORITAIRE avant D7; aucun refill/inventaire/SRAM
importe. Historiquement94inaccessible au planificateur depuis8B; ne pas compter
ses propositions comme points joues. Voir d7_supplies_v0309.md,merchant2E.
17 etapes preparation et3boss/retour ont relectureRAM65536/PNG exacte.
Sources v0310-d6-sources: source_index initial/natif immuables, Earth_grab2,
earth_grab_revision.json et executed_recipes_r02.json; auditeur progress_r02.
Earth126-01 bloquait hero12 saisi par5B: pilote Earth n'envoyait pas directions.
Correction seulement du pilote; Earth126-02 observegrab165300 puisouvre165317,
source originale preservee, aucune modification ROM. Sept casts8PM sur6ouvertures.
Une reentree ordinaire137 pendanttorch117; sortie137ouverte contournee.
Gate125-02 fin175542 HP72 PM40 keys2,release175543 hurt0.
BOSS01(step32) frame_limit193543 boss60; BOSS03(step16) frame_limit185543 boss24.
Ne pas compter ces essais comme victoires. BOSS02(step8) gagne fin185904,
first175645 hero72/hurt0 vs64/60HP; hit185239 72->58 puiscristal80/80.
Retour sans nouvelleswrites fin190773 HP2/80 MP72,121predictions exactes,
combat1202exactes. HUD128+6marqueurs aux2points, imagesinspectees.
Rapports d6_progress_v0310 et d6_campaign_v0310 passent; auditeurs *_r02.py.
Sources boss v0310-d6-boss-sources; selected_boss_trial.json lieboss02/reportSHA.
Tous jobs de ce jalon terminaux:73010/70392/39812/76097=0;
12079=1 diagnosticboss01;33963=1 diagnosticgrab;8327=0 Earthcorrige.
Prochaine action: soin normal faisable depuis8B, puis D7 episode cible179,
bossintermediaire1B8/type78 doit etre combattu sans protection aussi.
References v309 = propositions seulement; aucun import d'ancien etat.
ROM toujours310; objectif complet ouvert:R/IRQ global,temporisation/fidelite,
contenus et suite310. Deadline6novembre au soir, aucune garantie100%sanspreuves.

## Point courant : Continuer et soin gratuit verifies

analysis/death_heal_v0310_report.json passe : trois etapes exactes RAM65536/PNG.
Mort naturelle9B190909,menu191001,resume95 en191130 a24PV/24PM,gold30->21.
Six cristaux et17items conserves,keys2. Route94 sans nouvelleswrites,
soin gratuit24->80PV,MP24 conserve,sortie94 fin192089 x136,y64.
Tracecourante natural-service-route/md-v0310-d7-healer94-service01.
Aucune nouvelle aide depuisD6exit; six episodes historiques et81941writes.
Sources v0310-d7-sources, revision continue_exposure_revision.json et healer_source_index.
Jobs death_heal_finish termines, rapport passe. PasdeROMnouvelle pourpreuves.
Branches exclues: gift7D+5EbloqueTerre2,pasachat;Continue01patrolframe_limit;
healer-route01 gameplayreussi maisepisodeaidevide invalide;route02 sansaide valide.
EntreeD7 verifiee depuis ce point: natural-dungeon-route/md-v0310-d7-healed-entry01,
fin197049 en1DB a68/80PV,24PM,21cornes,deux cles. Relecture26674 terminal0.
Le pilote lit desormais flag49 (SMS149, MD save+99) et applique les cellules
4A=0A/5A=6B du pont. Passage reel49->4A, trois coupes,742 waypoints,aucun retry.
Rapport d7_entry_v0310; source initiale preservee et revision dans v0310-d7-sources.
Episode7 cible1B8. Pipeline93876 terminal0. Key01 fin198110 salle1CB PV68 PM24 keys2.
Key03 fin204926 salle1B9 PV80 PM40 keys3. Terre36 fin205242 PM32, Terre2B fin205582
PM24. Quatre relectures exactes. Voir analysis/d7_prep_v0310_report.json.
Gardien1B8 vaincu. Release205583, entree205710, premier combat205768 (80PV,
hurt0, type78/30PV). Fin206928 avec80PV/24PM/3cles, aucune perte de PV,
112 predictions RAM completes, aucun write apres release. Replay victoire exact.
Reprise garde206929 apres victoire, cible179. Pipeline71575 termine par la
relecture de resume01. Audit tools/summarize_d7_midboss_v0310.py.
Pipeline48065 attend la fin de71575 puis exige le replay canonique de resume01
pour lancer healed_d7_finish.py (bateau, boss principal, retour D7).
Pipeline41475 attend 48065 puis exige sortie D7 canonique avec bateau avant
le passage3C/9F, paiement10, entree D8 et gardien1C9 sans protection.
Les commandes sont dans validation/v0310-d7-sources/healed_d7_prep_commands.jsonl.
Poll les memes handles ou verifie processus et journal, ne pas dupliquer.
resume_after_intermediate.py accepte le boss intermediaire cible directement
quand ses preuves d'entree et de combat concordent avec la nouvelle relecture.
Route sud1D6 fin212107 PV80 PM40 keys3. Levier1E6 (72,40) image213826,
retour1D6 fin214003. Bateau slot16 0->1, dialogue ferme en1D5 fin215155,
PV80 PM40 gold23 keys3, quatre pieges5E a0PV conserves. Relectures exactes.
Audit tools/summarize_d7_campaign_v0310.py --through-ship et rapport d7_ship_v0310.
Pipeline48065 poursuit nord1B8, Terre1A8, approche189. Toujours retirer la
protection avant le boss179/type67. Pipeline41475 attend la sortie D7.
D7 termine : nord1B8 fin218853, Terre1A8->198 fin219826, approche189 fin225253.
Retrait225254 hurt0, premier combat225393 PV80/type67 PV60. Boss et cristal
fin229346 PV88 PM72,209 predictions RAM exactes, aucun degat, aucune aide.
Terre retour1B7 fin230503 PM64; sortie1B fin230879 PV88 PM64 keys2 gold23,
bateau et7 cristaux, aucune nouvelle ecriture apres225254. Audit d7_campaign_v0310.
Prochain passage payant3C puis D8. Pipeline41475 attend le succes de48065.
D8 gardien1C9/type7A vaincu sans aide fin240758 avec22PV. Reprise garde240759.
Passages1EB fin245779 et1EC fin248768, Terre1E8->1AA fin258410. Cle des voleurs
slot15 0->1 en1A9 fin263693, PV62 PM72 keys2, sept cristaux. Six relectures exactes
et HUD controle. Pipeline30149 poursuit levier19A, boss196 sans aide, sortie29.
Pipeline36012 attend sortie D8 canonique avant passage1A et D9.
Approche D8 terminee en1A6 fin270144 PV66 PM72 keys2; levier19A fin265714.
Rapport d8_approach_v0310. Le pipeline30149 retire garde avant196 puis teste boss.
D8 boss196 et sortie29 verifies, fin273836 PV96 PM72, deux cles, huit cristaux.
Audit d8_campaign_v0310. Pipeline36012 a lance la route vers D9.
Prototype marchand prefere validation/v0310-merchant/merchant-candidate02 :
9 images noires et8 poses completes exactes NTSC/PAL; panneau exact NTSC,
1 image tard PAL. 43 cas /23 villes et premier marchand valides.
Campagne fixe: D1 sortie exacte sur candidat; derive observee entre retourD1
16450 et premiere cle hache19585, avant bossD2. Retenir v310 pour campagne.
Details dans merchant_candidate02_timing.json et candidate02-d2-localize.
Bossintermediaire1B8/type78 etprincipal179/type67 sansprotection obligatoire.

## Dernier jalon : huile tardive,corde et D3 v310 termines

analysis/oil_service_v0310_report.json et d3_campaign_v0310_report.json passent.
DepuisD2exit44790,nouvelleepisode3 cible1C3 via oil-route01 fin46346,
oil-service01 fin47077 :1F->0F->1F->C7,gift6482 item8=1/flagC7=2.
PV31/gold2/MP24 conserves,2cristaux. Aucunewritenouvelle dansservice.
natural_oil_stairs accepte --assisted-prefix via prefix_writes canonique,
FrameWrites reprenantseulementancienneswrites;manifeste transparent,rejoue.
Sourceopcode6482 confirmegiftgratuit. Deux relecturesfroidesexactes,HUD128exact.
D3 entry50064,rope54923,switch55410 (Haut120104,ennemisactifs),key56899,
approach58420,release58421,boss65056,exit66413 en62 46/56PV.
Huitrelectures RAM65536/PNGexactes. Huile+corde+3cristaux conserves.
Boss reel69/32PV,first58573 hero39/hurt0;hit64349 39->31,hurt47.
Dernierewrite58421,seulementanciennesaides depuisboss etretour.
182predictionsboss+7retour exactes,passtackdifferences;HUD128+3markers aux2points.
Planner32frames,horizon96,evasive;exit planifie TOUSles vraisrooms1C3/1D3/
1E3/1E2/1E7/1F7/1F8. Boss1496terminal0,exit7044terminal0;aucunjobactif.
Snapshots v0310-oil-service-sources et v0310-d3-campaign-sources. Imagesinspectees.
Source tabletype65 trouveUNIQUEMENTen163 (pasbossD2niD3). Source1C3=69.
Prochainepriorite:ecartsnatifsR/IRQ,etprogressionfuturevers163pourvraicombat65.
ROMinchangee,pasv311pourdocs/pilote. Fullcampaignv309historique seulement.

## Dernier jalon : hache,fee et D2 v310 termines

analysis/d2_approach_v0310_report.json et d2_campaign_v0310_report.json passes.
Suite memeNewGame D1 canonique :reentry02 fin16450,axe-key01 19585,
axe01 21176,axe-exit01 22295,fee-route01 23350,fee-service01 23872,
d2-entry01 26033. Sept replaysexacts RAM65536/PNG. Hacheacquise/equipee,
3coupesfee+1versD2,coeur+soin reel32->40,flagC9=2. Pasd'importressources.
Nouvelleepisodeaideapres16254 cible144 ;premiereepisodeD1 reste fermee.
D2 key02 27110 en160, key03 28562 en152,key04 32362 en131 ;40PV.
Boss01 fin42327 secondcristal48/48 ;exit01 fin44790 D6 31/48PV,1cle.
Cinq replaysexacts. Dernierewrite33960,boss34017 hero40/hurt0.
TYPE REEL D2=63/30PV (PAS65satellites). Coup41640 40->24,hurt47.
Commentaireintermediaire "sansdegat" etait premature,rectifieavantbilan.
479predictionsboss+15retour exactes. HUD128+2marqueurs verifies aux2endpoints.
Aucuneaidependantboss/retour,aucunewritenouvelleauretour. 2cristauxsource.
Bosscoarsestep16,horizon96,width3,evasion11. EnterUP/targetsatellites flags
65 sans effet sur type63. Pipeline39888 terminal0,48602 terminal0,51544terminal0.
D2key01 diagnostic exclu :mauvaisecible151 sanscle,controller_stalled sansmort.
Retouraxe01 ferme ancienepisode,brancheconservee ;02 ouvre2eepuisemploiee.
Sources figes v0310-d2-approach-sources et v0310-d2-campaign-sources.
Aucunjobactif,ROMinchangee. Prochainepriorite:ecartsnatifsR/IRQ globaux,
etvrai type65 lorsqu'atteint dans progression D3/suivante (verifiertables,
nepasidentifierbossd'apresnumeroD). Toute aide retiree AVANTchaqueboss.
Pasdefaussev311 pourdocs/preuves. Fullcampaignv309historique,310jusqueD2ici.

## Dernier jalon : campagne froide v310 D1 + retour

analysis/d1_campaign_v0310_report.json passe. Quatre relecturesfroides exactes :
route md-v0310-d1-entry01 fin4237(14PV),cle md-auto-v0310-d1-key01 fin4989(14PV),
gem03 fin14551 cristal32/32PV,exit01 fin16254 B9 28/32PV. PrefixeNewGame sansSRAM.
Aideapproche apres4989 seulement,dernierewrite13546,boss13617 10PV/hurt0,
degat13709 10->6. 32predictionscombat+16retour RAMexactes. AucunerefilleHP,
ressources/progression/etat primaire injectes. Retour aucuneaide. HUD128+1marker
exact apresgem etretour. Imagesfinalesinspectees. Sources validation/v0310-d1-campaign-sources.
Handles62664 terminal0 gem01 echouepointes14->10->6->2->0 frames13481..84
carpilotzeroeffacecooldown;57272 terminal0 gem02 mortbossHP4restants;
77542 terminal0 gem03 reussi;cautious.9081 terminal0 exitreussi. Aucunjobactif.
assisted_boss_route preserve-floor-hurt devient BooleanOptionalAction defaultTrue;
--no-preserve-floor-hurt pourreproduireanciensdiagnostics. Parseurreel3modesverifie.
Driversexecutescopiesdanschaquetrace,pasconfondreavecfichiercourantmodifie.
ROMpublique inchangee. Prochaineetapeutile v310 :hache/queteD2 depuisexitcanonique,
etecartsnatifsR/IRQ. Fullcampaignv309historique uniquement. Invincibiliteautorisee
approche,retireeavantboss. Argentinf/potionsautorises maisnonutilisesici.
LimiteIYfullpool :4965preserveancienIYsurfailure;A82Decritquandmeme;2346peut
changerIYseloncontacts,ouretourprecoceleconserve. Nefixerspeculativementpas.

## Dernier controle : dispatch boss65 + RNG v310

Pipeline19733 terminal0. tools/validate_second_boss_rng_v0310.py :732cas
NTSC et732PAL passent,tous768octetsacteurs/graineterminale/nombrelectures.
Fragment e0==65 extrait EXACT actors.c (hors contact/tail) compile avec
vrai runtime.inc etpureboss. SMS anciengenerateur prive controle3LDAR+04E1,
resteinstructionsoriginales. Toutes256sortiesgate,pauses,retourstimers,
20segments,directions,pool couverts. A921=04E1,A935=R confirme,nepasmasquergate.
Aucunbugnatif trouve,ROMinchangee. Sources figes validation/v0310-second-boss-rng-sources.
Premieressai01 stopavantcompilation:parentfixture/validation absent;02corrige.
Lire analysis/second_boss_rng_v0310.md/report. Limites :pascomplettick,
pasnaturalfight/naturalRphase/pixels/audio/hardware. Prochainepriorite reste
lefluxglobalR/IRQ et autres routines dont appels04E1 charges/butin ont change.

## Dernier controle : mini-jeu v310 compare SMS/MD

Pipeline43586 termine0. Douze cas (6scenarios x2regions),24traces6600images.
analysis/minigame_rng_v0310_report.json et _audit_report.json passent :
cartes ordinaires/chance/inversion,paiement/reward/replay,poor/entry-no,
inventaireaprespremiertirage. 28samples game_rng_seed=733C prouventadaptateur.
Pilote derivehistorique mais adapte XORseed,game_rng_seed reset0 etrandbase
controles explicitement. Source SMSavec override04E1 etroutine relocalisee.
FrameWrites garde le reglagedynamiqueworld_clock_shift (ancien sortedcopy
ignorait lesappendsposterieurs). Les deux images MDreward/retour inspectees.
Snapshots validation/v0310-minigame-rng-sources. ROMinchangee,aucunnumeroajoute.
Ne pas appeler cette preuve une sequencealeatoire naturelle ou untrajetfroid.
La priorite reste phaseglobale R/IRQ etvalidation des routinesmodifiees.

## Priorite actuelle : v310 compilee, recurrence SMS raccordee

ROM v0310-32fe75a6,2MiB,AFC5. Voir analysis/rng_integration_v0310.md/report.
67 anciens appels SGDK (3main+63actors+1minigame),pas66 au total.
source_rng_runtime gere la graine froide0,lecturesR7bit,resultat04E1 8bit.
Sept expressions semees couvrent huit sites SMS actifs (historique commun
aux deux PCs). CALL0503 utilitaire04FE separe. Boss65 gateA921=04E1,
pauseA935=R ;ne surtout pas limiter le gate a7bits. Entrees fixtures intactes.
Le fournisseur R reste SGDK-low7 PROVISOIRE ;phase globale non integree.
Runtime PC65536 +68000 NTSC65536/PAL65536 passes. Gameplay froid3140
parregion,18endpoints exacts RAM65536/PNG,semence executee,mouvement,sanswrites.
Processus GX distincts pour relecture froide :meme processus conservait
28octets de pile (essai01 conserve,non preuve exacte).
Vraie SRAM v309 Save04 chargee normalement sur310 :compat02 ready1321,
mouvement1343,fin1443 ;stats,17objets,9gemmes,HUD128+9,arbreFA5D=4 exacts.
Une importation SRAM voulue,zeroRAMwrites/actorclear. Compat01 controles
passes mais exportrapport plante sur variable Python masquee ;02 corrige.
Snapshots validation/v0310-rng-before et v0310-rng-sources. Aucune tache active.
La campagne complete appartient toujours a309 ;pas de claim campagne310.
Prochaine action :poursuivre la fidelite R/IRQ globale depuis les modeles
source_clock/source_rng_timed existants,puis validations natives ciblees
des boss/butin/mini-jeu modifies. Pas de nouvelle ROM sans byteschanges.
Argent infini autorise pour achats reels de potions dans tests seulement,
non utilise ici. Aucune aide ajoutee a la ROM publique.

## Etat precedent v309 (historique)

## Priorite actuelle : fin et vraie sauvegarde/Continuer verifies,code fidelite

Campagne Nouveau Jeu->FIN :cold_palace_final_v0309_report.json passe,
401556 apres retourintro401456. Save reelle :game_written_save_v0309_report.json
et game_written_save_audit_v0309_report.json passes. AUCUN changement ROM.
Parent route02 canonique302751 viaFA,arbre83/5D coupe normalement ;maison6F.
Save04 ecrit302961,UI fermee303022,checkpoint303172 HP82 MP64 gold32 keys2.
Payload592 exact ;SRAM export3224octets,quatre FF logiques finaux omis,restes
FF controles. Relecture independante v0309-04b exacte RAM65536+PNG+SRAM.
Vrai Continuer dans nouveau coeur :SRAM ecrite par le jeu (UNE importation
legitime,non fixture),aucune ecriture RAM ni suppression d'acteurs. Ready1321,
mouvement1343,fin1443 roomFA HP82 MP64.17objets/neuf cristaux restores,
HUD128mots/neuf marqueurs exacts ;arbreFA:5D restaure4 avec son flag.
Snapshots sources04 et04b. Images save/reload inspectees. Pipeline2503 terminal0.

Essais exclus :route01 sans coupe ;save02/03 rouvraient la fenetre a cause
DU PILOTE (UP pendant restaurationhero0). Save04 corrige en attendant neutre.
Pipeline49364 terminal1 seulement car validateur exigeait circulairement
la preuve a produire ;04b valide d'abord le parent canonique puis cree sa
preuve. Les gardes d'approche copies sont anciens,aucun nouveau apres D9.
Ne pas transformer le reload SRAM reel en preuve de campagne froide.

Prochaine action utile :traiter les ecarts NATIFS encore identifies,notamment
les66appels SGDK random (3main,63actors),source_rng/source_rng_timed exacts
mais non raccordes a la production. Lire native_remaining_v0309.md et son
inventaire lie aux SHA main5488e979... et actorsd3a07e62... . Distinguer les
sites04E1 de LD A,R avant toute substitution ;pas de faux R au compteur MD
ni de remplacement aveugle uniforme. L'objectif reste le portage fidele,
pas seulement un jeu terminable. La phase globale SMS,les autres saves,
les contenus optionnels et les essais materiels restent a examiner.
Ne pas relancer toute la campagne sur la meme ROM sans nouveau probleme.
Pas de v310 avant changement reel du binaire. Aucune tache emulation active.

## Jalon precedent : campagne froide v309 terminee

Audit analysis/cold_palace_final_v0309_report.json passe. Onze endpoints
canoniques RAM65536+PNG ;dernier ending01 401556,jeu0/intro suivante.
Release386942 en15C a104PV ;perte386950104->100 avant boss. Combat387036
hero100/hurt0 vs6D90PV ;victoire392966 a100PV,180 predictions fullRAM.
Aucune ecriture apres release,aucun degat pendant combat. Neuf cristaux
393310,credits394003..401426,retourintro401456. Pipeline88543 terminal0.
BUT COMPLET TOUJOURS OUVERT :RNG SGDK/phase SMS,saves,optionnels,materiel.

Pipeline76613 terminal1 :route01 arretee devant arbre83 FA:5D,pas de save ecrite.
Retry93021 termine (voir priorite actuelle) :coupe normale
avec hache1 (--axe-terrain,--required-chop0xfa:0x5d) avant porte.
Branche SEPAREE depuis le vrai d9-exit01 (302306 EB,neuf cristaux,ballon),
route statique EB/FB/FA39waypoints vers porteFA216,96 maison6F,saveNPC136,72.
GameWrittenSavePlan :validation/game_written_save_plan_v0309_02.json.
Helpers prepares tools/natural_save_service.py et validate_game_written_save.py,
non encore valides :transaction normale Oui/slot0,export SRAM reel,comparaison
592octets serializees,relecture froide RAM+PNG+SRAM,puis NOUVEAU core avec
cette SRAM ecrite par le jeu et Continuer normal,aucune suppression d'acteurs.
Le reload importe necessairement la SRAM reelle et NE DOIT PAS etre appele
campagne froide Nouveau Jeu. Ne pas confondre avec l'ancienne fixture palais.
D9exit a save_last_slot0 lu dans son vrai RAM canonique. Sources v0309-game-written-save02-sources.
Attendre le resultat du pipeline puis auditer,inspecter et publier ;ne pas
relancer sur simple timeout. Pas de v310 sans changement effectif de ROM.

## Jalon precedent : gardien froid et vraie Hache d'or verifies

Audit analysis/cold_palace_guardian_v0309_report.json passe. Six endpoints
canoniques RAM65536+PNG :switch12c347516,pre-guardian354193,release354194,
guardian365263,resume-final365264,goldenaxe367133. Premier combat354248
hero104/hurt0,boss7C60PV ;339 predictions fullRAM,aucun degat ni ecriture
apres release pendant le combat. Hache1->2 a366733,dialogue fini367033.
Dernier trace natural-dungeon-combat/md-auto-v0309-cold-palace-goldenaxe01,
room11D HP104 MP72 gold35 keys2,axe2 selectionnee. Pipeline38472 terminal.
Pipeline88543 termine :validation/run_cold_palace_final01.py (voir priorite actuelle).
Terre13E369442 (16A HP100 MP64) et levier17C376548 (HP104 MP72)
ont chacun leur relecture canonique RAM65536+PNG passee.
Audit tools/summarize_cold_palace_final_v0309.py passe :boss,credits et retour intro/titre verifies.
Proposition controlee source-bound dans cold_palace_final_route_proposal_v0309.json
(UNEXECUTED pour les parties non encore jouees). Etapes :13E Terre3A->16A,
levier17C,portal13C via17B/18B/18A/17A/17B,levier14B,portal15A via13B/13A/
14A/14B,Terre15B48->16B,levier16C,prefinal15C,release avant14C,6D puis fin.
Le script refuse de partir sans audit guardian passe ;aucun prefix SRAM
controle n'est utilise. Source snapshots final01-sources. Hache2 normale,
protection a retirer avant Death Adder,aucune ecriture apres release.
L'objectif complet du portage reste ouvert,notamment RNG/phase,sauvegardes,
contenus optionnels et essais materiels. Pas de v310 sans changement ROM.

## Jalon precedent : mecanismes interieurs froids verifies

Audit analysis/cold_palace_inner_v0309_report.json passe :resume327639,
portal14e03 336921,Terre14E337338,Terre11A342640,levier129344707.
Cinq relectures canoniques RAM65536+PNG,HUD128/neuf marqueurs exacts.
Dernier trace natural-dungeon-combat/md-auto-v0309-cold-palace-switch12901,
room12A HP104 MP64 gold33 keys2. Pipeline93373 terminal success.
Validation/run_cold_palace_guardian01.py lance,pipeline38472 termine :
contact12C via12A/11C (--mechanism-during-combat),puis12C/11C/11B/12B/
12C/12D/12E (--rush-rooms0x12c :salle separee,non declaree nettoyee).
Release avant11E,7C60PV sans protection,budget20000 step32,puis reprise du
garde APRES victoire canonique et acquisition reelle axe1->2 en11D.
Audit tools/summarize_cold_palace_guardian_v0309.py passe.
Sources mesurees inner01-sources,guardian01-sources. Aucun argent de test.
Toujours separer cette campagne froide des anciennes preuves SRAM controlees.

## Priorite du 3 novembre : premier geant du palais froid valide

Audit analysis/cold_palace_giant_v0309_report.json passe. Cinq checkpoints
canoniques : panel16d01, switch16d01, pre-giant02, giant-release02, giant02.
Dernier trace natural-dungeon-combat/md-auto-v0309-cold-palace-giant02,
327638 room15E HP86/104 MP72 gold32 keys2. Release321494 avant15E ;
combat321571 hero102/hurt18 naturel,7B60PV ;185 predictions fullRAM exactes.
Degats16E321506104->102 puis15E327380102->82 et32742882->62 ;
coeur32749662->86. Aucune nouvelle ecriture apres release,aucun import.
Le pilote patrouille pour spawn56/59/5A avec --wake-sentinels ;ROM inchangee.
Pipeline29182 terminal success. Premier pre-giant01 echoue exclu.
Suite reprise validation/run_cold_palace_inner03.py,pipeline93373 termine (voir priorite actuelle) :
resume327639 canonique (episode15 pending14C),15E->15D->16D->16C->14D->14E,
Terre14E58->119,Terre11A35->12A,contact129->12A. Garder14D dans avoid-portal,
mais PAS16C ; --defer-puzzles-rooms0x16c a ce passage.
Pipeline74139 : portal14e01 echoue (sortie16E->16D inexistante).
Pipeline88711 : portal14e02 arrete volontairement (oubli deferral16C).
Ces branches ne sont pas des preuves reussies. Portal14e03 reussit a336921,
room14E HP94 MP72 keys2 ;16slots vides,une reentree ordinaire16C.
Relecture canonique65536RAM+PNG passee,image inspectee ;Terre14E en cours.
Audit tools/summarize_cold_palace_inner_v0309.py prepare mais PAS encore
execute : attendre les deux Terre et le contact129 avant de publier le bilan. Puis11E, vraie
hache1->2 en11D et final14C. Aucune preuve SRAM controlee ne peut remplacer
cette partie froide. L'objectif complet reste ouvert,notamment RNG/phase.

## Etat courant : NEUF cristaux v309 verifies depuis Nouveau Jeu,sortieD9
302306 exterieurEB HP102/104 MP64 gold32 keys2. Ballon,navire,cle des voleurs acquis.
Ravitaillement :dons27->57->87 en7D/AC,chopAC1C,cle60 chez2E laisse27,
entree1DB187840 HP50,premierecle1CB188960 HP58. Le detour vers94 n a pas
ete trouve par le planificateur (base et cartecourante) :aucune trace jeu
n est creee pour ces propositions. Le marchand2E remplace ce detour,sans soin.
8 endpoints canoniques,audit d7_supplies_v0309_report.json passe.

Intermediaire78/30HP :cle03 et deux Terre1B9:36/2B verifies,release198523,
premier combat198708 hero66/hurt0,degat19989866->54,victoire200066 HP54.
136 predictions fullRAM,6 endpoints canoniques,audit d7_midboss_v0309 passe.
Aucune ecriture apres release pendant ce combat. Reprise du garde200067
uniquement apres victoire canonique ;episode ferme retargete vers1B8,puis
nouvel episode8 pendingmain179. Source resume conserve PV/objets/ressources.
Sud205966 HP80,remote1E6 au72,40 a207552,bateau208659 HP80 MP72 keys2 gold32.
4pieges5E0HP et44/10HPslot4 conserves,salle non declaree nettoyee. HUD128mots/
6marqueurs apres bateau exact ;4 endpoints canoniques,audit ship passe.
Retour nord210300,Terre1A8:34->198211386 MP64,approche189215847 HP80,key1.
3 endpoints canoniques,audit navigation passe. Sources figees dans
validation/v0309-d7-sources,midboss-sources,ship-sources,navigation-sources.

Pipeline72068 termine : release215848, premier boss67/60HP216012 hero80/hurt0,
victoire et cristal220976 hero88/88,272 predictions fullRAM exactes,relecture
canonique RAM65536+PNG passee. Aucun degat pendant combat,aucune ecriture
apres release. Le retour-earth01 echoue controller_stalled apres destruction
effective de57 a222007 : la recette attendait a tort un flag de passage et
a recaste jusqu a epuisement PM. Branche exclue du parcours valide.
Pipeline82262 terminal success. Terre action-only cellule57 detruite222007,
8PM,re-equipe hache,checkpoint222203 ;sortie222579 exterieur1B HP76/88 MP64.
Retour sans aide,un degat normal221546 en198 88->76. Les4 endpoints finaux
ont leurs relectures RAM65536/PNG exactes. Audit d7_campaign_v0309 passe,
HUD128mots/7marqueurs apres cristal et sortie ;25 checkpointsD7 au total.
Pipeline39725 terminal success :3 checkpoints D8 verifies,route3C->9F224027
HP64/88 gold38,paiement10->1A224409 gold28,entree1EA224999 HP64 MP64 key1.
Audit d8_entry_v0309 passe,3 relectures RAM65536/PNG exactes.
Premier script entry01 terminal exit1 avant capture (budget16000 absolu
inferieur au prefix222579),aucune trace jeu ;entry02 corrige budget238579.
Sources D8 figees dans validation/v0309-d8-entry-sources.
Pipeline93653 terminal exit1 :ready01 bloque en1CA devant2sentinelles58
endormies HP30 flags40,option wake-sentinels omise. Branche exclue.
Pipeline47886 terminal success :ready02 en1CA229029 HP64 gold33 MP64 key1,
2 retours ordinaires,sentinelles reveillees,release229030 ;premier7A229267
hero64/hurt0 vs50HP. Victoire231568 HP28 ;degats23121464->46 puis23134846->28,
2x18 source. 267 predictions fullRAM et3 relectures RAM65536/PNG exactes,
audit d8_midboss_v0309 passe. Aucune ecriture apres release pendant combat.
Pipeline17957 terminal success :resume231569,postmini233542 HP52,
switch1EB234368,switch1EC237269 HP84,Terre1E8->1AA242150 MP56,
cle15 en1A9250470 HP88,switch19A253098 gold40,approche1A6256794 HP88 MP64.
8 relectures exactes ;audit d8_thief_v0309 passe. 7A ne reapparait pas vivant.
Watcher18661 terminal exit1 uniquement a l audit final (hash copie d7->d8
avait altere2 caracteres hexadecimaux) ;quete et pipeline main termines.
Empreinte corrigee,audit d8_campaign_v0309 passe sans relance du jeu.
Release256795 avant196,combat256980 hero88/hurt0 vs6B80HP,victoire260756
HP96/96 MP72,sans degat. 396 predictions fullRAM,sortie9 predictions.
Retour sans aide,coup261240 en1A7 HP96->94 MP72->64,exterieur29261634.
3 relectures RAM65536/PNG exactes,HUD128mots/8marqueurs deux fois ;17pointsD8.
Sources d8-thief-sources et d8-main-sources ;nativev309 inchange.
Pipeline74658 terminal success ;audit d9_entry_v0309 passe,3 relectures
RAM65536/PNG exactes. Coast1A->9F262214 HP94 gold40,paiement10 ->3C262569
gold30,clocheCB ouvre265080 cellule86 2F->39 et flag1,normale sans ecriture
terrain/ressource,entree1FC266242 HP94/96 MP64 key1 gold30,hache reequipee.
Sources validation/v0309-d9-entry-sources. Aucun9e cristal encore valide.
Watcher5834 terminal success ;audit d9_midboss_v0309 passe,5 relectures
RAM65536/PNG exactes. Terre/contact272518 HP94 MP64 ;Terre1CE272862 MP56 ;
ready276463 HP94 MP72 gold32 keys2 (ramassages naturels),release276464.
Premier79/60HP276636 hero94/hurt0 ;coup27802394->78,victoire278275 HP78,
MP72 gold32 keys2. 184 predictions fullRAM. Aucune ecriture apres release
pendant combat. Source validation/v0309-d9-first-mini-sources,ROM inchangee.
Job29490 terminal success ;audit d9_balloon_v0309 PASSE8 endpoints canoniques.
Reprise278276,contact1AD282557 HP96,19E283730,pieges19D283935 au24,88 HP96
4acteurs62HP0 conserves,salle NON nettoyee ;release283936 avant19C.
Premier7B60HP283988 hero96/hurt0,victoire287675 HP16,4coups20 a284303/
284513/284561/285205 ;440 predictions fullRAM,no later writes during fight.
Reprise apres victoire287676,ramassage28777116->40,ballon11 reel19B289111
HP36/96 MP72 gold32 keys2 ;coup normal19B28910240->36,fenetre fermee,hache1.
8 relectures RAM65536/PNG exactes,HUD128mots/8marqueurs finaux verifies.
Deux apercus d audit avant completion manquaient seulement des fichiers futurs ;
rapport consolide maintenant passe. Ne relancer aucune etape terminee.
Sources v0309-d9-balloon-sources ;16 pointsD9 couverts,8cristaux. Episodes13.
Watcher8858 terminal success ;audit d9_campaign_v0309 PASSE4 endpoints finaux.
Approche295159 en1BC HP36/96 MP72 gold32 keys2,BC/BD ouverts,canonique.
Release295160 avant1AC,premier6C90HP295276 hero36/hurt0,coup29738336->16,
victoire/recompense300396 HP104/104 MP72. 270 predictions fullRAM.
Retour SANS AIDE,coup3017431EE HP104->102 MP72->64,sortieEB302306 ;15 predictions.
4 relectures RAM65536/PNG exactes,HUD128mots/9marqueurs apres cristal et sortie.
20 pointsD9 couverts avec entree/gardiens/ballon. Neuf cristaux surv309 courant,
sans import SRAM ni ressources. Episode13 ferme devant1AC,native inchangee.
APRES D9 :overview reel et entree palais froids maintenant VALIDES.
Job39874 terminal success ;owned_overview_v0309 passe. Activation302468,
carteprete302964,retour303055(selection0),hache1303147,checkpoint303247.
HP102/104 MP64 gold32 keys2 inchanges,x136 y96 EB,Ballon1. Zero nouvelle
RAMwrite/SRAMimport. Fond5120+map1280+cells160+metadata restaures ;768mots
physiques carte/HUD et9marqueurs verifies,canonique RAM65536/PNG exact.
Job19691 terminal exit1 :premier palais entry01 refuse avant emulation car
ordinary overview n est pas une salle nettoyee. Aucune trace jeu creee.
Correction pilote monde :--prefix-completed-action explicite,assiste et MD,
prior.passed/no new writes/imports,canonique valide,position lue depuis RAM
(rapport overview conserve x/y en8.8). Contrats historiques inchanges par defaut.
Preconditions resserrees ensuite ;mode incompatible refuse avant emulation.
Job88273 terminal success :entry02 palais18D306434 HP102/104 MP64 gold32 keys2.
Gate8B cellules35/35/35 a305511 ->30/31/1F305800,289images observees.
Audit cold_palace_entry_v0309 passe,canonique RAM65536/PNG exact,HUD128/9marqueurs.
Sources v0309-cold-palace-entry02-sources gardent le pilote execute17fdc...,
independamment des seules preconditions ajoutees apres mesure. Ne pas editer
les preuves pour forcer egalite avec le helper courant ;anciens audits liant
helper courant et ancien snapshot peuvent exiger revision Git historique.
NativeROM v309 inchangee,toutes les nouvelles ecritures restent hero_hurt0/129
pour l approche autorisee. Nouvel episode14 pending FINAL14C (pas15E).
ACTIF32757 : validation/run_cold_palace_giant01.py,panel16D depuis18D/17D,
switch16D,contour18D/18E/17E->16E/switchNord,retrait avant15E,puis7B60HP
basic2,entreeUP si besoin,planning32,relecture a chaque etape. Aucune preuve
combat geant froid encore. Poll32757,ne dupliquer aucun travail terminal.
Ancien chemin controle =proposition seulement ;aucun --controlled-sram-prefix
ni fixture dans le nouveau pipeline. Garde doit aussi etre retire avant11E/7C
et14C/6D ;vraie hache2 en11D encore a obtenir avant dernierboss.
Ballon WORLD OVERVIEW,pas transport,usage seulement exterieur terrainnormal.
La fin froide/globalRNG/phases/optionnels/sauvegardes/materiel restent ouverts.
Le parcours historique v306 evitait19C/7B et ballon ;ils sont maintenant couverts surv309.
Le detour valide utilise reach-room19D24/88 avec4pieges62HP0 conserves et
retire le garde avant19C. Cette preuve specifique couvre le geant et la collecte
du ballon ;ne pas inferer les autres contenus optionnels depuis9 cristaux.
Le 9e donjon exige retrait du garde avant1BE/79,19C/7B et1AC/6C.
Pipelines10831 terminal exit1 (plan94),60451,99237,78712 et19015 terminaux
success. 21 checkpoints D7 verifies avant le combat principal.

Autorisation utilisateur :argent de test infini pour acheter des potions
normalement si utile,alternative a l invincibilite. Toute utilisation sera
indiquee dans les rapports et distincte des preuves sans injection de
ressources. Non utilise actuellement ;aucun argent/objet/PV/MP/acteur/
progression/SRAM importe. La protection est retiree avant chaque boss,
y compris les intermediaires. ROM distribuee inchangee v3097270576d.
Inventaire source native_remaining_v0309 :66 sites random SGDK provisoires,
5 commentaires de phase approximative ;TODO14ED/4C7E obsoletes,fonctions presentes.
Objectif complet encore ouvert. Lire validation/current_palace_handoff.json
pour l etat le plus recent. Copier tout le workspace pour les preuves ignorees.

Historique D3 :
Le parcours froid v0309 valide maintenant trois cristaux et la sortieD3 :
64422,exterieur62,48/56PV,24PM,0cle,corde13=1 et huile8=1,hache1 selectionnee.
Checkpoint validation/natural-dungeon-combat/md-auto-v0309-d3-exit02.
Huit relectures RAM65536/PNG exactes et HUD physique128mots/3marqueurs verifies
apres cristal et sortie. Voir analysis/d3_campaign_v0309_report.json et .md.
Le premier1E3 ouvre normalement le mecanisme pendant que des ennemis restent.
Le premier trajet avait saute la vraie cle1D2 : approche01/release01/boss01
sont exclus de la branche gagnante. key01 collecte la cle,reprise approche02.
Guard retire57767,premier combat69 a57859 HP48/hurt0/boss32.139 predictions
fullRAM exactes ; coup62251 HP48->40,puis vrai cristal avec soin56/56.
Aucun write apres57767,ni pendant le retour. exit01 n'avait pas de planning
sur les salles D3 ; exit02 utilise les vraies sorties et9 fenetres step32.

Le helper unassisted complete maintenant les metadonnees du boss principal
par relecture de son entree et combat depuis le retrait,etend end_frame,mais
ne change aucune ecriture. Cela permet --new-assistance-episode APRES la
sortie,sans protection du retour. Les intermediaires gardent leur prochain
boss principal distinct. Sources exactes des deux versions du helper :
validation/v0309-d3-pre-episode-finalization-sources et
validation/v0309-d3-exit02-sources ; hashes compares aux vrais rapports.

La preparationD4 est maintenant franchie : gold-entry01 atteint3F a67608,
gold50-01 recoit normalement50cornes (12->62),retourF4 a68044. earth-entry01
reussit la coupe A3:4A et entreBF a69783 ; earth-learn01 paye50cornes,apprend
Terre1 et augmente/refait la magie a48PM,sortieA3 a70796. Les relectures
canoniques de ces quatre etapes passent. d4-entry01 atteint1F0,48PV/48PM,
12cornes,corde et huile conservees. Pipeline32346 termine,ne pas le relancer.
Ces passages D4 sont maintenant termines ; voir le bilan D4 en tete de note.
Lire validation/current_palace_handoff.json pour le dernier checkpoint.
Le nouvel episode D4 commence64422 APRES le vrai retourD3,boss suivant180.
Aucune SRAM n'est importee. Ne jamais relancer dans un dossier deja cree.

## Priorite : campagne froide courante complete et fidelite globale

La fixture validation/palace-save-fixture-v0309-02/controlled-derived.srm est
SYNTHETIQUE,derivee du vrai RAM v0306 neuf cristaux. Ce n'est pas une sauvegarde
produite par le jeu. Ne jamais compter ce scenario comme campagne v0309 depuis
Nouveau Jeu. Le mode --controlled-sram-prefix est obligatoire ; le mode strict
refuse ces enregistrements. Les rapports declarent primary_state_imports=1,
controlled_sram_fixture=true,natural_campaign_proof=false.

La phase1 est figee dans analysis/controlled_palace_phase1_v0309_report.json :
entree18D,interrupteurs16D/16E,geant7B15E sans protection,deux portails,Terre14E
et11A,interrupteur129 et retour12A. Quinze relectures RAM/PNG exactes.
Checkpoint de fin de phase1 :
validation/natural-dungeon-combat/md-auto-controlled-v0309-palace-switch12902,
48495. Les neuf cristaux naturels restent prouves sur v0306 uniquement.

La phase2 est figee dans analysis/controlled_palace_phase2_v0309_report.json :
contournement12C->11C->11B->12B->12C->12D->12E termine a76952 ; guard retire
76953,combat7C11E commence77054 HP104/hurt0. guardian01 atteint90000 avec8PV
au gardien et80PV au heros,404 fenetres fullRAM exactes. Ce checkpoint est
incomplet. guardian02 finit via controleur ordinaire : salle vide90564,
checkpoint90715 HP56/PM72. Aucune ecriture d'assistance depuis76953.
Neuf relectures RAM65536/PNG de phase2 exactes.

final-approach01 reprend la protection seulement a90716 apres victoire
verifiee. resume_after_intermediate --boss-room0x11e --next-boss-room0x14c
verifie que14C n'apparait jamais dans tout le prefixe. Cas maintenant exerce.
goldenaxe01 obtient la recompense11D normalement : objet1 passe1->2,texte
ferme,hache2 selectionnee. Checkpoint93233 HP80/PM72/2cles,relecture exacte.
Aucun PV,objet,monstre ou flag injecte apres l'import SRAM initial.

La phase3 est maintenant verifiee : quinze relectures RAM65536/PNG exactes.
Voir analysis/controlled_palace_phase3_v0309_report.json et son document.
Vrai chemin : retour12C->12B->11B->11C(portail)->12A->11A->119(portail)->14E,
13E Terre3A(portail)->16A,combat16A libere la barriere,17A->18A->18B->17B->17C.
Bouton17C met flag4 de17B ; revenir17B->18B->18A->17A->17B(portail)->13C.
13B->14B flamme droite ; boucle13B->13A->14A->14B(portail)->15A.
15B Terre48 depuis136,88 dirige UP ;16B->16C bouton nord72,40 ->15C.
Les sentinelles58 de15C sont reveillees et vaincues normalement.
L'ENTREE FINALE EST15C->14C PAR LE NORD, PAS14D. Les anciennes hypotheses
via14D ne sont pas des chemins verifies et ne doivent pas etre reutilisees.

pre-final03 termine151244,15C vide,100PV/72PM/2cles,hache2 selectionnee.
final-release01 retire le guard151245 ; relecture canonique exacte.
Le combat final et la fin sont maintenant VERIFIES dans le scenario controle.
Voir analysis/controlled_palace_ending_v0309_report.json et son document.
finalboss01 : premier6D151328 HP100/hurt0,boss90PV ;114 predictions fullRAM
exactes. Victoire155151,game14,flag donjon10=1,heros48PV. Checkpoint155152
canonique exact. Aucun write apres le dernier zero151245.
ending02 :9gemmes155477,generique156170->163593,nouvelle toucheC163623,
retour game0 et nouvelle intro ; checkpoint163723 canonique exact.
Requetes musicales8D155433 et88155838 observees. Images gemmes/credits vues.
Les pipelines81287,18772 (negatif),24561 sont termines ; ne pas les relancer.

ending01 avait donneC trop tot,pendant le dernier tick de credits : generique
fini mais aucune nouvelle pression pour quitter. Ce n'est pas un bug natif.
Le helper attend maintenant30 images avant la vraie nouvelle touche.
--stop-on-ending et continue_recorded_ending sont maintenant exerces en jeu.
Le champ ending_stage est optimise et absent : ne pas le lire. L'audit lit
les vrais descripteurs8495/84E1,les9gemmes,ending_credits.done,game0 et
intro_running non nul (ou title_phase vrai). Le titre repasse par son intro.

PROCHAINE PRIORITE : poursuivre la vraie campagne froide v0309 D4 et suivants,
selon le dernier checkpoint ci-dessus. L'ancien D2 exit47255,D6,33/48PV,est
maintenant un jalon anterieur. AUCUNE SRAM ni RAM de la fixture palais ne doit
entrer dans cette campagne. Les neuf cristaux froids restent prouves seulement
sur v0306. Le palais courant complet est un scenario controle independant.
Ne pas confondre ces deux preuves et ne pas marquer l'objectif complet.
Revoir aussi la pile avec le vrai parcours final,les contenus optionnels et
les limites de fidelite/RNG/horloge signalees dans README et rapports.

L'inspecteur read-only tools/inspect_recorded_dungeon_room.py lit le vrai RAM
capture,les sorties accessibles,les portails et les scripts source. Il ne
prouve pas un deplacement reel. Il permet d'eviter les mauvais compartiments.
16A cellule76=10 : clear-kind5 apres ennemis,pas Terre. Un essai Earth16A01
s'arrete avant toute nouvelle action sur l'assertion du type de bloc.
13E cellule3A=11 et15B cellule48=11 : vrais lancements Terre verifies.
Les essais incomplets de route restent explicitement etiquetes dans phase3.

close_assisted_approach accepte63..6D et78..7C ; le cas6D est exerce.
Les bits20/40 seuls ne distinguent PAS les boss des ennemis ordinaires.
L'audit de continuation reobserve tout le combat apres le dernier retrait du
guard,y compris les touches heritees,afin de supporter un prefixe pendant
la mort du boss. Aucun helper ne doit ajouter d'assistance apres le retrait.
Le guide Quarbit est une aide de route ; les tables ROM et le jeu font preuve.

Les outils controles conservent un cooldown naturel<=128 lors d'un premier
combat seulement avec marqueur natural_cooldown_observed,apres verification
du prefixe sans129. Le geant commence a102PV/hurt18 (danger61 avant la salle),
gagne a104PV via les ramassages. Ne pas confondre cela avec le guard129.
La recherche evasive du helper unassisted choisit maintenant par defaut la
salle closed_before_room ; un premier essai sans cette salle etait reste sur
le pilote ordinaire et est mort,donc exclu.

Les slots8..15 peuvent contenir des enfants ennemis4C vivants : le critere
room_cleared a ete renforce. clear14e01 verifie les seize slots vides. Les
acteurs61/62 a0PV sont des dangers persistants,avec objectifs de mecanisme.
Le helper Terre restaure le type d'arme demande (--equip-basic ou axe),ce qui
evite un conflit de pilotes dans l'inventaire. Les echecs capturent desormais
leur derniere image,et les budgets captures incluent le maximum demande.

Le premier probe controle01 etait demarre trop tard,apres la mort du heros.
Il est invalide. Son processus a ete arrete,puis toutes ses captures ont ete
archivees avec hashes avant suppression ;1,79Go nets liberes. Le catalogue
analysis/controlled-palace-discarded-v0309/manifest.json et ses objets restent
LOCAUX,volumineux et exclus de Git. Les312originaux/ROMs/alias sont inchanges.
La fixture02 attend le reset hero0->1 apres le chargeur avant de lancer le
trajet. Ne jamais reutiliser le rapport fixture01 comme preuve.

Attention : le core ne vide pas toute la RAM inactive entre deux ROMs dans
un meme processus. Executer les references dans des sous-processus neufs.
Le README a aussi ete repare d'un double encodage CP1252/UTF-8. Lire/ecrire
explicitement en UTF-8 : Python3.13 utilise CP1252 par defaut ici.

## Correctif precedent : v0308, passage du palais

Le correctif a ete publie en v0308. Le correctif porte6911-698A : apres les neuf cristaux,
la salle8B ouvre le passage ouest vers8A puis89. Quatre tests controles SMS/MD
valident le garde huit/neuf cristaux,les289 images et chaque decalage horizontal.
Voir analysis/palace_gate_v0308.md et analysis/palace_gate_v0308_report.json.
Ce ne sont pas des preuves naturelles : le checkpoint campagne ci-dessous reste
sur v0306 ; le parcours froid v0309 et les scenes controlees sont suivis ci-dessus. La v0307 intermediaire
est conservee ; v0308 corrige le choix de file sonore9E (DE06).
Cette suite est maintenant executee dans le scenario controle v0309 decrit plus haut.
Elle ne remplace pas la campagne froide courante.

## Point de reprise campagne : neuf cristaux

Le jalon `analysis/d9_campaign_v0306_report.json` valide la victoire6C et le retour dehors enEB :270242 images,104/104PV,72/72PM,1cle,37pieces,neuf cristaux. Le checkpoint est `validation/natural-dungeon-combat/md-auto-v0306-d9-exit01`, avec sa relecture froide complete. Ce checkpoint utilise v0306. Aucun processus de validation ne reste actif a la livraison de ce jalon.

Voir `analysis/d9_campaign_v0306.md` pour les mecanismes regroupes,les200 predictions exactes et les six nouveaux checkpoints froids. L'archive locale est `analysis/d9-campaign-v0306`. Le profil de pile reste celui du huitieme donjon ; ne pas attribuer les402octets a toute cette nouvelle partie.

## Objectif et regles du projet

Decompiler la ROM Master System fournie et porter Golden Axe Warrior en code natif 68000 sur Mega Drive, avec SGDK si utile. Obtenir d'abord une version fidele ; les ameliorations viennent ensuite. Le portage complet reste non valide.

Conserver toutes les ROMs numerotees. Ne creer une nouvelle version que si les octets de la ROM changent. Mettre a jour le README et enregistrer les livraisons sur main. Les essais de campagne peuvent utiliser l'invincibilite pour les approches, mais elle doit etre retiree avant chaque boss, y compris les boss intermediaires. Aucun PV, PM, argent, objet, acteur, avancement ou SRAM n'est importe dans ce parcours. Les controles du jeu produisent les acquisitions et les soins.

## Dossier a conserver

Dossier de travail du depot :
`C:/Users/UniKennY/Documents/Codex/2026-10-07/hel/outputs/gaw-md`

Sur le meme PC, ouvrir ce dossier dans Codex avec le nouveau compte. Le contenu du disque reste la source de travail. Sur un autre PC, copier tout le dossier `hel`, y compris les fichiers caches et `.git`, pour conserver aussi `work/` et les dependances presentes localement. Conserver les sauvegardes existantes jusqu'a verification de la copie.

ATTENTION : `.gitignore` exclut notamment `validation/`, `megadrive/out/` et les objets volumineux des archives `analysis/*/objects/`. Les manifestes sont sur Git, mais leurs objets compresses restent locaux. Un clone Git seul conserve le code et les ROMs versionnees, pas toutes les preuves ni les points de reprise necessaires aux outils. Copier le dossier complet pour poursuivre le parcours actuel.

## Jalons de reference

Commit de reference pour l'acces : `b0f743f007b7b06240bd48286d59ebf49a8720d4`. Pour le dernier commit publie, consulter git log et origin/main.
Depot actuellement redirige vers `https://github.com/spamkenny02/goldenaxe.git` ; l'ancien origin spamkenny02-commits fonctionne par redirection. Apres un futur transfert GitHub, mettre origin a jour avec l'URL du nouveau proprietaire.

ROM du checkpoint de campagne : v0306, 2048 Kio.
SHA-256 : `3a12380b86c193148d1cbd29d68a880901860cfb1c276aa96d61d2da16ac2c01`.
Checksum Mega Drive : `343B`.
306 ROMs numerotees ; les deux fichiers racine ont les memes octets que v0306.

Le parcours publie valide huit cristaux et l'entree du neuvieme donjon en1FC :239841 images,84/96PV,72/72PM,1cle,21pieces. L'acces utilise le vrai transport1A->3C puis la cloche enCB. Voir `analysis/d9_entry_v0306.md` et `analysis/d9_entry_v0306_report.json`.

## Premier boss intermediaire du neuvieme donjon valide

Le jalon est decrit dans analysis/d9_midboss_v0306.md et analysis/d9_midboss_v0306_report.json. Il comprend :

- `md-auto-v0306-d9-switch1de-02` :246418, Terre casse le bloc34 en1DE, puis UP actionne la torche pour rejoindre1CE ;84PV,64PM.
- `md-auto-v0306-d9-earth1ce-01` :246742, Terre casse56 en1CE ;84PV,56PM.
- `md-auto-v0306-d9-mini-ready01` :250495, salle1CE vide ;84PV,72PM. Les ramassages normaux ont restaure les PM.
- `md-auto-v0306-d9-guard-release01` :250496, protection retiree dans1CE avant le boss1BE/type79. Relecture froide complete reussie.

- `md-auto-v0306-d9-midboss01` :252171, boss79 vaincu en1BE sans protection ;48/96PV,72/72PM,1cle,27pieces,huit cristaux. Epee longue2 selectionnee.

Ces cinq checkpoints disposent de leur relecture `-assisted-fixed-replay-FRAMES`, identique sur65536 octets de RAM et PNG final. Les repertoires sont sous `validation/natural-dungeon-combat/`.

Le pipeline et sa relecture sont termines avec succes. Le combat comporte164 fenetres de prediction identiques sur toute la RAM. Le retrait250496 precede le premier combat250692 (84PV,hurt0,boss60PV). Deux pertes de PV sont observees :84->64 et64->48. Aucune protection ne reprend pendant ce combat. Verifier les derniers rapports avant toute continuation et ne pas relancer un essai dans un repertoire existant.

Le test01 vers la torche1DE s'est arrete parce que le controleur n'avait pas encore casse le bloc. Il est negatif, sans preuve terminale, et exclu des jalons positifs. Le controleur combine `tools/natural_earth_then_contact.py` traite cette action normalement. L'audit tools/summarize_d9_midboss_v0306.py est reussi. L'archive locale analysis/d9-midboss-v0306 conserve les preuves ; ses objets restent ignores par Git. Les RAM du retrait et de la victoire restent disponibles pour la reprise.

## Anciennes pistes apres D9 v0306

Les neuf cristaux et la sortieD9 sont verifies sur v0306. Le palais,la Hache d'or,Death Adder et la fin sont maintenant verifies separement dans le scenario controle v0309. Reprendre la campagne froide courante selon la priorite en tete de ce document ; les sauvegardes restent ouvertes. Le geant optionnel19C/7B et le ballon restent non valides dans ce parcours ; ne pas les oublier dans le bilan final.

Piste de route a confirmer contre le SMS : le guide Any% Quarbit indique la cinematique en L8 (8B,ancienne entreeD6),puis le donjon final en J8 (89). La marche statique directe vers89 n'est pas trouvee,mais cela n'est pas une preuve de bug du jeu. Ce controle original est maintenant realise et le correctif v0308/v0309 est verifie ; voir les rapports palais. Source : https://www.speedrun.com/golden_axe_warrior/guides/yfxxr

Le boss final6D n'accepte que la hache2 selectionnee. La table originale place la Hache d'or en11D : index inventaire1,valeur2,objet5. Sa collecte1->2 est maintenant verifiee dans goldenaxe01 ; un test booleen de possession d'une hache ne suffit pas.

Le controleur `tools/entered_boss_route.py` finit l'entree par UP avant la recherche. Il a permis d'eviter les sorties involontaires au seuil du6C ; la ROM n'est pas modifiee. Les prochaines routes doivent regrouper les salles et mecanismes ordinaires,avec une relecture complete par jalon,et conserver les retraits verifies avant les boss. Le lecteur evidence met aussi les manifestes d'archives en cache par processus,avec invalidation sur changement du fichier ; les hashes des preuves restent verifies. Les trois auditsD9 donnent des rapports identiques avec ce cache.

Les relectures deterministes MD ne prouvent pas toute la fidelite SMS. Le hasard SGDK global reste provisoire ; les timings/audiovisuel globaux restent a valider. Le dernier profil de pile couvreD8 jusqu'a235211 images :402octets observes,pas une borne pour tous les chemins suivants. Le materiel reel n'a pas ete teste.

## Outils et precautions de reprise

Python local utilise : `C:/Users/UniKennY/AppData/Local/Programs/Python/Python313/python.exe`.
SGDK : `hel/work/sgdk`. Java utilise : `D:/jdk-25.0.1/bin/java.exe`.
Le build accepte `./build.ps1 -Sgdk CHEMIN -Java CHEMIN`. Installer/adapter les outils si le nouveau PC differe. MSYS GCC pour les profils : `C:/msys64/ucrt64/bin`.

Avant de modifier : lire `git status --short`, cette note, le README et les derniers rapports. Ne pas ecraser les changements non encore commits. Utiliser `tools/rebase_natural_campaign.py:evidence` pour lire les preuves archivees. Toujours conserver le delai naturel des degats de sol avec `--preserve-floor-hurt` dans les approches assistees. Apres retrait anticipe, continuer avec `unassisted_dungeon_continuation.py`, sans ajouter de protection ; ne reprendre un episode qu'apres victoire effectivement prouvee.

`analysis/world_next.md` contient des octets non UTF-8 : ajout ASCII en mode binaire uniquement, sans relecture/reencodage complet. Conserver CRLF dans les fichiers existants qui l'utilisent.

Nettoyage : uniquement apres compression sans perte, relecture et verification des hashes. Proteger l'original, les deux alias et toutes les ROMs numerotees. Ne jamais supprimer globalement les traces encore necessaires a la reprise.

## Message a donner au nouveau chat

> Lis REPRISE_CODEX.md, README.md, git status et les derniers rapports de validation. Reprends l'objectif complet : portage Mega Drive natif et fidele de Golden Axe Warrior. Verifie d'abord les derniers rapports et le checkpoint du retour avec neuf cristaux avant de poursuivre. Conserve les changements en cours, les ROMs numerotees et les archives locales ; ne declare pas le jeu termine avec les seuls neuf cristaux ou avec une preuve de determinisme MD.

## Résultats c0046 du 6 novembre, soirée

Les deux pilotes resume_d1_key.py sont terminés avec succès. Le premier
cristal et la sortie B9 sont prouvés en NTSC (17169, 28/32 PV) et PAL
(19596, 32/32 PV). Les sept checkpoints par région reproduisent RAM/image.
Source boss 68 à 12 PV, retrait avant combat : 14253 avant 14465 en NTSC,
16248 avant 16449 en PAL. Respectivement 21 et 19 prédictions RAM exactes.
Rapports analysis/c0046_d1_auto_report.json et c0046_d1_pal_report.json.
La V318 demeure référence ; ne pas confondre le premier donjon c0046 avec
le parcours PAL complet V318 qui continue indépendamment.

La continuation c0046 NTSC récupère la hache, reçoit la première fée de vie
et entre en D2 à 27553 avec 40/40 PV. Audit et archive :
analysis/c0046_after_d1_report.json, analysis/c0046-after-d1.
Les pilotes spécifiques sont des fichiers ordinaires dans les tools du
laboratoire : continue_after_d1_c0046.py puis continue_d2_c0046.py.
Le premier a terminé ; le second enregistre ses commandes et ses sources
dans validation/c0046-d2-sources du projet isolé. Vérifier son processus
réel avant de reprendre. Les outils partagés par lien physique demeurent
inchangés ; les sorties ne touchent pas au parcours PAL V318.

## Fin PAL V318 confirmée et format c0047

Le pipeline PAL est terminé avec succès. Death Adder : retrait de protection
381583, premier combat 381672 à 100 PV/hurt0 contre 90 PV source, victoire
et passage état14 à 383429. 98 prédictions RAM exactes. Neuf gemmes visibles
383712, générique 384405..391828, retour intro391858, dernier checkpoint
391958. Audit complet : analysis/pal_palace_ending_v0318_report.json et
analysis/pal-palace-ending-v0318. RAM/image exactes depuis Nouvelle partie.
Ne pas relancer les pilotes sur ces dossiers existants.

Erreur de format repérée : les fichiers c0045 et c0046 faisaient 1152 Kio
bien que leur en-tête annonce 2 Mio. Ils sont conservés et documentés.
La ROM c0047-d3ea2a83 complète c0046 avec FF à 2 Mio et recalcule le checksum
DA29. Aucun autre octet du programme et des ressources ne change.
Les deux campagnes du premier cristal c0046 se rejouent sur c0047 avec
RAM entière/image finale identiques. La ROM V318 reste référence. Les
pilotes de compilation concernés ajoutent maintenant le complément et
finalisent le checksum avant toute publication future.

## Deuxième cristal de l’optimisation confirmé

c0046 NTSC atteint le deuxième cristal et le retour D6 à 56219, 37/48 PV.
Le premier pilote key201 était limité en 151 ; un aller-retour normal
résout la rencontre et key202 ramasse la vraie clé. Le premier combat
boss01 atteint son budget à 51406 avec 8 PV ennemis et 40 PV héros, sans
mort ni ajout de protection. Après preuve RAM/image du point partiel,
resume_d2_boss_c0046.py prolonge les commandes avec un pas de 16 images.
Victoire, cristal et retour extérieur passent leurs rejeux indépendants.
Audit : analysis/c0046_d2_report.json, archive analysis/c0046-d2.

Le rejeu intégral de ces mêmes entrées jusqu’à 56219 sur c0047 est lui aussi
RAM entière/image finale identique : analysis/c0047_d2_auto_report.json.
Tous les processus de ce deuxième donjon sont terminés. Les pilotes à
reprendre ensuite concernent le don d’huile puis D3 ; ne pas relancer les
anciens pilotes sur les dossiers de preuve existants.

## Huile et reprise D3 de l’optimisation

Le don d’huile c0046 NTSC est audité et archivé dans
analysis/oil_service_c0046_report.json et analysis/c0046-oil-service.
Route 57774, service terminé 58477 : huile obtenue, 37 PV/12 pièces/24 PM
inchangés, deux cristaux conservés, HUD physique128 mots exacts. Aucun
nouvel ajout de protection pendant le service. Les preuves RAM/image
indépendantes passent.

Le pilote continue_d3_c0046.py est maintenant en cours dans les tools du
projet isolé. Sources et commandes : validation/c0046-d3-sources02, dans
ce même projet. La première tentative de résumé de l’huile manquait du
module local z80dis ; le lien de dépendance a été ajouté, puis le résumé
et son archive ont terminé correctement. setup_c0046_links.ps1 rend
ces liens reproductibles et est appelé par setup_c0046_campaign.py.
Ne pas relancer l’ancien pipeline huile sur ses dossiers existants.

## Corde D3 et reprise après les essais de portail

Entrée D3 à 61462, corde obtenue et fenêtre de récompense terminée à
67763, 37/48 PV. Audit : analysis/c0046_d3_rope_report.json et archive
analysis/c0046-d3-rope. Le rejeu sur c0047 de ces mêmes commandes jusqu’à
67763 est RAM entière/image exacte : analysis/c0047_d3_rope_auto_report.json.

rope01 et rope02 s’arrêtaient après un retour involontaire par le portail.
L’essai d’un maintien supplémentaire de direction dans le pilote n’a rien
résolu et a été annulé. Le fichier privé natural_dungeon_combat.py est
revenu byte-identique au fichier partagé original ; il est maintenant un
fichier ordinaire, pas un lien physique. La ROM et le pilote du dépôt
racine sont inchangés. portal_controller_fix.json trace cet essai écarté.
Le succès rope03 utilise l’option existante --avoid-portal-rooms 0x1e2.

Le processus actif exécute resume_d3_c0046.py, depuis les tools du projet
isolé. Il a rejoué la corde et poursuit le mécanisme, la clé puis le boss.
Ses sources/commandes sont dans validation/c0046-d3-sources03 du projet
isolé. Ne pas relancer l’ancien continue_d3_c0046.py ni ses sorties rope01.

## Troisième cristal de l’optimisation confirmé

resume_d3_c0046.py a terminé. Retrait de protection71643, premier combat
71791 à 37 PV/hurt0 contre le boss69 à 32 PV source. 69 prédictions de
combat exactes, puis 21 sur le retour. Cristal puis sortie62, dernier point
75250 à 48/56 PV. Audit analysis/c0046_d3_report.json, archive c0046-d3.
Le rejeu sur c0047 jusqu’à ce même point est RAM entière/image finale
exacte : analysis/c0047_d3_auto_report.json, archive c0047-d3-auto.

Le processus actif suivant exécute continue_earth_learning_c0046.py dans
le projet isolé. Il va chercher le don réel de 50 pièces, puis acheter
Terre normalement. Son journal et les sources sont dans
validation/c0046-earth-learning-sources du projet isolé. Ses preuves
indépendantes utilisent un nouveau flux de rejeu froid persistant dans
validation/c0046-earth-cold-stream. Vérifier le processus avant reprise.
