# Deuxième donjon terminé sur SMS et Mega Drive, v0286

La ROM Mega Drive reste la **v0286**,
SHA-256 `611e3db48f20f3317faef9b5145160dd944589b99e0e3b9790fd4ec1b625fd4a`.
Cette étape apporte des parcours vérifiés et des outils d’essai ; le binaire
du jeu ne change pas.

La visite de la fée est rejouée par les commandes ordinaires : dialogue,
capacité portée à 40, vie remplie par le jeu et sortie à C9. L’assistance
autorisée commence ensuite. Elle conserve ces 40 points jusqu’au deuxième
boss, en écrivant uniquement le compteur d’invulnérabilité du héros.
La dernière écriture remet ce compteur à zéro pendant l’entrée dans sa salle,
avant la première étape de combat. Aucune écriture de test ne suit : le boss,
son cristal et le trajet de sortie utilisent les règles normales.

| Résultat | Mega Drive v0286 | SMS originale |
| --- | --- | --- |
| Nouvelle clé du deuxième donjon | compteur 1 → 2 | compteur 1 → 2 |
| Vie au début du boss | 40, compteur de blessure à zéro | 40, compteur de blessure à zéro |
| Deuxième boss | vaincu | vaincu |
| Cristal | pris, vie et capacité à 48 | pris, vie et capacité à 48 |
| Sortie | D6, 45/48 PV | D6, 48/48 PV |
| Décès pendant ces essais | 0 | 0 |
| Relecture indépendante | 65 536 octets de RAM et PNG exacts | 8 192 octets de RAM et PNG exacts |

Les **256 indicateurs persistants et les 1 280 octets de carte** sont identiques
entre SMS et MD à la sortie. Les deux indicateurs de cristal valent `$80`.
L’identité des rencontres, de l’argent ou de la santé restante n’est pas
revendiquée : le hasard SGDK et les horloges source restent à raccorder.
Les enregistrements démarrent tous à froid, sans import de SRAM ni d’état
d’émulateur dans le jeu principal.

Le pilote de combat choisit des boutons après prévision dans un cœur
secondaire. Les 74 fenêtres MD et les 75 fenêtres SMS concordent avec toute
la RAM principale. Les parcours retenus sont ensuite rejoués sur le cœur
officiel avec boutons et écritures d’approche fixes, sans lecture de retour.
Il s’agit d’essais à approche assistée, pas de campagnes naturelles complètes.
Le premier essai latéral a échoué ; l’autre recherche a été arrêtée après
la victoire du pilote retenu. Leurs fichiers restent conservés.

L’observation de chaque instruction MD jusqu’à la frame 32 419 retrouve
le minimum SP `$FFF79C`, soit **412 octets au-dessus de la limite observée**.
Le tas reste valide. La RAM et le PNG de cet observateur correspondent aussi
à l’enregistrement officiel. L’observateur ne modifie pas la mémoire ; il
rejoue explicitement l’assistance d’approche consignée.

Le segment de boss MD observé compte encore trois intervalles de deux frames
entre étapes de simulation sur 559 frames. Cela ne constitue pas une mesure
comparative de FPS avec l’ancien combat, dont les boutons et rencontres
diffèrent. Les échéances physiques complètes restent à vérifier.

Les outils peuvent désormais prolonger un préfixe assisté seulement avec
une option explicite et une preuve de relecture complète liée par SHA-256.
Les chemins ordinaires refusent ces préfixes. La version SMS utilise son
compteur d’un octet à C305 ; le port utilise son mot natif. L’extraction de
direction du pilote SMS a été corrigée de C302, qui contient la base des
motifs, vers C30A. Les octets des pilotes utilisés avant cette correction
sont conservés ; les commandes et les relectures réussies restent la preuve
du parcours historique.

Voir le [rapport reproductible](d2_campaign_v0286_report.json) et
[sa synthèse](../tools/summarize_d2_campaign_v0286.py).
Les captures sont archivées localement sans perte avant nettoyage ; le
manifeste est versionné. La suite de la campagne, le PAL, les horloges
R/IRQ, la fidélité audio complète et le matériel restent ouverts.
