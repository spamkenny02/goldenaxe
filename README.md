# Golden Axe Warrior — portage Mega Drive

Reconstruction de Golden Axe Warrior depuis la ROM Master System fournie,
puis portage de sa logique Z80 en code natif 68000 avec SGDK.
La fidélité à la Master System passe avant les améliorations.

<!-- ROM-RELEASE:START -->
**Version courante : v0310 — 2048 Kio.**

[Télécharger la ROM v0310](versions/v0310-32fe75a6/gaw-megadrive-v0310.bin) · [Toutes les versions](versions/README.md)

Contrôles ciblés réussis ; portage complet encore non validé.

SHA-256 : `32fe75a653d7152f7cbf873a32f2ffef14234ea190885ae8a8235f2ccd10e071`
Checksum Mega Drive : `AFC5`
<!-- ROM-RELEASE:END -->

## État du portage

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

Les sept premiers cristaux et leurs sorties ont été validés sur **v0304**.
Dans le huitième donjon, la clé des voleurs et le chemin vers le boss sont
atteints. Les approches comportent une protection de test déclarée, retirée
avant chaque boss principal ; les adversaires intermédiaires de D7 et D8
ont été abordés avec cette protection. Le premier essai du huitième boss
se termine par une défaite : sa victoire reste à valider.

Ces résultats restent propres à v0304. La relecture de ses commandes sur
v0305 diverge et se termine par une mort au cinquième boss ; elle ne valide
pas la campagne sur la nouvelle ROM. Les parcours doivent être poursuivis
et adaptés sur cette version.

Les routines d’acteurs utilisent encore le générateur aléatoire SGDK.
Le raccordement au hasard SMS et à sa phase globale reste à faire.
Ces limites concernaient le parcours v0304 décrit ci-dessus. Le scénario
contrôlé v0309 valide désormais le palais et la fin ; les sauvegardes,la
campagne froide courante complète et la fidélité vidéo/audio/matériel restent ouvertes.

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

Les outils de validation mettent en cache les manifestes d'archives pendant
un processus et les rechargent si leur signature de fichier change. Les hashes
et la decompression restent controles a chaque lecture. Les trois auditsD9
produisent des rapports strictement identiques : voir [le controle du cache](analysis/evidence_manifest_cache_v0306_report.json).

`build.ps1` accepte `-Sgdk` et `-Java` pour sélectionner leurs emplacements.
Le vérificateur compare les ROMs locales avec les objets du dernier commit
Git : il s’exécute après l’enregistrement de la livraison.

Code natif : [boucle et transitions](megadrive/src/main.c),
[acteurs](megadrive/src/actors.c). Les preuves volumineuses sont archivées
sans perte et vérifiées avant le nettoyage des fichiers générés.
