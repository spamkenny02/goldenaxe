# Scènes de l’intro : chargement, palette et plans graphiques

La production reste v316. Les huit ROMs de travail 19..26 et les preuves sont
archivées ; le candidat 26 conserve son binaire et son cache localement.
Les régressions mesurées restent ouvertes : aucun contrôle de publication
n’est déclaré réussi par la seule amélioration des totaux.

## Corrections du candidat 26

Le temps de chargement des images est calculé depuis le travail Z80 :
1005162 T pour la scène 2,1195746 pour la scène 3, avec le coût des interruptions
audio retiré du budget disponible. Les quatre attentes complètes des deux
copies 0EFA sont rétablies. L’initialisation des acteurs précède le chargement,
comme dans la SMS ; SAT et palette sont préparés après une attente complète
et publiés à l’attente complète suivante, sans publication aux IRQ audio.

La scène 2 conserve désormais sa palette d’image. Le callback SMS 1055 exécute
1061 puis retourne ; il ne passe pas dans la routine d’éclairs BE25, réservée
au callback 104A de la scène 3. Le natif appliquait à tort cette dernière aux
deux scènes, ce qui expliquait une grande partie de l’écart de couleur.

La révélation finale de la troisième scène est également corrigée : 0DA5
écrit deux octets aux plans 2/3, avance de quatre octets dans la VRAM, puis
fait tourner le masque de deux bits. Le natif n’écrivait que le plan 2, utilisait
un seul octet par ligne et tournait le masque une ligne sur deux. Les deux
flux compressés décodent chacun 1536 octets : le correctif les entrelace,
comme la source, puis ne convertit que les 192 tuiles réellement modifiées.

Le rythme du transfert utilise le coût de la boucle source : 1536×178−5+31
= 273434 T. Les passages suivants reprennent à V112 ; les 80 lignes avant V192
comptent comme temps de travail. Le premier passage et la cadence NTSC restent
à corriger complètement. Aucune horloge n’est forcée sur un enregistrement.

## Mesures liées au binaire

| Sur 6500 images par région | NTSC | PAL |
| --- | ---: | ---: |
| Images identiques à la SMS sur v316 | 1398 | 2003 |
| Images identiques sur candidat 26 | 6157 | 6213 |
| Pixels différents de la SMS sur v316 | 37352244 | 30810098 |
| Pixels différents sur candidat 26 | 1948330 | 522113 |
| Pixels améliorés | 35845158 | 30292807 |
| Pixels devenus moins fidèles | 441244 | 4822 |

Ces comptes couvrent les images effectivement émises, avec les niveaux DAC
ramenés aux couleurs SMS. Ils ne donnent aucun pourcentage de finition ou de
fidélité du jeu entier. Les erreurs par image et les cas défavorables restent
conservés dans le rapport ; les plus gros écarts NTSC touchent les éclairs.

En PAL, les 1800 images appariées de la scène 2 et les 1932 de la scène 3 ont une
horloge et un compteur identiques à la source. En NTSC, ce n’est pas encore
le cas : les pertes d’IRQ complètes pendant le travail de premier plan et
le début des masques restent à traduire. Les phases de chargement ne sont
pas toutes couvertes par la seule sélection des images appariées.

À l’image 4100, les 9216 octets des motifs de l’image finale correspondent à
la SMS dans les deux régions. Le candidat 22 avait 1811 octets différents.
Ce contrôle porte sur l’image finale en mémoire, sans certifier chaque
transfert intermédiaire ni la conversion matérielle des sprites.

Sur 6500 images par région, les 400 octets du lecteur audio, la requête de
bruitage et les huit registres PSG restent identiques à v316. Les PCM et
l’égalité de toute la musique avec la SMS ne sont pas certifiés par ce test.

Il reste à corriger le NTSC et les transitions, à vérifier la réentrée de
l’intro après attente sur le titre, les menus sur le binaire retenu, puis un
nouveau parcours complet. Le seed initial 22 reste provisoire. Le RNG global
et le matériel physique restent hors des validations de ce correctif.

[Rapport lié aux huit binaires](intro_actor_loading_v0316_report.json) ·
[Patch candidat 26](intro_actor_candidate26_v0316_crlf.patch) ·
[Archive complète](intro-actor-loading-v0316/manifest.json) ·
[Nettoyage vérifié](intro_actor_loading_cleanup_v0316_report.json)
