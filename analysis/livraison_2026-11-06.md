# Livraison du 6 novembre 2026 au soir

Échéance reportée au vendredi 6 novembre au soir par l'utilisateur le 4 novembre. L'objectif reste le portage
Mega Drive fidèle de Golden Axe Warrior ; la date ne transforme pas une preuve
partielle en validation complète.

État constaté :

- ROM courante v310, 2 Mio, SHA32fe75a6… : récurrence SMS 04E1 raccordée.
  Parcours froid jusqu'au sixième cristal et retour en extérieur vérifié.
- v309 : campagne depuis Nouveau Jeu jusqu'à la fin, générique, retour intro,
  et sauvegarde réelle/Continuer vérifiés. C'est une référence historique,
  pas une preuve de fin v310.
- Sur v310, la reprise après une mort et le soin gratuit en 94 sont vérifiés.
  Le héros franchit le pont du cinquième cristal et entre dans D7, puis
  récupère deux clés et ouvre deux obstacles avec Terre.
- Le gardien intermédiaire de D7 est vaincu sans protection ni dégât reçu.
  La victoire est relue exactement jusqu'à l'image 206928. Le héros termine
  avec 80/80 PV, 24/72 PM et trois clés. Le bateau et le septième cristal
  restent à vérifier. Voir `d7_midboss_v0310_report.json`.

Ordre de travail pour la livraison :

1. Achever la validation du parcours v310 et traiter les blocages ou régressions
   réellement rencontrés. Réutiliser les préfixes froids déjà vérifiés ; ne pas
   recommencer les étapes acquises. Les protections restent sur les approches,
   retirées avant chaque boss ; aucun état ou progression n'est importé.
2. Revenir aux contrôles ciblés seulement en cas de changement de code, d'échec
   ou d'incertitude concernant la ROM livrée. Réserver les analyses secondaires
   après ces contrôles critiques ; aucune amélioration de confort supplémentaire.
3. Publier sur main le code, le README et la ROM numérotée effectivement testée,
   avec ses empreintes et des limites explicites. Ne pas créer de numéro pour
   les seuls documents ou preuves. Ne pas annoncer une fin de campagne sur la
   version courante à partir des seules preuves v309.

Risques matériels de planning : il reste la suite v310 après D6 et la fidélité
R/IRQ globale, ainsi que des vérifications audiovisuelles/optionnelles. La phase
exacte du fournisseur R demeure provisoire. Ne pas garantir une version finale
sans réserve le6 novembre tant que ces preuves manquent. La livraison doit
indiquer clairement ce qui a été vérifié et ce qui reste ouvert.
