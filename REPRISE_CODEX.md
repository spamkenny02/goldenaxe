# Reprise du portage dans un autre compte Codex

État courant au 8 novembre 2026. Les notes historiques conservées
plus bas décrivent des versions antérieures. Lire d’abord cette section,
le README et les rapports cités.

## Suivi courant — V320, 8 novembre 2026

STOCKAGE ET PASSATION : anciennes sorties locales compactées, cache ignoré
`analysis/local-validation-cache/catalog.json`. Ne pas supprimer ce cache sans
accepter de régénérer les sorties non versionnées. Restauration ciblée :
`python tools/restore_validation_cache.py --path validation/...`.
Fixtures v319-scene-live-vdp02 et deux enregistrements canoniques c0046 conservés.
319 anciennes ROMs retirées du poste avec skip-worktree ; historique Git intact.
Seule la V320 numérotée reste déployée. `tools/prune_local_roms.py --apply` pour
les futurs nettoyages ; le constructeur overlay lit la base319 depuis Git.
Paquets locaux `handoff/gaw-v320-ready-to-build-windows.zip` (autonome Windows)
et `handoff/gaw-v320-sources-pour-llm.zip` (léger,sans outils binaires).
Sources du script BUILD_V320.ps1 + instructions + PASSATION_LLM.md versionnées.
Paquet complet compilé après extraction : SHA9e5b0abe… exact. Gros caches,
MP4 et ZIP restent horsGit. Sources/données du paquet indépendantes des caches.

DERNIÈRE ÉTAPE NATIVE : workspaceIRQ privé sans rollback redondant.
`analysis/v320_irq_workspace_report.json`, archive `analysis/v320-irq-workspace`.
source_irq_workspace.c instancie le même corps via macro GAW_IRQ_PRIVATE_WORKSPACE.
La routine canonique conserve les mêmes tokens préprocesseur et son rollback.
La variante privée enlève old[336]/copie ; après rejet son état est jetable.
Seuls l’adaptateur fullIRQ et le preview vidéo, déjà sur RAM privée, l’utilisent.
23000cas host +46000compilés,acceptations/rejets/queue/reset/overflowwork exacts.
133fixtures source/frame/SAT/PSG par région passent en composition host ;
20scènes compilées exactes. GainCPUmodeste~1%,helper69..77NTSC/58..64PAL.
Rebuild baseV319 puisoverlayV320 identiques. Pas de changement ROM publique.
Prochain : motifs/clock25..35framesNTSC ;gateCPU et auditsVDP/PSG restentouverts.

DERNIÈRE ÉTAPE NATIVE : envois SAT IRQ groupés entre frontières de ligne.
`analysis/v320_sat_runs_report.json`, archive `analysis/v320-sat-runs/manifest.json`.
source_intro_vdp_sat_run :64Y/128XY,OUTI16T,source_raster/epoch validés,
checkpoint initial puis avance avant chaque ligne ; mutations dans une ligne
sans nouvelle évaluation,avec caches/flags/VINT/adresse/buffer finaux exacts.
Les registres/BF et palette gardent leurs écritures datées individuelles.
48300cas host et48300par région MD :575lignes,6phases,7tailles,displayon/off,
patterns aliasSAT,caches,counters,overflow/collision/VINT et wrap32.
VDP/cache/SAT exact après run/read ; canaris16KiB après chaque bloc de ligne.
Premier test01 arrêté à sa limite180000frames sans écart,non compté comme
succès complet ; test02 évite les comparaisons16KiB inutiles à chaque octet.
20scènes compilées exactes. HelperNTSC88..96→70..78,PAL74..80→58..65.
CPUgateFALSE ; aucun branchement vers cette composition en ROM publique.
Rebuild baseV319 exact puis overlayV320 exact/9e5b0abe…/B0A2. Pas de V321.
Prochain : motifs25..34framesNTSC,coût preview/rollbackIRQ ; dates originales
IRQ,coldboot natif continu,livraison physiqueVDP/PSG et PCM restent ouverts.

DERNIERS CONTRÔLES V320 : `analysis/v320_followup_tests_report.json`,
archive `analysis/v320-followup-tests/manifest.json`.
PAL382208imagesdepuisNewGame :9cristaux,DeathAdder,7424étatscredits bordures
noires,retourintro382108,imagefinaleidentiqueàréférenceV319. Approcheguard196493
écritures autorisées,retiréeavantboss ;aucunimportSRAM/progression.
Aprèsfixturemortboss,finproduction→acknormal→intro→nouvellepartie enNTSC/PAL.
Jeu12,cristauxàzéro,hérosvivant,masqueWindowdésactivé,BG_B26/27zéro.
ROM320 inchangée/9e5b0abe…/B0A2 ;pasdeV321pourcesseulstests.
Cescontrôles ne clôturentpasPCM/matériel/toutesroutes ni compositionCPUexpérimentale.

DERNIÈRE ÉTAPE : correction bordure du générique, V320.
`analysis/v320_credits_report.json`, archive `analysis/v320-credits/manifest.json`.
Source : `megadrive/overlays/credits_border.s` ; build reproductible :
`python tools/build_credits_border_overlay.py --out validation/NOUVEAU_DOSSIER`.
Base V319 auditéed3ea2a83…,124octets68000 à1F0000. Deux LEA originaux2144E/
226F6 redirigés vers entrée,CLR221E2 vers sortie ; instructions originales
rejouées, registres/SR/arguments préservés. Les autres octets du jeu identiques
hors checksum. Palette49 noire,BG_Bprioritaire lignes26/27 puis remiseàzéro.
7424 états PAL+NTSC : image192lignes identique V319, bordures noires, dates
4701/12124/12800 identiques dans fixture fin contrôlée. Les recompilations
SGDK/LTO générales ont fait diverger l’ancien parcours au8e donjon ; rejetées.
Le correctif livré conserve donc la disposition et les instructions V319.
Port natif expérimental/sourceclock toujours non sélectionné, CPU gate non
atteint ; le correctif générique ne clôt pas la fidélité globale du portage.
Vidéo V319 existante non régénérée : utilisateur enverra lui-même en privé,
mais capture conserve l’ancien défaut de bordure.

ÉTAPE PRÉCÉDENTE : raccourcis exacts du calendrier sans sprites, rapport
`analysis/v319_empty_sprite_clock_report.json`, archive
`analysis/v319-empty-sprite-clock/manifest.json`.
SourceIntroSpriteClock : avance directe avant prochaine ligne ; sinon saut
stable uniquement hors Mode4 ou, sans zoom, avec deux caches vides, aucun
overflow en attente et premier Y SAT=D0. Conserver drapeaux, collision et
entrées inutilisées ; calculer VINT à la ligne193 et phase finale exactement.
Les autres états gardent la boucle précédente.
172500 états complets host +172500 par région MD : toutes les 575 lignes,
3 phases, 10 états mode/cache/SAT/drapeaux, 5 deltas et wrap32. Aucun écart.
Profil stages05 : NTSC 144..162 →88..96 ; PAL120..136 →74..80.
Stages NTSC : prepare24..27, patterns25..35, clear9..12, transfert22..25.
20 scènes source/clock/R/audio/statut identiques ; ports originaux14000 images
par région puis préfixes compilés sur les deux régions MD sans écart.
Rebuild production identique V319/d3ea2a83…/DA29. CPUgateFALSE : ne pas
activer cette composition, budget source encore dépassé. Aucun nouveau binaire
publié pour ce code non sélectionné. Profil exclut livraison vidéo/PSG physique.
Prochain : coûts attentes/IRQ et calendrier actif, puis budget composé ; dates
originales IRQ, coldboot continu et livraison physique toujours ouverts.
Vidéo complète V319 locale ; utilisateur enverra lui-même le MP4 en privé.
Cette capture conserve le défaut de bordure du générique signalé ensuite.

ÉTAPE PRÉCÉDENTE : runsclear/map versownedVDP, rapport
`analysis/v319_map_runs_report.json`, archive `analysis/v319-map-runs`.
source_intro_scene_load_video_runs ajoute map_run(sharedsink_user),scène met
miroirlegacyàjour enbulk et transmetles SourceIntroVideoRun existants (sinks
standalone conserventfrontières).source_intro_scene_vdp_run adapte vers
source_intro_vdp_map_run :CLEARBE101T,stride124T,address+4,FF ;TRANSFERBE16T,
stride32T,address+1,bytesRAMborrowedimmediate. Propriétésfinales code/pending/
low/address/buffer/instructiondate respectentchaqueOUT. Bancsopposés sansSAT
peuventavancerunefois ;banque activesprites gardeavanceavantchaqueBE.
Profilstages01→03 :totalNTSC316..335→144..162,PAL265..281→120..136.
StagesclearNTSC165→22..24 ;patterns51..73,prepare30..34,transfer29..32
restentdominants. 20cas68000 sourcefinalstate/status/clockR exacts.
Unitmap02 host576 +1152cas68000 comparefullVDP/16KiBVRAM,2regions/2banques/
2kinds/6phases/4counts/3adresses,readstatusavantsequence etindicespatterns
recouvrantzonesécrites. Unit01plusbasiqueconservé aussi. Sourceskernel snapshots
autonomes pourpreuve réexécutable. RebuildV319 identique/d3ea2a83…/DA29.
CPUgateFALSE :144..162resteau-dessusbudgetSMS24..27. NePASactiverenROM.
DatesIRQ/coldbootcontinu/physicalbackground/PSG/PCM restentouverts. Conserver
descripteursparbyte pourlivraisonphysique,nepasinstantanéifieruploadbackground.
Prochain :pattern/attentesIRQ/coûtscalendrier,runstableslimitésauxobservations,
puisbudgetcomposéetphysique. VidéoV319 prête,YouTubeaccès/visibilitétoujourspending.

ÉTAPE PRÉCÉDENTE : SourcePatternVideoRun/source_pattern_decode_runs et
source_intro_scene_load_runs, rapport `analysis/v319_pattern_runs_report.json`,
archive `analysis/v319-pattern-runs`. BF30/45T,BE77T,strides135/134T,carry-1T,
terminal-5T,ROMborrowed,count<=256,runs uniquementfenêtresstablesavantIRQ.
FallbackOUT obligatoire.SinkownedVDP avance avantchaqueBE affectantsprites.
Runentièrementdansbanque8KiBopposée àcelle dessprites(reg6bit2) :écritures
sans effet surSAT/pixelsprites,uneavancecalendrierfinale suffit. Dates originales
toujoursdansdescriptor pourfond physique futur ;nePASfaireuploadinstantané.
392832OUT des24assets/IRQedges développés :hashdates/valeurs/clock/mirror
identiquespreuves indépendantesprécédentes.1728cas host +3456cas68000 :
fullVDP/cache/latch/VRAMcomparées vsOUTindividuels,2banques/6phases/3adresses/
6counts/literal-repeat/terminal. Snapshotcompilationsources autonome dansunit03.
Premierkernelunit01 nefinissaitpas en30000frames (setupmémoiredivisioncoûteuse),
rejetconservé. Unit02 avantoptimbanque passait864cas ;unit03final1728passe.
Profil05 :NTSC316..335,PAL265..281,vs606..711/507..595précédent.20scènes68000
liveIRQ/statusfinalstatesexactes,sourcecallbackcomparaisonsIRQretenues.
CPUgateFALSE,toujoursau-dessus budgetSMS~24..27/21..23. Pas derenduphysique.
RebuildtoujoursidentiqueV319.PasdeV320. Correctioncommentairefinal8KiBau lieu
4KiBdocumentée dansanalysis/v319_pattern_runs_source_note.json :codeexécutable
inchangéaprèspreuve,SHAversiontestéeetcommentée tousdeuxconsignés.
Prochain :profilparstage(clear/map surtout),runssinks équivalents etévaluation
lignesstables,budgetcomposé ;IRQdates/coldboot/image/PSGphysique ouverts.
VidéoV319 localeprête,upload toujoursattenteaccèsnavigateur/visibilité.

ÉTAPE PRÉCÉDENTE : premierprofilhelper liveVDP +arithmétique optimisée,
rapport `analysis/v319_video_math_report.json`, archive `analysis/v319-video-math`.
Profile01 vs02 :vTimer uniquement autour source_intro_scene_load_ports,exclut
copiesfixture/comparaisonsfinales etperOUTexpected ;comparesstatutsIRQ restent
présents (faible coût mais diagnostic). Profile01 NTSC1406..1684frames MD,
profile02NTSC606..711 ;PAL1176..1409→507..595. Gainmoyen~57%,CPUgateFALSE.
source_video_clock_math.h :wrap soustractionbornée si delta<period sinonmodulo
rare,longgap ;DIVU.W3420 quotient/remainder pourraster<313*3420 ;linecounter
incrémenté àfrontières,phase viauntil_line. Layout inchangé. Mis àjour
source_intro_vdp/source_intro_sprite_clock/source_intro_scene_vdp.
1966500rasterticks+6325wraps vérifiés exhaustivement surchaqueregionMD ;
8.49Msourcewrites/33707status/5616VRAMreads exacts host14000frames/région ;
535716accès compilés/9856reads,préfixesboot réelsNTSC/PAL→2régionsMD.
10scèneslivestatushost exactes ;profilekernels20cas68000 conserventRAM/audio/
clock/R/sourceVRAM. Rebuildcomplet toujoursidentiqueV319/d3ea2a83…/DA29.
PRIORITÉ :606..711frames est encore trop lent (~scènes24..27sourceframes),
nePASactivercesinksperOUT enROM. Profilercoûtsappels/stages,traiterrunsdatés
etplagesstables sansperdrelecturesstatus/IRQ,mémoireécriteavantévaluationligne.
IRQdates indépendantes/coldboot/imagePSGphysique restentouverts.
VidéoV319 complète localeprête,YouTube toujoursenattente accèsbrowser/visibilité.

ÉTAPE PRÉCÉDENTE : vidéo complète V319 produite enlocal, rapport
`analysis/v319_gameplay_video_report.json`, archive `analysis/v319-gameplay-video`.
Livrable `videos/v0319/golden-axe-warrior-md-v0319-gameplay-complet-ntsc.mp4`,
1564288703octets,SHA ebf049475a5f92672cd7103066e2f6c3e58c16dbd2624cfd6635936bd34aa11e.
410213frames,59.9227433977fps,960x720,stéréoAAC192k,durée6845.698s=1h54m06.
Deuxsegments :intro/titre intégral6725frames,puis403488frames campagnecontinue
NewGame→DeathAdder→générique→retourintro. 190764écrituresguardapproches,
bossnonassistés,aucunimportvie/inventaire/progression/saveétat/SRAM.
RAMfinale65536octets etPNGfinal exacts référencecampagne. Tout le fluxvidéo
lu(packet),toutaudio décodé,12aperçus issus du MP4 final inspectés,peakaudio
-12.38dBFS,pas deNaN/Inf. N’est pas une preuve de fidélitéaudioSMS complète.
Titre,descriptiontransparente,chapitres dansvideos/v0319. MP4 horsGit.
Outilsrecord/finalize/archive ajoutés ;run_core aaudio_observer optionnelpour
streamWAV,sansbuffer1.2GB enRAM. Dépendances imageio-ffmpeg danswork/video-tools
etcv2/numpy/Pillow existants. EncodeurNVENC ici lent,CPUlibx264veryfast~16x réel.
Capturesintro tronquées/probe conservéesdanspreuves,intermédiairesMP4/WAV
supprimés après vérification etarchivage desmétadonnées ;finalMP4conservé.
ENVOIYOUTUBE PENDING :chaîne @KennYMcCormick-m2b,userdit sessionconnectée.
Tentativecua.getTab renvoie 'Local browser use is disabled in Work settings'.
Aucun accèsàlasession,vérificationchaîne ouupload effectué. Ne pas contourner.
Questionasyncvisibilité ouverte(nonrépertoriée/publique/privée) etquestionpour
activeraccèsbrowser ouenvoyer soi-même. Attendre réponses pourpublication.
Modulepluginmanagement consulté :vidIQ/Metricool trouvés,pas de connecteur
YouTube direct vérifié pouruploadlongfichier ;rieninstallé/lié/publié.
Objectifportagetoujoursactif ;aprèsremisevidéo,reprendreauditdatesIRQ/coldboot,
profilage/optimisation composés etimage/son physique avant nouvelleROM.

ÉTAPE PRÉCÉDENTE : source_intro_scene_vdp.c/.h +source_intro_vdp_out,
rapport `analysis/v319_scene_live_vdp_report.json`, archive
`analysis/v319-scene-live-vdp`. Sinks pattern11T /mapBE16T dans3800..3AFF,
clear11T ;OUT valide origineelapsed/raster etcheckpointdébutinstruction.
IRQ compact callback publie regs10/9/8 viaOUTD16T/OUT(C)12T,SAT192OUTI16T,
palette32OUTI/DJNZ29T avec pollPAL/NTSC canonique. Scopeintro sans requêtes
pendingtiles/HUD/map ; autres requêtes rejetées avantpublication. Publication
partielle fatale. HorsIRQ RAM/audio reste gérée par adaptercanonique.
SourceIntroVdp status provider pilote MAINTENANT C01B dansces10vecteurs :
aucune assignation depuis queueattendue,contrôle aprèsIRQ uniquement.
244lectures et40fullIRQvideo surhôte ;20cas68000 NTSC/PAL :488lectures,
80fullIRQvideo,états15081RAM/mirror+400audio+clock/R exacts. Modulesextra
etheaders ajoutés enoption aucompileurintro générique ;maxframesdiag50000.
Snapshotinitial explicite regs/SAT/VRAM/palette ; caches/latchescold :cescas
passent,mais histoirecoldboot/titrecontinue reste àprouver. Pas de preuve
indépendante des datesIRQvideo nouvelles,niCPUbudgethelpersansoracle,niMD
physique/PCM. Les16054..19188frameskernel incluentcomparaison,setups ;PASFPS.
RebuildV319 identique ; rapportinitialdehashavait lu unéditiontemporaire
révoquée,correctionprovenance conservée :touslesinputscompilationcopiés sont
byteidentical auxsources réellementtestées/courantes. Aucun binaire modifié.
Prochain :audit datesIRQ,profilage/optimisation,coldboot,image/sonphysique.
Vidéo complète :préparer MAINTENANT enregistrement deV319publiée/parcours
validé,labelversiondéveloppement ;Youtube @KennYMcCormick-m2b,sessionsignalée
connectée,visibilité nonchoisie,pas encoreupload. Encodingoutilàpréparer.

