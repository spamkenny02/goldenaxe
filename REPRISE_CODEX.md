# Reprise du portage dans un autre compte Codex

Etat de cette note : 2 novembre 2026. Lire aussi README.md et les rapports plus recents eventuellement ajoutes depuis cette note. Le changement de compte ne termine pas l'objectif du portage.

## Etat courant : v0309

ROM v0309,7270576d6eeb2aee641776a3e364f2f3f320711d70bb91a566d7578161261049,
checksum4080. Les transferts du palais utilisent les bits2/4 du travail VBlank
existant ; pas de nouveau test IRQ quand aucune video n'est en attente.
Le controle SMS/MD du palais reste exact sur289 images et chaque decalage.

Etat courant : quatre cristaux depuis Nouveau Jeu, sortie D4 image101777,
exterieur10,62/64PV,48PM,0cle,Terre1 et canoe acquis ; corde et huile conservees.
Checkpoint validation/natural-dungeon-combat/md-auto-v0309-d4-exit01.
Boss6A commence91391,hero56PV/hurt0 contre30PV ; victoire sans degat subi.
Dernier write91328,aucune aide au combat ni au retour. Quinze relectures
RAM65536/PNG exactes ; HUD physique apres canoe,cristal et sortie exact.
Rapport analysis/d4_campaign_v0309_report.json et .md. Sources pilotes figees
validation/v0309-d4-sources. Pipeline82695 termine ; aucun job actif.
La preparationD5 ci-dessous prolonge cette sortie ; ne pas reutiliser de SRAM synthetique.

PreparationD5 terminee : Feu appris contre huile108195,magie72 ; epee longue2
obtenue111709,entree186 a116210. Cle176117326,Terre176:4A->166 a117777,
bottes157 a120893. Sortie de ravitaillement49 a121571,60/64PV,64PM,16cornes,
0cle,bottes1 et hero_attack_speed1,hache selectionnee. BossD5 jamais entre,
episode5 pending163,protection d'approche toujours declaree. Aucun importSRAM.
Checkpoint validation/natural-dungeon-combat/md-auto-v0309-d5-supply-exit01.
Rapports analysis/fire_sword_v0309_report.json et d5_progress_v0309_report.json.
Onze relectures RAM65536/PNG exactes,HUD physique apres Feu,epee,bottes,sortie.
Pipelines75907,83445 et14467 termines ; aucun job actif. Suite : dons30 A1/B4,
cle60 et soin chez94,puis retourD5,Terre153:44->162 et contact162->172.
Ce sont des propositions historiques v0306 a revalider. Ne pas reactiver un
nouvel episode : l'episode5 existe deja et attend toujours le boss163.

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
