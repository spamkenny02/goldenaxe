# Reprise du portage dans un autre compte Codex

Etat de cette note : 4 novembre 2026. Lire aussi README.md et les rapports plus recents eventuellement ajoutes depuis cette note. Le changement de compte ne termine pas l'objectif du portage.

## Priorite utilisateur : livraison vendredi6novembre au soir

Lire analysis/livraison_2026-11-06.md. User demande etatdeslieux et rappelle
DEADLINE REPORTEE par utilisateur au6novembre au soir (message du4novembre). Priorite aux blocages/regressions/validation
ROMlivree,finparcours310,paquetnumerote+README+main. Pasdegarantie100%sanspreuves.
Ne pas confondre campagnev309complete etcourante310jusqueD3.
Pointcourant APRESD3 :gold-entry01 fin69600,gold50-01 fin70043 roomF4,
Earth-entry02 fin71785,Earth-learn01 fin72795 roomA3,46/56PV,gold2,MP48/48,
Terreitem5niveau1,huile+corde+3cristaux. Donreel2->52,achat50->2.
Quatre coldreplays RAM65536/PNGexactes,HUD128exact pourles2services,imageinspectee.
Episode4 approche cible180,aucunewritenouvelle dansservices,zeroresourcesimports.
analysis/earth_learning_v0310_report.json passe; sources v0310-earth-learning-sources.
Aucunjobactif. Prochaine action:assisted_boss_route --boss-room0x180 --world-route
--prefix-service md-v0310-earth-learn01 --assisted-prefix --door-index4
--axe-terrain --rope-terrain,trialv0310-d4-entry01,frames79000ouplus.
Referencev309d4 pouritineraires seulement,jamaisRAMimport.
SourceD4boss=6A/180,pas65.65originalensalle163 uniquement.
RouteTerre01 arret AVANTemulation:no base-map route car --rope-terrain omis.
02 a cordeacquise et --required-chop0xa3:0x4a valide. PasdebugROMetabli.
ROMinchangee v310. Nouvelledeadline6novembre au soir,notesdatees4novembre.

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
