# Golden Axe Warrior — portage Mega Drive

Reconstruction de Golden Axe Warrior depuis la ROM Master System fournie,
puis portage de sa logique Z80 en code natif 68000 avec SGDK.
La fidélité à la Master System passe avant les améliorations.

<!-- ROM-RELEASE:START -->
**Version courante : v0309 — 2048 Kio.**

[Télécharger la ROM v0309](versions/v0309-7270576d/gaw-megadrive-v0309.bin) · [Toutes les versions](versions/README.md)

Contrôles ciblés réussis ; portage complet encore non validé.

SHA-256 : `7270576d6eeb2aee641776a3e364f2f3f320711d70bb91a566d7578161261049`
Checksum Mega Drive : `4080`
<!-- ROM-RELEASE:END -->

## État du portage

La **v0309 regroupe les transferts du palais dans la file VBlank existante**.
Le test SMS/MD conserve les 289 images et tous les décalages de la secousse.
Le parcours v0309 depuis Nouveau Jeu valide maintenant **quatre cristaux et
le retour du quatrième donjon**, à 62/64 PV, avec Terre et le canoë acquis.
Le quatrième boss est vaincu sans protection et sans dégât subi ; aucune
protection ne reprend au retour. Quinze relectures D4 reproduisent toute la
RAM et le PNG. Le HUD physique est vérifié après le canoë, le cristal et la sortie.
Voir [le quatrième donjon v0309](analysis/d4_campaign_v0309.md),
[le troisième](analysis/d3_campaign_v0309.md) et
[le deuxième](analysis/d2_campaign_v0309.md).

Le **scénario contrôlé du palais atteint maintenant la fin du jeu** :
géant et gardien sans protection,hache dorée,Death Adder,générique complet
et retour au flux titre. Le combat final commence à100PV contre90PV pour
le boss ; le héros gagne à48PV. Aucune écriture de test après le retrait de
l'invincibilité avant le boss. Les relectures du combat et de la fin
reproduisent les65536 octets de RAM et le PNG final.
Voir [Death Adder et la fin](analysis/controlled_palace_ending_v0309.md),
ainsi que les [mécanismes du palais](analysis/controlled_palace_phase3_v0309.md).

Ce scénario démarre avec **une SRAM synthétique dérivée du parcours neuf
cristaux v0306**. Il reste séparé de la campagne depuis Nouveau Jeu. La
campagne froide complète sur la version courante,les contenus optionnels,
la fidélité globale SMS et les essais matériels restent ouverts.

La **v0308 restaure l'ouverture du passage vers le palais apres les neuf
cristaux**. Le test controle SMS/MD reproduit les289 images,les neuf amplitudes
de secousse et chaque changement de decalage. Avec huit cristaux,le passage
reste ferme. Voir [le correctif du palais](analysis/palace_gate_v0308.md).
Ce controle utilise un scenario isole ; le parcours complet sur la version courante reste a valider.

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
