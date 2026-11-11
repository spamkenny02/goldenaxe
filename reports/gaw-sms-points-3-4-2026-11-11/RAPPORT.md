# Points 3 et 4 SMS — clôture du 11 novembre 2026

Les deux points sont validés sur la ROM SMS fournie, SHA-256 `852e068e331dbfb01b9c38a62eecf81ce5b9f0f1bd10fff497117bd885c716c9`.
Le relevé conserve **145 enregistrements sélectionnés**, leurs preuves de relecture, les hashes des entrées et les états finaux. Chaque relecture reproduit les 8192 octets de RAM et les pixels finaux, depuis le démarrage, sans import d'état d'émulateur.

Les rapports d'exécution et de relecture sont conservés dans [PREUVES.json](PREUVES.json). Les commandes brutes et captures restent dans le répertoire local `validation` ; elles ne sont pas incluses dans ce fichier de rapports.

## Point 3 — services

| Obligation | Résultat |
| --- | --- |
| Marchands | 23 contextes visités ; les six groupes de marchandises et les deux commerces spécialisés sont exercés. |
| Achats | Les 18 offres distinctes objet/prix sont effectivement achetées ; monnaie et effet vérifiés. Les tables partagées sont recoupées octet par octet avec la ROM. |
| Refus marchands | Argent insuffisant, objet déjà possédé, équipement inférieur et capacité pleine observés. Vie pleine, magie pleine et 99 clés sont distingués. |
| Auberges | 11 lieux : refus et nuit acceptée ; manque d'argent aux tarifs 20 et 40 ; revisite payée avec vie déjà pleine, magie conservée. |
| Sauvegardes | 14 lieux : écriture réelle puis redémarrage avec Continuer ; trois slots vérifiés à Eren ; écrasement d'un vrai slot après un vrai gain d'argent, puis rechargement du nouvel état. |
| Passages | Six directions : paiement, destination réelle et refus ; insuffisance de fonds vérifiée pour le tarif commun de 10. |
| Jeux | Quatre hôtes ; premier refus, manque d'argent, pertes, gains, seconde partie payée et refus de rejouer. Les deux cartes spéciales 38/39 sont obtenues sans écrire le hasard. |

Chaque lieu a sa visite propre. Les transactions équivalentes sont regroupées seulement quand les données et le code originaux sont identiques ; tous les croisements lieu × inventaire ne sont pas rejoués artificiellement.

## Point 4 — équipements et annexes

Les huit récompenses sont effectivement obtenues : deux armures, deux épées, le bouclier de dragon, les deux pommes et l'huile cachée. Les huit contextes sont ensuite revisités, avec contacts des anciens emplacements des donneurs et indices, sans second don ni modification des ressources.

**Les neuf dialogues du catalogue original de ces quêtes sont tous affichés et acquittés** : AC1E, A52F, 8E5C, 8E94, 8ED9, 8BEA, 8FE3, 90BF et 905B. Les cas couvrent l'absence de Foudre, la vie maximale inférieure à 56, le sixième cristal absent/présent, et la possession préalable d'une pomme ou d'huile.

Pour atteindre les états précoces, des détours réels sont utilisés : corde prise avant le troisième cristal ; autre branche entrant au troisième labyrinthe avant de finir le deuxième, sans apprendre Foudre. Les deux accès derrière les cheminées sont empruntés avant et après les dons. La corrosion résulte d'un vrai contact ennemi après retrait de la protection ; l'huile est réellement consommée pour lever l'effet.

## Aides déclarées et limites

L'aide d'approche est enregistrée et interdite pendant les boss. Deux essais séparés utilisent l'argent infini déjà autorisé : achats normaux jusqu'à 99 clés, puis refus ; achat normal d'une pomme avant le premier don de Saylun, puis réponse 905B. Ces deux branches ont leur propre relecture et restent identifiées comme tests monétaires assistés. Aucune clé, pomme, vie, créature ou étape de quête n'est injectée.

Cette clôture porte sur les deux obligations SMS demandées. Les trois textes DA58/DA7C/ED3C restent au point 5. Le montage vidéo exhaustif et les annexes restent au point 6. La comparaison correspondante sur Mega Drive, notamment en PAL/NTSC, n'est pas déduite de ces preuves SMS. Les deux lignes d'argent AD/F3 sans entrée directe restent un audit distinct ; elles ne sont pas comptées comme lieux de services supplémentaires.

[Relevé détaillé et hashes](../../analysis/sms_points_3_4_closure.json).
