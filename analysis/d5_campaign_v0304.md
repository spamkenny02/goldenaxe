# v304 : cinquième cristal et retour hors du donjon

Le cinquième donjon est terminé sur la v304, SHA-256
`b7b4e15008a6f0a913c9ad43f15386abcdfbb719e5a575873d92712ba52503a8`.
Le programme du jeu reste inchangé. Cette étape prolonge le
[ravitaillement et les mécanismes](d5_supplies_v0304.md).

La clé réellement achetée permet l'accès au boss 65 de la salle 163. Ses
données originales sont 480C0240 : 72 PV, dégâts de base 12, armure 2 et
drapeau de boss 40. La dernière écriture de protection est à la frame
114 294 ; le premier état de combat normal est à 114 321, 27 frames plus
tard, avec 64 PV et un délai d'invulnérabilité nul.

Le premier segment de 3 200 frames finit à 64 PV pour le héros. Le noyau
conserve ses 72 PV, avec deux satellites à 8 et 4 PV. Le noyau est encore
invulnérable, comme le prévoit son comportement tant que les satellites
restent présents. Ce segment partiel a sa relecture indépendante exacte.

Le contrôleur de test comptait principalement les ennemis dans les huit
premiers emplacements. Il considère désormais aussi les satellites 66
attaquables des emplacements 8 à 15 pour choisir ses boutons. Cette option
change la conduite du combat ; les règles du boss dans la ROM ne changent pas.

La continuation reprend le même combat, sans soin ni remise à zéro. Les
satellites restants sont détruits, puis le noyau est vaincu. Aucun dégât au
héros n'est observé pendant le combat. Le cristal et son soin normal portent
la capacité et la vie à 72/72 PV, avec 48/48 de magie et aucune récompense
encore active.

| Étape | Frame finale | Résultat |
| --- | ---: | --- |
| Combat partiel | 117 521 | Héros 64/64 PV ; noyau 72 PV ; deux satellites restants |
| Victoire et récompense terminée | 119 965 | Cinq cristaux, 72/72 PV |
| Mécanisme de retour 173 vers 174 | 120 313 | Passage ouvert normalement, 72/72 PV |
| Sortie à l'extérieur en 49 | 121 051 | 72/72 PV, zéro clé, bottes/canoë/corde conservés |

Le retour utilise le mécanisme HAUT de 173, le téléporteur 174 vers 155,
puis les pièces 165, 166, 176 et 186. Il ajoute zéro écriture d'aide après
la libération précédant le boss. Les quatre segments ont chacun une relecture
indépendante depuis le démarrage, avec les 65 536 octets de RAM et le PNG
final identiques. Les 200 et 112 fenêtres de prédiction des deux combats,
ainsi que les 12 du dernier retour, correspondent à toute la RAM primaire.
Les aides d'approche historiques restent explicitement consignées.

Le contrôle avant chaque instruction normale du 68000, de la frame 14 à
121 051, observe 496 octets de marge entre le minimum de pile et la limite
du tas. Les en-têtes de l'allocateur restent valides ; RAM et image finales
correspondent au parcours canonique. Cette mesure ne borne pas les chemins
futurs.

Le [rapport reproductible](d5_campaign_v0304_report.json) lie les relectures,
les commandes, les aides, les deux versions du contrôleur et le contrôle
de pile. Cinq cristaux et leurs retours sont maintenant vérifiés sur v304.
Les donjons suivants, la fin, les sauvegardes, le hasard global et la
fidélité complète vidéo/audio/matériel restent ouverts. Aucune campagne
SMS équivalente contre ce boss n'est revendiquée ici.


Erratum2026-10-30 : la marge de496 octets citee ci-dessus concerne les points instrumentes. Le minimum avant chaque instruction est478 octets sur les parcours D1-D6. Voir la [correction de mesure](stack_minimum_v0304_erratum.md).
