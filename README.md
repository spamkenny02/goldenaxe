# Golden Axe Warrior â€” portage Mega Drive

Reconstruction de Golden Axe Warrior depuis la ROM Master System fournie,
puis portage de sa logique Z80 en code natif 68000 avec SGDK.
La fidÃ©litÃ© Ã  la Master System passe avant les amÃ©liorations.

<!-- ROM-RELEASE:START -->
**Version courante : v0309 â€” 2048 Kio.**

[TÃ©lÃ©charger la ROM v0309](versions/v0309-7270576d/gaw-megadrive-v0309.bin) Â· [Toutes les versions](versions/README.md)

ContrÃ´les ciblÃ©s rÃ©ussis ; portage complet encore non validÃ©.

SHA-256 : `7270576d6eeb2aee641776a3e364f2f3f320711d70bb91a566d7578161261049`
Checksum Mega Drive : `4080`
<!-- ROM-RELEASE:END -->

## Ã‰tat du portage

La **v0309 regroupe les transferts du palais dans la file VBlank existante**.
Le test SMS/MD conserve les289 images et tous les decalages de la secousse.
La reprise froide v0309 valide le premier cristal,hache,huile,fee et les
trois cles du deuxieme donjon,avec40/40PV. Les quatre relectures independantes
reproduisent toute la RAM et l'image. L'ancienne suite de touches diverge apres cette entree ; la suite
utilise un controleur adapte. Les neuf cristaux ci-dessous restent une preuve
v0306. Voir [le point de reprise v0309](analysis/palace_rebase_v0309_report.json).

La **v0308 restaure l'ouverture du passage vers le palais apres les neuf
cristaux**. Le test controle SMS/MD reproduit les289 images,les neuf amplitudes
de secousse et chaque changement de decalage. Avec huit cristaux,le passage
reste ferme. Voir [le correctif du palais](analysis/palace_gate_v0308.md).
Ce controle utilise un scenario isole ; le parcours complet sur la version courante reste a valider.

La **v0306 restaure le HUD aprÃ¨s les fenÃªtres dâ€™objet et de cristal** et
affiche les neuf indicateurs de cristal selon la table SMS. Les comparaisons
PAL/NTSC couvrent 22 scÃ©narios, 44 images aprÃ¨s fermeture et les fenÃªtres
avant fermeture : carte physique du HUD et tuiles utilisÃ©es conformes.

Le parcours courant valide les **neuf cristaux et le retour dehors en EB**,
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
La fin,les sauvegardes et la fidelite globale restent a valider.
La note [REPRISE_CODEX.md](REPRISE_CODEX.md) contient le point de reprise courant.

Les **21 Ã©tapes validÃ©es du sixiÃ¨me donjon** comprennent la sÃ©lection de la
hache par le menu, les clÃ©s, les mÃ©canismes, sept lancers de Terre, la cloche,
le combat et le retour. Chaque Ã©tape possÃ¨de une relecture froide indÃ©pendante
identique sur les 65 536 octets de RAM et le PNG final.
Les protections dâ€™approche sont retirÃ©es avant les boss principaux et ne sont
pas rÃ©activÃ©es pendant le retour. Aucun PV ni objet nâ€™est injectÃ©.
Les 128 mots du HUD final et les six indicateurs de cristal sont vÃ©rifiÃ©s.

Le dernier profil, jusquâ€™Ã  la sortie du huitiÃ¨me donjon Ã  **235 211 images**, observe
**402 octets de marge de pile**, sans corruption du tas. Le portage complet,
la fin et la fidÃ©litÃ© audiovisuelle globale restent Ã  valider.
Voir le [huitiÃ¨me cristal](analysis/d8_campaign_v0306.md),
le [septiÃ¨me cristal](analysis/d7_campaign_v0306.md),
le [sixiÃ¨me cristal](analysis/d6_campaign_v0306.md),
le [cinquiÃ¨me cristal](analysis/d5_campaign_v0306.md),
le [parcours Feu et Ã©pÃ©e](analysis/fire_sword_v0306.md) et le
[correctif du HUD v0306](analysis/reward_hud_v0306.md).

