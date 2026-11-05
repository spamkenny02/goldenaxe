# Livraison du 6 novembre 2026 au soir

Échéance confirmée par l'utilisateur : vendredi 6 novembre 2026 au soir. L'objectif reste le portage
Mega Drive fidèle de Golden Axe Warrior ; la date ne transforme pas une preuve
partielle en validation complète.

État courant : v313, 2 Mio, SHA48fb6e92…, checksum544B.
Le titre s’aligne sur SMS en PAL/NTSC et les 130 comparaisons de lignes du
récit passent. Le parcours froid atteint huit cristaux et dix entrées de boss
sans protection, puis la sortie à96/96 PV et72 PM. Un rejeu indépendant
reproduit les65536 octets de RAM et l’image finale. Voir startup_v0313_report.json.
D9, palais, fin et sauvegarde restent à valider sur cette ROM.

Entrée D9 v313 vérifiée : paiement réel 23→13 cornes, tombe ouverte par la
Cloche de glace, entrée à96 PV et72 PM avec huit cristaux. Trois étapes avec
rejeu froid RAM/image exact. Rapport d9_entry_v0313_report.json. Les mécanismes
Terre et le premier gardien sont vérifiés : cinq étapes avec rejeu RAM/image
exact. Deux coups normaux, 96→64 PV ; 72 PM conservés. 174 fenêtres de
prédiction sont exactes. Rapport d9_midboss_v0313_report.json. La suite
vers le second gardien et le ballon est lancée.

Historique des étapes précédentes (périmètres propres à chaque version) :

- ROM courante v312, 2 Mio, SHA0b9aecb4… : transition marchande corrigée,
  neuf images noires et huit étapes du portrait alignées SMS PAL/NTSC.
  43 cas couvrant les 23 villes passent ; le parcours NTSC jusqu'à la sortie
  de D2 conserve les champs de jeu comparés et l'image finale de la v311.
  Le panneau complet reste une image tardif en PAL.
- Campagne v312 : D2 rejoué depuis le démarrage, huile obtenue par le dialogue
  et les escaliers, puis corde, mécanisme, clé et troisième cristal. Retour
  extérieur vérifié à 56/56 PV, sans protection ni dégât pendant le boss D3.
  Chaque point promu a un rejeu indépendant RAM/image exact ; trois marqueurs
  et les 128 mots physiques du HUD sont vérifiés après le boss et la sortie.
- Préparation D4 sur v312 : don de 50 cornes et achat réel de Terre pour 50,
  niveau 1 et capacité de 48 PM. Quatre points avec rejeu RAM/image exact.
  Entrée D4, clés, canoë et deux passages Terre vérifiés par sept relectures
  RAM/image. Boss vaincu sans protection ni dégât, quatrième cristal et retour
  extérieur vérifiés à 62/64 PV. Combat et sortie relus exactement en RAM/image,
  quatre marqueurs et 128 mots physiques du HUD vérifiés. Déplacement réel en
  canoë observé pendant le rejeu ; préparation D5 en cours.
- Préparation D5 v312 terminée : huile échangée contre Feu, épée longue
  réellement reçue et entrée dans D5 à 62/64 PV, 72/72 PM. Sept étapes avec
  rejeu RAM/image exact ; cinquième cristal encore hors de cette preuve.
- D5 v312 : première clé, passage Terre, bottes et sortie de ravitaillement
  vérifiés par quatre relectures RAM/image. Sortie à 58/64 PV, 64 PM ; gain
  de vitesse actif. Préparation du cinquième boss en cours.
- Ravitaillement D5 v312 : dons de 30 + 30 cornes, achat d'une clé pour 60,
  soin gratuit, retour, second passage Terre et mécanisme vérifiés. Treize
  étapes depuis l'entrée avec rejeu RAM/image exact ; point préparatoire à
  64/64 PV et 56 PM avec une clé. Protection retirée en 173 à l'image 127330,
  avant l'entrée du boss 65 en 163.
- D5 v312 terminé : huit satellites et boss vaincus sans protection, coup
  normal de dix PV observé. Cinquième cristal et retour extérieur à 72/72 PV
  et PM ; cinq étapes finales relues exactement en RAM/image et cinq marqueurs
  du HUD vérifiés. Le pilote ciblant les satellites réduit la recherche de
  415 à 60 décisions ; la partie retenue continue sur cette branche.
  Préparation D6 terminée : cinq acquisitions de clés, passages Terre,
  Cloche de glace et accès du boss vérifiés par 17 rejeux RAM/image exacts.
  Point préparatoire à 72/72 PV et 64 PM, sans objet ni ressource injecté.
  Le retrait de l'aide est relu exactement à l'image 156803, avant la salle
  du sixième boss et en conservant les ennemis ordinaires de l'antichambre.
  Sixième boss et cristal vérifiés sans protection ni dégât reçu. Retour
  extérieur à 80/80 PV et 72 PM ; combat et sortie ont un rejeu froid RAM/image
  exact, avec six marqueurs et 128 mots physiques du HUD contrôlés.
  Le premier pilote de retour reste immobile et atteint sa limite d'images ;
  la variante à décisions de huit images réussit en 94 prédictions exactes,
  sans nouvelle écriture d'aide.
