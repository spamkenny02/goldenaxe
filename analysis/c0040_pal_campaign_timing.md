# Rejeu PAL étendu de l’aperçu c0040

Après recalage de trois images à la première entrée du donjon 1, le rejeu
compare 37 champs de jeu sur 230 950 images. Le premier écart arrive
à l’image de référence 80 003, pendant le combat contre le boss 6A.
Les compteurs et positions des acteurs divergent tandis que les PV, la
position du héros, le générateur aléatoire et l’horloge logique concordent
encore. Les commandes enregistrées divergent ensuite jusqu’à la fin du rejeu.

L’observation en lecture seule du 68000 retrouve les captures RAM et PNG
du cœur standard. Les deux ROM sautent un appel à la simulation à l’image
de référence 80 001. La V318 saute aussi l’appel à 80 003, tandis que
c0040 exécute la simulation. Dans la V318, le masquage des sprites se termine trop tard pour les
deux interruptions. La routine VBlank consulte la file à 4 623 et
4 626 cycles maîtres des images 80 001 et 80 003. Le jeu signale que
l’image est prête à 102 119 et 82 606 cycles. Le transfert est donc
reporté à l’image suivante dans les deux cas.

Dans un essai contrôlé, la ROM Master System PAL charge la salle 180,
puis reprend l’état des acteurs qui précède l’écart. À chacune des 16
phases testées, dont la phase 193 de l’écart, elle produit exactement les
768 octets d’acteurs obtenus par c0040. Le rejeu d’un combat SMS enregistré
en NTSC retrouve la RAM et les pixels finaux. Les 480 compteurs de
projectiles admissibles avancent d’une unité, sur 60 images distinctes.
Le test suivant charge la salle 180 sur la Master System PAL, puis
laisse le combat se dérouler sans écriture de test. Aux images 3 562,
3 808 et 4 054, le boss lance ses huit projectiles. Le compteur de
chaque projectile baisse d’une unité à chacune des sept images suivantes.
Les deux ROMs Mega Drive sautaient encore une image après le lancement
observé dans leur rejeu. Les phases des deux combats restent distinctes.

Deux essais supplémentaires restent écartés. Le premier parcourt les
emplacements de projectiles en une passe et teste leur type plus tôt.
Il garde le résultat de c0042 en PAL, y compris l’image 80 001 sautée.
Le second initialise le cache à son premier usage. Il rejoint la V318
sur la fenêtre NTSC jusqu’à 7 710, puis diverge en PAL dès 79 474 et
saute encore les deux mises à jour mesurées.

- [Rapports, commandes et captures](c0040-pal-campaign-timing/manifest.json)
- [Essais sur la ROM Master System](c0040-source-burst-cadence/manifest.json)
- [Mesure de la publication au VBlank](v0318-burst-video-publish/manifest.json)
- [Trois salves en jeu sur la Master System PAL](sms-pal-room180-burst-cadence/manifest.json)
- [Essais après c0042](burst-cadence-trials-after-c0042/manifest.json)

La réutilisation d’un masque plus large pour construire un masque plus
strict conserve les 108 images de sprites contrôlées. Dans le parcours
PAL, cet essai diverge à 79 474 et saute encore les deux mises à jour
mesurées. Il est écarté. La ROM temporaire de 2 Mio est conservée sous
forme compressée et son exemplaire de compilation a été supprimé.

- [Réutilisation partielle des masques](mask-clone-subset-v0318/manifest.json)
