# Cinquième cristal et retour dehors sur v0306

La ROM reste la v0306, SHA-256 `3a12380b86c193148d1cbd29d68a880901860cfb1c276aa96d61d2da16ac2c01`.
Le code du jeu n’a pas changé. Le parcours reprend l’entrée du cinquième donjon,
image 100 808, après l’acquisition réelle du Feu et de l’épée longue.

Les treize premières étapes valident la première clé, Terre sur le rocher 4A de 176,
les bottes en 157, une sortie de ravitaillement, deux dons de 30 pièces,
l’achat d’une clé à 60 pièces et le soin gratuit du marchand de 94.
L’argent passe de 10 à 40, puis 70 et enfin 10 après l’achat. Le soin porte les PV de 42 à 64.
Au retour, Terre détruit le rocher 44 de 153 pour 8 PM et le portail mène en 162.
Le mécanisme original 5C96 s’active par UP stationnaire en (72,40), sans devoir tuer
les ennemis présents. La salle 172 est atteinte à l’image 120 356, à 60/64 PV et une clé.
Ces treize étapes ont chacune une relecture froide indépendante exacte sur toute la RAM et le PNG final.

| Étape finale | Image finale | Résultat |
| --- | ---: | --- |
| Boss 65 et cinquième cristal | 124 375 | 72/72 PV, 72/72 PM |
| Mécanisme du retour en 173, puis 174 | 124 723 | Passage ouvert, 72/72 PV |
| Portail, sortie et pont de 49 | 125 472 | Cinq cristaux, 40/72 PV, aucune clé |

L’épée longue, obtenue sans fixture, est sélectionnée par le menu ordinaire : niveau 2,
force 6. L’armure reste au niveau 1 ; la hache est possédée mais n’est pas sélectionnée.
La protection d’approche est relâchée à l’image 122 250, 27 images avant le premier
état de combat 122 277, avec un compteur de blessure nul. Des cœurs ordinaires ont
porté les PV de 60 à 64 avant le boss. Les dégâts normaux sont observés dès 122 416,
de 64 à 54 PV. La victoire et le cristal sont acquis à 124 225.

La recherche du combat vérifie 87 fenêtres sur les 65 536 octets de RAM ; celle du retour
en vérifie 14. Les trois étapes finales ont aussi leur relecture froide indépendante
exacte sur toute la RAM et le PNG final. Aucune protection n’est réactivée après
122 250. Aucun PV, PM, argent, objet, acteur, progression ou SRAM n’est importé.
Les protections des approches restent une aide de test explicitement autorisée ;
ce parcours ne constitue pas une campagne sans aide sur les approches.

Le premier essai de contrôleur restait au seuil de la salle et n’est pas promu comme
victoire. Sa relecture négative est conservée. Une option du contrôleur fait désormais
huit entrées UP ordinaires pour finir de pénétrer dans la salle avant la recherche.
Le contrôle de budget rejette aussi un nombre d’images inférieur au préfixe enregistré.
Ces ajustements concernent les outils de test, sans modification de la ROM.

Le profil de chaque instruction normale couvre tout le parcours de 125 472 images :
SP minimum 63 418, limite du tas 62 976, marge observée 442 octets et tas valide.
La RAM et le PNG finaux du profil correspondent à la relecture canonique.
Le pont de 49 possède son drapeau original débloqué. Les 128 mots physiques du HUD
final et les cinq indicateurs de cristal suivent la table SMS 1EDC.

La fin du jeu, les autres donjons, les sauvegardes complètes et le hasard/phasage source
global ainsi que la fidélité audiovisuelle complète restent à valider.

Rapports : [ravitaillement](d5_supplies_v0306_report.json), [cinquième cristal](d5_campaign_v0306_report.json).
Audits : `python tools/summarize_d5_supplies_v0306.py` puis `python tools/summarize_d5_campaign_v0306.py`.
Les captures volumineuses sont archivées localement et vérifiées avant nettoyage ;
les ROMs numérotées sont conservées.
