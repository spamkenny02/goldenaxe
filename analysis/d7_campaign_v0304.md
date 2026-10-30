# v304 : septième cristal et retour du donjon

La ROM reste inchangée : SHA-256 `b7b4e15008a6f0a913c9ad43f15386abcdfbb719e5a575873d92712ba52503a8`, checksum `0558`. Ce parcours continue l’[approche D7](d7_navigation_v0304.md).

Le boss principal de la salle 179 est le type 67 de la ROM SMS, données `3c120240` (60 PV, attaque 18, armure 2, drapeau boss 40). La protection de test s’arrête à la frame 182050. Le combat commence 27 frames plus tard à 80 PV, sans délai d’invulnérabilité résiduel ; le premier dégât ordinaire arrive en 182232.

| Étape retenue | Frame finale | Salle | PV | Cristaux | Magie |
| --- | ---: | --- | ---: | ---: | ---: |
| Combat partiel, boss à 26 PV | 185677 | 179 | 78/80 | 6 | 48 |
| Victoire, commandes ordinaires | 187841 | 179 | 88/88 | 7 | 48 |
| Retour et Terre sur le bloc 57 | 188942 | 1B7 | 52/88 | 7 | 40 |
| Sortie extérieure | 189330 | 1B | 36/88 | 7 | 40 |

Deux clés restent présentes à chaque étape. Le minimum avant la récompense est de 42 PV ; le cristal soigne normalement le héros et augmente sa capacité à 88. Le retour ne réactive aucune aide : Terre consomme réellement huit points de magie, le bloc disparaît, la hache est rééquipée et le téléporteur devient accessible.

Chaque étape possède une relecture indépendante à commandes fixes depuis le démarrage : les 65536 octets de RAM et le PNG final sont identiques. Aucun état secondaire n’est importé dans le jeu. L’essai boss02, qui finit à 18 PV de boss, est une branche partielle distincte, jamais l’ancêtre de la victoire. L’essai de retour exit01 reste bloqué près du bloc entourant le téléporteur ; la branche retenue repart de la victoire et le dégage avec Terre.

Le profil de pile relit tout le parcours jusqu’en 189330 : minimum avant chaque instruction 63454, minimum aux points instrumentés 63472, limite du tas 62976. La marge observée est donc de 478 octets. Le tas reste cohérent et la RAM ainsi que le PNG finaux correspondent aussi au parcours canonique.

La campagne conserve les aides d’approche déclarées des donjons précédents. Le dragon intermédiaire type78 de D7 a été affronté sous cette protection. Le combat principal de 179 et son retour sont sans protection ; ce résultat ne prouve pas une campagne entièrement sans aide, une égalité complète du combat SMS ou tous les chemins possibles.

Le [rapport reproductible](d7_campaign_v0304_report.json) lie les relectures, les sources et le profil de pile. Les donjons suivants, la fin, les sauvegardes, le hasard et la phase globale, ainsi que la fidélité vidéo/audio complète restent à vérifier.
