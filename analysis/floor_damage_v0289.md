# v0289 : dégâts des sols dangereux

ROM : `1abcdb4735d8edaee1c6723522f8f5e2fbb77b044aba6c8e6c47761b0775a5f4`, 2 Mio, checksum `AC68`.

Le portage omettait les dégâts du contexte de terrain 4. La routine SMS
2EB6–2EDA ajoute quatre points aux dégâts en attente lorsque C305 vaut zéro.
Elle déclenche une protection de 48 ticks et l'effet sonore 91. Le passage
commun 2753/2768 puis 27CF applique la soustraction saturée après le
mouvement et le compteur de clignotement. Le sol seul ne fait pas reculer
le héros et ignore l'armure ; un contact simultané ajoute ses dégâts.
La réflexion d'un projectile supprime ses dégâts, mais conserve ceux du sol.
La v0289 rétablit ces règles dans la boucle native, sans aide distribuée.

## Vérifications

- 140 cas dans les boucles de jeu originales SMS et natives MD, en PAL et
  NTSC : 12 892 frames et douze champs identiques (PV, protection, état,
  indicateurs, compteurs, animation, position, vitesse, défense et terrain).
- PV initiaux de 1 à 96, protections 0/1/47/48/128/129, deux armures,
  contacts corporels sur sol sûr ou dangereux et réflexions de projectiles.
  Les assertions vérifient que les contacts et réflexions ont effectivement lieu.
- Sur le sol dangereux, les impacts seuls arrivent aux offsets 0/48/96 et
  enlèvent quatre PV. La garde de test 129 reste active dans les deux versions.
- Régression : 96 cas de déplacement et 64 frames de corde, PAL/NTSC.
  Les 204 octets des tables de marche compilées correspondent à la source.
- Premier donjon depuis le démarrage, sans injection, aide ni décès : entrée,
  hache, boss, cristal et sortie à 32/32 PV. Quatre relectures à froid
  reproduisent les 65 536 octets de RAM et l'image finale.
- Pile observée à chaque instruction jusqu'à la sortie, frame 16 569 :
  minimum F79C, limite du tas F600, marge observée de 412 octets.

Le rapport [consolidé](floor_damage_v0289_report.json) lie les preuves à la ROM.
Les premières tentatives de fixtures sont conservées : une sélection d'acteur
absente, puis un acteur gelé qui empêchait le contact, puis une défense dérivée
héritée du cas précédent. Seul l'essai 05 est crédité pour les contacts et
réflexions ; il synchronise la défense et affirme leurs effets réels.

## Limites

Les tests de terrain sont des situations contrôlées en RAM, pas encore un
parcours naturel sur sol dangereux. Ils ne prouvent pas la fidélité de tout
le framebuffer, du HUD, des formes d'onde audio ni du matériel réel.
Les donjons 2 et 3 réussis sur la v0287 restent des preuves historiques ;
la campagne complète, les chronologies globales et le flux RNG/R/IRQ restent
à vérifier sur cette version. Aucun pourcentage global n'est déduit de ces cas.

Les captures générées sont archivées sans perte avant nettoyage, avec SHA-256
et relecture intégrale. La ROM originale et toutes les ROMs numérotées restent
conservées. Voir le [manifeste](floor-damage-v0289/manifest.json).
