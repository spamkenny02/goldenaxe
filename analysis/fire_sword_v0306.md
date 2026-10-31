# Feu, épée longue et entrée du cinquième donjon sur v0306

La ROM reste la v0306, SHA-256 `3a12380b86c193148d1cbd29d68a880901860cfb1c276aa96d61d2da16ac2c01`.
Aucun code du jeu n’a changé ; aucun nouveau numéro de ROM n’est créé pour ces validations.

Le parcours reprend les quatre cristaux et le retour dehors en 10, à l’image 86 364.
Le canoë, la corde et la hache permettent de rejoindre le maître du Feu en E6.
La première visite ne fait que le présenter et conserve l’huile récupérée réellement en C7.
La seconde consomme cette huile, apprend le Feu et porte la magie de 48 à 72.
L’épée longue est ensuite donnée dans la maison de 50 : niveau 1 vers 2, drapeau 48 vers 50.
Le personnage atteint enfin l’entrée 186 du cinquième donjon à l’image 100 808,
avec 50/64 PV, 72 points de magie, 9 pièces et aucune clé. La hache reste sélectionnée.

| Étape | Image finale | Résultat |
| --- | ---: | --- |
| Entrée du maître du Feu | 91 330 | BF atteint |
| Présentation et sortie | 91 916 | Feu 0, huile 1 |
| Seconde entrée | 92 126 | BF atteint |
| Apprentissage et sortie | 92 797 | Feu 1, huile 0, magie 72/72 |
| Entrée du donateur | 95 807 | Maison 4F de 50 |
| Don de l’épée et sortie | 96 309 | Épée longue niveau 2 |
| Entrée du cinquième donjon | 100 808 | Salle 186, 50/64 PV |

Chaque étape possède une relecture froide indépendante reproduisant les 65 536 octets
de RAM et le PNG final. Les seules écritures de test sont les protections d’approche
héritées et journalisées. Aucun objet, acteur, PV, magie, argent, progression ou SRAM
n’est importé. Les quatre épisodes précédents retirent la protection avant leur boss
principal ; le cinquième reste en attente du boss 163. Cela ne constitue pas un parcours
sans aide sur les approches.

La comparaison ciblée de l’apprentissage du Feu avec la SMS passe en PAL et NTSC.
Elle utilise ses propres fixtures contrôlées, distinctes du parcours ci-dessus.
Le profil de pile de chaque instruction normale couvre 96 309 images : SP minimum
63 418, limite du tas 62 976, marge observée 442 octets, tas valide et RAM/PNG finaux exacts.
Ce profil ne couvre pas encore la portion ultérieure vers l’entrée du cinquième donjon.

La tentative d’armure en 27 n’est pas promue : la porte reste fermée après l’approche.
Le script SMS AE91 appelle 5FB1, extrait comme récompense de salle vidée (kind 7).
Une approche UP sur la carte fermée est également bloquée sur SMS et MD en PAL/NTSC.
Cette comparaison prépare une carte et des acteurs contrôlés ; elle ne prouve ni un
combat naturel ni un don d’armure. Les propositions vers B1 et 6A n’ont pas trouvé
un trajet dans le modèle de base avec l’équipement actuel. L’armure reste au niveau 1.

Le cinquième cristal, la seconde moitié du jeu, la fin, les sauvegardes complètes,
le hasard/phasage source global et la fidélité audiovisuelle complète restent à valider.

Rapport : [fire_sword_v0306_report.json](fire_sword_v0306_report.json).
Audit reproductible : `python tools/summarize_fire_sword_v0306.py`.
