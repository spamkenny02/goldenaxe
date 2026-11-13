# V325 — sortie de la présentation / essai flashkit

ROM de développement de 2 097 152 octets, destinée à retester le blocage
signalé après la voix et le fondu sur Mega Drive 1 / flashkit 2 Mo + SRAM 32 Ko.
La V322 RC1 fonctionne sur ce matériel selon le retour utilisateur.

La V324 parcourait 24 registres depuis le cache SGDK `regValues[0x13]`,
qui ne contient que les registres 0 à 18. Les cinq lectures suivantes prenaient
les octets voisins en RAM et les écrivaient dans les registres DMA.
La V325 limite la lecture au cache réel, attend que le FIFO soit vide et
initialise explicitement les cinq registres DMA à zéro. La modification
porte sur la sortie du splash ; image, voix, fondus, Konami, sauvegardes
et moteur sont conservés. Deux compilations donnent le même SHA-256.

Les preuves jointes couvrent le démarrage et la voix en PAL/NTSC,
les deux campagnes enregistrées jusqu'à la fin avec neuf cristaux et zéro mort,
les douze cas du menu Konami et les quatre cas de chargement Continuer.
La protection d'approche des campagnes reste déclarée et retirée avant
les combats contre les boss ; ces tests ne constituent pas une nouvelle
certification de tous les PNJ ou de la fidélité matérielle.

**Confirmation sur console encore attendue.** La lecture hors limites est
une erreur démontrée du code. Sa responsabilité dans le blocage physique
et l'efficacité de cette correction doivent être confirmées sur le flashkit.
Le test à effectuer est un démarrage à froid jusqu'à l'introduction, puis
l'écran titre et Nouveau jeu / Continuer, avec la voix et le fondu actifs.

[Rapport de validation](VALIDATION.json) · [Versions](../../versions/README.md)
