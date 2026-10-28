# v0304 : cadence des salves et premier donjon revalidé

La ROM de 2 Mio `b7b4e150` réduit le travail du rendu tout en gardant
les huit sprites SMS par ligne. Le calcul de débordement utilise les mêmes
compteurs que le masquage, sans reconstruire une deuxième carte de lignes.
Les compteurs sont codés en disponibilité unaire ; huit séquences ADD/ADDX
68000 produisent le masque et mettent à jour les huit lignes. Les clones
sont écrits directement dans leur tampon final et transférés en un bloc
dans la banque absente de la liste actuellement affichée. La tuile vide
reste séparée. Le rendu manuel réécrit tous ses sprites actifs et ferme
leur chaîne ; il ne réinitialise plus l'allocateur SGDK inutilisé par image.

## Mesures et limites

Le segment contrôlé de la variante 7C ne saute plus d'images de simulation,
dans les deux régions. Les écarts constatés pendant cette recherche :

| ROM | Écarts NTSC | Écarts PAL | Statut |
| --- | ---: | ---: | --- |
| v296 | 36 | 36 | Référence précédente |
| v297 | 36 | 36 | Compteurs groupés, essai écarté |
| v298 | 36 | 36 | Lectures VRAM sélectives, essai écarté |
| v299 | 36 | 36 | Saturation scalaire, intermédiaire |
| v300 | 36 | 30 | Routine unaire 68000, intermédiaire |
| v301 | 34 | 0 | Comptage partagé, intermédiaire |
| v302 | 4 | 0 | Passe unique et transferts regroupés, intermédiaire |
| v303 | 1 | 0 | Construction directe et lectures longues, intermédiaire |
| v304 | 0 | 0 | Version retenue |

Ces écarts sont des intervalles de deux images entre entrées de simulation
sur le segment 2880..3052 de ce test. Ce tableau ne mesure pas le débit
de l'ensemble du jeu. Les durées du masque incluent interruptions et
contention VDP ; une comparaison de ces durées ne constitue pas une
accélération intrinsèque de toutes les instructions ou de tout le jeu.

Les six comparaisons de production 6A/6B/7C, PAL/NTSC, retrouvent exactement
les 768 octets d'acteurs à chacune des 252 images du premier cycle :
apparition, huit projectiles, branche de variante, disparition et nettoyage.
Le héros et le boss sont placés dans un extérieur, avec statistiques SMS et
horloge initiale alignée. Les choix de déplacement aléatoires suivants et
la phase naturelle entre démarrage et combat ne sont pas prouvés ici.

Le test hôte compare 133 120 cas et les pixels/statuts de masquage avec
la v295. Son port VRAM renvoie une constante, tandis que les motifs en
attente de transfert varient. La routine assemblée dispose d'un test natif
séparé : 8 192 cas par région, incluant les 256 combinaisons de disponibilité,
les états unaires, toutes les valeurs d'octet et les deux alignements.
Des sentinelles vérifient l'absence d'écriture hors des huit lignes.
Les 108 images de sprites physiques et douze images naturelles composées
indépendamment depuis VRAM/CRAM passent également.

## Campagne sur cette compilation

Les anciennes commandes ne rejoignent pas le premier donjon au même moment :
la première relecture s'arrête proprement avant d'activer une aide dans une
mauvaise situation. Un nouveau parcours adaptatif atteint le donjon à
14 PV, obtient la première clé, puis termine le boss 68 et prend son cristal.
La protection d'approche est retirée à l'image 11893 ; le premier combat
ordinaire commence à 11965, à 20 PV et compteur de protection nul.
Un coup réel est enregistré à 12049 : 20 vers 16 PV.

Le cristal est confirmé à 32/32 PV en 12867 images. Le retour extérieur B9
se termine en 14583 images à 28/32 PV, sans nouvelle aide. Les deux
relectures indépendantes retrouvent toute la RAM de 65 536 octets et
le PNG final. Aucun soin, objet ou état de jeu capturé n'est importé dans
le parcours. La recherche secondaire du retour vérifie ses 36 fenêtres de
prédiction ; elle n'injecte aucun état dans le jeu principal.
La pile observée à chaque instruction normale depuis l'image 14 atteint
F7F0, pour une limite de tas F600 : 496 octets de marge sur ce parcours.

Les donjons suivants, la fin et les sauvegardes restent à revalider sur304.
Les preuves antérieures de deux cristaux/corde et de six cristaux restent
respectivement liées aux v296 et v293. Le portage complet et la fidélité
globale du rythme, de la vidéo et de l'audio ne sont pas déclarés acquis.

[Rapport et empreintes](burst_cadence_v0304_report.json),
[comparaison des variantes](burst_variant_7c_v0304_gameplay_report.json),
[profil de cadence](burst_render_cost_cost-v0304_report.json),
[variantes de compilation conservées](burst_cadence_v0304_candidates.json).