ÉTAPE PRÉCÉDENTE : source_intro_scene_load_ports, rapport
`analysis/v319_scene_ports_report.json`, archive `analysis/v319-scene-ports`.
Nouveau point E50 identique au legacy,avec pattern_sink/pattern_user séparés
avantoutput. Le sink scene existant conserve clear/map ;sinkpattern reçoit
les OUT11T032A. Un VDP vivant DOIT posséder un miroir distinct du miroir de
sortie decoder/scene, pour ne pas voir les mutations directes trop tôt.
10scènes sourceexactes (5NTSC/5PAL),15081RAM/mirror+400audio+18clock/R,
252520OUT surhôte et244IRQ/audio natifs réels. Compilé2régions :20cas,
505040OUT et488IRQ. Chronologie des sinks foreground vérifiée ensemble.
Anciennes8452clear/map OUT/cas restent exactes enelapsedsource. PatternOUT
comparées à datesforeground originales indépendantes moins IRQ réels.
IMPORTANT :filesstatusIRQcapturées encore utilisées ; pas de statutVDPvivant
ni livraisonIRQvideo,coldbootcomplet ou rendu physique. Pas de CPUgate composé.
Rebuildcomplet identiqueV319/d3ea2a83…/DA29,pas de nouvelleROM numérotée.
Prochain :sinkVdpclear/map/pattern avec durées11T/16T correctes,IRQ/SAT/status
vivant,histoireboot,puisprofilage/optimisation etimage/son physique. Vidéo
complète demandée toujours enattente pour @KennYMcCormick-m2b (session signalée
connectée,visibilité à choisir) ; préparer après validation du step intégré.

ÉTAPE PRÉCÉDENTE : dates032A originales indépendantes et binding decoder+VDP
compilé, rapport `analysis/v319_pattern_dates_report.json`, archive
`analysis/v319-pattern-dates`. 65472OUT originaux (2assets/2régionssource),
foregroundMaster/port/value exacts,HL/DE de retour et durée foreground exacts.
Instrumentation source capture à032A/0364 et OUTBF/BE horsIRQ ; RET final150master
ajouté au point0364. Compteurs gaw_elapsed/gaw_irq_elapsed réels séparent temps
IRQ de la référence. Tous les IRQ sources restent exécutés,aucune mutationRAM.
Duréesforeground :12883290master pour9D74 et9874470pourA659. DélaisIRQ réels
capturés dansrapport, pas remplacés par moyenne. Sources cœur restaurées,
étatsPSG14000frames/région identiques à l’archive indépendante antérieure.
Binding natif decoder->SourceIntroVdp désormais compilé :48cas/785664OUT,
VRAM16KiB etclock/R exacts,6edgesIRQ/asset/régionsource,rejouésNTSC/PALMD.
Test IRQ natif reste82T/8M1 synthétique : PAS preuve des dates absolues avec
IRQ audio/SAT réel. PAS encore histoireboot/scène complète ni sortiesphysiques.
Runtimes diagnostic4188..6466frames incluent comparaisons : pas deCPUgate,
optimiser etprofiler helpersansoracle avant activation. Produit inchangé depuis
c283f6913 ; pas de nouvelleROM. Prochain : scèneclear/map/reveal+pattern
sink daté,IRQ/status/SAT réel,histoireboot,puisprofilage/vidéoPSG physique.

ÉTAPE PRÉCÉDENTE : source_pattern_decode_ports, rapport
`analysis/v319_pattern_ports_report.json`, archive `analysis/v319-pattern-ports`.
API additionnelle dans source_pattern_clock.c/.h : sink(user,elapsed,raster,
port,value) pour chaque OUT11T BF/BF/BE, sans changement des API legacy.
Plan/window/commande/repeat développent les dates exactes avant prochainIRQ ;
fallback émet après chaque S. RST28 byte :BF30T/BF45T/BE77T ;135Tliteral,
134Trepeat,carry-1T,terminalDJNZ-5T ;prefix44T,suffix16/29T. Échec sink fatal.
1054cas hôte x3modes legacy/ports/scalar sansbatch :clock/R/RAM/mirror/outputs
exacts. 2assetsintro x6phasesIRQ x2régionssource x2régionsMD =48cas68000,
785664OUT exacts. Originaltrace confirme18528port/value du premierasset par
région ; PAS encore une preuve des dates absolues OUT032A originales.
Binding decoder -> SourceIntroVdp sur hôte :24cas/392832OUT,checkpoint avant
OUT11T,write à completion,VRAM16KiB exacte. Interruption de test82T/8M1
synthétique : pas de publicationaudio/SAT réelle. Binding composite pas encore
compilé/profilé ; anciens tests68000 couvrent séparément decoder etmiroir.
Rebuild complet identiqueV319/d3ea2a83…/DA29. Pas de nouvelleROM numérotée.
Prochain : capture indépendante dates032A,compile/profile decoder+miroir,
compose map/reveal+IRQ/SAT/status avec histoireboot, puis budget physique.
Demande utilisateur en attente après cette étape : vidéo gameplay complète
jusqu’au générique,upload YouTube @KennYMcCormick-m2b ; utilisateur indique
session connectée. Accès chaîne à vérifier lorsupload ; visibilité non choisie.

ÉTAPE PRÉCÉDENTE : miroir natif source_intro_vdp.c/.h, rapport
`analysis/v319_port_mirror_report.json`, archive `analysis/v319-port-mirror`.
Own16KiB VRAM externe,16regs,32palette,adresse/latch/code/buffer,calendrier
sprites/VINT. Init SMS2 sansBIOS :reg0=36,reg1=80,reg2..6=FF,reg10=FF.
Checkpoint au début IO puis write/read à la fin. ProviderIRQ complet efface
le latch commande, sample0137-37T, checkpoint au début du IN11T. Pas de MD IO.
BE(code<3) avance/rend la nouvelle ligne AVANT la mutation VRAM ; BF n’avance
pas le calendrier avant changement de registre, sauf HScroll anticipé15master.
Redraw/parse sur écritures de registres en début de ligne, lecture VRAM avec
buffer/préfetch,CRAM et incréments reproduits. Tout échec est fatal.
Banc n’injecte PLUS de VRAM/registres source : seulement OUT/IN et tempsCPU.
8494239writes +33707status +5616VRAMreads exacts ; mémoire/protocole/regs/palette
comparés après chaque accès sur14000frames/région. ÉtatsPSG référence inchangés.
535716accès compilés,9856lectures exactes et3056lectures via providerIRQ sur68000.
Préfixes complets200périodes source par région, chacun rejoué NTSC/PAL MD.
IMPORTANT : CPU commence159*3420+990 NTSC /132*3420+990 PAL, pas192*3420.
Échec initial du noyau venait de cette mauvaise origine. Probe201frames capture
l’origine et reproduit les mêmes préfixes/hash. Code produit inchangé.
La référence ne reset pas FIFO ; utiliser une imageDLL froide séparée pour PAL,
pas importer son buffer dans le produit. Première capture rouvrait sa fenêtre
après epochwrap : capture finale ferme définitivement à200périodes, monotone.
Rejets et sources instrumentation conservés ; copiesDLL froides identiques
supprimées après vérification, baseline core conservé, sources cœur restaurées.
Les4258..5500frames du noyau incluent le rejeu diagnostic : PAS desFPS jeu ni
un budgethelper mesuré. Coût composé calendrier/ports/loader reste à optimiser
et profiler, ancien19..22frames exclut ces modules. Pas de vidéo/PCM physique.
Prochaine étape : sorties vidéo foreground/IRQ natives vers ce miroir, surtout
dates032A, ordre des instructions IO et histoireboot ; optimiser/profile avant
activation ROM. Rebuild sourcecomplet identiqueV319/d3ea2a83…/DA29. Pas deV320.

ÉTAPE PRÉCÉDENTE : calendrier natif source_intro_sprite_clock.c/.h, rapport
`analysis/v319_sprite_clock_report.json`, archive `analysis/v319-sprite-clock`.
SourceIntroSpriteClock : sprites72 +elapsed/raster/period/until_line +lines
+vint/error =92octets. Init cold-history, raster0=ligne0 (comme SourceClock),
le frameAPI de référence démarre à192*3420. Advance source-master15/T, delta
modulo32bits <=1période, déclenche render/parse pour192lignes et parse(-1)
avantligne0. VINT80 à193 ; lecture efface les drapeaux et gère le HC32
(85..93,E9..FF,00..84,20master/count,phase+545).3420phases vérifiées.
Read reçoit la fin du IN et sa longueur ; conserve le comportement de lecture
qui traverse191→blanking. Binding IRQ fourni : vérifie originesraster/elapsed,
échantillonne37T avant0137, compatible status_read compact/jeu.
Le banc référence NE fournit PLUS parse/render : seulement checkpoints CPU,
fin des IN, VRAM/registres vivants.186498983checkpoints,33707lectures complètes
exactes ; PSG14000frames/région identique à l’archive source indépendante.
58730vecteurs →117460cas68000 +6326vérifications du providerIRQ.48contrats
hôte et par région compilée : spans d’une frame/ligne, epochwrap, latches,
lecture horizontale précoce synthétique, erreur d’origineIRQ et span invalide.
Vecteurs advance-only normalisent les fractions de ligne vides ; lectures
conservent leur phase exacte. L’état vivant du test n’est jamais normalisé.
Premier stockage non normalisé a saturé : diagnostic rejeté conservé ; capture
finale complète sans saturation. Aucun patch RAM/SRAM, sources cœur restaurées.
IMPORTANT : VRAM/registres restent ceux de la référence, pas encore un miroir
écrit par les producteurs natifs. Pas de certification cadence/vidéo/PCM.
L’ancien budget19..22frames EXCLUT ce calendrier : budget composé à mesurer.
Prochaine étape : miroir ports VRAM/registres, lectures foreground, SAT IRQ
datée, dates032A et checkpoints avant/après instructions à effets visibles ;
puis mesures composées et activation d’une ROM numérotée. Rebuild V319 identique
SHA d3ea2a83…/DA29 ; pas de V320 pour ce module non sélectionné.

ÉTAPE PRÉCÉDENTE : point de raccordement du statut dans SourceIrqContext,
rapport `analysis/v319_irq_status_binding_report.json`, archive
`analysis/v319-irq-status-binding`. Champs optionnels status_read/status_context
ajoutés en fin de contexte ; signature commune SourceIrqStatusRead, alias
SourceGameStatusRead. Provider reçoit l’entrée0137 : IN terminé37T plus tôt,
modulo période. Écrit C01B avant full/video/audio, y compris audio-only.
Sans provider, C01B reste fourni par l’appelant. Refus →804, work nul, aucune
publication vidéo/PSG ni mutation RAM/audio ; échec fatal, ne pas réessayer.
Les quatre adapters partagent source_irq_context.c (base/timed/fast/master).
384cas hôte +768 exécutions68000 NTSC/PAL passent (full/audio-only,20/40,
262/313lignes,epoch normal/wrap,off/on/refus). Modèle sprites réellement appelé
mais latches initialisés par le test : PAS encore de producteur VRAM/raster
vivant connecté. La reconstruction complète est identique V319/DA29 : voir
`analysis/v319_irq_status_rebuild_report.json`, archive
`analysis/v319-irq-status-rebuild`. Pas de nouvelle ROM numérotée.

ÉTAPE PRÉCÉDENTE : modèle temporel natif des statuts sprites, rapport
`analysis/v319_chip_temporal_report.json`, archive `analysis/v319-chip-temporal`.
Module `source_intro_sprite_status.c/.h` : caches de deux lignes, collision20,
débordement40 en attente, lecture avec remise à zéro et report horizontal.
33707 lectures source +27986 statuts IRQ exacts ;33179 transitions distinctes
→66358 exécutions68000 NTSC/PAL sans écart. La VRAM/les registres/les événements
viennent encore de la référence : PAS de raccordement producteur natif achevé,
PAS de suppression des files de statuts attendus des anciens bancs de scènes.
La branche de lecture précoce sur la ligne de collision n’est pas couverte par
le corpus naturel. Rebuild publié identiqueV319, pas deV320 pour ce seul module.
Prochaine étape : alimentation par VRAM/SourceClock natifs, lectures foreground
et IRQ, histoire des caches dès le boot ; réutiliser status_read et SAT datée
de source_game_irq lorsque possible. Ensuite livraison vidéo/PSG physique.
Erratum :9F/BF diffèrent par collision20, PAS overflow40 ; anciennes données
numériques intactes. Voir `analysis/v319_sprite_status_erratum.json`.

ÉTAPE PRÉCÉDENTE : optimisation source_intro_video/scene/map et plans032A,
rapport `analysis/v319_intro_runs_report.json`, archive `analysis/v319-intro-runs`.
GATE CPU DU HELPER OBSERVÉ SATISFAIT pour les10cas source/région correspondante,
avec1frame ajoutée par prudence à la mesure. Ce n’est PAS une preuve de
livraison vidéo/PSG réelle ni une certification du jeu sur matériel.
NTSCsame-region :98..99 ->19..22framesMD,source24.27..26.95 ;PAL81..83 ->
15..18,source21.48..22.96. Marge minimale conservative1.31frameNTSC et
2.48PAL. Le reste du budget devra absorber sortiesMD et statutVDP vivant.

SourceIntroVideoRun nouveau :kindCLEAR/TRANSFER,elapsed/raster/period,
address/count,constbytes. run_sink optionnel ajouté APRÈS out_sink dans
prepare/transfer/clear (puis sink_user,output). Legacy appelle run_sink=0.
CLEAR décrit3OUT/byte offsets30/45/101T,espacement124T ; dernier119T même
outputs. TRANSFER décritOUTBE16T,espacement32T. Descripteurs seulement
avantpossibleIRQ ; appliquer les effets vidéo avant retour. Les bytes de
transfert sont un pointeurRAM vivant : COPIER ou garantir sa durée de vie
si livraison physique différée. Aucune avanceClock/mutationRAM par sink.

SceneRun applique les fills/memcpy rapides quand aucun observateurOUT.
Avecobservateur, développe par scene_out, chaque écriture voit le miroir
au bon état intermédiaire. Chemins comparés aux mêmes états/horloge/VRAM
source. Ne pas extrapoler une visibilité GPU par ligne depuis le seul
miroir final : futur statutVDP doit consommer les temps de ces runs.

Optimisations additionnelles :OUTI/NOP/JR nonterminal32T/4M1 ;LDIR forward
21T/2M1 jusqu’àIRQ/dernier16T, pas memcpy avec chevauchementD600/D602.
7357 LDI/DJNZ29T/3M1 nonterminal copie disjointe. BD3 commandes complètes
literal52+39N,increment58+30N ;BFE literal52+57N-carries,repeat51+51N-carries,
avecM1exacts. Seulement source_clock_block stable avantVINT, chemins
instruction conservés aux frontières. Profil mapdecode10 ->1..2framesNTSC,
clear31..32 ->2..3,place5 ->1 ;prepare4..7,patterns4..7,transfer2..5.

Plans intro immuables générés par tools/generate_intro_pattern_plans.py,
header source_intro_pattern_plans_generated.h,rapport
analysis/intro_pattern_plan_assets_report.json. Flux9D74/A659 bank6,
chaquecommande comparée à Trace/pattern_rle. Prefixes T/M1 etdataROM,
pas de phases/frames capturées. Plans valides pour adresseVDP4000/alignment
original ; ne pas réutiliser leurs coûts pour une autre base de page.
source_pattern_decode_planned accepte plan ouNULL ;fonctionordinaire reste.
HeadergénéréSHAépinglé dans rapports etbuilderprofile. Fichierspattern_clock
C/H normalisésLF lors de l’ajout de l’API,codecommun validé par rebuild.

Work final scene-runs04,profile scene-throughput05,map-runs01(bank7reg).
10vecteursE50,20exécutions68000,84520OUTmonitoredsource/169040compilés ;
états15081bytes+400reader,horloge etmiroirs exacts. Regressionsprepare14,
clear14,transfer28,mapdecode14vecteurs avec2régionscibles, toutes passent.
Prototypes intermédiairesruns01..03/throughput03..04/place-runs01 archivés.
Revalidate scripts all/final/budget conservés ;ne pas relancer dans dossiers
existants gelés. build_v319_intro_scene_profile.py réutilisable en nouveauwork.

Handles53819/64834/90974/32423/99086/80234/95497/53291/74344/30144/66453
terminaux0. Rebuild03 exactV319 d3ea2a83/DA29 ;ROMpublique inchangée.
Archive relue :134496634bytes générés supprimés,94805973netslibérés.
Aucune nouvelle ROM : nouveaux modules restent non sélectionnés.

PROCHAINE PRIORITÉ : lier statutVDP des sprites vivant et mémoirecompacte,
puis sortiesvidéo/PSG aux vrais délaisMD. Définir amorçage de SourceClock
sans importer d’état source ni phases de frames enregistrées. Réutiliser
SourceIrqContext.video pour effetsIRQ nécessaires. Patterns032A n’exposent
pas encore OUTindividuels ; considérer leurs temps pour statutGPUparligne.
Tester l’intro visible et les deadlines en exécution réelle avant V320.
Les paragraphes suivants sont historiques,notamment anciengapCPU désormaisréduit.