- D7 v312 préparé : achat réel d'une clé pour 60 cornes, entrée du donjon,
  deux acquisitions de clés et deux ouvertures Terre pour 16 PM. Sept étapes
  avec rejeu froid RAM/image exact ; six cristaux conservés, 64 PV, 56 PM et
  deux clés au point préparatoire.
- Intermédiaire D7 v312 vaincu sans protection. Coup normal de 12 PV observé,
  reprise de l'approche après victoire à 52 PV et 56 PM. Quatre points avec
  rejeu froid RAM/image exact : retrait, passage, combat et reprise.
  Le navire et le boss principal sont validés par la suite ci-dessous.
- D7 v312 terminé : navire, septième cristal et retour extérieur vérifiés à
  68/88 PV et 64 PM, avec une clé. Dix étapes depuis la reprise passent leur
  rejeu froid RAM/image exact ; HUD physique contrôlé après navire, cristal
  et sortie. Aucun soutien pendant les deux boss ou le retour ; les dégâts
  restent enregistrés. Parcours vers D8 lancé depuis cette sortie.
- Entrée et gardien D8 v312 vérifiés : passage réellement payé 10 cornes
  (12→2), puis victoire sur7A/50 PV sans protection ni dégât reçu, à56/88 PV.
  Les six étapes ont un rejeu froid RAM/image exact ;124 prédictions complètes
  sont vérifiées pendant le combat. Le huitième cristal reste à valider.
- Approche D8 v312 vérifiée : reprise après le gardien, mécanismes distants,
  Terre et clé des voleurs, jusqu'à l'antichambre du boss principal. Huit points
  ont leur rejeu froid RAM/image exact, à88/88 PV et72 PM au dernier point.
  L'aide est retirée avant196 ; le combat principal est en cours.
- Menu Nouveau jeu / Continuer v312 : musique active et audible en PAL/NTSC,
  événements des bruitages de curseur et validation alignés SMS. Aucune
  comparaison globale des formes d'onde n'est déduite de ce contrôle.
- Accélération des simulations de commandes : rendu secondaire supprimé,
  audio et format de sauvegarde conservés. Soixante cas D6 conservent la RAM
  et la phase processeur, avec un débit environ 38 % supérieur sur ce benchmark.
  Un retour D5 conserve ses sept prédictions RAM, son image finale et son rejeu
  froid officiel. Aucun changement de ROM ; ce n'est pas un gain global de 38 %
  sur tous les tests. Le combat D6 utilisait le calcul initial ; son retour
  retenu emploie cette option avec les mêmes contrôles.
- v311, 2 Mio, SHA0972465d… : correction d'une image du
  chargement vers le haut en NTSC. Premier donjon, hache, fontaine et clés du
  deuxième donjon vérifiés par rejeu exact. Deuxième cristal et retour extérieur
  vérifiés à 48/48 PV, sans protection ni dégât pendant le boss. La fin de
  campagne v310 ne vaut pas validation complète des versions suivantes.
- ROM de référence v310, 2 Mio, SHA32fe75a6… : récurrence SMS 04E1 raccordée.
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

Le correctif du chargement initial est intégré à la v313 ; le binaire public
est identique au candidat testé jusqu’à la sortie du huitième donjon.
La suite repart du préfixe froid md-auto-v0313-d8-cold01.

1. Poursuivre la validation de la ROM courante et traiter les blocages ou régressions
   réellement rencontrés. Réutiliser les préfixes froids déjà vérifiés ; ne pas
   recommencer les étapes acquises. Les protections restent sur les approches,
   retirées avant chaque boss ; aucun état ou progression n'est importé.
2. Revenir aux contrôles ciblés seulement en cas de changement de code, d'échec
   ou d'incertitude concernant la ROM livrée. Réserver les analyses secondaires
   après ces contrôles critiques ; aucune amélioration de confort supplémentaire.
3. Publier sur main le code, le README et la ROM numérotée effectivement testée,
   avec ses empreintes et des limites explicites. Ne pas créer de numéro pour
   les seuls documents ou preuves. Ne pas annoncer une fin de campagne sur la
   version courante à partir des seules preuves d'une version précédente.

La fidélité R/IRQ globale et les vérifications audiovisuelles, optionnelles
et sur console réelle restent ouvertes. La phase
exacte du fournisseur R demeure provisoire. Ne pas garantir une version finale
sans réserve le 6 novembre tant que ces preuves manquent. La livraison doit
indiquer clairement ce qui a été vérifié et ce qui reste ouvert.
