# v0295 : variante7C et reprise de campagne

La ROM de 2 Mio b71a6bc6 raccorde le type7C de la salle11E a sa routine
SMS54D3/AB40, comme6A/6B, et publie ses collisions apres la simulation.
795 cas controles comparent les768 octets d'acteurs :501 cas de parent et
294 de projectiles, dont les128 candidats de placement et leurs rejets.
Les deux lectures LD A,R de placement recoivent des entrees explicites ;
ce test ne prouve pas le hasard global.

Sur les six comparaisons de production (6A/6B/7C, options auto/PAL), les
109 premieres images2800..2908 correspondent. Sur294,7C diverge des2800
car sa routine n'est pas executee. **Les cycles complets divergent encore
des2909** : apres la salve, la MD saute des iterations physiques. Le meme
resultat existe pour6A/6B sur294 ; ce n'est pas une regression de295.
L'observateur CPU en lecture seule mesure36 ecarts de deux images sur le
segment2880..3052 du type7C. Le cout de simulation et de rendu est a reduire ;
ni l'horloge initiale ni un ajustement des attentes du test ne corrigent ce fait.

La campagne froide sur295 retrouve les deux premiers cristaux et revient
enD6 a31/48PV en37128 images, hache equipee, une cle restante. Les gardes
de test sont regeneres selon les vraies transitions, retires71 et57 images
avant les premiers combats ordinaires des boss1 et2. Aucun soin ni equipement
n'est injecte ; l'invincibilite n'est pas livree dans la ROM.
La relecture independante retrouve les65536 octets de RAM et le PNG final.
La pile est observee a chaque instruction normale depuis l'image14 ;
minimumF798, limite du tasF600, marge observee408 octets sur ce parcours.

La route suivante atteint le troisieme donjon1F8 en40308 images a31/48PV,
avec trois coupes normales a la hache. Elle ajoute une nouvelle garde
d'approche vers le boss1C3, qui n'est pas encore atteint. Sa propre relecture
froide est exacte. Ce resultat ne valide pas le troisieme donjon.

[Rapport et empreintes](variant_7c_v0295_report.json),
[cas controles](burst_variant_7c_v0295_policy_report.json),
[diagnostic production](burst_variant_7c_v0295_diagnostic.json),
[baseline294](burst_variant_7c_v0294_baseline_diagnostic.json),
[mesure de cadence](burst_cadence_v0295_report.json).

La campagne restante, la fin, les rythmes globaux et l'ensemble video/audio
ne sont pas encore prouves sur cette version.
