# Golden Axe Warrior — portage Mega Drive

Reconstruction de Golden Axe Warrior depuis la ROM Master System fournie,
puis portage de sa logique Z80 en code natif 68000 avec SGDK.
La fidélité à la Master System passe avant les améliorations.

<!-- ROM-RELEASE:START -->
**Version courante : v0305 — 2048 Kio.**

[Télécharger la ROM v0305](versions/v0305-83dfaf69/gaw-megadrive-v0305.bin) · [Toutes les versions](versions/README.md)

Contrôles ciblés réussis ; portage complet encore non validé.

SHA-256 : `83dfaf697521ce97597af259835eccae70bde055e70f321176caad34f93a23c7`
Checksum Mega Drive : `C3B8`
<!-- ROM-RELEASE:END -->

## État du portage

La **v0305 corrige le blocage des escaliers entre pièces intérieures**.
Chez les marchands de C7, il est maintenant possible de monter de la pièce
1F vers la pièce 0F, de récupérer l’huile, de redescendre et de ressortir.
Une exclusion du défilement de toutes les pièces intérieures bloquait ce
passage ; le gestionnaire de bordure SMS ne comporte pas cette exclusion.

Validation de cette correction :

- Le blocage est reproduit sur v0304 et absent sur v0305. Les comparaisons
  SMS/MD en PAL et NTSC retrouvent le parcours 1F → 0F → 1F → C7,
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

**Défaut visuel identifié sur v0305 :** le HUD physique reste partiellement
remplacé par la fenêtre d’acquisition après les objets ou cristaux. Ces
preuves de progression ne valident pas ce rendu ; sa correction est en cours.

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
La suite des boss, le dernier donjon, la fin, les sauvegardes et la fidélité
complète vidéo/audio/matériel ne sont pas encore validés.

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

`build.ps1` accepte `-Sgdk` et `-Java` pour sélectionner leurs emplacements.
Le vérificateur compare les ROMs locales avec les objets du dernier commit
Git : il s’exécute après l’enregistrement de la livraison.

Code natif : [boucle et transitions](megadrive/src/main.c),
[acteurs](megadrive/src/actors.c). Les preuves volumineuses sont archivées
sans perte et vérifiées avant le nettoyage des fichiers générés.
