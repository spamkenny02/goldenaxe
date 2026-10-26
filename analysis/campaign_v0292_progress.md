# Campagne v0292 : corde acquise, Terre et passage du quatrième donjon

La ROM reste la v0292, SHA-256 6eeb56086a81c230c75b154f51cafab72167a1eec42c691aed9bf317fd19dd82.
Les changements de cette étape concernent les contrôleurs de test et leurs
preuves, sans modifier le programme 68000 ni créer un numéro de ROM artificiel.

## Parcours Mega Drive réellement exécuté

La campagne démarre normalement. Les gardes de test ne touchent que le délai
de protection pendant les approches ; aucune position, équipement, monnaie,
progression, recharge de vie ou sauvegarde n'est transplantée. Chaque boss
retrouve les dégâts ordinaires avant son premier frame de combat.

- Deuxième donjon : boss et cristal obtenus, puis sortie à 11/48 PV.
- Troisième donjon : corde obtenue en 1F4, boss vaincu, cristal et capacité de
  56 PV. Le combat démarre à 27 PV et finit après la récompense à 56/56 PV.
  La garde est retirée 35 frames avant le premier frame de combat. Les 260
  fenêtres de prédiction du contrôleur reproduisent toute la RAM primaire.
- Sortie du troisième donjon à 50/56 PV sans nouvelle garde sur le retour.
- Nouvelle approche du quatrième boss : ouverture de la maison F4 à la hache,
  vrai don de 50 cornes, puis montée B2/A2 avec la corde acquise. Le héros
  coupe l'arbre spécial 4A de A3 et rejoint le maître de la Terre.
- Le vrai dialogue retire 50 cornes, accorde Terre niveau 1 et passe la
  réserve magique de 24 à 48. Sortie en A3 à 50 PV et 32 cornes.
- Entrée du quatrième donjon, acquisition de la première clé, puis sélection
  normale du sort dans l'inventaire. Un lancer de Terre coûte 8 unités et
  ouvre le passage E1 vers D1. La salle D1 est atteinte, pas nettoyée.

Les douze segments natifs et trois segments SMS de référence ont chacun
une seconde exécution depuis le démarrage, sans contrôleur adaptatif,
avec toute la RAM et le PNG finals identiques. Les gardes d'approche restent
explicitement enregistrées : ces campagnes ne sont pas dites sans aide.
Le [rapport consolidé](campaign_v0292_progress_report.json) lie les captures,
les commandes, les épisodes d'aide et leurs empreintes aux deux ROMs.

## Comparaison du passage de Terre

La SMS apprend son propre sort puis suit sa propre route. Avant le lancer,
les portes déjà ouvertes par le combat sont distinguées du rocher à détruire.
Les cinq cellules modifiées par le sort sont 36–39 et 58. Après l'ouverture,
les 160 cellules, les 1 280 octets de carte, les 17 octets d'inventaire et le
drapeau E1 54 correspondent entre SMS et MD. Les vingt mots VDP de ces cinq
cellules et les indices de couleur de leurs tuiles correspondent également.
Les PV, cornes, acteurs, horloges, image complète et audio ne sont pas déclarés
équivalents par cette comparaison.

## Outils et suite

Les écritures d'aide sont indexées par frame, en conservant leur ordre. Les
listes de fixtures remplaçables gardent leur comportement précédent. Les
boutons fixes utilisent un balayage des débuts et fins d'intervalles avec
compteurs de chevauchement ; les nouveaux enregistrements fusionnent les
intervalles identiques et les bornent aux frames réellement exécutées.
Deux mille cas comparent les masques à l'ancien compilateur. Une nouvelle
relecture du précédent enregistrement MD de 58 752 frames reproduit toute
sa RAM et son PNG, comme les relectures de référence SMS.

Les propositions de route évitent désormais les autres entrées de maisons,
y compris quand on les aborde par le côté ou depuis le haut. Le contrôleur
peut sélectionner les lignes de l'inventaire, orienter le héros avant de
lancer Terre et rééquiper la hache. Il peut aussi approcher les ennemis
inactifs au lieu d'attendre indéfiniment leur activation, et différer un
puzzle qui n'est pas nécessaire à la porte visée.

Les derniers essais vers le canoë atteignent B2, avec zéro clé, sur les deux
machines. Le détour intermédiaire et ses déclencheurs de clé restent à
exécuter correctement ; ces essais ne prouvent ni acquisition du canoë ni
combat contre le quatrième boss. Le reste des dix donjons, la fin du jeu,
les timings globaux et le matériel restent à vérifier. Le guide
[RPGClassics](https://tartarus.rpgclassics.com/gaxwa/w09.shtml) sert uniquement
à proposer les détours ; les preuves viennent des jeux réellement exécutés.

Les diagnostics conservés comprennent : ancien trajet fixe qui ne ressort
pas du deuxième donjon, entrée involontaire dans une maison en 13, navigation
incorrecte entre lignes d'inventaire, lancer avec une mauvaise orientation,
attente d'acteurs inactifs et essais de canoë sans tous les prérequis.