DERNIÈRE ÉTAPE : `source_intro_scene.c/.h`, rapport
`analysis/v319_intro_scene_report.json`, archive `analysis/v319-intro-scene`.
Composition E50..E72 en un SourceClock :setDCEC,EA5,032A,E2B,BD3/BFE,
7357,EFA, sortie E75 préfetch (avant LD D7F). API reçoit HLheader/DEtarget,
miroir16KiB SMS,dispatch callback vivant et sinkoptionnel. SceneMirror
met à jour commandes/adresse VDP pour OUTclear/map ;032A écrit directement
lespatterns. Pas de publication MD ni de replay de frames source.

10entrées naturelles(5/région),14000frames source/région,20exécutions68000.
Tous15081bytes suivis incluant9216patterns+768nametable,400reader,clock/R/
latches et84520 OUTmonitored identiques.169040comparaisonsOUT compilées.
OUTcollector couvreclear+map, PAS OUT032A individuels ; finalpatterns exacts.
Headers9D70/F37 etA655/1055. IRQsource27/25NTSC,23/22PAL. Durées source
24.27..26.95framesNTSC,21.48..22.96PAL. RegistresfinHL D900,DE7800,BC00BE.

PROBLÈME À RÉSOUDRE AVANT INTÉGRATION : coûtCPU natif tropgrand. Profil sans
oracleOUT et horscopiesfixtures/comparaisons, vtimer mesuré DANS helper :
avant124..125framescibleNTSC,103..105PAL ;aprèsoptim97..99NTSC,81..83PAL.
Environ20% gagné, encore~4fois la durée source. Ces temps excluent les IO
physiquesMD et sont donc optimistes. Résolution1frame, instrumentationlégère.
Étapes aprèsoptNTSC :prepare23..26,patterns6..9,clear31..32,decode10..11,
place4..5,finaltransfer19..21. Priorité suivante clear/transfers puisLDIRprepare,
pas une intégration lente ni un calibrage artificiel des compteurs source.

Optimisation source_intro_map.c :1er étage literal39T/5M1,increment30T/4M1
nonterminal ;2e literal57T/8M1,repeat51T/7M1 noncarry/nonterminal. Coupe
avantcarry de l’octet bas et avantVINT via source_clock_repeat. Commit RAM
avantfrontièreIRQ suivante. Sourcepathinstruction resteauxlimites.
Rétgression14vecteurs mapdecode bank6/bank7,28exécutions68000 passent aussi.
Premierhostbuild a rejeté warning value possiblementnoninit, initexplicite0
sans suppressionwarnings puis tous les vecteurs passent.

Works finauxscene03,mapdecode05,scene-throughput02 ;baseline scene01 et
scene-throughput01 conservés avecsource préoptim de rebuild01. Nouveau
build_v319_intro_scene_profile.py --source-work --out-name produit un profil
reproductible, épingle SHA sources, désactive seulement l’oracleOUT, conserve
miroir/calculs etcomparetoutétatfinal. Compilateur ajoute wrappers deprofil
uniquement au diagnostic (macros aprèsheaders), aucunemodifsourceproduction.
Six étapes prepare,patterns,clear,decode,place,finaltransfer. Profils mesurent
vtimer autourappels, pas le nombre de frames du banc entier.

Builder/validator --profile callback --scene implique layoutmapdecode,
appelle source_intro_scene_load. Snapshot15488,extra14680 ; RAM5032..14247
patterns,14248..15015nametable,15016IRQcount puis64statuses. Recordstride98864,
events àsnapshot*2+268,8452monitoredOUT/call. Cap512records. CibleRAMfixture15K,
full_ram8K,miroir16K,leskernels passent. StatutVDP resteinputdiagnostic.

Handles20817/26708/14754/79239/18585 terminaux0. Rebuild02 sourceexacte,
byte-identiqueV319 d3ea2a83/DA29. Archive relue :75544902bytes générés
supprimés,50824811netslibérés. ROMpublique inchangée ; helpersnon sélectionnés.
AprèsoptimCPU : liermémoirecompacte/statutVDPdespritesvivants, livraison
vidéo/PSG réelle et vérifierdeadlines. EntréesE3F/E4A,révélationE75 etskip
ne sont pas dans ce profil de chargement. Paragraphes suivants historiques.

DERNIÈRE ÉTAPE : source_intro_plane_clear dans source_intro_video.c/.h,
rapport `analysis/v319_intro_clear_report.json`, archive `analysis/v319-intro-clear`.
E2B..E3E : PUSH HL/LDDE4003,2304boucles RST28 DI/EI,4INCDE,OUTBE FF,
CP64/JRC puis POPHL/RET/checkpoint. Sink reçoit les3OUT horodatés par byte.
14vecteurs naturels (7/région),tousavecIRQ,96768OUT source vérifiés.
2025octets suivis+400reader,wall/IRQ/R/latches identiques. Foreground exact
285732T/39172M1. Toutes entrées compilées sur68000 NTSC+PAL :28exécutions,
193536OUT vérifiés,zéro erreur. Rebuild02 source exacte byte-identiqueV319.

Optimisation :source_clock_repeat124T/17M1 pour boucles JRtaken, dernier119T.
Regroupe plusieurs boucles jusqu’àVINT seulement,aucun pending/first/EI.
OUT offsets30/45/101T, data FF. Sans sink, avance aussi compte/adresse sans
IO. Avec sink, publie chaque event avant prochaine frontière IRQ, ordre exact.
Sinon chemininstruction DI/EI complet. Prototype lent conservé avec source
SHA vérifiée contre rebuild01. Kernel14vecteurs passe de3428/2869frames à
1176/985 NTSC/PAL ; débit du banc avec oracle, PAS vitesse du jeu.

Builder/validator --profile callback --clear implique le layout transfer,
mais appelle uniquement clear. Snapshot2432,recordstride60432 (6912events
au lieu770),events à snapshot*2+268,64statusesIRQ etmapsnapD600 conservés.
Workclear02 final ;clear01 prototype lent valide. Z80source restaurée.
Handles37070/21239/69063 terminaux0. Archive relue :43088352 octets générés
supprimés,25585991nets libérés. Aucun nouveau numéro ROM, helpernon sélectionné.

PROCHAINE ÉTAPE prioritaire : composer E50..E75, entrée HLheader/DEcallback,
avec EA5,032A(source_pattern_decode),E2B,BD3/BFE,7357,EFA. E75 est avant
LD D7F ; ne pas inclure le dévoilement déjà validé dans ce premier profil.
Source_pattern_decode écrit un miroir pattern et RAMC031/C032, ne fournit
pas les OUT individuels. Comparer aussi le miroir source final :patterns
0000..23FF etmap3800..3AFF. Collector OUT clear+map couvre8452events par
chargement complet (2*770+6912), pas touslesOUT RLE032A. Ne pas prétendre
avoir prouvé les timestamps pattern individuels si non capturés.

Piste layout diagnostic si utile : extra4696 ancienlayoutmap +9216patterns
+768nametable =14680, snapshot15488 ; RAM15016+65statuses=15081. Static
full_ram8K+patternmirror16K etramfixture15K devront tenir dans64K cible.
Attach IRQ video si nécessaire : ne pas supposer que le miroir n’est jamais
modifié par IRQ ; la comparaison source doit trancher. Le sink de composition
pourrait maintenir commande VDP/adresse etmiroir, puis déléguer les events.
Après preuve de composition : mémoirecompacte/statutVDPspritevivant et
publication MD avecdeadlines. Les paragraphs suivants sont historiques.

DERNIÈRE ÉTAPE : `source_intro_map.c/.h`, rapport
`analysis/v319_intro_map_report.json`, archive `analysis/v319-intro-map`.
source_intro_map_decode :BD3 literal/increment vers scratchD100..D5FF,
BFE literal/repeated en deux plans intercalés versC900..CFFF, RET/checkpoint.
Prend explicitement un const u8 *map_bank (fenêtre ROM16KiB courante),
indépendant du context->bank6 réservé au lecteur audio. Données observées
bank6:A598/AE6F et bank7:A886. Ce dernier décode1278bytes, les autres576.
source_intro_map_place :7357 strided rows,contrat intro sourceC900..CFFF,
48bytes*12rows versD608, stride64. OutputHL CB40,DE D908,BC3000.
API rejette largeur0 ou>64 et hauteur0 ; pas de preuve générique zéro.

7décode+7placement par région sur14000frames sans input :28vecteurs,
13avecIRQ et15sans. Tous5097octets suivis+400reader,HL/DE/BC,wall/IRQ/R/
latches identiques. Décode scratchcounts281/242/728, placements576bytes.
Tous vecteurs compilés sur NTSC+PAL :56exécutions,zéro erreur. Pas de IO
avant-plan dans ces helpers ; la livraison VDP est toujours distincte.
Rebuild source exacte byte-identique V319 d3ea2a83/DA29,aucune nouvelle ROM.

Incidents rejetés :premier BFE repeat avait remonté LD A,(HL) hors boucle ;
source le relit à chaque octet. Wall/R rejetaient, correction lecture7T
parbyte. Puis bank7 observée :pointeur ROM explicite à la place de bank6
fixe. Placement sansIRQ a corrigé une précondition trop stricte du harness.
Toutes captures finales incluent les bytes de RAM suivis sans exclusions.
Observer2 filtre seulement les contrats intro :BD3 DE=C900 ;7357 HL=C900,
DE=D608,BC=300C. Observer1 antérieur nonfiltré conservé mais pas utilisé.

Builder/validator --profile callback --map decode|place --observer-revision2
(ce dernier seulement validator), implique layout transfer/sequence, pas
leurs appels natifs. Nouveau module source_intro_map compilé dans kernels.
Snapshot5504,extra4696 ; inputRAM1192..1959=D600 map,1960..3239=D100scratch,
3240..5031=C900 decoded,5032 IRQcount/5033..5096statuses. HL1184/85,
DE1186/87,BC1188/89. Events record à snapshot*2+268, stride17440, mais
countIO=0. Kernel utilise un tableau events d’au moins1mot pour zéroIO.
Work finaux mapdecode03/mapplace03. Prose héritée EFA corrigée au gel.

Handles80466/86687/16998/63537/39618 terminaux ; derniers lots terminaux0.
Archive relue :34652365octets générés supprimés,25246550nets libérés.
Prochaine étape :0E2B plane clear, puis composer E50..E75 avec032A existant,
EA5,BD3/BFE,7357 etEFA. Ensuite mémoire compacte/statut sprite vivant et
publication MD avec deadlines ; helpers nouveaux toujours non sélectionnés.
Les paragraphes suivants décrivent les étapes précédentes.

DERNIÈRE ÉTAPE : `source_intro_video.c/.h`, rapport
`analysis/v319_intro_transfer_report.json`, archive `analysis/v319-intro-transfer`.
source_intro_map_transfer modélise EFA : CALL F1E, LD HL D600/DE7800/BC0300,
CALL384 (RST28 DI/EI/OUT adresse,768 OUTI avec NOP/JR/DEC exacts), puis
FALLTHROUGH F09 pour une deuxième attente/callback avant le vrai RET.
Ne pas traiter F06 CALL384 comme fin de EFA : il n’y a pas de RET ici.
source_intro_map_prepare modélise EA5..ED3 : remplissage D600..D8FF par
FA09, EFA complet, zéro16 palettes, mapper6,4 couleurs depuis HL ROM restauré.
SourceIntroMapOutput :writes,palette_end,skip. full_ram/live aliases requis.
Même callback dispatch vivant DCEC et sink sémantique elapsed/raster/port.

EFA :14 source NTSC+14 PAL ; EA5 :7+7, soit42 vecteurs d’entrée (profils
imbriqués distincts), tous avec IRQ. EFA3IRQ, EA5 3ou4. Chaque invocation
émet770 OUT dont768dataBE,32 340 OUT source en tout, tous comparés avec
temps et raster dérivé.2025 octets suivis+400 reader, wall/IRQ/R/latches
identiques. EA5 vérifie map FA09,clear16palette et4 couleurs originales
aux adresses9D70/A655/AF1F. Callbacks F36/F37/1055 observés.
Tous vecteurs compilés sur les deux régions :84 exécutions,64 680 OUT,
zéro erreur. Aucun skip n’est prouvé dans ces nouveaux profils d’entrée.

Builder/validator --profile callback --transfer ou --prepare. --prepare
implique --transfer/--sequence/--reveal pour réutiliser le layout et dispatch,
pas pour appeler le dévoilement. Noms observers hérités intro-intro_transfer
et intro-intro_prepare. Snapshot2432, extra1624, map768 à extra856,
soit inputRAM1192..1959 ; IRQcount1960,valeurs1961..2024 (64 slots).
Prepare capture HL à inputRAM1184/1185 avant/après ; transfer pas de regs.
Events à snapshot*2+268,recordstride11296,cap512.770events parappel.
Output[12]events770,[13]writes768. Module source_intro_video inclus au kernel.

Derniers works transfer03/prepare02. Erreur préprocesseur tokenhex0x15fe+n
au premier append EA5 corrigée avec espace, aucun résultat accepté avant
correction. Transfert seul antérieur transfer01 était déjà exact ; gardé
avec rebuild01/sources. Handles39689/61307/67754/9870/96513 terminaux0.
Rebuild02 source finale exacte,byte-identique V319 d3ea2a83/DA29.
Archive relue :44541475 octets générés supprimés,29662215 nets libérés.
Pas de nouvelle ROM publique : les helpers restent non sélectionnés.

Prochaine étape : composition E50..E75 avec EA5/EFA, réutiliser
source_pattern_decode pour032A ; traduire0E2B,0BD3/0BFE et7357 si nécessaire.
Puis plan mémoire compact,statut VDP des sprites vivants et publication MD
avec deadlines. Les queues de statut source restent réservées au diagnostic.
Les paragraphes suivants décrivent les étapes précédentes.

DERNIÈRE ÉTAPE : oracle de skip composé, rapport
`analysis/v319_intro_skip_report.json`, archive `analysis/v319-intro-skip`.
Aucun changement du code public natif : la branche skip déjà présente dans
source_intro_reveal_sequence est maintenant confrontée à l’original.
84 scénarios normaux de manette :2 boutons libretro0/8,3 callbacks vivants
F36/F37/1055,7 seuils de progression,2 régions.84 sorties D0B après0..6
passes. Chaque essai observé rejoué dans le core PSG source indépendant,
mêmes appuis sur les mêmes frames ;154280 frames d’états PSG identiques.
Aucune écriture RAM/importSRAM source. Ce n’est pas une comparaison PCM.

Entrée E79, sortie préfetch EA4 ou D0B. Scope ne comprend PAS LD SP/RET D0B
ni le nettoyage/affichage titre. Joy source capturé après IN DC au01BC,
associé à l’entrée IRQ0137 correspondante. Audio-only IRQ ne lit pas joy.
Le diagnostic lie ces entrées joy/statut à chaque IRQ native, sans replay
de frames dans la production. Tous1321 octets suivis+400reader,clock/R/
latches et les OUT précédant la sortie correspondent à l’original.

88 vecteurs conservés :42 skips+2 préfixes complets par région. Déduplication
retire seulement les origines absolues master/IRQ du KEY ; conserve les
records source représentatifs et les durées mesurées inchangés. Les84
invocations originales par région sont archivées aussi (work skip02).
Work finalskip03 :1963008 OUT source,22 kernels de4 cas,176 exécutions
68000 et3926016 comparaisons OUT, toutes passent. Fin script affiche88
(correction du texte hérité14, les compteurs structurés étaient déjà88).

Builder/validator --profile callback --skip ; implique --sequence/--reveal.
Capture helper capture_v319_intro_skip.py pilote les boutons via getters
read-only, puis rejoue dans genesis_plus_gx_v319_psg_writes_libretro.dll
SHA épinglé. --capture-work réutilise captures terminales après vérification
SHA des records/PSG et résultats du rejeu. Events variables : kernel utilise
le maximum de longueur du lot, configure le compte réel par cas, y compris0.
Snapshot1664, stride446224 ; events à snapshot*2+524 ; entréeRAM1192,
statut count+64 bytes jusqu’à1256,64 joybytes1257..1320. Output[16]skip.

Tous handles6867/12545/15017/14811 terminaux0. Archive relue :593346062
bytes générés supprimés,443608615 nets libérés. Ancien skip01 a seulement
échoué sur le nom du rapport build référence (report vs build-report),
aucune capture acceptée. La prose héritée no-input de skip02 est corrigée
avant gel, résultats numériques/captures inchangés. Public V319 d3ea2a83
inchangé ; aucun rebuild de jeu nécessaire pour ces seuls diagnostics.

Prochaine étape : setup E50..E75 (réutiliser source_pattern_decode pour032A),
fonctions EA5/EFA/0E2B et0BD3/7357 si nécessaire ; puis plan mémoire et statut
VDP des sprites vivants avant intégration/publication MD avec deadlines.
D0B ne fait que LD SP,(C02A)/RET ; suivre le vrai appelant pour son nettoyage.
Les nouveaux helpers ne pilotent toujours pas l’intro publiée.
Les paragraphes suivants décrivent les étapes précédentes.

DERNIÈRE ÉTAPE : source_intro_reveal_sequence dans source_intro_reveal.c/.h,
rapport `analysis/v319_intro_sequence_report.json`, archive
`analysis/v319-intro-sequence`. Composition E79..EA2, sortie EA4 préfetch
(RET non inclus), même SourceClock pour setup registres alternatifs,
rotations E, F1E/callback courant, passe E8B et SRL D/JR carry.
Le masque D=7F produit HUIT passes : sept carry-set puis une à D=0.
Ceci corrige les mentions anciennes de sept passages dans les notes.