L'approvisionnement du **septiÃ¨me donjon est aussi validÃ©** : deux dons de
30 piÃ¨ces, achat rÃ©el d'une clÃ© pour 60, ouverture de la porte et premiÃ¨re clÃ©
rÃ©cupÃ©rÃ©e en 1CB. Huit relectures indÃ©pendantes reproduisent la RAM et l'image
finales. Cette Ã©tape conserve les six cristaux et s'achÃ¨ve Ã  **72/80 PV**.
Une premiÃ¨re branche de test qui effaÃ§ait le dÃ©lai des dÃ©gÃ¢ts de terrain est
exclue ; le trajet retenu prÃ©serve ce dÃ©lai. Aucun changement de ROM.
Voir [l'entrÃ©e du septiÃ¨me donjon](analysis/d7_supplies_v0306.md).

La suite valide le **combat intermÃ©diaire du septiÃ¨me donjon sans protection**,
vaincu avec **80/80 PV**, puis la **rÃ©cupÃ©ration du bateau**. Ce jalon
sâ€™achÃ¨ve en 1D5, Ã  **80/80 PV, 72/72 PM et deux clÃ©s**, avec six cristaux. Dix nouveaux
checkpoints reproduisent toute la RAM et l'image finale. Les 128 mots du HUD
aprÃ¨s la fenÃªtre du bateau et les six indicateurs de cristal sont vÃ©rifiÃ©s.
La protection d'approche avait repris aprÃ¨s le combat intermÃ©diaire ; son
retrait avant le boss principal est vÃ©rifiÃ© dans la phase suivante. L'essai
sud sans protection mort en 1B7 est conservÃ© sÃ©parÃ©ment. Voir [le combat intermÃ©diaire et le bateau](analysis/d7_progress_v0306.md).

Le **septiÃ¨me cristal et le retour extÃ©rieur sont validÃ©s**. Le boss principal
est vaincu Ã  l'Ã©pÃ©e longue sans perte de PV pendant le combat. La protection
est retirÃ©e 28 images avant son dÃ©but et reste dÃ©sactivÃ©e pendant le retour.
Sept nouveaux checkpoints reproduisent toute la RAM et l'image finale ;
157 sÃ©quences prÃ©dites sont vÃ©rifiÃ©es. Le HUD final affiche les sept indicateurs
de cristal. Les deux derniers donjons, la fin et la fidÃ©litÃ© globale restent
Ã  valider. Voir [le septiÃ¨me cristal et la sortie](analysis/d7_campaign_v0306.md).

Lâ€™**entrÃ©e du huitiÃ¨me donjon et son combat intermÃ©diaire sont validÃ©s**.
Le passeur prÃ©lÃ¨ve rÃ©ellement 10 piÃ¨ces ; une sortie/rentrÃ©e ordinaire permet
de rÃ©soudre un ennemi hors de portÃ©e sur lâ€™approche. La protection est retirÃ©e
avant lâ€™entrÃ©e en 1C9. Lâ€™ennemi de 50 PV est vaincu Ã  lâ€™Ã©pÃ©e longue, avec un seul
coup encaissÃ©. Six checkpoints reproduisent toute la RAM et lâ€™image finale ;
215 sÃ©quences de combat sont vÃ©rifiÃ©es. Le boss principal et le huitiÃ¨me
cristal sont validÃ©s dans la phase suivante. Voir [lâ€™entrÃ©e et le combat intermÃ©diaire du huitiÃ¨me
donjon](analysis/d8_progress_v0306.md).

La **clÃ© des voleurs, le huitiÃ¨me cristal et la sortie sont validÃ©s**. Les
mÃ©canismes et le passage avec Terre sont actionnÃ©s par les boutons du jeu.
Le boss principal est vaincu Ã  lâ€™Ã©pÃ©e longue sans coup encaissÃ©. Le garde
est retirÃ©31 images avant le combat et reste dÃ©sactivÃ© pendant le retour.
Onze nouveaux checkpoints reproduisent toute la RAM et lâ€™image finale ;
425 sÃ©quences prÃ©dites sont vÃ©rifiÃ©es. Les 128 mots du HUD et les huit
indicateurs de cristal sont contrÃ´lÃ©s. Le neuviÃ¨me donjon, la fin et la fidÃ©litÃ©
globale restent Ã  valider. Voir [le huitiÃ¨me cristal et la sortie](analysis/d8_campaign_v0306.md).

La **v0305 corrige le blocage des escaliers entre piÃ¨ces intÃ©rieures**.
Chez les marchands de C7, il est maintenant possible de monter de la piÃ¨ce
1F vers la piÃ¨ce 0F, de rÃ©cupÃ©rer lâ€™huile, de redescendre et de ressortir.
Une exclusion du dÃ©filement de toutes les piÃ¨ces intÃ©rieures bloquait ce
passage ; le gestionnaire de bordure SMS ne comporte pas cette exclusion.

Validation de cette correction :

- Le blocage est reproduit sur v0304 et absent sur v0305. Les comparaisons
  SMS/MD en PAL et NTSC retrouvent le parcours 1F â†’ 0F â†’ 1F â†’ C7,
  lâ€™huile, 17 valeurs sÃ©mantiques dâ€™inventaire et les 160 cellules finales.
  Ces comparaisons utilisent une position intÃ©rieure de test explicite.
- Un parcours sÃ©parÃ© depuis une nouvelle partie rÃ©cupÃ¨re lâ€™huile et revient
  dehors sans modification de RAM ni import de sauvegarde. Les deux Ã©tapes
  sont rejouÃ©es : les 64 Kio de RAM et le PNG final sont identiques.
- Le profil de pile avant chaque instruction couvre les 4 677 images de ce
  parcours. La marge observÃ©e est de 666 octets ; cette mesure ne couvre pas
  encore la campagne entiÃ¨re sur v0305.

DÃ©tails et limites : [rapport de la v0305](analysis/indoor_stairs_v0305.md)
et [rÃ©sultats vÃ©rifiables](analysis/indoor_stairs_v0305_report.json).

La suite sur v0305 confirme maintenant le **premier cristal et le retour
Ã  lâ€™extÃ©rieur en B9, Ã  28/32 PV**, avec lâ€™huile conservÃ©e. La protection
dâ€™approche est retirÃ©e 72 images avant le premier combat du boss et ne reprend
pas pendant le retour. Quatre relectures froides reproduisent toute la RAM
et le PNG final. Le profil de pile de cette branche, jusquâ€™Ã  17 482 images,
observe 466 octets de marge. Voir le [rapport du premier donjon](analysis/d1_oil_v0305.md).
Cette vÃ©rification ne valide pas encore les donjons suivants sur v0305.

La **hache, la premiÃ¨re fÃ©e de vie, le deuxiÃ¨me cristal et sa sortie** sont
Ã©galement vÃ©rifiÃ©s sur v0305. Le retour finit en D6 Ã  31/48 PV, avec une clÃ©,
la hache Ã©quipÃ©e et lâ€™huile conservÃ©e. Douze Ã©tapes disposent de relectures
RAM/PNG exactes. La protection dâ€™approche se termine 57 images avant le
combat du deuxiÃ¨me boss et ne reprend pas au retour. Le profil de pile
jusquâ€™Ã  40 562 images observe 450 octets de marge. Voir le
[rapport du deuxiÃ¨me donjon](analysis/d2_campaign_v0305.md).

Le **troisiÃ¨me cristal et le retour en extÃ©rieur 62** sont maintenant
vÃ©rifiÃ©s sur v0305, Ã  56/56 PV, avec la corde obtenue dans son donjon.
Le mÃ©canisme original de la salle 1E3 ouvre le passage avant le boss ; cette
salle est traversÃ©e avec ses ennemis encore prÃ©sents. Quatre relectures
RAM/PNG sont exactes, et aucune protection ne reprend aprÃ¨s le dÃ©but du
combat. Le profil de pile jusquâ€™Ã  55 110 images observe 450 octets de marge.
Voir le [rapport du troisiÃ¨me donjon](analysis/d3_campaign_v0305.md).

Le **quatriÃ¨me cristal et le retour en extÃ©rieur 10** sont Ã©galement
vÃ©rifiÃ©s sur v0305, Ã  50/64 PV. Le parcours obtient normalement 50 cornes,
achÃ¨te Terre, dÃ©gage deux passages, rÃ©cupÃ¨re le canoÃ« et utilise le
tÃ©lÃ©porteur. Quatorze relectures RAM/PNG sont exactes ; la protection cesse
avant le boss et ne reprend pas au retour. Voir le
[rapport du quatriÃ¨me donjon](analysis/d4_campaign_v0305.md).

Le dÃ©faut visuel du HUD documentÃ© sur v0305 est corrigÃ© dans la v0306.
Les rapports v0305 ci-dessus conservent leur pÃ©rimÃ¨tre historique.

## Campagne et travail restant

Les sept premiers cristaux et leurs sorties ont Ã©tÃ© validÃ©s sur **v0304**.
Dans le huitiÃ¨me donjon, la clÃ© des voleurs et le chemin vers le boss sont
atteints. Les approches comportent une protection de test dÃ©clarÃ©e, retirÃ©e
avant chaque boss principal ; les adversaires intermÃ©diaires de D7 et D8
ont Ã©tÃ© abordÃ©s avec cette protection. Le premier essai du huitiÃ¨me boss
se termine par une dÃ©faite : sa victoire reste Ã  valider.

Ces rÃ©sultats restent propres Ã  v0304. La relecture de ses commandes sur
v0305 diverge et se termine par une mort au cinquiÃ¨me boss ; elle ne valide
pas la campagne sur la nouvelle ROM. Les parcours doivent Ãªtre poursuivis
et adaptÃ©s sur cette version.

Les routines dâ€™acteurs utilisent encore le gÃ©nÃ©rateur alÃ©atoire SGDK.
Le raccordement au hasard SMS et Ã  sa phase globale reste Ã  faire.
La suite des boss, le dernier donjon, la fin, les sauvegardes et la fidÃ©litÃ©
complÃ¨te vidÃ©o/audio/matÃ©riel ne sont pas encore validÃ©s.

Lâ€™[historique du README jusquâ€™Ã  v0304](analysis/readme_history_through_v0304.md)
conserve les Ã©tapes et leurs liens de preuve. Le [journal de recherche](analysis/world_next.md)
conserve les observations dÃ©taillÃ©es ; certaines entrÃ©es anciennes sont
supplantÃ©es par les rapports de versions plus rÃ©centes.

## ROMs et compilation

Chaque ROM diffÃ©rente conserve son numÃ©ro et son SHA-256 dans
[lâ€™index des versions](versions/index.json). Les fichiers racine
`gaw-megadrive.bin` et `gaw-title-megadrive.bin` pointent sur les mÃªmes octets
que la version courante. Les anciennes ROMs numÃ©rotÃ©es sont conservÃ©es.

Depuis ce rÃ©pertoire, avec SGDK, Java et Python disponibles :

```powershell
.\build.ps1
python tools/verify_git_roms.py
```

Les outils de validation mettent en cache les manifestes d'archives pendant
un processus et les rechargent si leur signature de fichier change. Les hashes
et la decompression restent controles a chaque lecture. Les trois auditsD9
produisent des rapports strictement identiques : voir [le controle du cache](analysis/evidence_manifest_cache_v0306_report.json).

`build.ps1` accepte `-Sgdk` et `-Java` pour sÃ©lectionner leurs emplacements.
Le vÃ©rificateur compare les ROMs locales avec les objets du dernier commit
Git : il sâ€™exÃ©cute aprÃ¨s lâ€™enregistrement de la livraison.

Code natif : [boucle et transitions](megadrive/src/main.c),
[acteurs](megadrive/src/actors.c). Les preuves volumineuses sont archivÃ©es
sans perte et vÃ©rifiÃ©es avant le nettoyage des fichiers gÃ©nÃ©rÃ©s.
