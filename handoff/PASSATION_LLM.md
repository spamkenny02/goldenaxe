# Passation du portage Golden Axe Warrior

## But et état réel

Portage fidèle de la Master System vers la Mega Drive, logique Z80 traduite en
68000 avec SGDK. Améliorations graphiques seulement après la fidélité.
La V320 est une version de développement jouable ; elle n’est pas une
certification de fidélité complète, de PCM ou de fonctionnement sur matériel.
Il ne s’agit pas d’un émulateur Z80 exécutant le jeu SMS dans la ROM MD.

La ROM publiée et attendue par ce paquet est :
`9e5b0abed80678ce864a0bb796c17e97047d1d34e5227a5275bf9336129ceaff`, 2 Mio, B0A2.
La ROM SMS originale fournie porte le SHA-256 :
`852e068e331dbfb01b9c38a62eecf81ce5b9f0f1bd10fff497117bd885c716c9`.

## Où intervenir

- `megadrive/src/main.c` et ses `.inc` : orchestration du jeu distribué.
- `megadrive/src/ending.inc`, `ending_credits.inc`, `ending_data.c` : fin et générique.
- `megadrive/overlays/credits_border.s` : correction 68000 effectivement livrée en V320.
- `megadrive/src/source_*` : routines natives modélisant les comportements et
  horloges SMS ; certaines sont expérimentales et ne sont pas sélectionnées en ROM.
- `analysis/` : rapports ciblés, avec portée et limites, sans les gros caches.

## Construction particulière de la V320

Les sources SGDK reconstruisent exactement la base auditée V319 :
`d3ea2a83ea24ed8a0d3c9857f9fbe70d000a4f73358452c1887f40e78966c56e`.
Le build assemble ensuite 124 octets de code 68000 à 1F0000 et redirige trois
instructions contrôlées : deux entrées du générique et sa sortie commune.
La bordure basse supplémentaire de 16 pixels MD est masquée pendant le générique,
puis remise à zéro ; les 192 lignes SMS et l’arithmétique du défilement restent
inchangées. Tous les autres octets de jeu restent ceux de la base, hors checksum.

Les adresses de branchement sont fixes et vérifiées avant modification.
Une modification générale du C peut déplacer le code avec le LTO de SGDK :
le build refusera alors l’ancienne implantation. Il faut réexaminer les points
de branchement et valider la nouvelle construction, plutôt que supprimer
les vérifications de SHA ou appliquer aveuglément ces adresses à un autre binaire.
Des candidats recompilés intégralement ont fait diverger un parcours enregistré
vers le huitième donjon ; ils n’ont pas été publiés. La V320 garde la disposition
binaire de jeu déjà validée.

## Contrôles déjà réalisés

- Parcours enregistrés complets NTSC et PAL : neuf cristaux, Golden Axe,
  Death Adder, générique, puis retour à l’introduction.
- Protection de test sur certaines approches, retirée avant les combats de boss.
  Aucun import de progression ou de sauvegarde pour ces campagnes.
- 7424 états de générique par région : image des 192 lignes identique à V319,
  avec suppression des lignes fantômes dans la bordure MD.
- Nouvelle partie après le générique testée en PAL et NTSC : progression à zéro,
  héros jouable et masque de bordure retiré.

Consulter les rapports `analysis/v320_credits_report.json` et
`analysis/v320_followup_tests_report.json` pour les preuves et limites exactes.
Les anciens captures, outils d’émulation et gros jeux de données ne sont pas
inclus ; les références historiques restent dans le dépôt Git :
https://github.com/spamkenny02/goldenaxe

## Travail expérimental restant

La composition native d’introduction avec statut VDP calculé en temps réel reste
non sélectionnée dans la ROM publique. Après regroupement des écritures SAT et
suppression de rollbacks sur copies privées, le helper coûte encore environ
69..77 images MD en NTSC et 58..64 en PAL dans les diagnostics, au-dessus du
budget de la scène source. Ces nombres ne sont pas les FPS du jeu.

Ne pas activer cette composition telle quelle. Les motifs et le coût des appels
à l’horloge restent des cibles de réduction. Les dates IRQ d’introduction doivent
encore être auditées indépendamment, le démarrage natif continu validé et la
livraison vidéo/audio physique mesurée. Les rapports `v320_irq_workspace_report`
et `v320_sat_runs_report` détaillent ce qui a réellement été comparé.

Les scripts `BUILD_V320.ps1` et la chaîne embarquée servent à reproduire la V320
avant toute modification. Commencer par obtenir le SHA attendu.