14 séquences naturelles complètes :7 NTSC+7 PAL,14000 frames source/région.
Chacune traverse40 IRQ,55296 OUT,18432 écritures de plan,8 passes.
Tous774144 OUT comparés (port/valeur/temps fin instruction/raster dérivé),
1257 octets suivis+400 reader, durée totale/IRQ/R/latches identiques.
Dispatch du diagnostic lit DCEC vivant, sélectionne F36/F37/1055 observés ;
104A supporté mais absent de ce profil. Pas de replay de timings de frames.
Tous14 vecteurs compilés en4 kernels de4/4/4/2cas, chacun NTSC+PAL :
28 exécutions et1548288 comparaisons OUT, zéro erreur.
Les entrées statut VDP source restent explicites à chaque0137 ; à remplacer
par le calcul vivant avant production, jamais par des enregistrements.

API source_intro_reveal_sequence(clock,ctx,mask,callback,callback_user,
sink,sink_user,output). Output contient last,passes,writes,mask,skip.
Skip sort D0B via F1E, mais aucun cas skip n’est prouvé dans ce profil.
Le code couvre le terminal de boucle, pas E50..E75/setup, ni EA4 RET.
--sequence sur builder/validator implique --reveal et layout acteurs ;
aucun callback fixe. Snapshot1664, extra856 dont index848=D, statut IRQ
count+64 valeurs : entréeRAM1192 puis65bytes statut,
soit1257bytes totaux. D à inputRAM1184, statut count1192, valeurs1193.
Events record à snapshot*2+268, stride445968, cap32records. Output[12]
compte OUT55296, [13]passes8, [14]writes18432, [15]mask0.
compileur kernel déduit longueur des tableaux events depuis les fixtures.

Processus78967(all) et32863(rebuild) terminaux0. ROM rebuild01 source exacte,
byte-identique V319 d3ea2a83/DA29 ; aucune nouvelle ROM publique.
Archive relue :67879504 octets générés supprimés,31762021 nets libérés.
Prochaine étape : oracle du skip composé, setup E50..E75 selon besoin,
plan mémoire compact, statut VDP vivant puis publication MD avec deadlines.
Les helpers ne pilotent toujours pas l’intro publiée. Notes suivantes historiques.

DERNIÈRE ÉTAPE : `source_intro_reveal.c/.h`, rapport
`analysis/v319_intro_reveal_report.json`, archive `analysis/v319-intro-reveal`.
API source_intro_reveal_pass(clock,context,state,sink,user), E8B..E9D,
sortie EA0 préfetch. state.address=HL alternatif, step=DE alternatif,
value=E principal. Chaque passe écrit2304 octets de plan,6912 OUT BF/BE.
Sink reçoit elapsed/raster/port/value à la fin sémantique de l’instruction ;
il ne doit ni modifier RAM sémantique ni avancer clock/injecter IRQ.
Ce n’est pas un scheduler de publication sur le VDP MD.

112 vecteurs naturels (56/région) sur14000 frames sans entrée, tous avec IRQ.
774144 OUT capturés, tous comparés sans hash de substitution : port, valeur,
temps de fin d’instruction et raster dérivé. Origine source = observation
entrée instruction +12T pour OUT, pas une mesure de bus matériel.
1193 octets suivis+400 reader, durée totale/IRQ/R/latches identiques.
Tous112 vecteurs compilés,5 kernels bornés24 cas, chacun NTSC+PAL :
224 exécutions,1548288 comparaisons OUT, zéro erreur. Dernier work reveal05.
Source statut VDP à chaque0137 reste une entrée diagnostic explicite,
pas une solution de statut dynamique pour la production.

Optimisation : boucle100T/18M1 regroupée via source_clock_repeat seulement
sans first/EI/pending et avant frontière VINT. Sinon instructions individuelles
DI/EI/OUT/rotations. Écritures regroupées horodatées20T,32T,83T, vérifiées
individuellement contre source. Ancien modèle lent exact conservé (source
reconstruite avec SHA identique au rapport reveal03). Ne pas assimiler le
nombre de frames des kernels avec oracle au débit réel du jeu.

Incidents rejetés : warning signé/non signé au host ; offset des events
lu4 octets trop loin (padding de fin de struct confondu avec son contenu).
Observer corrigé et read-only, source émulateur restaurée. Dans ces outils,
--reveal implique le layout acteurs seulement ; aucun callback1055 appelé.
Le champ polls du record et output[12] comptent alors les OUT, pas les IN.
Les events commencent snapshot*2+44, stride total58656. 128 records max.
Builder accepts --profile callback --reveal ; validator idem. Le compileur
utilise events ROM sans gros buffer RAM, partitions requises sous2MiB.

Tous processus terminaux :22020(all),9349(rebuild),93915(provisoire).
Rebuild source exact byte-identique V319 d3ea2a83/DA29. Aucune nouvelle ROM.
Archive relue :114765009 octets générés supprimés,71793238 nets libérés.
Prochaine étape : composition F1E+pass puis SRL D/JR de sept passages,
setup/transfert vidéo selon besoin, plan mémoire compact et statut sprite
vivant avant intégration. Les nouveaux helpers restent non sélectionnés.
Les notes suivantes sont les étapes précédentes.

DERNIÈRE ÉTAPE : initialisation F51/F54 ajoutée à source_intro_actors.c/.h,
rapport `analysis/v319_intro_init_report.json`, archive `analysis/v319-intro-init`.
API source_intro_actors_initialize(clock, context, data, template_address,
entry_f51) inclut le RET et le checkpoint préfetch. F51 charge F95 ; F54
utilise le HL source fourni. DCE2=0, 768 octets C300..C5FF effacés à chaque
frontière LDIR, templates six octets vers records de48, neuf/six acteurs.
SourceClock/instructions natifs, aucune interprétation Z80.

Deux entrées F51 et quatre F54 par région sur14000 frames naturelles :
12 vecteurs d’entrée (F54 inclut aussi le suffixe commun de F51), puis
24 exécutions 68000 compilées dans les deux régions, zéro erreur.
1193 octets suivis +400 reader, durée/raster/R/latches identiques.
Ces appels naturels ne traversent AUCUNE IRQ : ne pas étendre cette preuve
aux initialisations interrompues ou au skip. Le harness accepte --init
avec --actors second|third --profile callback. phase[4] transporte alors
HL source, pas vc_max ; output polls reste0. Capture poll brute contient
HL dans ce profil uniquement. F51 ignore ce HL et charge F95.

Incidents retenus : assertion diagnostic IRQ>0 corrigée pour ce profil ;
checkpoint final initialement absent rejeté par delta R=1 malgré durée
exacte. Versions provisoires archivées. Derniers profils second05/third04,
compilation des deux kernels terminal0 ; rebuild02 terminal0, source exacte
et ROM byte-identique V319 d3ea2a83/DA29. Aucun nouveau numéro public.
Archive relue, 57 802 240 octets générés supprimés, 43 840 581 nets libérés.
Ne pas relancer les handles18561/62071/98844/56905, tous terminaux.

Prochaine étape : E8B..E9D dévoilement et composition F1E, puis plan mémoire
compact, statut VDP depuis les sprites vivants et deadlines vidéo/PSG.
Ces helpers ne sont toujours pas sélectionnés dans l’intro publiée.
Les sections suivantes sont les étapes précédentes, pas l’état courant.

DERNIER CODE NATIF : `source_intro_actors.h/.c`, rapport
`analysis/v319_intro_actors_report.json`, archive `analysis/v319-intro-actors`.
Callbacks 1055/104A, scan 1061, activation/poses 108B, lookup RST08,
listes SAT A60/A78/0978 et palette éclair BE25 traduits avec SourceClock.
6992 vecteurs source scène 2 + 7712 scène 3 = 14704, tous avec IRQ.
29408 exécutions compilées 68000 sur les deux régions passent, tous les
états suivis comparés sans exclusion. Aucun changement de ROM publique :
recompilation complète byte-identique V319 d3ea2a83/DA29.

Attention : scène 3, C01B prend 9F/BF selon collision sprite source (bit20 ; erratum ci-dessus).
Le diagnostic reçoit ce statut indépendant à chaque entrée IRQ 0137,
puis délègue au modèle IRQ natif inchangé. Ce n’est pas un replay autorisé
en production : calculer ce statut depuis les sprites vivants avant
intégration. full_ram 8K est un backing diagnostic, pas le plan mémoire final.
Initialisation F51/F54 et dévoilement E8B..E9D pas encore traduits/validés.
Prochaine étape : F51/F54 avec oracle source, puis composition F1E,
plan mémoire compact et deadlines vidéo/PSG. Ne pas intégrer les helpers
isolés à l’aveugle : la fidélité finale reste à démontrer dans le jeu.

Tous les lots sont terminaux. Incidents conservés : C01B externe absent,
puis queue diagnostic non initialisée, tous deux rejetés avant correction.
Un kernel a échoué au lien LTO (chemin temporaire MSYS) : mêmes objets
reliés avec -flto=1, recette/log conservés, exécution ensuite validée.
compile_v319_intro_actors_all.py gère partitions et reprise ; le compilateur
ne relance en série que ce motif précis d’échec terminal. Ne pas relancer
les anciens handles 19373/61905/17802/76108/28193.
Archive terminée, 1791 fichiers générés supprimés après relecture vérifiée,
vecteurs/kernels restaurables ; scripts et sources conservés.

Les paragraphes suivants décrivent les étapes précédentes.

DERNIER CODE NATIF : `source_intro_fire.h/.c`, rapport
`analysis/v319_intro_fire_report.json`, archive `analysis/v319-intro-fire`.
F37..F4E etbank5BDFF..BE12 traduits surSourceClock :retourrapide clock&7,
banque5,INC compteurbyteDCE2/CP6/JRC/XOR,3LDI deBE13 versDCA1..DCA3,
RET. Signature SourceIntroCallback,user pointe18octetsBE13(table ROM).
ctx.full_ram requis pour palette/compteur/mapper via source_room_get/put.
Aucune écriture IO/hardware, seulement sémantique native et temps source.
Intégration au jeu publiée NON sélectionnée ; sources recompilées finales
byte-identiques V319 d3ea2a83/DA29. Aucun nouveau numéro de ROM public.

Oracle source original sans écriture RAM/ROM :F09/F37 3533NTSC+3566PAL,
F1E/F37 30NTSC+30PAL, soit7159 cas, tous traversantIRQ. Snapshots incluent
336RAMIRQ+400reader et80octets de palette/counter/mapper/target (padding
inclus). Source exactement durée/raster/workIRQ/R/IFF/EI/pending/états et
polls. CallbackF37 sélectionné par DCECsource, pas fixé surune frame.
Compteurs retenus observés0..5 et225NTSC/227PAL ;441/445changements
palette/counter dansF09,75retoursà0 chaque région. Tous vecteurs compilés
68000 :8kernels F09 de900max sous2MiB +1kernel60F1E, chacun dansles2
régions cibles,14318exécutions,0erreur. Ce sont des kernels sémantiques,
pas une preuve de deadlines de publication vidéo/PSG dans le jeu.

Incidents conservés :premierharness host `<string.h>` résolu versSGDK et
rejeté ; utiliser__builtin_memset, pas le headerSGDK surhost. PremierDLL
window lié avec ancienobjetcallback (planmake ne recompilaitpas z80.c,
timestamp trop proche). Assertion PCF1E a REJETÉ ses captures ; aucunpass
report pourwindow02. Nouveauwindowobserver02+D L Lsuffixr02 :force-source
core/z80/z80.c. tools/build_timing_core.py a maintenant --force-source
(make-W, chemin validé souswork/genesis-plus-gx) ; builderempty/fire l'utilise.
Ne pas invoquer deux builds modifiant la même source émulateur en parallèle.
La sourcez80.c est restauréeenfinally etSHAvérifié. PSGsource28kframes par
profil identiqueaux anciennescaptures ; pas de DLLémulateur distribué.

Tousprocessus terminal0 après corrections ; aucun handleàattendre. Archives
relues :1286références,129979484octets générés supprimés,112167663nets
libérés. Sources gardées, vecteurs et kernelsrestaurables depuisgzip.
Scripts validate_v319_intro_poll.py accepte--fire et--observer-revision ;
build_v319_intro_empty_observer.py accepte--fire,--revision ;
compile_v319_intro_poll_68k.py acceptepartitionscase-start/count etRAM416,
fixeTMPDIR/TMP/TEMP='.' uniquementdanssonprocessusbuild ;
compile_v319_intro_fire_all.py,archive_v319_intro_fire.py versionnés.

Prochaine étape :callbacks1055/104A/1061/108B acteurs/SAT, distincts du
fire ;capturerétatC300..C5FF etDD40/DD80 en pluspalette/clock, modéliser
instructions/retours viaSourceClock. Branche skipD0B surentrée normale
resteouverte. PuiscopieE8B..E9D etpublicationraster nativeavecdeadlines.
Ne pas remplacer ces modèles par un worktotalmoyen ou des overridesframes.

DERNIÈRE PREUVE : `analysis/v319_intro_empty_report.json`, archive
`analysis/v319-intro-empty`. API source_intro_wait_callback et window
vérifiées DIRECTEMENT sur captures naturelles source DCEC=0F36, donc
callbackvide F36RET seulement. F09retourappelant :986NTSC+994PAL cas.
F1Eattentecomplèteretourappelant :36NTSC+36PAL cas,32705+40288 lecturesVC.
Toutes2052captures traversent au moins uneIRQ. Durée/raster/workIRQ/R,
IFF/EI/pending,336RAMIRQ+400reader identiques. Aucun writeRAM/importSRAM,
ROMsource nonmodifiée. Getter enregistre débutF09/F1E et VRAI PCretour,
pas seulementF2B. Deux nouveaux DLLobservateurs locaux callback/window,
sources z80.c restaurées enfinally ;PSG source identique aux anciens
14000frames/région pour chaqueprofile. Aucun DLLémulateur distribué.

Compiled68000 :tous1980vecteursF09 et72F1E testés dans chaque région
cible,soit4104exécutions,0erreur. KernelF09-N986 :1008framesNTSC/844PAL ;
kernelF09-P994 :1028/861 ;kernelF1E72 :106/89. Ces frames mesurent le
banc, pas le FPS ni la durée du jeu. Aucun changement sourceproduction ni
ROM depuis50918125e (seuls scripts/rapports/docs ajoutés ou étendus).

Un link kernel2PAL a échoué avec cheminTMPMSYS/GCC. État terminal clair,
logfirstfailure sauvegardé ; même arborescence d'objets relinkée avec
TMPDIR/TMP/TEMP='.' seulement dans la commande enfant, puis kernelconstruit
réutilisé par run_v319_intro_empty_pal68k.py. Pas de modificationoracle/code.
Tousprocessus terminal0 après récupération, aucun ancien handle à attendre.
Nettoyage archivé/relu :279références,36015764octets générés supprimés,
32198996nets libérés. Sources gardées ; données/kernel/symboles restituables.

Prochaine action :callbackfeuF37..F4E+bank5BDFF..BE12. Source :litC02F,
AND7,RET NZ ;sinon banque5, INCcompteurDCE2/CP6/JR C/XOR vers0, écrit
DCE2, JPBDFF ;BDFF multiplieindexpar3 et copie3octetsBE13→DCA1avecLDI.
Palette+compteur hors vue336RAMIRQ :utiliser ctx.full_ram/source_room_get/put
ou un adaptateur explicite, puis capturer aussi ces octets au source pour
l'oracle. Ne pas remplacer par un simpleworktotal car IRQ peut intervenir
entre instructions. Puiscallbacks1055/104A acteurs/SAT. Branche skipD0B
surC021&30 reste à tester avec entrées normales. Ensuite intégrer le modèle
continu dansintro :preuve sémantique ne vaut pas deadlinesvidéo/PSGphysiques.

Scripts build_v319_intro_empty_observer.py,validate_v319_intro_poll.py
(--profilepoll/callback/window),compile_v319_intro_poll_68k.py
(--source-regionboth/ntsc/pal),run_v319_intro_empty_pal68k.py,
archive_v319_intro_empty.py. V319resteversionpublique, aucun nouveauROM.

NOUVEAU CODE NATIF : `megadrive/src/source_intro_wait.h/.c`, rapport
`analysis/v319_native_intro_poll_report.json`, archive `analysis/v319-native-intro-poll`.
F21pollage VCounter traduit sur SourceClock, avec vrais IN11T/CP/JR et
discontinuités Mode4/192(218NTSC/242PAL). SourceIntroWaitOutput comptepolls,
below,above,counter,skip,error. API poll s'arrête à F2B RET préfetché.
API callback modélise F09/B95+restore/F32LDHLJP+callbacknatif/continuation,
NULL=F36RET. API window inclut F1E CALLF09,poll et RET. ATTENTION :seul
F21pollage a une preuve oracle directe ; F09/F32/F1E restent à vérifier,
non sélectionnés par sound.inc/intro.inc de production. Aucun nouveau binaire
public ; reconstruction finale des sources identique V319 SHA d3ea2a83/DA29.

Preuve source originale sans entrées :86 cas NTSC+86 PAL,77629+95141
lectures port7E. Snapshots à premièreF21 et F2B, durée/raster/R/polls/IFF,
EI/pending,336octetsRAM IRQ et400reader exacts. AUCUN de ces cas naturels
ne traverse une IRQ pendant le poll (ne pas prétendre le contraire).
Observateur dédié local genesis_plus_gx_v319_intro_poll_libretro.dll,
sourcez80.c restaurée enfinally, ROM inchangée ; PSG source préexistant
identique sur28000frames donc non-interférence vérifiée à ce niveau.

Versioninitiale non batchée source vérifiée, conservée dans archive comme
unbatched-source.c avec SHA comparé au rapport initial. Version courante
batch30T/3M1 dessous112,44T/5M1 au-dessus127, seulement jusqu'au changement
de condition et avantVINT ; source_clock_repeat refusefirstfetch/EI/DI/pending.
5948 cas bords synthétiques comparent batché/nonbatché avec lecteur vivant
ou pause :5587acceptés,361rejetés identiquement,1705acceptés avecIRQ dont
756avecfullIRQ. Ce contrôle est une parité native, pas second oracle Z80.

