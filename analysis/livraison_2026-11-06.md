# Livraison du 6 novembre 2026 au soir

Échéance reportée au vendredi 6 novembre au soir par l'utilisateur le 4 novembre. L'objectif reste le portage
Mega Drive fidèle de Golden Axe Warrior ; la date ne transforme pas une preuve
partielle en validation complète.

État constaté :

- ROM courante v310, 2 Mio, SHA32fe75a6… : récurrence SMS 04E1 raccordée.
  Parcours depuis Nouveau Jeu vérifié jusqu’à la victoire sur Death Adder,
  au générique complet et au retour à l’intro.
- v309 : campagne depuis Nouveau Jeu jusqu'à la fin, générique, retour intro,
  et sauvegarde réelle/Continuer vérifiés. C'est une référence historique,
  pas une preuve de fin v310.
- Sur v310, la reprise après une mort et le soin gratuit en 94 sont vérifiés.
  Le héros franchit le pont du cinquième cristal et entre dans D7, puis
  récupère deux clés et ouvre deux obstacles avec Terre.
- D7 terminé sur v310. Gardien et boss principal vaincus sans protection ni
  dégât reçu, bateau et septième cristal conservés en extérieur. Voir
  `d7_campaign_v0310_report.json`.
- D8. Gardien et boss principal vaincus sans invincibilité. Le huitième cristal
  est récupéré à l’image 272 980 et le rejeu du combat est exact en RAM et
  en image. Le retour en extérieur est vérifié à l’image 273 836 avec les
  huit cristaux.
- D9. Deux gardiens et boss principal vaincus sans invincibilité. Sortie
  vérifiée avec les neuf cristaux et le ballon. Le ballon restaure la carte
  et le HUD à la fermeture.
- Palais. La porte des neuf cristaux s’ouvre. Le géant et le gardien de la
  Hache d’or sont vaincus sans invincibilité. La hache est récupérée et
  équipée. Death Adder est vaincu sans invincibilité ni dégât reçu. Le rejeu
  exact de la campagne et de la fin atteint l’image 415 125.
- Sauvegarde v310. Un enregistrement écrit en jeu dans le premier emplacement
  restaure les objets, les neuf cristaux, le HUD et les déplacements après
  redémarrage via Continuer.

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

La fidélité R/IRQ globale et les vérifications audiovisuelles, optionnelles
et sur console réelle restent ouvertes. La phase
exacte du fournisseur R demeure provisoire. Ne pas garantir une version finale
sans réserve le6 novembre tant que ces preuves manquent. La livraison doit
indiquer clairement ce qui a été vérifié et ce qui reste ouvert.
