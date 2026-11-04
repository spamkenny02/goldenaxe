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
- Étape courante v310 : clés, Terre, cloche de glace et D6 terminé.
  Dernier checkpoint `md-auto-v0310-d6-exit01`, image190773 dans
  `natural-dungeon-combat`, salle8B,2/80PV et72PM. Vingt étapes depuis D5
  relues avec RAM65536/PNG exacts. Boss64 sans protection ; 1202 prédictions
  combat et121 retour exactes. Soin normal prioritaire avant la suite D7.
  Aucun processus de validation actif sur ce jalon.

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
