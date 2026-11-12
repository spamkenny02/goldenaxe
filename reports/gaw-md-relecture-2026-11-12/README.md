# Relecture MD des parcours SMS — en cours

La V322 de développement SHA1421abe4 corrige Saylun ; elle n’est pas une RC qualifiée.
Le point 6 reste ouvert : toutes les branches retenues doivent être réellement
jouées, vérifiées et filmées sur MD avant qualification de la RC.

Les trois emplacements de sauvegarde d’Eren sont écrits normalement puis
rejoués, SRAM exacte. Un processus indépendant charge ensuite cette SRAM par
Continuer : inventaire, jauges, HUD et déplacement vérifiés. Le chargement est
rejoué une seconde fois, 65536 octets de RAM et PNG final identiques. Les six
rapports joints conservent les bornes et les limites. Les versions -02 des
preuves Continuer utilisent une instance GX fraîche, sans résidus d’une
exécution précédente dans les octets de pile inactifs.

Les PNJ ordinaires, services et acquisitions supplémentaires sont suivis dans
[le relevé cas par cas](../../analysis/md_annex_replay_coverage.json),
[la tournée des maisons](../../analysis/md_plain_house_census_campaign.json) et
[la tournée des refus](../../analysis/md_service_refusal_campaign.json).
Les rapports des cas échoués ne sont pas comptés comme réussites.

Les [vidéos MD](../../videos/md-annexes-2026-11-12/README.md) sont des branches
identifiées, avec son du jeu, décodage audio/vidéo complet et preuves de rejeu.
Une entrée de route ne valide ni le dialogue ni la récompense : ces étapes
ont leurs propres contrôles. Une correspondance du bitmap final ne certifie
pas encore toutes les pages intermédiaires ou le timing physique SMS/MD.

La campagne MD complète en PAL/NTSC et sa vidéo ne remplacent pas les annexes.
Aucun pourcentage global ni certificat tous PNJ/tous objets/tous monstres
n’est déduit du nombre d’enregistrements contrôlés.

## Correction du critère de sortie

Un retour de maison peut publier le numéro de l’écran extérieur et le héros
avant la fin réelle du fondu. Les anciens clips arrêtés à cet instant conservent
leur preuve de dialogue et de rejeu, mais ne sont plus qualifiés comme une
sortie complète. Le relevé général les liste dans `partial_exits_not_credited`.
Les nouvelles preuves attendent `resume_phase=0`, chargement terminé, classe
extérieure, puis une commande de déplacement effectivement exécutée. Les
prolongements rejouent tout le préfixe à l’identique, sans importer de RAM.

Le cas marchand72 a aussi montré un projectile frappant le héros sur la carte
extérieure déjà restaurée : [diagnostic](../../analysis/md_merchant72_damage_audit.json).
Les refus peuvent désormais déclarer explicitement la protection d’approche
autorisée, avec audit de l’absence de boss vivant ; aucun point de vie, objet
ou état de quête n’est injecté pour faire réussir le test.

Impact marchand72 : [image avant](marchand72-avant.png), [image de l’impact](marchand72-impact.png). Le numéro de frame et les états exacts figurent dans le diagnostic.
