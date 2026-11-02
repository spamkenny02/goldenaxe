# Feu, épée longue et entrée D5 sur v0309

Le parcours reprend la sortie du quatrième donjon, image 101777, sans import
de SRAM. La ROM reste v0309, SHA-256
`7270576d6eeb2aee641776a3e364f2f3f320711d70bb91a566d7578161261049`.

| Étape | Image finale | Résultat |
| --- | --- | --- |
| Entrée chez le maître du Feu | 106742 | Maison BF de E6 |
| Première visite et sortie | 107316 | Présentation faite, huile conservée |
| Seconde entrée | 107525 | Maison BF atteinte |
| Apprentissage et sortie | 108195 | Feu 1, huile consommée, magie 72/72 |
| Entrée chez le donateur | 111204 | Maison 4F de 50 |
| Épée longue et sortie | 111709 | Épée de niveau 1 vers 2 |
| Entrée du cinquième donjon | 116210 | Salle 186, 62/64 PV, 72 PM |

L'huile acquise plus tôt est réellement échangée contre Feu lors de la seconde
visite. Le don de l'épée vient du dialogue normal ; le drapeau de la maison
est posé par le jeu. Aucun objet, argent, PV, acteur ou état de progression
n'est injecté. La hache reste sélectionnée, l'épée longue est disponible.

Les sept étapes ont chacune une relecture fixe depuis le démarrage,
identique sur toute la RAM de 65536 octets et le PNG final. Les 128 mots de
la carte physique du HUD sont vérifiés après Feu et après l'épée.
Les protections d'approche sont déclarées et journalisées ; le cinquième
épisode attend le boss de 163, encore non abordé à ce point.

Voir le [rapport](fire_sword_v0309_report.json) et
l'[audit reproductible](../tools/summarize_fire_sword_v0309.py).
La [suite vers les bottes](d5_progress_v0309.md) prolonge ce même parcours.
Les sources des pilotes sont figées localement dans `validation/v0309-d5-sources`.
Le programme du jeu n'a pas changé ; aucune nouvelle version de ROM n'est créée.
Le cinquième cristal et la fidélité globale ne sont pas validés par ce rapport.
