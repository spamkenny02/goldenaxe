# Bottes et sortie de ravitaillement D5 sur v0309

Le parcours poursuit [Feu, épée longue et entrée D5](fire_sword_v0309.md),
toujours sur la ROM v0309 inchangée. Les quatre cristaux précédents sont conservés.

| Étape | Image finale | Salle | PV | PM | Clés |
| --- | --- | --- | --- | --- | --- |
| Première clé | 117326 | 176 | 62/64 | 72 | 1 |
| Passage Terre | 117777 | 166 | 62/64 | 64 | 1 |
| Bottes acquises | 120893 | 157 | 60/64 | 64 | 0 |
| Sortie de ravitaillement | 121571 | Extérieur 49 | 60/64 | 64 | 0 |

Terre détruit le rocher 4A de 176 en consommant huit PM. La clé est dépensée
sur le chemin du coffre. Les bottes passent réellement de 0 à 1, comme le
sélecteur natif `hero_attack_speed`. Leur fenêtre de récompense est terminée
avant le point de contrôle. L'épée longue niveau 2, Feu, Terre, canoë et corde
sont conservés ; la hache reste sélectionnée.

Les quatre étapes ont chacune une relecture fixe depuis le démarrage, exacte
sur les 65536 octets de RAM et le PNG final. La carte physique du HUD est
conforme sur ses 128 mots après les bottes et après la sortie. L'image après
les bottes a également été inspectée.

Le parcours n'importe aucune SRAM, ressource, possession, acteur ou progression.
La protection d'approche autorisée reste explicitement active dans cet épisode,
uniquement via les écritures journalisées de `hero_hurt`. Le cinquième boss
n'est pas entré et son cristal reste absent. Cette sortie n'est donc pas
comptée comme un cinquième donjon terminé.

Le héros dispose de 16 cornes et d'aucune clé. La suite prévoit un
ravitaillement par les actions normales du jeu, puis le second passage Terre,
le mécanisme et le boss sans protection.

Voir le [rapport et ses empreintes](d5_progress_v0309_report.json) et
l'[audit reproductible](../tools/summarize_d5_progress_v0309.py).
Ces preuves de progression ne valident pas le rythme global SMS, l'ensemble
de l'audio/vidéo, le hasard source ou les essais matériels. L'objectif du
portage complet reste ouvert.
