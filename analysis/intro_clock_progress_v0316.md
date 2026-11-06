# Travail sur l’horloge et la publication de l’intro — après v316

La ROM publique reste **v0316**. Neuf ROMs privées ont été compilées et
comparées à l’original SMS, sur 6500 images sans entrée par région.
Aucune n’est promue en v317 : des régressions de pixels restent mesurées.
Les preuves des menus du candidat 08 ne sont pas transférées par supposition
aux candidats 10..18.

## Corrections et origine

La SMS utilise C02F pour le feu et les acteurs. Cette horloge avance sur les
interruptions complètes demandées par 0F09, tandis que les interruptions audio
pendant les transferts ne l’avancent pas. Le natif utilisait directement vtimer,
qui compte toutes les images. Un observateur Z80 en lecture seule mesure les
frontières des chargements ; ses 3800 états d’horloge par région correspondent
à ceux du cœur officiel. Les sources du cœur sont restaurées après compilation.

Le candidat 11 remplace l’horloge de toutes les animations sans corriger leurs
chargements. La comparaison montre une dégradation : cette généralisation est
rejetée. Le candidat 12 réserve la nouvelle horloge au feu, avec le callback
actif avant le premier chargement ; le candidat 13 publie sa palette à la
prochaine interruption complète au lieu de la changer immédiatement.

La routine SMS 0D59 copie 768 octets de texte. Le transfert natif de toute la
carte convertissait et envoyait aussi les lignes de l’image, ce qui pouvait
retarder le texte jusque dans le balayage visible. Le candidat 10 limite ce
transfert aux 12 lignes de texte. Les variantes 14 et 17 explorent une copie
DMA en file à deux moments différents ; leurs régressions restent conservées.
Les variantes 15 et 16 isolent le feu depuis les sources publiques, sans retirer
les travaux de menus archivés. Le candidat 18 reprend le 13 et retarde également
la publication du fondu à la prochaine interruption complète.

## Mesures du candidat 18

| Région | Pixels différents de la SMS sur v316 | Sur candidat 18 | Pixels améliorés | Pixels dégradés |
| --- | ---: | ---: | ---: | ---: |
| NTSC | 37352244 | 25792159 | 11585147 | 25062 |
| PAL | 30810098 | 25311392 | 5504826 | 6120 |

Ces sommes couvrent6500 images du viewport 192 lignes. Elles ne représentent
ni un pourcentage de fidélité du jeu entier, ni une validation des parcours.
Les couleurs DAC sont ramenées aux indices 2 bits SMS, et chaque image est
observée. Les différences et les erreurs par image restent consultables.

L’état du lecteur audio (400 octets), la requête de bruitage et les huit
registres PSG sont identiques à v316 pour les 6500 images de chaque région.
Ce contrôle ne prouve pas l’identité des formes d’onde PCM à la SMS.
Le frontal propage désormais les erreurs de l’observateur vidéo au lieu de
laisser ctypes les ignorer ; une exception volontaire vérifie ce comportement.

## Suite nécessaire

- Résoudre les régressions raster restantes, notamment aux images NTSC 2993,
  4163 et 4523 et PAL 3546/3554 ; ne pas conclure sur la seule baisse de la somme.
- Traduire le chargement des scènes 2/3 et leurs quatre attentes complètes avant
  la révélation ; leur durée dépasse actuellement celle du chargement natif.
- Séparer la préparation SAT/palette de leur publication pour les acteurs.
- Remplacer le seed initial expérimental 22 par une continuité d’horloge couvrant
  aussi la reprise de l’intro après attente sur le titre. La mesure SMS à CE0
  vaut 20 au premier démarrage ; les deux attentes de fin de copie absentes du
  chargeur natif expliquent les deux ticks ajoutés, sans certifier la réentrée.
- Revalider les menus sur le binaire retenu puis un nouveau parcours complet.
  Le RNG/rafraîchissement global et le matériel physique restent ouverts.

[Rapport et empreintes](intro_clock_progress_v0316_report.json) ·
[Patch du candidat 18](intro_clock_candidate18_v0316_crlf.patch) ·
[Archive avec ROMs et preuves](intro-clock-progress-v0316/manifest.json) ·
[Nettoyage après lecture intégrale](intro_clock_progress_cleanup_v0316_report.json)