Tests compilés68000 sur2régions cibles, les172vecteurs source dans chacune :
nonbatch2453framesNTSC/2053PAL ;batch105/89, zéro erreur et172770lectures
comptées chacune. Gain de throughput du BANC, pas FPS du jeu ni mesurecycle
isolée. Premierkernel échouéaupackaging(headerSGDKpar défaut),kernel02
avecrom_headerprojet2MiB. Capinitial2000frames avait144cas et0erreur ;
kernel02 construit réutilisé dans nouveau run5000frames, puis complété.
Commandes toutes terminales ; aucun job à attendre. Fichiers temporaires
compressés/relu/nettoyés :768références,32250012octets supprimés,
23243238nets libérés. Sources gardées ; tableaux/kernel/DLLhost restituables.

Prochaine action : oracle direct F09/F32/F1E, d'abord cas naturels callback
F36vide (DCEC=0F36), puis callbacksfeu/acteurs avec instructionsSourceClock,
et copieE8B..E9D. Réutiliser source_wait_complete, ne pas moyenner son coût.
Conserver les frontières source et brancheskipD0B de C021&30. Le callback
natif fourni modélise son RET ;les tests actuels compilent ces API sans
les certifier. Ensuite seulement intégrer les délais de publication natifs.
Scripts build_v319_intro_poll_observer.py,validate_v319_intro_poll.py,
compile_v319_intro_poll_68k.py,run_v319_intro_poll_68k.py (reprise cas2000),
stress_v319_intro_poll.py,archive_v319_intro_poll.py.

DERNIER ESSAI : `analysis/v319_intro_irq_ack_report.json`, archive
`analysis/v319-intro-irq-ack`. Cinq variantes privées, TOUTES ÉCARTÉES.
01demande complète explicite et callback dans IRQ après son ;02idem avec
prefetch02. 03IRQ incrémente clock et signale ready, F32 exécuté au premier
plan après retour ;04idem+prefetch02 ;05version03 allégée sans compteurs,
requête binaire et choix du callback conservé par l’appelant.
Toutes :420octets reader/DE/T-M1/effet/requêtes/track identiques V319 à
chaque frame, états PSG source exacts14000NTSC+14000PAL, zéro erreur monitorée.
PAL cinq champs intro exacts pour toutes. NTSC03/05 cinq champs exacts aussi
(clock/counter/line/timer/scene seulement, pas toute la RAM ou tous les acteurs).
NTSC01 première divergence8517,02/04dès1784. Requests=acks+1 à la fin des
variantes instrumentées, pending2 ;05pending1. Normal :attente IRQ suivante,
pas preuve d'un blocage. Tous les processus sont terminal0.

Vidéo NTSC diff pixelsV319147429 →01:1709395,02:16050450,03:147438,
04:4839961,05:147548. PAL124148→124070/124126/124122/124126/124090.
Même03 reste75pixels améliorés/84dégradés enNTSC ;05:45/164. Pas de
promotion pour une simple égalité d’états fin de frame ; le raster change.
Callback F32 doit rester foreground après B95. Réexécuter arbitrairement
le callback dans la queue IRQ ne reproduit pas le source. Le simple booléen
hardwareIRQ n'est pas suffisant : il manque l'ordonnancement source continu.

PROCHAINE ÉTAPE CONCRÈTE : réutiliser source_clock(.h/.c),source_irq_context,
source_wait,source_wait_restore. Ces modèles natifs comptent instructions,
R/M1,DI/EI/attente B95 et IRQ avec le VRAI coût reader, pas une moyenne.
Modéliser la continuation F09/F32/F21 au-dessus, puis les copies E8B..E9D
et la publication vidéo. SourceF32 est après wait_restore, avec PUSH/POP
et callback à coûts variables ; F21 poll IN/CP70/JRC/CP80/JRNC/RET doit
garder ses vrais points de lecture. SourceIRQ audio-only décrémente aussi
C030 (0205..020C), donc garder le timer courant chaque IRQ. Aucun besoin
de changer globalement musique/compensation pour réparer les callbacks.
Anciennes approximations reveal count-3600 et F09request physique seul ne
suffisent pas. Ne pas refaire une sixième variante de déplacement IRQ sans
modèle source. Sources de production/ROM restées byte-identiques au HEAD
précédent ; V319 publique inchangée, aucun nouveau binaire final annoncé.

Scripts prepare_v319_intro_irq_ack.py (génère01..05, option06 non construite),
measure_v319_intro_irq_ack.py,archive_v319_intro_irq_ack.py versionnés.
Archivage/relecture :2834références,215755522octets générés supprimés,
185881941nets libérés. Sources privées conservées ; ROM/symboles restituables
depuis gzip. Ne pas relancer dans les dossiers déjà archivés, aucun ancien
handle de build ou de comparaison à attendre.

NOUVEAU : préparation audio foreground testée et ÉCARTÉE, puis observateur
direct IRQ/F32 source. Rapports `analysis/v319_audio_prefetch_report.json`
et `analysis/v319_intro_irq_trace_report.json`, archives `v319-audio-prefetch`
et `v319-intro-irq-trace`. Sources de production/ROM inchangées depuis le
dernier commit ; pas de nouvelle ROM publique. Trois candidats privés :
01préparation spéculative+replay IRQ,02compte IRQ franchie pendant préparation,
03contrôle préparation+émission immédiate sans attente datée. Chacun garde
400 octets reader+effet et états PSG/source et octets/ordre exacts sur14000
frames par région. Cache utilisé>13000 fois, fallback natif conservé pour
requête/effet tardif, paramètres fade/compensation changés, contexte périmé,
rejet ou dépassement du prototype. Cela ne prouve pas les interactions.

Vidéo NTSC source :V319147429 pixels diff,01→15725485,02→6278199,
03→4382562. PAL124148→124010/124008/124218, quelques pixels dégradés
même quand le total baisse. Aucune promotion. Erreur médiane timing01/02
~492NTSC/400PAL contre6246/6260 V319 ; contrôle immédiat03→8957/8957,
confirmant qu'émettre les listes préparées en rafale n'est pas la correction.

OBSERVATEUR RÉEL source PCB95,BB3,F09,F0C,F32,0137,01DD,0CE0 :
getter compte8192 par lecture hôte ; source CPU/cycles/état jamais modifiés.
DLL distincte locale work/genesis-plus-gx/genesis_plus_gx_v319_intro_irq_libretro.dll,
source z80.c restaurée exactement enfinally. Rapports et source avant/après
archivés, pas de DLL distribuée. Non-interférence :PSG tous5flux NTSC/PAL
sur14000frames ; états intro antérieurs SMS/baseline/prefetch01 exacts enNTSC.

Preuve source :13397 retours IRQ complets NTSC/13466PAL, tous C02F+1.
F32total11857NTSC/11926PAL, égal au total intro_tick V319, mais frame
différente94NTSC/84PAL. Les trois prototypes gardent les frames callback
PAL V319 ; NTSC deltas totaux-6,-2,+1. IMPORTANT :fullcounts égaux ne
prouvent pas la phase. Deuxième révélation :source/V319 F32 aux frames
1784/1789/1794/1799 ;prefetch01 aux1785/1790/1795/1800. Préfetch02
retire les attentes supplémentaires bootstrap mais conserve ce passage.
Contrôle03 diffère de V319 plus tard dès3624, +1callback accumulé à10425.
Prochain travail : ordonnancement source B95/IRQ/F09/F32 aux frontières
loader/reveal indépendant du coût CPU MD du son ; maintenir les dates
source sans imposer des counters/frame overrides enregistrés. Une sortie
asynchrone nécessite toujours deadlines de préparation et phase première
écriture ; les wrappers md_z80_psg existent mais leurs anciens kernels ne
prouvent pas l'intégration boot/jeu/IRQ/DMA. Pas de nouveau test console.

Scripts nouveaux prepare_v319_audio_prefetch.py,measure_v319_audio_prefetch.py,
probe_v319_intro_clock_prefetch.py,archive_v319_audio_prefetch.py,
build_v319_intro_irq_observer.py,trace_v319_intro_irq.py,
archive_v319_intro_irq_trace.py. Toutes commandes terminales0, aucun handle
à attendre. Archivages relus :128921718+33361312 octets générés supprimés,
109282125+28557045 nets libérés. Sources conservées, candidats/symboles
restaurables depuis gzip ; choisir de nouveaux dossiers pour de futurs essais.

Dernier travail : `analysis/v319_buffered_psg_report.json`, archive
`analysis/v319-buffered-psg`. Cinq prototypes d’émission datée 68000,
TOUS ÉCARTÉS, aucun changement de ROM publique. Variante03 compacte :
14000 frames par région, zéro erreur runtime, zéro écart d’état PSG,
de commandes musicales ou d’intervalles SOURCE PRÉPARÉS. Maximum20 événements.
Erreur physique médiane d’espacement :6246→431 ticks NTSC,6260→415 PAL.
Mais vidéo face SMS :147429→6293441 pixels différents NTSC (13636→12715
frames exactes),124148→125392 PAL. Ne pas promouvoir sur la seule preuve
audio. Les attentes dans l’IRQ changent le rendu/rythme de l’intro.
Variante04 planned : dérive NTSC à5963, sans code erreur ; PAL états exacts.
Variante05 raw dix écritures : faute horloge NTSC dès23, PAL états exacts.
La fenêtre entre seed et entrée consommateur inclut rebasing/classification ;
ne pas l’ignorer ni augmenter une constante d’attente pour masquer une faute.
Variantes01/02 restent noires avant PSG ; sonde PC montre DMA_init/MEM_alloc,
puis aucun PSG_reset. Variante03 réduit la file DMA initiale80→32 et borne
le workspace daté à32 écritures/canal, dans scratch+D00, rejet explicite.
Ces limites de prototype ne prouvent pas une capacité suffisante au jeu entier.

Seul ajout aux sources principales : API source_audio_reader_stream_timed_work
et fast_timed_work avec workspace de l’appelant. Anciennes API wrappers,
composition master renommée pour éviter les collisions. Vérification host :
25644 vecteurs du reader SMS, deux implémentations,89200 octets datés chacune,
400 octets état/DE/T/M1/track/octets/dates exacts. Rebuild production privé
`validation/v319-timed-workspace-rebuild01` byte-identique à V319, checksumDA29.
API non sélectionnée par sound.inc publié. Aucun correctif audio public annoncé.
Prochaine action : émission des événements préparés sans bloquer l’IRQ vidéo,
avec phase physique de première écriture et deadlines de préparation établies.
Scripts prepare_v319_buffered_psg.py / measure_v319_buffered_psg.py /
check_timed_reader_workspace.py / archive_v319_buffered_psg.py versionnés.
Toutes les commandes terminales ; ne pas attendre leurs anciens handles.
Archivage relu :3100 références,85993032 octets générés supprimés,
50851406 nets libérés. Sources et scripts conservés, ROMs privées restituables
depuis gzip ; ne pas relancer dans les mêmes répertoires d’expérimentation.

Dernière preuve : `analysis/sms_psg_writes_v0319_report.json`, archive
`analysis/v319-psg-write-spacing`. Observateur séparé avant décodage PSG,
aucune modification des cycles/états émulés ; ses 28000 états de fin de frame
reproduisent exactement ceux du précédent cœur. Aucun overflow. Les huit
états exposés SMS/MD restent égaux ; les volumes sont des amplitudes, pas
des nibbles d’atténuation. Erratum : ancien libellé « registres bruts » et
ancien comptage <15 incorrects ; le rapport historique est immuable.
Comptage corrigé :13739 frames actives NTSC,13480 PAL ; première23/20.
Quatre frames d’initialisation diffèrent dans chaque région, toutes avant
le premier état actif. Ensuite31546 écritures musicales NTSC et36915 PAL
par système : octets, nombre et ordre identiques chaque frame.
En revanche aucun des20028/23371 intervalles entre écritures consécutives
dans une même frame n’est exact. Médiane14980 ticks MD contre9405 SMS.
Les origines absolues ne sont pas alignées : ne pas appeler leur delta
un retard physique. Les intervalles dans la même frame annulent l’origine.
Ne pas retarder globalement la musique pour corriger une révélation vidéo.
Le reader natif calcule puis émet des listes par canal ; les intervalles
intercanaux sont souvent trop longs, ceux intraliste trop courts. Ajouter
seulement des attentes ne résoudra pas les deux. Étudier production anticipée
et livraison datée avec budget réel ; les APIs fast_timed existent mais
leur surcoût et workspace (~2560 octets) interdisent un remplacement aveugle
du workspace actuel scratch+D00..F05. Aucune ROM de production modifiée.
Scripts constructeurs et captures compressées archivés ; DLL diagnostic
locale sous work/genesis-plus-gx, hors dépôt. Job94890 terminal0.
Audit/archivage terminal0,7376066 octets générés supprimés après relecture,
6738531 nets libérés. Aucun ancien job à attendre.

ÉTAT PRIORITAIRE : PARCOURS COMPLETS NTSC ET PAL VÉRIFIÉS SUR V319.
Palais PAL terminé0 :22points froids depuis le premier géant, gardien7C/60PV
sans protection (303prédictions), Hache d'or acquise à341509. Retrait final
371775, DeathAdder6D/90PV à371856,héros92PV,hurt0.101prédictions, zéro
écriture d'assistance durant combat ; vraie victoire373655. Neuf gemmes
373962, générique374655→382078, retour intro382108, point final382208.
Audit de fin passé0 ; rejeu complet officiel C47/V319 passé0,65536RAM et
PNG final exacts,aucune SRAM initiale,aucun import primaire. Rapports
`palc0046_palace_ending_report.json`, `c0047_pal_ending_report.json`,
`pal_ending_v0319_report.json`. Le reçu V319 est copié enversions et indexé.
README/index mis à parcours complets et sauvegardesNTSC/PAL. ROM toujours
2048Kio/d3ea2a83/DA29. Les sessions74524 et11254/PID50376 sont terminales0.
Il n'y a plus de campagne ni de suivi vivant à attendre/repartir par défaut.
Tous les autres pilotes/sessions prétendus actifs plus bas sont historiques.

Le portage n'est pas déclaré globalement achevé : source_rng_runtime.c
emploie encore SGDK pour la fourniture de R ; phase source R/IRQ globale,
révélations/fondus résiduels, PCM global et matériel restent non certifiés.
Autres slots/refus et phase des quatre motifs animés des maisons non
couverts par les contrôles ciblés déjà publiés. Continuer sur de vrais écarts,
ne pas relancer les campagnes inchangées pour leur seule ancienneté.

Trois nouveaux prototypes d'intro sont REJETÉS, jamais promus. Archive
`analysis/v319-reveal-experiments`, rapport
`analysis/v319_reveal_experiments_report.json`. Comparaisons14000images
PAL/NTSC chacune,aucune écriture RAM/SRAM. Premier : coût fullIRQ+audio
facturé entre tranches, NTSC147429→4837920différences, PAL124148→121065,
mais3284pixels PAL dégradés. Deuxième : vrai reliquat182lignes au lieu180,
rotation de masque conservée ; sonde physique première tranche et passe
complète égales SMS dans les deux régions, logique native inchangée aux
points contrôlés. Mais rendu NTSC147429→147593 etPAL124148→124273.
Troisième : reliquat + coût audio seul courant (524/536T+lecteur8000),
NTSC147429→147720 etPAL124148→124227. Aucun modèle n'a passé le garde
visuel. Pas d'erreur audio ni abandon intro dans les captures finales.
L'égalité VRAM physique seule ne prouve pas l'égalité du rendu en cours de
balayage : ne pas promouvoir ces prototypes parce que la sonde182passe.
F1E appelle F09/B95 AVANT sa fenêtreV112, donc pas de second débit fullIRQ
entre tranches. Prochaine piste : phase continue des instructions/écritures
et leur publication visible ; éviter encore un décalage de frame arbitraire.
Archive relue avant nettoyage :1716références,40721930octets générés
supprimés,22797527octets nets libérés. Sources prototypes conservées,
ROMs de développement restaurables depuis gzip ; aucune ROM numérotée
ni source de production modifiée. Sessions40342,74121,25137,34426,91370,
12935,73201,74105,35667 toutes terminales ; ne pas les relancer dans les
mêmes dossiers. Générateurs `prepare_v319_reveal_*` et sonde suivis.

Point prioritaire : premier géant du palais PAL vaincu et audité.
Session50681/PID15980 terminée0. Retrait313520 ; première simulation du
7B/60PV à313599,héros102PV,hurt14 naturel (pas de129 de test). Victoire
315704,point froid315855,héros104/104PV.260prédictions RAM entière,
zéro écriture d'assistance durant combat. Six étapes froides passées,
porte neuf cristaux en89 réellement ouverte, vue ballon/restauration
vérifiée,128mots HUD/neuf marqueurs source. Rapport
`analysis/palc0046_palace_giant_report.json`, archive
`analysis/palc0046-pal-palace-giant`. Candidatc0046 ; rejeu complet public
du palais prévu au jalon de fin, pas encore acquis.

Suivi74524/PID50376 actif : audit géant passé0, a démarré
`continue_pal_palace_inner_c0046.py`. Reprise315856 puis trajet
`palc0046-palace-portal14e01` actif au dernier contrôle. Lecteur unique
`palc0046-pal-palace-inner-sources/cold-stream`,22points prévus.
Suivi11254 attend le vrai handle50376, puis audit de fin et rejeu V319
seulement si la suite entière réussit. Les anciens15980/50681 ne sont
plus vivants. Hache d'or, Death Adder et générique PAL encore non acquis.

Intro résiduelle relue : chargeur `intro.inc` et budget audio524T dans
`main.c`. La précédente expérience map-wait rejetée dégradait plus de
4millions de pixels NTSC : ne pas la promouvoir ni appliquer un simple
ajout/suppression de frame. Aucun nouveau changement ROM sur cette reprise.
La ROM resteV319 ; README à neuf cristaux PAL et sauvegardesNTSC/PAL.

