# Combat intermédiaire du septième donjon sur v0309

Le parcours poursuit le [ravitaillement D7](d7_supplies_v0309.md), depuis
le même Nouveau Jeu sans import de SRAM. Le code du jeu reste la v0309,
SHA-256 `7270576d6eeb2aee641776a3e364f2f3f320711d70bb91a566d7578161261049`.

| Étape | Image finale | Salle | PV |
| --- | --- | --- | --- |
| Clé supplémentaire | 197864 | 1B9 | 66/80 |
| Deuxième obstacle Terre dégagé | 198522 | 1B9 | 66/80 |
| Protection retirée | 198523 | 1B9 | 66/80 |
| Passage vers le combat intermédiaire | 198810 | 1B8 | 66/80 |
| Combat intermédiaire remporté | 200066 | 1B8 | 54/80 |

Les deux lancers de Terre dégagent les cellules 36 et 2B de 1B9, pour huit PM
chacun. Le mécanisme ouvre ensuite le passage vers 1B8. La protection est
retirée avant ce passage, à 198523. Le premier état de combat est observé
à 198708 : héros à 66 PV, compteur de protection nul, ennemi original 78 à 30 PV.

Le combat est gagné avec les commandes ordinaires et des décisions par
séquences de huit images. Le premier dégât reçu est observé à 199898,
de 66 vers 54 PV. Les 136 fenêtres de prédiction correspondent à toute la RAM.
Aucune nouvelle écriture de test n'a lieu après le retrait de la protection.

Les six étapes, dont chacun des deux lancers Terre, ont une relecture fixe
depuis le démarrage, exacte sur les 65536 octets de RAM et le PNG final.
Les six cristaux précédents sont conservés ; le boss principal 179/type67
n'est pas entré et le bateau n'est pas encore acquis à ce point.

Les écritures de test du préfixe restent les protections d'approche déclarées
sur `hero_hurt`. Aucun PV, PM, argent, objet, acteur, progression ou SRAM
n'est importé. Le combat intermédiaire est sans protection ; toute reprise
de l'aide pour la suite doit commencer après cette victoire vérifiée et
s'arrêter à nouveau avant le boss principal.

Voir le [rapport et les empreintes](d7_midboss_v0309_report.json) et
l'[audit reproductible](../tools/summarize_d7_midboss_v0309.py).
Les sources exactes des pilotes sont figées dans
`validation/v0309-d7-midboss-sources`. Cette preuve ne valide pas encore
le bateau, le septième cristal, le retour ni la fidélité globale SMS.
