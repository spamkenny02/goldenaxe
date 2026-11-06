# ROM de travail c0029

[Télécharger gaw-megadrive-c0029.bin](gaw-megadrive-c0029.bin)

Cette version de développement corrige les menus et plusieurs erreurs de
traduction de l’intro. Elle est numérotée séparément des versions publiques
v0001..v0316 ; les alias de production restent sur v316.

SHA-256 : `c3fca1d60110b78d1ea2207974031401d1c7ed531c8695569e0281d8ffc70d74`

Checksum Mega Drive : `A7AF` · Taille : 2097152 octets.
Une recompilation sans cache produit exactement le binaire testé.

Les 6500 images du démarrage sans entrée ont été comparées à la SMS par région :
6355 images NTSC et 6381 PAL sont identiques, contre 1398/2003 sur v316. Les
horloges et compteurs des scènes 2/3 correspondent sur les images appariées.
Les états audio et registres PSG restent identiques à v316 sur ce démarrage.

Les contrôles de saisie du nom (210 cas), sélection/confirmation sonore,
270 images de menus, six retours d’inventaire et deux nouvelles parties
jusqu’au premier donjon passent. Les trajets utilisent les commandes normales,
sans injection de mémoire, sauvegarde importée ou invincibilité.

Des écarts visuels restent dans les révélations partielles des images et le
titre. La réentrée de l’intro, les phases d’IRQ ambiguës, le RNG global, un
nouveau parcours complet et le matériel physique restent à vérifier.
Le contrôle d’absence de régression de pixels n’est pas déclaré réussi :
il s’agit d’une ROM de travail disponible pour essai.

Les deux sources modifiées sont fournies dans [src/](src/). Le reste du projet
provient du commit `94d449be959ec4569111c085d446fc94bed4ed92`.
Pour reconstruire, appliquer [source.patch](source.patch) à une copie des
sources de ce commit, puis exécuter `build.ps1` avec SGDK. Le patch est vérifié
par reconstruction exacte des deux fichiers, et le binaire par un build propre.

[Mesures et limites complètes](../../../analysis/intro_text_irq_preview_c0029_report.json)
