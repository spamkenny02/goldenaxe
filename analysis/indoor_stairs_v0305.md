# v0305 — Escaliers intérieurs et huile

ROM : `83dfaf697521ce97597af259835eccae70bde055e70f321176caad34f93a23c7`,
2 097 152 octets, checksum Mega Drive `C3B8`.

## Correction native

Le retour anticipé `world_graphics_class == 1` de `begin_room_transition`
interdisait le défilement des intérieurs reliés. Le gestionnaire SMS aux
adresses 2051..21C5 ne comporte pas cette exclusion. La seule modification
de production supprime cette exclusion ; les contrôles normaux de voisinage
et les protections propres aux donjons et à l’extérieur sont conservés.

La porte réelle de C7 mène à 1F ; l’escalier supérieur mène à 0F où se trouve
le don d’huile. Il faut ensuite redescendre vers 1F et sortir normalement en C7.

## Preuves et portée

`tools/summarize_indoor_stairs_v0305.py` vérifie les octets de la ROM,
les alias, l’original SMS et les 304 anciennes ROMs. Il vérifie aussi les
sources de production avant/après : seul `megadrive/src/main.c` diffère.

Le contrôle de référence reproduit le blocage sur v0304 : la MD reste en 1F
sans huile tandis que la SMS parcourt 1F, 0F, 1F puis C7. Le même contrôle
passe en PAL et NTSC sur v0305. Il utilise la véritable porte extérieure
puis une position intérieure de test, sans ajout d’objet ni suppression
d’acteur. Les 17 valeurs sémantiques d’inventaire et les 160 cellules finales
concordent. Les niveaux d’arme primaire et de hache sont lus dans les champs
natifs dédiés. Ce contrôle ne prouve pas une égalité de toutes les images,
de l’audio ou des durées absolues.

Un second parcours part d’une nouvelle partie sans écrire la RAM ni importer
une sauvegarde. Arrivée dans 1F à l’image 3965, puis huile, retour en 1F et
sortie en C7 à l’image 4677, avec 8/24 PV. Chacune des deux étapes a une
relecture canonique indépendante : les 65 536 octets de RAM et le PNG final
sont identiques. Le premier contrôleur d’escalier oscillait sur son point
cible ; cet essai négatif est conservé et exclu des réussites.

Après ces relectures, le profil de pile avant chaque instruction du parcours
4677 images observe SP minimal 63642, frontière de tas maximale 62976 et
marge 666 octets. Le résultat RAM/PNG est identique. Ce parcours étant plus
court, cette marge ne constitue pas une amélioration démontrée des 478 octets
mesurés sur la campagne v0304.

## Campagne historique

Les sept cristaux, la clé des voleurs et l’approche du huitième boss restent
des preuves v0304. Le premier combat contre le huitième boss est perdu.
La sortie de ravitaillement et le passage payant inverse sont rejoués
exactement sur v0304 ; ils ne constituent pas une victoire de ce donjon.

Deux essais de reprise des commandes v0304 sur v0305 sont conservés comme
résultats négatifs. Le second, avec libération dynamique de la protection
d’approche, atteint quatre cristaux puis meurt dans la salle 163 du cinquième
boss. Aucun de ces essais n’est promu comme campagne v0305 validée. Une
séquence historique qui diverge ne suffit pas à conclure à un nouveau bug
natif ; une conduite adaptée et des comparaisons ciblées restent nécessaires.

Les prototypes de reprise et de porte révélée par Terre sont conservés comme
prototypes inutilisés. Ils ne modifient pas les outils de conduite actifs.

## Archivage

`tools/archive_indoor_stairs_v0305.py` conserve les captures et résultats dans
`analysis/indoor-stairs-v0305`, relit et vérifie leurs empreintes avant de
nettoyer les fichiers générés. L’original, les deux alias et les 305 ROMs
numérotées sont protégés. La RAM finale du parcours naturel reste disponible.
Le préfixe préexistant de `analysis/world_next.md` est conservé octet pour octet.

Le portage complet reste non validé : hasard SMS et phase globale, suite de
campagne, fin, sauvegardes et fidélité vidéo/audio/matériel restent à traiter.