Dernier résultat : vraie sauvegarde PAL + Continue validés sur V319.
Le pilote74571 et son suivi38252 sont terminés1 après les vérifications
runtime : le validateur générique avait déjà écrit son rapport de reload,
mais échouait ensuite faute de versions/index.json dans le projet isolé.
Pas de bug ROM ni nouveau jeu rejoué : `archive_pal_save.py` a revérifié
les SRAM,592octets de payload, RAM complète, images, champs restaurés,
neuf marqueurs et HUD, puis publié l'identité c0046. Archive
`c0046-pal-real-save`, rapports `game_written_save_pal_c0046_nine_crystals_report.json`
et `c0046_pal_real_save_report.json`. Vérificateur public76287 terminé0 :
V319 écrit ses propres octets SRAM, puis Continue normal sans écritures RAM ;
RAM et images exactes au sauvegardeur/chargeur. Rapports
`c0047_pal_real_save_report.json` et `pal_save_v0319_report.json`, archive
`c0047-pal-real-save`. Reçu copié enV319, README/index à sauvegardesNTSC/PAL.
Autres slots/refus et fidélité globale restent ouverts.

Archive intermédiaire D9 terminée0 (10408) :3449références,113121984octets
générés supprimés après relecture,80403145octets nets libérés. Tous les
points finaux des20étapes et toutes les captures PNG gardés. Archive
`analysis/palc0046-d9-intermediate-captures`, script de nettoyage suivi.
ROMs numérotées, sources et traces de commandes conservées.

Palais PAL :50681/PID15980 toujours actif au dernier contrôle, géant15E
sans protection après retrait313520 ; entrée et deux mécanismes passés.
Suivi74524/PID50376 attend ce pilote, audit du géant puis suite intérieure.
Nouveau suivi11254 attend le vrai handle50376 ; après succès complet, il
lancera `audit_pal_palace_inner.py --through ending`, puis rejeu V319
`--milestone ending`. Ces preuves de fin ne sont pas encore acquises.
Les sessions/save/PID historiques plus bas ne doivent pas être relancés.

État prioritaire : NEUF cristaux PAL et retour désormais vérifiés.
Entrée/premier gardien D9 terminés0, huit étapes froides, retrait277883,
79/60PV source affronté sans protection (152prédictions), point279458,
80PV. Rejeu V319 exact, rapports `palc0046_d9_midboss_report.json` et
`c0047_pal_d9_midboss_report.json`. Suite D9 terminée0, douze points,
géant7B/60PV et boss6C/90PV sans protection, ballon acquis. RetourEB
à302755,104/104PV,72PM,deux clés,20pièces. Audit final corrigé uniquement
sur un chemin de manifeste PUBLIC_ROOT (aucun combat rejoué), passé0.
Rapports `palc0046_d9_report.json`, `c0047_pal_d9_report.json`,
`pal_d9_v0319_report.json` ; reçu copié dans versions/V319,index et README
mis à neuf cristaux. ROM toujours2048Kio/d3ea2a83/DA29, octets inchangés.
Les sessions15964,42108,74503,93674 sont terminales. Le74503 avait échoué
sur le chemin de fichier de l'audit ; audit/rejeu/reçu ont été repris et
réussis, ne pas attendre ces anciens handles. Aucun palais PAL complet
ni sauvegarde PAL encore annoncé.

Palais PAL actif : session50681/PID15980, script
`continue_pal_palace_entry_c0046.py`, six étapes prévues jusqu'au géant15E.
Dossier `palc0046-pal-palace-entry-sources`. Vue ballon réelle passée,
décor/ressources restaurés ; trajet porte89 en cours au dernier contrôle.
Suivi74524 attend le vrai handle15980, puis audit
`audit_pal_palace_entry.py --through giant` et lancement de
`continue_pal_palace_inner_c0046.py`, seulement si tout réussit. Dossier
suivant `palc0046-pal-palace-inner-sources` ; générique encore non acquis.
Sauvegarde PAL indépendante active : session74571,
`continue_pal_nine_save_c0046.py`, routeFA après D9 et hache sur5D.
Elle utilise de vrais menus/écriture SRAM puis Continue, aucun état forgé.
Résultats et ROM publique de ce test de sauvegarde à vérifier ensuite.
Les autres sessions actives mentionnées ci-dessous sont historiques.

Dernier point confirmé : entrée D9 atteinte et audit de préfixe réussi,
trois points froids exacts : maison264827, vrai péage265208 (19→9pièces),
entrée268807 en1FC (96PV,72PM,deux clés,huit cristaux). Clochette de
glace utilisée enCB à267660, vrai drapeau de passage ouvert. Commande
`audit_pal_d9_funded_entry.py --prefix-only` terminée0 pour ces trois
étapes. Le premier gardien n'est pas encore validé. Pilote15964/PID15736
actif sur `palc0046-d9-funded-switch1de-02` au dernier contrôle.
Suivi42108/PID14600 attend ce pilote puis audit8étapes/rejeuV319/finD9.
Nouveau suivi74503/PID31556 attend le vrai handle14600 ; seulement si
la suite termine0, il exécutera `audit_pal_d9_funded_finish.py --through
exit`, le rejeu V319 D9 et le reçu `summarize_pal_milestone_v0319.py
--dungeon9`. Ces résultats futurs ne sont pas acquis. Le nouvel audit
contrôle géant7B60PV, ballon réel, boss6C90PV, neuf cristaux/HUD et
retour extérieurEB ; aucun donjon ni générique complet PAL encore annoncé.
Git main poussé5a176e20 pour le financement. ROM publique inchangéeV319.

Mise à jour prioritaire : détour de financement D8 terminé et audité.
Fonds13/session15631 terminé0, objectif atteint à262688 :14pièces,
96PV,1CA. Rejeu indépendant65536RAM/PNG exact à262788. Le retour
normal avec hache, session68311, termine0 :19pièces,96PV,8cristaux,
extérieur29 à264258. Audit91807 terminé0, quatre étapes exactes,
rapport `analysis/palc0046_d9_funding_return_report.json`, archive
`analysis/palc0046-d9-funding-return`. Aucune écriture argent, ressources,
acteurs, progression ou SRAM ; protection d'approche déclarée seulement.
Le fonds12 reste un objectif10 échoué, malgré son vrai ramassage7→8.

D9 reprend désormais sur ce retour, sans nouveau donB5 ni nouvel épisode.
Pilote `tools/continue_d9_funded_entry_palc0046.py` actif session15964,
PID15736. Première route vers la maison payante1A atteinte sans erreur,
19pièces ; lecteur froid `palc0046-d9-funded-entry-cold-stream01`.
Pas encore de premier gardien D9 validé. Suivi session42108 attend le vrai
handle15736 ; il lance le nouvel audit `audit_pal_d9_funded_entry.py`,
puis le rejeu V319 du premier gardien et, seulement en cas de succès,
`continue_d9_funded_finish_palc0046.py`. Nouveaux dossiers sources
`palc0046-d9-funded-entry-sources` et `palc0046-d9-funded-finish-sources`.
Les anciens pilotes D9 sans le préfixe funded ne sont pas à relancer.
Les suivis/sessions actifs indiqués plus bas sont historiques si contredits ici.

Dernière reprise : fonds10 et11 terminés sans atteindre10pièces, aucun
succès de collecte à revendiquer. Le diagnostic
`analysis/palc0046_d9_funding_shore_report.json` explique fonds10 : la
pièce de cinq existe en40,144 mais sa zone de contact est inaccessible
depuis le bateau en40,120, même avec les deux embarcations acquises.
Pilote07 : géométrie de ramassage issue des descripteurs source, ignore
un butin inaccessible ; trajet29/39/3A, terminé sans pièces supplémentaires.
Nouveau trajet `md-pal-palc0046-d9-funding-d8-reentry01` terminé0 : vraie
entrée D8 en1EA,96PV,7pièces,83images de transition. Rejeu indépendant
session37376 terminé0 :65536octets RAM et PNG final exacts à261049.
Rapport `palc0046_d9_funding_reentry_report.json`, archive dédiée.
Contrôleur privé08/fonds12 terminé0 : première pièce vraiment ramassée
à261406,7→8pièces,96PV,1DA nettoyée,objectif10 non atteint. Rapport
explicitement faux pour cet objectif. Il hérite de la même approche1AC.
Suite privée09 préparée pour1DA/1CA/1C9/1C8. Coordinateur
`continue_pal_d9_funding13.py` actif en session15631 : rejoue fonds12
à froid avant de lancer fonds13, jamais un import de cet état.
Archives des échecs10/11 relues et nettoyées :365références,8923776octets
générés supprimés,4074821octets nets libérés. Aucune ROM numérotée supprimée.
Cartridge et version restent V319 ; ces changements concernent les tests.
Les anciens paragraphes de sessions actives ci-dessous sont historiques.

ROM publiée : V319/d3ea2a83 (SHA complet dans le README),2Mio/DA29.
NTSC terminé, vraie sauvegarde/Continue validés. Huit cristaux PAL avec
retours désormais validés ; portage complet toujours ouvert.
D8 : boss6B80PV source, retrait256435,365 prédictions RAM entière,
cristal260034, retour260858 en29,héros96/96PV,72PM,deux clés,7pièces.
Rapports `palc0046_d8_report.json`, `c0047_pal_d8_report.json`,
`pal_d8_v0319_report.json`. Archives `palc0046-d8`, `c0047-pal-d8`.
Le rejeu V319 passe sur65536 octets RAM et PNG final exacts. Index/README
V319 mis à jour et poussés, dernier jalon publié c557c4d7.

D8 pilote2744,14979/suivi5420 et12149/suivi47148 terminés0. Aucun
combat D8 actif. D9 initial s'est arrêté avant émulation : le plan statique
vers le donB5 n'a pas de chemin depuis la carte29 actuelle. Le lecteur
`palc0046-d9-entry-cold-stream01` n'a reçu aucun checkpoint (pas de
completed.json). Sources initiales `palc0046-d9-entry-sources/entry-tools`
et journal de commande conservés. Pipeline38454/PID12088 et son
suivi35066 sont terminés1. Ne pas relancer dans ces dossiers ni attendre
ces vieux handles ; aucun premier gardien D9 n'est encore validé.
Le plan sans carte courante trouvait des chemins vers les dons, mais la
vraie carte29 après D8 ne permet pas ces chemins : ne pas ignorer cet état
pour prétendre rejoindre une maison. Il manque3pièces pour le péage10.

Collectes de fonds01/02/03 terminées sans atteindre10pièces.01 s'arrêtait
trop tôt ;02 et03 ont parcouru19/1A/29,avec pertes dePV,aucune pièce.
Archives sans perte des01/02 : `analysis/palc0046-d9-funding-attempts01`,
rapport diagnostic faux `palc0046_d9_funding_attempts_report.json`.
11548416 octets générés supprimés après relecture ;7441220 nets libérés.
Ces captures n'avaient pas de nouvel assistance.json : le pilote ordinaire
hérite seulement des anciennes écritures, vérifiées identiques dans les
capture.json au D8. Aucun écrit nouveau ni SRAM importée. Pas de preuve
canonique publiée. Le03 reste brut ; même résultat7pièces.

Cause de la collecte impossible sur cette boucle identifiée par tables
ROM : `analyze_d9_funding_drops.py` et
`analysis/palc0046_d9_drop_planning_report.json`. Les types2E/2F/33/34
(catégorie4) n'ont aucun byte aléatoire produisant une pièce. Type21,
présent en2B, en possède128/256 (énumération, pas probabilité mesurée).
04 a tenté29→2A→2B mais est mort en29 sans pièces : pilote trop dangereux.
Les scripts de collecte ordinaires sont conservés ; aucune modification ROM.

Fonds05/session84878 et fonds06/session6689 terminés0 mais objectif
non atteint :7pièces,96PV,restés en29 àx240. Rapports explicitement en
échec frame_limit,ne pas les traiter comme fonds suffisants. Le05 impose
les sorties centrées de donjon ; le06 accepte tout le bord mais tente de
faire chercher un point hors de la grille de collision et n'appuie plus.
Les deux copies privées sont conservées, aucun code ROM modifié.

Fonds07/session83466 terminé0 mais sans pièces. Une erreur du cache
manette du pilote privé renvoyait [droite] à une première requête puis[]
aux suivantes dans la même image ; contrôles dupliqués même frame.
Corrigé dans copie04 (bouton mémorisé avant retour). Fonds08/session76285
atteint bien29→2A→2B,mais repart aussitôt par son bord gauche avant le
réveil des ennemis : sept pièces,échec frame_limit. Suivi19742 termine1
sur le garde de fonds insuffisants ; aucun replay ni reçu de succès créé.
Les captures et les événements prouvent la traversée ; aucune règle ROM
n'a été modifiée. Ne pas relancer07/08 ou leurs anciens suivis.

Parcours actif : fonds09,session96304/PID21496,via
`validation/palc0046-d9-guarded-funding05/run.py` dans le projet isolé.
Commande : `--boss-room 0x1ac --planner ordinary --release-near-coins
--new-assistance-episode --pal --assisted-prefix --continuation
md-pal-palc0046-d8-exit01 --rooms 0x29,0x2a,0x2b --target-room 0x2b
--rush-rooms 0x29,0x2a --frames 278858 --trial palc0046-d9-funds09
--max-deaths 0 --collision-aim --settle-attacks --doorway-ranges
--ignore-inactive-actors --equip-basic --wake-sentinels`.
La destination est maintenant2B : le pilote s'y avance vers le centre,
attend les vrais ennemis et les combat au lieu de retraverser l'écran.
Protection d'approche autorisée uniquement hurt,retirée près des pièces.
Copie du guard limitée à cet itinéraire extérieur et préfixeD8 ; ne pas
l'employer pour un boss. Le code ROM et les scripts partagés sont inchangés.

Suivi68261 : `after_pal_d9_funding.py --pid 21496 --trial 09` détient
un handle réel du pilote09 ; après sortie0,exige fonds réellement>=10,
audit des adresses autorisées,propriété des objets/cristaux conservée,
replay froid65536 octets RAM/PNG puis archive. Script de vérification
`verify_pal_d9_funding.py`. Pas de reçu de succès ni de preuve canonique
encore publiés. Le suivi ne lance pas D9 automatiquement après le replay.
Si succès il faudra adapter le pilote/audit D9 au nouveau point extérieur,
sans prétendre avoir vidé l'écran si l'objectif pièces a arrêté plus tôt.
Les essais précédents et les copies privées sont conservés ; ne pas les
modifier en place après lancement,ni relancer un trial existant. Vérifier
les vrais handles avant reprise : un délai n'est pas une fin de processus.

Fin D9 préparée mais non lancée : `prepare_pal_d9_finish.py` exécuté,
`tools/continue_d9_finish_palc0046.py` généré. Exige futur audit du premier
gardien79 puis géant7B avec retraits séparés, ballon11, boss6C, retourEB.
Les suivis antérieurs sont morts, il faudra préparer un nouveau suivi sur
le vrai processus relancé après résolution des fonds. Ne pas importer
les ressources ou états des parcours NTSC/V318. Reste PAL D9/palais/fin/
sauvegarde, révélations/fondus, phase R/IRQ et fidélité audio globale.

## Notes historiques du 7 novembre — états de processus périmés

### Ancien suivi V319, 7 novembre 2026

La ROM courante publiée sur main est V319, 2 Mio, SHA-256
`d3ea2a83ea24ed8a0d3c9857f9fbe70d000a4f73358452c1887f40e78966c56e`,
checksum DA29. Les deux alias racine et la ROM numérotée sont identiques
à c0047. La compilation normale reconstruit exactement ces octets ;
`analysis/optimization_v0319_report.json` décrit ce jalon daté.
Les sources principales intègrent désormais l'optimisation c0047.
La reconstruction historique épingle 03f21f34 puis applique le patch publié.

NTSC : campagne nouvelle partie complète jusqu'à Death Adder, générique
et retour intro, 403488 images. Rejeu c0047 avec les 65536 octets RAM et
l'image finale identiques. Sauvegarde réelle à neuf cristaux et Continue
sur la SRAM produite par ce même binaire c0047 également vérifiés.
Rapports `c0047_palace_final_auto_report.json`, `c0047_real_save_report.json`.
Aucune égalité image par image globale SMS n'est revendiquée.

PAL : quatre cristaux et retours terminés, puis vrai échange huile/Feu,
don de l'épée longue et entrée D5 à 109653 images. Sept étapes froides
vérifiées, puis même point rejoué sur c0047 : RAM entière et PNG exacts.
Rapports `palc0046_fire_sword_report.json`, `c0047_pal_fire_sword_report.json`.
D3 a connu une erreur de portée Python du pilote, récupérée depuis son
entrée déjà prouvée ; les deux contrôleurs et les dix étapes sont archivés.
Tous les pilotes NTSC et PAL jusqu'à cette entrée D5 sont terminés.
Ne pas relancer les anciens handles mentionnés dans l'historique.

PAL D5 terminé et audité : rapport `palc0046_d5_report.json`, archive
`palc0046-d5`. Dix-huit points froids sur lecteurs12+6. Le détour initial
contact01 vers153 est conservé en échec ; reprise depuis warp131421,
contact02 avec évitement du portail162, retrait133909 avant salle163,
premier combat134035 héros64PV/hurt0 et boss65 à72PV source. Huit
satellites observés,56 prédictions RAM entière, cristal136524, retour
extérieur137596 salle49,56/72PV,72PM. Aucune nouvelle aide après retrait.
Le rejeu c0047/V319 passe à137596 :65536 octets RAM et PNG exacts,
rapport `c0047_pal_d5_report.json`, archive `c0047-pal-d5`.
Pilotes96471 initial/38625 suivi terminal1 ; reprise36557 et suivi96285
terminés0. Ne pas relancer ces anciens handles.

