# Cinquième cristal et retour extérieur sur v0309

Le parcours poursuit le [ravitaillement et les mécanismes D5](d5_supplies_v0309.md),
depuis le même Nouveau Jeu sans import de SRAM. La ROM reste v0309, SHA-256
`7270576d6eeb2aee641776a3e364f2f3f320711d70bb91a566d7578161261049`.
Le programme du jeu n'a pas changé pendant cette validation.

| Étape | Image finale | Salle | PV |
| --- | --- | --- | --- |
| Antichambre nettoyée, épée longue sélectionnée | 138502 | 173 | 64/64 |
| Protection retirée | 138503 | 173 | 64/64 |
| Cinquième cristal, récompense terminée | 145576 | 163 | 72/72 |
| Mécanisme du retour traversé | 145917 | 174 | 72/72 |
| Retour extérieur | 146657 | 49 | 72/72 |

Le combat commence à l'image 138593 avec le héros à 64 PV, compteur de
protection nul, contre le boss original 65 à 72 PV. Ses huit satellites 66
sont présents dans le relevé du combat. Ils sont détruits avant les premiers
dégâts observés sur le noyau à 144016. Le premier dégât reçu par le héros
est observé à 139882 : 64 vers 54 PV. Le cristal et son soin sont ensuite
obtenus normalement ; aucune récompense n'est injectée.

La dernière écriture de test est le retrait de la protection à 138503,
dans l'antichambre, avant l'entrée chez le boss. Aucune nouvelle écriture
n'a lieu pendant le combat, le mécanisme du retour ou la sortie. Les
approches précédentes restent explicitement assistées, uniquement par
`hero_hurt`. Aucun PV, PM, argent, objet, acteur ou drapeau de progression
n'est importé, et aucun état secondaire de recherche n'est chargé dans le jeu principal.

Le retour active le mécanisme original de 173 puis traverse vers 174.
Le portail conduit à 155, avant le trajet 165, 166, 176, 186 et extérieur 49.
Le héros conserve ses 72 PV pendant ce retour, avec 72 PM, aucune clé,
Feu, Terre, bottes, canoë et corde. L'épée longue niveau 2 reste sélectionnée.

Les cinq étapes ont chacune une relecture fixe depuis le démarrage, exacte
sur les 65536 octets de RAM et le PNG final. Les 198 fenêtres de prédiction
du combat et les trois du retour correspondent à toute la RAM. Le pilote
utilise des décisions par séquences de 32 images et une entrée UP ordinaire
pour franchir complètement l'entrée du boss.

Après le cristal et après la sortie, les 128 mots de la carte physique du
HUD correspondent à la conversion SMS et les cinq marqueurs de cristal
suivent la table de la ROM originale. L'image après la récompense a été inspectée.

Voir le [rapport et les empreintes des preuves](d5_campaign_v0309_report.json)
et l'[audit reproductible](../tools/summarize_d5_campaign_v0309.py).
Les sources exactes des pilotes sont figées localement dans
`validation/v0309-d5-boss-sources`. La campagne courante couvre maintenant
cinq cristaux et leurs retours. Les donjons suivants, le parcours froid
complet jusqu'à la fin, le hasard source, les contenus optionnels et la
fidélité globale audio/vidéo/matériel restent ouverts.
