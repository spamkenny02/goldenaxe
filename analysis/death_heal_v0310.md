# Mort, Continuer et soin gratuit sur v0310

La campagne courante reprend le retour de D6, à 2/80 PV, sans importer de sauvegarde ni modifier les ressources. La ROM reste v0310, SHA-256 `32fe75a653d7152f7cbf873a32f2ffef14234ea190885ae8a8235f2ccd10e071`.

| Étape | Image finale | Salle | PV | PM | Cornes | Clés |
| --- | --- | --- | --- | --- | --- | --- |
| Mort puis Continuer | 191132 | 95 | 24/80 | 24/72 | 21 | 2 |
| Arrivée chez le soigneur | 191492 | Maison 0 de 94 | 24/80 | 24/72 | 21 | 2 |
| Nuit gratuite et retour extérieur | 192089 | 94 | 80/80 | 24/72 | 21 | 2 |

La mort survient normalement au contact des ennemis en 9B, image190909. Le menu apparaît en191001 et Continuer rend le contrôle en191130. Les six cristaux et les dix-sept emplacements d'inventaire sont conservés. Les cornes passent de30 à21 selon la formule du jeu `(30 >> 2)*3`.

Le soigneur de94 restaure ensuite les PV de24 à80, sans coût et sans restaurer les PM. Les trois phases du dialogue et de la nuit sont observées. La sortie de la maison est jouée normalement. Les trois étapes sont relues depuis le démarrage avec les mêmes entrées : RAM entière65536 octets et PNG final identiques. Les HUD après Continuer et après soin sont contrôlés physiquement.

Aucune nouvelle écriture RAM depuis le retour de D6 : seules les anciennes protections d'approche sont rejouées. Aucun argent, objet, PV, PM, acteur ou SRAM n'est injecté. Cette séquence suit une mort volontairement recherchée par déplacement ordinaire ; elle ne revendique pas un parcours sans mort.

Une branche exploratoire antérieure reçoit30 cornes en7D, mais sa proposition vers le vendeur de potions5E échoue devant un rocher exigeant Terre niveau2. Cet essai n'est pas un achat validé et son argent n'est pas transféré à la branche retenue. Le premier trajet au soigneur avec un épisode d'aide vide est également exclu ; le trajet retenu est rejoué sans nouvelle aide.

Le septième donjon et la fidélité globale restent ouverts. Voir le [rapport vérifié](death_heal_v0310_report.json) et l'[auditeur](../tools/summarize_death_heal_v0310.py). Sources et essais privés conservés dans `validation/v0310-d7-sources`.
