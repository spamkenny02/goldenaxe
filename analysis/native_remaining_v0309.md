# Limites de fidélité constatées dans les sources v0309

Cet inventaire est une lecture du code, sans modification du jeu.
Il est lié à la ROM `7270576d6eeb2aee641776a3e364f2f3f320711d70bb91a566d7578161261049`
et aux empreintes de sources du [relevé détaillé](native_remaining_v0309_source_inventory.json).
Il ne constitue pas une validation globale du portage.

Le code contient **66 sites d'appel direct au hasard SGDK** : trois dans
`main.c`, soixante-trois dans `actors.c`, hors commentaires. La bibliothèque
locale utilise un xorshift 16 bits. Le générateur SMS 04E1 est reconstruit
dans `source_rng.c`, avec une version temporisée dans `source_rng_timed.c`,
mais ces deux fichiers ne sont pas appelés par les routines de production
de `main.c` et `actors.c`. La mise à jour de la graine, l'échantillonnage du
registre R et leur phase globale restent donc à raccorder. Les relectures
exactes d'un parcours Mega Drive ne prouvent pas cette équivalence avec la SMS.

Cinq commentaires de `main.c` reconnaissent des estimations de phase ou de
contention hors des situations déjà mesurées : HUD/IRQ, PSG/VDP, portails,
préparation de carte et réserve de reconstruction. Ils indiquent les zones
où une comparaison temporelle globale reste nécessaire ; ils ne démontrent
pas à eux seuls un défaut visible sur chaque trajet.

Deux anciens commentaires ne doivent pas être comptés comme des fonctions
absentes. Le menu 14ED est implémenté par `start_menu()`, appelé après l'entrée
sur l'écran titre, avec Nouveau Jeu, Continuer, musique et bruitages.
Le clonage 4C7E existe dans `clone_hurt_actor()` et est appelé lors de la mise
à jour des ennemis concernés. Leur présence ne remplace toutefois pas les
comparaisons de comportement et de rythme avec la ROM originale.

Le parcours courant v0309 atteint désormais la fin depuis Nouveau Jeu :
voir [la campagne et la fin](cold_palace_final_v0309.md). Les approches sont
assistées et les boss combattus sans protection. Les anciennes preuves
contrôlées du palais restent séparées. La fidélité globale, les sauvegardes
normales, les contenus optionnels et les essais matériels restent à établir.