PAL D6 terminé et audité : `palc0046_d6_report.json`, archive
`palc0046-d6`,20 points d'un lecteur froid, Clochette acquise par le
pilote ordinaire et briques préparatoires Terre explicitement distinguées
des passages. Retrait167339 en125, héros64PV/hurt0 ; premier combat
167646 en115,boss64 à60PV source. 209 prédictions RAM entière, cristal
174966, retour176650 salle8B,80/80PV,72PM,0clé,43pièces.
Rejeu c0047/V319 passé :65536 octets RAM/PNG final identiques, rapport
`c0047_pal_d6_report.json`, archive `c0047-pal-d6`. Reçu de version
`pal_d6_v0319_report.json`, reproductible par
`validation/summarize_pal_milestone_v0319.py --dungeon 6`.
Pilote81839/PID48408 et suivi61129 terminés0. Ne pas relancer.
Premier refus D6 avant émulation (lecteur D5 erroné) conservé dans l'archive.

Préparation PAL D7 terminée : `palc0046_d7_preparation_report.json`,
archive `palc0046-d7-preparation`. Neuf points,193118 images,1B9,
80PV/56PM,deux clés,15pièces. Vrai don7D43→73 et clé94 à60 ; pas de
B5 ni de ressources injectées. Deux briques Terre préparatoires ouvertes.
Rejeu c0047/V319 exact RAM65536/PNG : `c0047_pal_d7_preparation_report.json`,
archive `c0047-pal-d7-preparation`. Ce jalon ne valide aucun boss D7.
Pilote22320/PID33288 terminé0 ; ne pas le relancer.

Intermédiaire PAL D7 terminé et audité : `palc0046_d7_midboss_report.json`,
archive `palc0046-d7-midboss`. Retrait193119 ; premier combat193298,
1B8,héros80PV/hurt0,boss78 à30PV source. 104 prédictions RAM entière,
victoire puis reprise d'approche194396 à80PV/56PM/deux clés. Protection
réactivée seulement après la victoire, avec un unique écrit hurt129.
Rejeu c0047/V319 exact RAM65536/PNG à194396 :
`c0047_pal_d7_midboss_report.json`, archive `c0047-pal-d7-midboss`.
Le cristal7 et le boss principal ne sont pas encore validés par ce jalon.

Pilote intermédiaire46780 et suivi23307 terminés0. L'ancien suivi14346
et sa dépendance86661 sont terminés1 : import Path manquant dans l'audit,
après les quatre preuves du jeu déjà terminées. Cet import a été corrigé
sans relancer le combat. Audit full exécuté et passé ; ne pas le relancer
sur l'archive existante. Même import ajouté à l'audit de la fin D7.

PAL D7 terminé et audité : `palc0046_d7_report.json`, archive
`palc0046-d7`. Dix points de seconde partie ; bateau203631, retrait
principal211333 en189/80PV/hurt0, premier combat211520 en179/boss67
à60PV source,245 prédictions RAM entière, aucun dégât pendant le combat.
Cristal216054, retour217575 en1B,88/88PV,64PM,deux clés,15pièces.
Rejeu c0047/V319 exact RAM65536/PNG : `c0047_pal_d7_report.json`, archive
`c0047-pal-d7`. Reçu `pal_d7_v0319_report.json` et README/index V319
mis à jour à sept cristaux. Les étapes physiques du HUD sont vérifiées
après le bateau, le boss et le retour. Les compteurs/poses globaux SMS
restent une limite distincte.
Pilote44180, suivi41915/PID44460 et postflight34690/PID3492 terminés0.
Ne pas relancer leurs anciens handles. Audits/archives D7 existants à préserver.

PAL D8 paiement/entrée/intermédiaire terminés : `palc0046_d8_midboss_report.json`,
archive `palc0046-d8-midboss`, six points. Retrait223759 avant1C9,
intermédiaire7A à50PV source vaincu sans protection,163 prédictions RAM
entière, point225457. Rejeu c0047/V319 exact RAM65536/PNG : rapport
`c0047_pal_d8_midboss_report.json`, archive `c0047-pal-d8-midboss`.
Le paiement normal3C15→5pièces est vérifié ; pas de soin nécessaire.
Pilote8480 et suivi44326/PID30416 terminés0 ; ne pas les relancer.

Approche PAL D8 terminée et auditée : `palc0046_d8_approach_report.json`,
archive `palc0046-d8-approach`, huit points du lecteur de seconde partie.
Reprise de protection seulement après victoire225458 ; mécanismes
lointains, un aller-retour ordinaire pour ennemi isolé1C8, vraie clé du
voleur15 acquise248723. Approche256434 en1A6,héros88PV/72PM/deux clés,
7pièces. Intermédiaire vaincu reste absent ; état source du boss principal
6B :80PV/16/2/64. Aucun import d'objet/ennemi/ressource/progression/SRAM.
Audit `audit_pal_d8_approach.py --prefix-only` passé avant publication.

Parcours actif : fin D8, PID2744 au lancement,
`tools/continue_d8_finish_palc0046.py` cwd projet isolé habituel.
Sources `palc0046-d8-finish-sources/main-sources`, lecteur
`palc0046-d8-finish-cold-stream01`. Retrait256435 en1A6/hurt0 déjà
prouvé. Boss principal lancé avec `unassisted_arrival_prediction.py`,
PID44116 au dernier contrôle, pas8, aucune nouvelle aide après retrait.
Le pilote vise cristal8 puis sortie29. Ne pas relancer dans les dossiers
existants. Aucun huitième cristal n'est encore annoncé à ce point.

Suivi14979/PID5420 attend ce pilote. Suivi12149 :
`after_pal_d8_finish.py --pid 5420` détient son handle, attend sortie0,
audit full `audit_pal_d8_finish.py` puis rejeu c0047 `d8`. La copie du
script en cours avait encore le reçu `--dungeon 7` à son lancement ;
ce paramètre a été corrigé dans le fichier pour les futures exécutions.
Après terminaison vérifier/créer explicitement le reçu D8 avec
`python validation/summarize_pal_milestone_v0319.py --dungeon 8`.
Ne pas relancer audit/rejeu complets si leurs archives existent déjà.
Suite conditionnelle D9 préparée : `prepare_pal_d9_entry.py` est exécuté,
`tools/continue_d9_entry_palc0046.py` généré mais non lancé. Le pilote
exige le futur vrai rapport D8. Si les fonds finaux sont inférieurs à10,
il vérifie le drapeau B5 non encore réclamé et demande son vrai don10
par dialogue normal avant de payer1A. Aucune monnaie n'est injectée.
Sources futures `palc0046-d9-entry-sources/entry-tools`, lecteur
`palc0046-d9-entry-cold-stream01`, passage10pièces puis Clochette/entréeD9.
Suivi38454 : `after_pal_d8_campaign.py --pid 47148`, handle réel du
postflight12149/PID47148 ; exige sa sortie0, crée/vérifie explicitement
le reçu D8, puis lance D9. Ne pas démarrer D9 manuellement en double.
Audit D9 préparé : `audit_pal_d9_entry.py`, mode `--prefix-only` sans
rapport final. Il exige la vraie sortie D8 et ses ressources, vérifie le
don B5 éventuel, le prix réel10 du passage1A, la Clochette, les huit
étapes et le premier gardien79 à60PV sans protection. Cet audit n'a pas
encore été exécuté sur D9 : aucun parcours D9 n'a encore commencé.
`audit_pal_d8_finish.py --prefix-only` passe le retrait256435,7cristaux,
88PV/72PM/deux clés/7pièces. Ce mode ne publie aucun rapport de fin.
Le boss44116 est désormais terminé0 :365 prédictions RAM entière,
victoire et cristal260034,96/96PV,72PM,7pièces,deux clés. L'audit en
lecture seule des deux premières étapes finales (retrait/boss) passe.
Le retour est en cours via PID33740 `unassisted_fast_prediction.py`,
planning-step8, mêmes écritures closes et aucune nouvelle protection.
Le huitième cristal seul ne suffit pas à déclarer le donjon terminé :
attendre le retour29, audit full et rejeu avant de mettre le README à8.
Suivi35066 : `after_pal_d9_midboss.py --pid 12088`, détient le handle
du pipeline D8→D9 ; après sa sortie0, audite le premier gardien D9,
rejoue c0047 avec `d9-midboss` puis lance la suite D9. Ne pas dupliquer.
`prepare_pal_d9_finish.py` est exécuté, son contrôleur est généré mais
pas lancé. Il exige le rapport réel de premier gardien D9 sans aide,
puis vise géant7B (retrait avant19C), ballon11, retrait avant1AC/boss6C,
neuvième cristal et retourEB. Aucun nouvel objet ou boss n'est revendiqué
par cette préparation ; seuls les itinéraires historiques sont réutilisés.


Vérifier les vrais handles/processus : un délai n'est pas une fin.
Le projet isolé conserve c0046/9e747d38 ; ne pas remplacer sa ROM ou ses
symboles par ceux de la racine pendant le parcours. Les sources racine
et privées ont été contrôlées sans lien physique partagé avant promotion.

Recherche d'intro séparée, sans promotion : `analysis/v319_intro_map_wait_report.json`,
archive `analysis/v319-intro-map-wait`. Captures V319/SMS : révélation du
3e tableau NTSC commence deux images plus tard côté MD (3653/3651),
1004 lignes de plan3 diffèrent à3670. Le prototype qui compte l'IRQ
traversée pendant l'envoi de carte dégrade4253777 pixels NTSC sur14000
images ; PAL inchangé. Prototype explicitement rejeté, V319 inchangée.
Ne pas promouvoir ce raccourci : intégrer la phase globale des demandes
IRQ/travail source avant de déplacer une attente isolée. Sources/preuves
conservées sans perte,17822758 octets générés supprimés après relecture
(10749468 octets nets libérés). Les dossiers de prototype/localisation
existent ; leurs binaires de travail ont été archivés et retirés. Ne pas
relancer dans les mêmes dossiers. Script `localize_v319_boot_fade.py`.

Archives de promotion et reconstruction : `v0319-root-promotion`,
`c0047-clean-rebuild`; première tentative avec complément zéro conservée
dans `c0047-clean-build-zero-padding` comme diagnostic échoué explicite.
Les doublons de compilation sont retirés uniquement après compression
sans perte et relecture par SHA. Les ROMs historiques sont conservées.

Restent PAL D8 à fin et sauvegarde, écarts de révélations/fondus et phase
R/IRQ source, fidélité audio PCM globale et vérification console réelle.
Le portage complet n'est pas déclaré terminé. Lire README pour les limites.

## Notes historiques antérieures à la promotion V319

La section suivante est conservée pour les chemins et décisions passées ;
ses états « en cours » sont périmés sauf confirmation ci-dessus.

### Ancien suivi au 7 novembre 2026

La V318 a terminé les parcours NTSC et PAL jusqu’à la victoire, au générique
et au retour à l’intro. Le pipeline PAL est fermé et son audit final passe.
Ne pas reprendre ses anciens pilotes mentionnés dans l’historique ci-dessous.

L’aperçu recommandé pour poursuivre l’optimisation est c0047-d3ea2a83,
2 Mio, checksum DA29. Il reprend le programme de c0046 avec un complément
correct de fichier. Neuf cristaux et retours sont rejoués en NTSC avec
RAM entière/image finale identiques, ainsi que la corde, le don de 50
pièces et l’achat de Terre. Dernier point Terre : 81636, 48 PV, 12 pièces,
48 PM, Terre niveau 1. Dernier retour D4 : 107105, 62/64 PV, canoë acquis.
Le premier donjon est aussi rejoué en PAL.
La campagne complète de cet aperçu demeure ouverte.

Suite PAL démarrée en parallèle du NTSC D9 : hache/fée/entrée D2 terminées,
sept points d’un même rejeu froid, sans import de ressources/SRAM.
Rapport analysis/palc0046_after_d1_report.json, archive palc0046-after-d1.
Entrée29846,salle171,40/40PV,hache niveau1 ; fée32→40PV par dialogue normal.
Rejeu c0047 PAL passé sur65536 octets RAM et PNG final : rapport
analysis/c0047_pal_after_d1_report.json, archive c0047-pal-after-d1.
Le pilote continue_after_d1_palc0046.py/session89302 est terminal0.
prepare_pal_after_d1.py et prepare_pal_d2.py sont exécutés, ne pas répéter.

PAL D2 est joué par tools/continue_d2_palc0046.py dans le projet isolé,
session86870, PID3280 au lancement (vérifier le processus réel). Préfixes
md-pal-palc0046 ; retrait nommé md-auto-palc0046-d2-release01, dont les
core_options restentPAL. Sources : validation/palc0046-d2-sources ; lecteur
palc0046-d2-cold-stream. Trois clés, antichambre et retrait37850 sont déjà
rejoués ; boss63 à30PV source ensuite sans protection, pas16, puis cristal
et sortieD6. Le contrôleur active les réveils/réentrées ordinaires qui ont
résolu les ennemis isolés dans les anciens parcours, sans modifier la ROM.
Audit préparé audit_pal_d2.py : attend le succès/fermeture du pilote et ses
sept points, puis gèle analysis/palc0046-d2 et écrit palc0046_d2_report.json.
Ensuite rejouer c0047 avec validation/replay_c0047_pal.py --report
analysis/palc0046_d2_report.json --milestone d2. Aucun deuxième cristal PAL
n’était annoncé par cette préparation. Ce parcours est désormais terminé et
archivé : palc0046_d2_report.json, archive palc0046-d2. Retrait37850,
premier combat38052, héros40PV/hurt0,boss63 à30PV source. 324 prédictions,
sept points froids exacts, victoire43765, sortie46869,D6,23/48PV,une clé.
Le rejeu c0047 PAL passe : c0047_pal_d2_report.json, archive c0047-pal-d2.
Sessions86870 et67753 terminées0 ; ne pas les relancer. Audit déjà exécuté.

La suite PAL D3 est lancée : tools/continue_d3_palc0046.py, session84152,
dans le projet isolé. prepare_pal_d3.py est exécuté, ne pas le répéter.
Sources figées palc0046-d3-sources ; lecteur palc0046-d3-cold-stream.
Part du vrai retour D2, vise huile/stairsC7, entréeD3, corde13, contact,
clé, retrait avant1C3/boss69, troisième cristal et sortie62. Les10 étapes
exigent chacune une preuve RAM/PNG indépendante. Le pilote initial84152
est maintenant terminal1 : erreur Python de portée du global current après
les trois premières étapes, avant toute exécution de corde. Ces trois
preuves sont terminées/passées dans palc0046-d3-cold-stream/completed.json :
huile48385→49114 puis entrée52030,salle1F8,23PV. Ne pas relancer ce pilote.

La reprise est lancée : tools/continue_d3_palc0046_resume01.py,session4773.
resume_pal_d3.py a conservé le contrôleur initial et ses sources, vérifié
les trois points puis repris l’entrée canonique, sans import d’état.
Nouvelles sources palc0046-d3-resumed-sources01 et lecteur
palc0046-d3-cold-stream02. Les sept étapes restantes reprennent les mêmes
noms, dont les sorties n’existaient pas lors de l’erreur. current est partagé
entre campaign/combat ; le générateur initial est aussi corrigé pour un
nouveau dossier, sans modifier le premier pilote figé. La vérification des
deux portées symboliques passe. Corde57593,contact,clé et antichambre60830
sont déjà rejoués ; retrait60831 avant boss69 à32PV source, combat en cours.
Audit préparé audit_pal_d3.py : attend les10 étapes sur lecteurs3+7, conserve
les deux versions sources et déclare explicitement la récupération de portée.
Après réussite/fermeture : lancer cet audit puis replay_c0047_pal.py avec
analysis/palc0046_d3_report.json --milestone d3. Aucun troisième cristal
n’est annoncé par ces seules étapes préparatoires.

Le démarrage c0047 est désormais vérifié : analysis/c0047_boot_report.json,
archive analysis/c0047-boot. Deux boucles sans entrée (14000 images) dans
chaque région, toutes identiques à V318 après normalisation du viewport.
Concordance SMS :13636/14000 en NTSC et13682/14000 en PAL ; écarts de
pixels147429/124148 conservés. Audio6500 images/région,402 octets d’état
et8 registres PSG identiques à V318. Pas de preuve PCM ni d’effacement
des limites de révélation/fondu. Les trois processus de test sont terminés.
Validation/summarize_c0047_boot.py a vérifié et archivé les preuves, puis
supprimé10704832 octets de doublons générés (9867796 octets nets libérés).
La vue de lecture seule du binaire publié dans validation/c0047-boot01
est archivée et supprimée ; ne pas relancer dans ce dossier. Les ROMs
numérotées et le candidat publié sont conservés.

Six retours d’inventaire c0047 sont également terminés : extérieur et
maisons0/2, PAL/NTSC, commandes normales, sans import RAM/SRAM. Les motifs
statiques parmi124 examinés concordent à3300,3440,3470 ; quatre motifs
animés de maison sont conservés dans les différences et exclus de l’égalité
statique. Rapport analysis/c0047_inventory_report.json ; archive c0047-inventory.
Processus6189 terminal0. Validation/summarize_c0047_inventory.py a vérifié
et archivé les preuves puis supprimé4922880 octets de doublons générés,
3890509 octets nets libérés. Ne pas relancer ce dossier ni son archivage.

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

La préparation D6 est terminée : dix-sept étapes, cinq acquisitions de clés,
six étapes Terre et cloche de glace avec son HUD physique. Rapport :
analysis/d6_progress_c0046_report.json ; archive analysis/c0046-d6-progress.
Dernier point 176002, salle 125, 72 PV et 40 PM, aucune clé restante.
Le passage préparatoire Terre est ouvert ; aucune entrée ni victoire contre
le boss 115 n’est revendiquée par cette préparation.

