# ROM de travail c0029 : attentes NTSC et couleurs de l’intro

[ROM numérotée et sources](../versions/candidates/c0029-c3fca1d6/README.md).
Les alias de production restent v316. Cette publication est une version de
développement ; elle ne déclare pas le portage complet ni le contrôle
d’absence de régression de pixels réussis.

## Changements

Le candidat 27 ajoute le troisième groupe de quatre couleurs écrit par la
routine SMS BE25, jusque-là omis dans le natif, et rétablit la couleur 31 de
la palette des sprites à 1, comme la ROM originale.

Les candidats 28/29 calculent le travail de chaque callback d’animation à partir
des branches Z80 : état des acteurs, pose, nombre de sprites et changement de
pose. Le premier essai surestimait de 20 T la fin d’une pose ; cette erreur de
calcul est corrigée dans 29. Le calcul final correspond à 5383 callbacks NTSC
et 5406 PAL appariés, sans différence mesurée. Les états non appariés et les
transitions de callback restent hors de cette affirmation.

Le transfert de texte 0384 est interruptible. Le travail entre le retour BB3
et la prochaine requête F09, après la première des deux copies, se décompose en :

`149+50+70+18+47+24708+20+17+16193+10+52+46+52 = 41432 T`

S’ajoutent 92 T par caractère et le travail du callback F32. L’interruption
complète est calculée par le module natif source_irq avec le travail réel du
lecteur audio. Une requête nécessite encore 187 T avant l’écriture de C02E.
Le sondage de palette a une granularité de 27 T ; le portage utilise une borne
basse couvrant la phase d’entrée et la fin du sondage B95. Seul un retard
certain ajoute une attente audio sans avancer l’horloge de l’animation.

L’observateur distingue le temps exécuté cumulé, utile pour soustraire les
interruptions des coûts, du raster physique Z80.cycles du cadre courant.
Le temps exécuté cumulé ne doit pas être réduit modulo une durée d’image pour
prétendre connaître ce raster. Le nouveau cœur est séparé, en lecture seule,
et les sources de l’instrumentation sont restaurées après sa compilation.
Ses 5950 états d’horloge par région correspondent à la trace du cœur officiel.

Les 130 prévisions du démarrage froid correspondent aux 65 lignes par région :
attente audio seule aux images 2992, 4162 et 4522 en NTSC, aucune en PAL. Deux
cas NTSC ont une phase théoriquement ambiguë : ils restent sans attente forcée.
Cela ne certifie pas toutes les phases possibles ni la réentrée de l’intro.

## Contrôles du binaire publié

La ROM c0029 et son build sans cache sont identiques :
`c3fca1d60110b78d1ea2207974031401d1c7ed531c8695569e0281d8ffc70d74`.
Checksum MD A7AF, taille 2 Mio. Le patch reconstruit exactement les deux sources
modifiées depuis le commit de référence indiqué dans metadata.json.

| Démarrage sans entrée : 6500 images | NTSC | PAL |
| --- | ---: | ---: |
| Images identiques à la SMS sur v316 | 1398 | 2003 |
| Images identiques sur c0029 | 6355 | 6381 |
| Pixels différents de la SMS sur c0029 | 233503 | 220758 |
| Pixels devenus moins fidèles à la SMS | 15393 | 4913 |

Les images sont comparées dans le viewport 192 lignes, après normalisation des
niveaux DAC. La baisse des erreurs ne supprime pas les régressions restantes.
Les compteurs et horloges correspondent sur les 1800 images appariées de la
scène 2 dans les deux régions et les 1917/1932 images de la scène 3 NTSC/PAL.
Ces comptes ne sont pas un taux de finition ou de fidélité globale du jeu.

Les 400 octets du lecteur audio, la requête de bruitage et les huit registres
PSG restent identiques à v316 sur 6500 images par région. Les formes d’onde
PCM ne sont pas comparées par ce contrôle. Les 9216 octets de l’image finale
de la troisième scène correspondent à la SMS à l’image 4100.

Les 210 premiers caractères saisis naturellement, 270 images sélectionnées des
menus, quatre cas sonores Nouveau Jeu/Continuer et six retours d’inventaire
passent sur ce binaire. Pour l’inventaire, les 124 premiers motifs sont comparés,
avec les quatre motifs animés distingués du décor fixe ; le framebuffer entier
n’est pas certifié par cette vérification.

Deux parties fraîches atteignent le premier donjon puis déplacent le héros,
avec 12 PV en NTSC et 8 en PAL, sans mort, modification de mémoire ou sauvegarde
importée. Le premier essai de ce contrôleur a utilisé par erreur la ROM v316
avec les symboles du candidat : il est conservé comme erreur du pilote et
exclu des preuves du candidat. Les deux essais corrigés sont liés à son SHA.

## Travail restant

Les révélations partielles et le titre gardent des écarts. Le premier seed 22
et la réentrée de l’intro après attente sur le titre restent à traiter.
Un nouveau parcours complet sur ce binaire, la fidélité du RNG/rafraîchissement
global et le matériel physique ne sont pas validés.

[Rapport, empreintes et cas défavorables](intro_text_irq_preview_c0029_report.json) ·
[Archive des essais et ROMs 27..29](intro-text-irq-preview-c0029/manifest.json) ·
[Nettoyage vérifié](intro_text_irq_preview_c0029_cleanup_report.json)
