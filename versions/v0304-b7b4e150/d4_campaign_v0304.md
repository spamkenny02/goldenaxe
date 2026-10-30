# v304 : quatrième cristal et retour hors du donjon

Le quatrième donjon est terminé sur la ROM v304, SHA-256
`b7b4e15008a6f0a913c9ad43f15386abcdfbb719e5a575873d92712ba52503a8`.
Le programme du jeu reste inchangé. Cette étape poursuit le
[parcours du canoë](d4_canoe_v0304.md).

Le boss réel est le type 6A de la salle 180 : données originales 1E100240
(30 PV, dégâts de base 16, armure 2, drapeau de boss 40). La protection
d'approche est retirée à la frame 78 342. Le premier état de combat normal
est observé à 78 388, soit 46 frames plus tard, avec 56 PV et un délai
d'invulnérabilité nul.

Le premier segment de 4 000 frames de combat finit vivant, à 56 PV pour le
héros et 12 PV pour le boss. Sa relecture indépendante depuis le démarrage
reproduit toute la RAM et le PNG final ; 500 fenêtres de prédiction sont exactes.
Ce segment est une étape partielle, sans victoire revendiquée.

La continuation reprend le même combat, sans soin ni remise à zéro. Un
contrôleur choisit les boutons par fenêtres de 16 frames et accepte davantage
de risques pour atteindre le boss. Les 33 fenêtres terminées prédisent les
65 536 octets de RAM sans différence. Le héros subit les dégâts ordinaires
à la frame 82 870 : de 56 à 32 PV, délai de blessure 47. Le boss est ensuite
vaincu ; le cristal et son soin normal portent le héros à 64/64 PV.

| Étape | Frame finale | Résultat |
| --- | ---: | --- |
| Premier segment de combat | 82 388 | Héros 56/56 PV, boss 12 PV, vivant |
| Victoire et récompense terminée | 83 593 | Quatre cristaux, 64/64 PV, magie 48/48 |
| Retour à l'extérieur en 10 | 86 158 | 62/64 PV, canoë et corde conservés |

Le retour traverse les pièces et le téléporteur inverse, puis la zone d'eau.
Il ajoute zéro écriture d'aide après la libération précédant le boss. Ses
83 fenêtres de prédiction reproduisent toute la RAM. Victoire et sortie ont
chacune leur relecture indépendante depuis le démarrage, avec RAM entière
et PNG final identiques. Les anciennes aides d'approche restent consignées ;
la campagne entière n'est pas qualifiée de parcours sans assistance.

L'observation avant chaque instruction normale du 68000, de la frame 14
jusqu'à 86 158, trouve 496 octets de marge entre le minimum de pile et la
limite du tas. Les en-têtes de l'allocateur restent valides ; RAM et image
finales correspondent au parcours canonique. Cette mesure ne borne pas
les chemins futurs.

Le [rapport reproductible](d4_campaign_v0304_report.json) lie les trois
relectures, les commandes, les aides, les sources figées et le contrôle de
pile. Le nouveau contrôleur change seulement les boutons de test ; aucune
ROM supplémentaire n'est créée pour cette étape.

Quatre cristaux et leurs retours sont désormais vérifiés sur v304. Les
donjons suivants, la fin, les sauvegardes, le hasard global et la fidélité
complète vidéo/audio/matériel restent ouverts. Aucune victoire contre ce
boss dans une campagne SMS équivalente n'est revendiquée ici.


Erratum2026-10-30 : la marge de496 octets citee ci-dessus concerne les points instrumentes. Le minimum avant chaque instruction est478 octets sur les parcours D1-D6. Voir la [correction de mesure](stack_minimum_v0304_erratum.md).
