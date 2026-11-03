# v0310 : raccordement du générateur SMS

ROM `32fe75a653d7152f7cbf873a32f2ffef14234ea190885ae8a8235f2ccd10e071`,
2 Mio, checksum AFC5. [Bilan lié aux empreintes](rng_integration_v0310_report.json).

La production distingue désormais les lectures directes de R et les appels
à 04E1. Ces derniers mettent à jour une graine globale avec la récurrence SMS
vérifiée, puis combinent son octet bas au R échantillonné. Les lectures directes
n'avancent pas cette graine. Après reset, R7 est nul ; aucun LD R,A n'est présent
dans la ROM fournie. Les valeurs directes restent donc entre 0 et 127, tandis
que le résultat 04E1 conserve ses huit bits.

Sept expressions natives couvrent les appels actifs relevés : historique des
salles (deux adresses SMS), butin, particules de boss, ennemi à phases, choix
d'attaque du boss chargeur, pause du boss 65 et mini-jeu. Le neuvième CALL 04E1
littéral, à 0503, appartient à l'utilitaire 04FE et est inventorié séparément.
Ce relevé d'opcodes ne prétend pas démontrer tout le graphe d'exécution.
Le test garde le seuil pleine largeur du boss 65 : A921 appelle bien 04E1 ;
A935 lit directement R pour la durée, ce sont deux usages différents.
Les entrées explicites des anciennes fixtures de combat restent inchangées.

La v309 avait 67 appels directs SGDK au total : 3 main, 63 actors et 1 mini-jeu.
Le relevé précédent de 66 omettait le mini-jeu. Dans la v310, le seul appel brut
à SGDK random est enfermé dans le fournisseur provisoire de R.
**Le rythme exact des lectures R et la phase globale R/IRQ restent à porter.**
Le raccordement de la récurrence ne prouve pas leur équivalence avec la SMS.

Contrôles terminés :

- 65 536 séquences sur PC, puis 65 536 en code 68000 pour chacune des régions
  NTSC/PAL : lecture directe, 04E1, lecture directe, reset intermédiaire,
  nombre d'appels au fournisseur et toutes les valeurs d'entrée 16 bits.
- Démarrage normal, nom, récit, premières cartes et déplacements, 3 140 images
  par région ; activité réelle de la nouvelle graine et zéro commande audio
  inconnue. Dix-huit points comparés en relecture exacte RAM 65 536 octets/PNG.
- Continuer avec la SRAM réellement écrite en v309 : statistiques, 17 objets,
  neuf cristaux, arbre coupé persistant, HUD physique et mouvement restaurés.
  Une importation SRAM normale, aucune écriture RAM ni suppression d'ennemis.
- Les 310 ROMs numérotées, les deux alias et la ROM SMS ont été vérifiés.

Les relectures de démarrage utilisent des processus de cœur distincts.
L'essai initial dans un seul processus conservait 28 octets de pile ancienne,
malgré des images identiques ; il est conservé et n'est pas compté comme preuve
exacte. Un premier export du bilan Continuer a aussi échoué dans le pilote
(variable Python masquée), après les contrôles ; compat02 termine et publie.
Les images finales de jeu et de rechargement ont été inspectées.

La campagne complète reste prouvée sur **v309**, pas encore sur v310.
La fidélité globale, les contenus optionnels, les autres cas de sauvegarde
et les essais matériels restent ouverts. Aucune aide de test n'est ajoutée
à cette ROM publique.