Le pilote finish_d6_c0046.py s’est arrêté avant le boss sur un délai
d’attente du lecteur de preuves. Son lecteur a toutefois terminé et fermé
correctement : preuve du retrait de protection à176003, 65536 octets RAM
et PNG exacts, completed.json passé. Aucun combat n’avait encore été lancé.
La reprise D6 est terminée : boss64 à60 PV, premier combat176965 avec héros
56 PV/hurt0, 190 prédictions ; retour avec97 prédictions à185456, six cristaux,
80/80 PV et72 PM, 38 pièces et aucune clé. Pas de nouvelle aide après176003.
Les audits vérifient la preuve de retrait puis les preuves combat/retour
sur deux lecteurs froids ; l’archive est analysis/c0046-d6-campaign.
Rapports : analysis/d6_campaign_c0046_report.json et
analysis/c0047_d6_auto_report.json. Le rejeu c0047 passe aussi sur toute la
RAM et l’image finale. Tous les pilotes D6 sont terminés.

Le premier pilote D7 est terminé en échec sur l’entrée A5 encore fermée.
La source A5 appelle5FB1 après les ennemis (room_clear kind7) : tuer les
ennemis ouvre la case83 en4 et pose le bit persistant1. Ce n’est pas une
entrée à forcer ni un terrain à couper. L’audit indépendant passe :
analysis/a5_hidden_shop_c0046_report.json, archive c0046-a5-hidden-shop.
Combat clear à190785 puis boutique à191070, 80 PV, 49 pièces après une pièce
ramassée normalement. Achat réel à40 : 49→9, une clé,80 PV, sans soin.

La préparation D7 est terminée et auditée : dix points froids sur deux
lecteurs indépendants, achat A5 à40, ouverture A5 par combat, entrée D7,
deux clés et deux actions Terre à8PM chacune. Rapport :
analysis/d7_prep_c0046_report.json ; archive analysis/c0046-d7-prep.
Dernier point205302, salle1B9,80/80PV,56PM,deux clés et10 pièces.
Le pilote préparatoire est clos.

Le gardien intermédiaire D7 est terminé et audité : source78 à30PV,
protection retirée à205303, premier combat205488, héros80PV/hurt0.
Victoire sans dégât,92 prédictions RAM exactes, quatre points froids.
L’approche ne reprend qu’à206489 après la mort, vers le boss179.
Rapport analysis/d7_midboss_c0046_report.json ; archive c0046-d7-midboss.
Tous les pilotes préparatoires et intermédiaires D7 sont terminés.

Le premier pilote de fin D7 (run-c0046-d7-finish-02) est terminal en échec
sur south01 : quatre52 cachés en1D6, aucune mort,80PV. La reprise south02
active --wake-sentinels et --retry-isolated-foes, vainc les quatre52 par
les commandes normales, puis franchit le mécanisme distant et reçoit le
bateau. Audit partiel exécuté : analysis/d7_ship_c0046_report.json ; archive
c0046-d7-ship. Dernier point bateau215194,1D5,80PV,72PM,21 pièces,deux clés,
six cristaux. Le HUD et les trois points froids concordent.

La fin D7 est terminée et auditée : dix étapes froides, bateau, boss67 à60PV,
protection retirée222304, premier combat222493 à72PV/hurt0.172 prédictions
RAM exactes, un dégât de2PV (72→70) puis cristal88/88PV. Retour227539 à88PV,
64PM,une clé,27 pièces,sept cristaux. Le rejeu c0047 retrouve toute la RAM
et le PNG final. Rapports analysis/d7_campaign_c0046_report.json et
analysis/c0047_d7_auto_report.json ; archives c0046-d7-campaign et c0047-d7-auto.
Tous les pilotes D7 sont terminés. Le trajet sud réussi est south02.

L’entrée et le gardien intermédiaire D8 sont terminés et audités : passage3C
payé27→17, entrée à76PV, garde7A à50PV source, protection retirée233384,
146 prédictions et six points froids exacts. Un dégât normal76→58 puis
récupérations normales : victoire à82/88PV,64PM,une clé,point235018.
Rapport analysis/d8_midboss_c0046_report.json ; archive c0046-d8-midboss.
Le pilote d’entrée D8 est terminal. Le huitième cristal n’est pas encore acquis.

La fin D8 est terminée et auditée : boss6B à80PV source, protection retirée
264943, premier combat265128 à88PV/hurt0. Victoire sans dégât reçu,344
prédictions RAM exactes ;30 au retour. Sortie269376 à96/96PV,72PM,une clé,
25 pièces et huit cristaux. Les onze points froids passent. Le rejeu c0047
retrouve aussi65536RAM/PNG au point final. Rapports d8_campaign_c0046_report.json
et c0047_d8_auto_report.json dans analysis ; archives c0046-d8-campaign et
c0047-d8-auto. Tous les pilotes D8 sont terminés.

Le retour sud est terminé et audité : deux points froids, passage1A→3C
payé25→15, huit cristaux,96PV,72PM,une clé conservés. Point final270329
en3C. Rapport analysis/d9_south_c0046_report.json ; archive c0046-d9-south.
Le pilote continue_d9_south_c0046.py est terminal. Aucun décès/Continue ni
ressource importée : les fonds réels ont permis le passage inverse normal.

Le pilote continue_d9_entry_c0046.py est terminé avec succès. Entrée D9 :
273982,salle1FC,96PV,72PM,15 pièces,une clé,huit cristaux. La cloche est
utilisée par le menu normal enCB ; drapeau persistant et case39 vérifiés.
Rapport analysis/d9_entry_c0046_report.json, archive c0046-d9-entry.
Les mécanismes Terre/contact1DE et Terre1CE, l’antichambre et le premier
gardien79 sont également audités et archivés : d9_midboss_c0046_report.json,
archive c0046-d9-midboss. Retrait de protection282688, premier boss282900
à60PV source/héros96PV/hurt0. Deux coups96→80→64 ; victoire284100,
point final284251. 148 prédictions et six points RAM/image exacts sur un
même rejeu froid. Ne pas recréer ces archives ni reprendre l’ancien pilote.
Sources figées : validation/c0046-d9-sources04/entry-tools ; lecteur clos
cold-stream. sources03 s’était arrêté avant émulation sur un chemin local.

Le processus courant joue tools/continue_d9_finish_c0046.py dans
validation/c0046-campaign01/isolated/project (session44962). Il reprend
après le gardien puis vise contact1AD, géant7B à60PV sans protection,
ballon réel, boss6C à90PV sans protection, neuvième cristal et retour.
Sources figées : c0046-d9-sources04/finish-tools ; lecteur finish-cold-stream.
prepare_d9_finish.py est déjà exécuté, ne pas le relancer dans les mêmes
sorties. Après huit étapes : summarize_d9_balloon_c0046.py puis, depuis
la racine, archive_d9_finish.py --balloon-only. Après douze étapes :
summarize_d9_campaign_c0046.py puis archive_d9_finish.py et rejeu c0047
avec validation/replay_c0047_d1.py auto --dungeon 9.
Ces étapes D9 ne revendiquent pas encore le neuvième cristal ni sa
reproduction c0047. Ne pas lancer la suite du palais avant leur succès.

La suite est mise en attente par after_d9_finish.py --wait-for-pid39884
(session97858). Il tient le handle Windows exact du pilote D9 et vérifie
son code0 puis les douze preuves froides, sans relancer le pilote. Il
lance les audits/archives ballon et D9, le rejeu c0047 D9, puis le ballon
possédé, l’entrée du palais et son premier géant. Chaque commande doit
réussir avant la suivante ; premier échec = arrêt. Ne pas lancer ces
étapes en parallèle à cette suite. prepare_palace_entry.py est exécuté :
cinq scripts privés de continuation/audit, identité c0046 et chemins
canoniques vers les rapports partagés. Aucun résultat du palais c0046
n’est revendiqué par cette préparation. Vérifier les deux sessions et
les processus réels avant toute reprise.

Le lecteur finish-cold-stream a vérifié cinq points : reprise284252,
contact1AD289095, portail19E290323, approche19D290556 et retrait290557.
Le héros a88PV avant le géant7B ; les quatre type62 à0PV en19D sont des
dangers persistants, pas une salle déclarée nettoyée. Le combat géant01
est lancé avec60PV source et sans protection après290557. Vérifier la
session44962 pour la suite, sans relancer dans les mêmes sorties.
Le géant est maintenant vaincu : victoire294980, point final295131,
8PV/72PM, aucune mort ni nouvelle aide après290557. Ses60PV source sont
conservés et545 fenêtres de prédiction RAM concordent ; la sixième preuve
RAM/PNG du flux partagé est passée. Reprise d’approche295132 seulement
après victoire canonique. Le pilote enchaîne vers ballon01 ; l’audit groupé
ballon reste réservé à la suite97858 après succès des douze points D9.
Le ballon est maintenant audité et archivé : analysis/d9_balloon_c0046_report.json,
archive c0046-d9-balloon, huit points RAM/PNG exacts. Récompense terminée
à296942, salle19B,32PV/72PM,15pièces,une clé,huit cristaux. Les cœurs
réels récupérés font passer8→32PV. Le pilote a lancé main-approach01
vers contact1BD, avant le boss1AC/6C. Le boss principal est désormais vaincu :
victoire306863, cristal et point final307014,104/104PV/72PM,une clé,
neuf cristaux. Protection retirée303258, combat sans dégâts reçus,
183 prédictions exactes et onzième point froid RAM/PNG passé. La sortie01
est lancée sans protection ; attendre sa preuve et les audits de la suite97858
Ces étapes sont désormais terminées : sortie308670,salleEB,104PV/72PM,
une clé,neuf cristaux. Retour sans nouvelle aide avec23 prédictions ;
le flux finish-cold-stream est clos et ses douze points passent.
Rapport analysis/d9_campaign_c0046_report.json, archive c0046-d9-campaign.
Le rejeu c0047 D9 passe aussi sur65536 octets RAM et PNG final : rapport
analysis/c0047_d9_auto_report.json, archive c0047-d9-auto. Session44962
et PID39884 sont terminés0 ; ne pas les relancer.
La suite97858 a passé les audits D9, revérifié l’archive ballon existante
sans la modifier, archivé la fin D9 et rejoué c0047. Elle joue maintenant
continue_after_d9_c0046.py palace : ballon possédé puis entrée réelle du
palais avant le premier géant. La suite70465 attend toujours la réussite
de cette suite97858 avant la fin du palais. Cette suite97858 est maintenant
terminée0 : ballon activé/restauré, entrée312797,salle18D,104PV/72PM ;
premier géant60PV source, retrait321705, premier combat321787avec102PV
et hurt14 naturel, victoire325979,point326130,86PV/72PM,131 prédictions.
Rapports owned_overview_c0046_report.json,cold_palace_entry_c0046_report.json,
cold_palace_giant_c0046_report.json ; archives c0046-palace-entry et giant.
La suite70465 a automatiquement repris : elle a archivé ces deux jalons,
terminé/audité/archivé les cinq étapes intérieures jusqu’à339846,salle12A,
104PV/56PM. Rapport cold_palace_inner_c0046_report.json, archive
c0046-palace-inner. Elle joue le gardien11E/7C avant la vraie GoldenAxe2,
puis la route finale ; vérifier son handle réel avant toute reprise.
Le gardien11E/7C est maintenant vaincu sans protection : victoire359007,
point359158,80PV/72PM,344 prédictions exactes. Retrait347920. Le pilote
continue vers resume-final01 puis GoldenAxe2 en11D ; attendre son audit
cold_palace_guardian_c0046 et son archive avant d’annoncer l’arme acquise.

Les captures binaires intermédiaires des trois combats D9 fermés ont été
archivées et compressées : analysis/c0046-d9-intermediate-captures.
cleanup_closed_d9_captures.py a supprimé24934080 octets bruts,14503733
nets libérés. Tous les fichiers déjà référencés par les archives canoniques,
les captures finales et tous les PNG restent en place. La revérification
idempotente de l’archive ballon passe encore après ce ménage. Ne pas répéter
ce nettoyage dans les mêmes sorties. Pour un ancien binaire intermédiaire,
utiliser evidence depuis la racine globale avec le chemin complet du manifeste
ou restaurer l’objet compressé ; aucune donnée n’est perdue. Les captures du
palais et PAL actifs n’ont pas été touchées.
L’archive ballon est figée ; archive_d9_finish.py sait désormais revérifier
une archive existante sans la réécrire. Il vérifie tous les objets/hashes,
le même rapport et toutes les sources ; seul le journal de points du
lecteur partagé peut avoir grandi avec le même préfixe exact. Le premier
archivage et un second appel idempotent sont passés. La suite97858 peut
ainsi refaire son audit/archivage ballon après les douze points D9 sans
écraser ce jalon ni échouer sur un dossier déjà présent.

La préparation de la suite du palais est aussi faite (non exécutée) :
prepare_palace_final.py génère six contrôleurs/audits pour mécanismes,
gardien7C, GoldenAxe2, DeathAdder6D, générique et intro. archive_palace.py
attend rapports c0046 passés et flux froids terminés avec2/4/5/6/11points
pour entry/giant/inner/guardian/final. replay_c0047_palace.py rejoue un jalon
c0046 déjà audité sur c0047, avec comparaison RAM entière/PNG à sa preuve.
Après réussite et fermeture de la session97858, lancer finish_palace.py
depuis la racine : archives entrée/géant, trois suites avec leurs audits
et archives, rejeu c0047 final, puis branche réelle sauvegarde/Continue.
Ne pas lancer cette suite avant le rapport cold_palace_giant_c0046 passé.

prepare_candidate_save.py est exécuté après prepare_palace_entry.py.
Il crée validate_candidate_game_written_save_c0046.py et adapte uniquement
le contrôleur privé continue_after_d9_c0046.py (encore non lancé). Tous
les contrôles du validateur original précédant la publication du rapport
sont identiques octet par octet ; seule la recherche dans versions/index.json
est remplacée par une identité c0046/SHA explicite et un rapport candidat.
Le projet isolé n’a pas d’index de versions de production ; aucun numéro
fictif n’est ajouté. La branche de sauvegarde n’a pas encore été exécutée.

La fin du palais est aussi mise en attente : after_palace_entry.py
--wait-for-pid50460, session70465. Le superviseur tient le handle exact
du processus de la session97858 ; il attend son code0 avant de lancer
finish_palace.py. Aucun appel parallèle manuel de finish_palace.py : il
est déjà programmé derrière les audits D9/entrée/géant. Au premier échec,
les attentes se terminent en erreur sans relancer ni effacer les sorties.
Surveiller les sessions44962 (D9),97858 (audits/D9/c0047/entrée/géant),
70465 (suite palais/finale/sauvegarde), et revalider les processus réels.


Historique de la fin D8 (clos) : continue_d8_finish_c0046.py dans
validation/c0046-campaign01/isolated/project. Cette branche continue sur
c0046 puis chaque jalon est rejoué sur c0047. Journaux et sources :
validation/c0046-d8-sources/main-sources dans ce projet, preuves indépendantes
partagées dans son sous-dossier cold-stream. Les huit premières étapes sont
terminées, auditées et archivées : analysis/d8_approach_c0046_report.json,
archive c0046-d8-approach. Dernier point264942,salle1A6,88PV,72PM,une clé,
25 pièces,clé du voleur possédée. Les mécanismes distants et le passage Terre
passent ; le gardien7A vaincu reste absent. Le boss6B n’est pas entré par
ce seul rapport. Le pilote a lancé close_assisted_approach pour le retrait
de protection avant196 ; vérifier le processus réel pour la suite.
Onze étapes au total : reprise après le
gardien, sept propositions de recettes source vers la clé du voleur et
l’antichambre, retrait de protection, boss6B à80PV puis retour extérieur29.
Les recettes ne fournissent que des actions ; aucune ressource ni état ancien
n’est importé. L’audit d’approche est déjà exécuté ; ne pas recréer son archive.
Après succès complet lancer summarize_d8_campaign_c0046.py dans le projet, et archive_d8_finish.py
à la racine. Rejeu final : replay_c0047_d1.py auto --dungeon 8.
Les générateurs prepare_d8_entry.py et prepare_d8_finish.py
et prepare_d7_finish.py sont déjà exécutés ; ne pas les relancer.
Les scripts de préparation D7 et resume_d7_sentinels.py sont déjà exécutés ;
ne pas les relancer. L’audit final utilise south02 dans ses trois conditions
(liste, possession bateau, condition de trajet sud). south01 reste un essai rejeté.
Les huit points du parcours corrigé sont dans run-c0046-d7-recovered03-02,
les deux premiers points (trajet
B5 et don10) restent dans run-c0046-d7-02/cold-stream. Les scripts de reprise
emploient un adaptateur privé du combat restreint à B5→A5 et au préfixe service,
sans changement ROM. La première tentative de cet adaptateur a échoué avant
toute émulation sur la restriction donjon ; recovered03 est la vraie reprise.
Les audits préparés combinent les deux lecteurs froids et l’ouverture A5.
Avec38 pièces au départ, le don B5 de10
permet la clé à40 chez A5 ; le pilote conserve les prix réels et choisit94
si son solde réel atteint60. Aucun argent ni objet n’est importé.
L’ancien seuil50 du pilote V317 est adapté à30, minimum avant don pour
la boutique à40. Après le succès, lancer summarize_d7_prep_c0046.py dans le
projet puis validation/c0046-campaign01/archive_d7_prep.py à la racine.
Ne pas annoncer de gardien ou septième cristal sur cette seule préparation.
Ne pas relancer les scripts de préparation : leurs fichiers existent déjà.
adapt_d6_resumed_audit.py est aussi déjà exécuté. Le lecteur de preuves
revérifie la présence du résultat aux limites de délai et de sortie du
processus ; quatre tests de cette course passent (test_cold_replay_wait.py).
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
