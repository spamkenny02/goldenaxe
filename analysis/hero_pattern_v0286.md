# v0286 : préparation graphique du héros

ROM de 2 Mio, SHA-256
`611e3db48f20f3317faef9b5145160dd944589b99e0e3b9790fd4ec1b625fd4a`,
checksum `4D3F`.

La préparation des poses du héros utilise maintenant la conversion par paires
de plans déjà présente dans le port. Les chargements sans échéance explicite
conservent leur chemin précédent. Le transfert des poses reste possédé par
la publication VBlank et ses indicateurs existants ; aucune mémoire permanente
supplémentaire n’est allouée.

Sur 48 changements de pose mesurés dans chaque région, le coût médian complet
de `prepare_hero_patterns` passe de 148 176 à 123 060 cycles maître :
**16,95 % de temps CPU en moins pour cette fonction**. Les appels chevauchant
une IRQ sont exclus de cette mesure. Les poses, nombres de tuiles et pixels
convertis concordent avec la v0285 sur 561 frames en PAL et 561 en NTSC.
Ce chiffre ne mesure pas le gain de FPS global.

Les six séquences de déplacement et de défilement PAL/NTSC retrouvent les
états SMS suivis, sans différence sur les frames observées. Les huit mouvements
déterministes de monstres passent également. Les six retours d’inventaire
conservent les fenêtres noires, le HUD, la reprise et la fermeture silencieuse
de la référence. Les segments contrôlés de boss et de projectiles conservent
les 768 octets d’acteurs SMS sur 308 frames.

Un nouveau parcours à commandes ordinaires récupère la hache, l’équipe,
termine le premier boss, prend son cristal et ressort sans décès ni injection.
Il termine à la frame 16 802, avec 28/32 points de vie. La relecture indépendante
reproduit les 65 536 octets de RAM et l’image finales. Les 256 indicateurs
persistants et les 1 280 octets de carte correspondent au parcours SMS archivé.
L’observation de chaque instruction conserve SP au-dessus de `$FFF79C`, soit
412 octets de marge sur ce parcours ; le tas reste valide et l’observateur
reproduit aussi la RAM et l’image finales.

Les anciennes commandes longues v0285 ne terminent pas ce parcours sur v0286.
Elles sont conservées comme essai négatif ; le parcours retenu a été régénéré
avec le pilote qui observe les positions réelles. Le flux aléatoire SGDK reste
provisoire. Une différence de relecture entre versions ne prouve donc pas une
régression de logique, et l’identité des rencontres entre versions n’est pas
revendiquée.

## Deuxième boss : diagnostic séparé sur v0285

Le pilote géométrique a abaissé sa vie de 30 à 12 avant de mourir. Une recherche
qui conserve des trajectoires d’esquive complètes atteint ensuite 16 points
de vie pour le boss en conservant les 32 points du héros pendant 1 800 frames
de combat. Ses 225 fenêtres prévues de huit frames concordent avec toute la
RAM réelle. L’invincibilité est coupée avant le combat ; aucune santé n’est
rechargée. Une relecture officielle à la frame 32 751 reproduit la RAM et
l’image avec le boss à 16 et le héros à 32. Le point final de l’essai borné
dispose de RAM, mais pas de PNG d’origine ; la capture anticipée des futurs
essais bornés a été corrigée.

Le profil v0285 a relevé sept intervalles de deux frames entre étapes de
simulation sur 443 frames de ce combat. L’optimisation v0286 réduit un coût
de préparation, mais la disparition de ces sept intervalles reste à vérifier
sur un nouveau combat v0286. Aucun deuxième cristal n’est encore validé.

Preuves : [rapport v0286](hero_pattern_v0286_report.json),
[mesure des poses](../tools/validate_hero_pattern_fast.py),
[synthèse reproductible](../tools/summarize_hero_pattern_v0286.py).
Les captures sont archivées localement sans perte et vérifiées avant nettoyage.
La campagne complète, les horloges source, le signal audio analogique et
le matériel restent à valider.
