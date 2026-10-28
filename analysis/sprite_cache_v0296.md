# v0296 : réutilisation des tuiles masquées et corde du troisième donjon

La ROM de 2 Mio `3446f41f` évite de recréer une tuile déjà masquée pendant
la même préparation d'image. La clé contient le numéro de tuile source et
les huit bits de lignes visibles. Les huit entrées du cache sont locales
à cet appel ; aucun résultat n'est conservé entre deux images, dont les
motifs peuvent avoir changé. Le numéro de clone peut changer, ses pixels
et les attributs de couleur et de retournement doivent rester identiques.

Les corps de production v295/v296 sont compilés dans le test hôte :
133 120 cas, 19 698 cas réutilisant des clones, 42 006 transferts évités.
Les sorties comparées sont les métadonnées des sprites, leurs huit lignes
de pixels et le statut de débordement. Les lectures du port VRAM y sont
simulées ; les motifs déjà en attente de transfert varient selon la ligne.
Le test natif séparé compare 108 images de sprites physiques, sans écart :
six cas dans chaque région, incluant chevauchement, seize acteurs,
coupure haute/basse et terminaison de liste.

Le profil de salve en boucle native passe de 12 à 10 travaux de tuiles
à l'image 2909 en mode auto, de 13 à 11 avec l'option PAL. Cependant,
les 36 écarts de deux images physiques restent présents dans le segment
profilé. **Ce changement ne corrige pas encore le ralentissement.**
La durée mesurée inclut les interruptions et l'attente du VDP ; elle
ne constitue pas un coût intrinsèque des seules instructions du masque.

Les relectures froides sur cette ROM retrouvent :

- Deux cristaux et la sortie D6 : 37 128 images, 31/48 PV, une clé et hache équipée.
- Entrée du troisième donjon en 1F8 : 40 308 images, 31/48 PV.
- Corde acquise en 1F4 : 45 394 images, 48/48 PV, sans troisième cristal.

Les aides de test ne modifient que le compteur de protection durant les
approches. Elles ne fournissent ni soin, ni clé, ni équipement. Les combats
des deux premiers boss et leurs retours se déroulent sans aide.
Chaque étape possède une relecture indépendante avec 65 536 octets de
RAM et PNG final exacts. Le profil de pile sur le parcours jusqu'à D6
observe un minimum F764, une limite de tas F600 et 356 octets de marge.
Cela ne prouve pas les autres parcours de la campagne.

Les deux tentatives ultérieures contre le boss 69 en 1C3 sont des défaites,
avec contrôle ordinaire puis recherche prudente de commandes. Elles ne
sont pas des preuves de victoire ; le troisième cristal reste ouvert.

[Rapport et empreintes](sprite_cache_v0296_report.json),
[test hôte](sprite_mask_cache_host_v0296_report.json),
[pixels dans les ROMs natives](sprite_mask_cache_gameplay_v0296_report.json),
[coût de rendu mesuré](burst_render_cost_cost-v0296_report.json).

La suite de la campagne, la fin et la fidélité complète du rythme,
de la vidéo et de l'audio restent à établir.
