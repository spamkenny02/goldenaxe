# v0310 : corde, troisième cristal et retour

Le [bilan vérifié](d3_campaign_v0310_report.json) prolonge la même partie
ayant terminé D2, puis [reçu l'huile en C7](oil_service_v0310.md). Le troisième
cristal est acquis et le héros ressort en 62 à **46/56 PV**, huile et corde
conservées. La ROM publique reste v310, sans changement de binaire.

| Étape | Image finale | Salle | PV |
| --- | ---: | --- | ---: |
| Entrée D3 | 50064 | 1F8 | 31/48 |
| Corde et récompense terminée | 54923 | 1F4 | 39/48 |
| Mécanisme activé | 55410 | 1E3 | 39/48 |
| Clé récupérée | 56899 | 1D2 | 39/48 |
| Antichambre dégagée | 58420 | 1D3 | 39/48 |
| Protection retirée | 58421 | 1D3 | 39/48 |
| Boss et cristal | 65056 | 1C3 | 56/56 |
| Retour extérieur | 66413 | 62 | 46/56 |

Le mécanisme est activé par Haut à 120,104 pendant que les ennemis sont encore
présents. Le héros récupère ensuite réellement la clé et revient par la
couronne extérieure. Aucun acteur n'est supprimé pour faciliter ce passage.

Le combat contre **type69, 32 PV** commence à 58573 avec 39 PV et compteur de
blessures nul, après la dernière écriture de protection à 58421. Un coup normal
à 64349 retire huit PV, de 39 à 31. Le cristal donne ensuite le soin du jeu à
56/56 PV. Aucune aide ne reprend pendant ce combat ou le retour.

Les 182 fenêtres de prédiction du combat et les sept du retour correspondent
à toute la RAM, sans différence de pile réservée. Les huit étapes ont une
relecture froide indépendante par commandes fixes : 65 536 octets de RAM et
PNG final exacts. Le HUD physique de 128 mots et les trois marqueurs sont
vérifiés après récompense puis après sortie. Les images finales ont été inspectées.

Les seules écritures de test restent les compteurs de blessures autorisés
sur les approches. Aucun PV, argent, objet, acteur, clé ou progression n'est
injecté ; aucun import SRAM ou état principal n'est utilisé. Le service de
l'huile rejoue seulement ses anciennes écritures, sans en ajouter.

Ce parcours NTSC confirme trois cristaux sur v310, pas encore la fin de cette
version. La phase globale R/IRQ, les autres contenus et la fidélité temporelle
et audiovisuelle complète restent ouverts. La campagne v309 complète demeure
historique. La table originale situe le type65 à satellites en salle163 ;
son futur combat réel doit être distingué des bancs contrôlés déjà réalisés.
