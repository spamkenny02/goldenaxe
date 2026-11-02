# Clé des voleurs et accès au boss du huitième donjon sur v0309

La campagne poursuit la victoire intermédiaire vérifiée. La protection
d'approche reprend seulement après cette victoire canonique ; le gardien 7A
vaincu ne réapparaît pas vivant lors du retour en 1C9. Aucun PV, PM, argent,
objet, acteur, progression ou état SRAM n'est importé.

| Étape | Image finale | Salle | PV | PM | Argent |
| --- | --- | --- | --- | --- | --- |
| approach-resume01 | 231569 | 1C9 | 28/88 | 64 | 33 |
| post-mini-c8-01 | 233542 | 1C8 | 52/88 | 64 | 33 |
| switch1eb-01 | 234368 | 1EB | 52/88 | 64 | 33 |
| switch1ec-02 | 237269 | 1EB | 84/88 | 64 | 33 |
| earth1e8-01 | 242150 | 1AA | 84/88 | 56 | 33 |
| thief-key01 | 250470 | 1A9 | 88/88 | 56 | 33 |
| switch19a-01 | 253098 | 1AA | 88/88 | 56 | 40 |
| approach01 | 256794 | 1A6 | 88/88 | 64 | 40 |

Les ramassages ordinaires remontent progressivement les PV de 28 à 88.
Les mécanismes 1EB et 1EC ouvrent les passages distants. Terre détruit
la cellule 58 de 1E8 pour huit PM et le portail mène à 1AA. En 1A9, l'objet 15
est réellement acquis et sa fenêtre se ferme. Le mécanisme 19A ouvre ensuite
1D8 ouest et 1D7 est. Le héros atteint l'antichambre 1A6 avec une clé.

Les huit points sont relus indépendamment depuis le démarrage : les 65536
octets de RAM et le PNG final sont identiques. Les 128 mots physiques du HUD
et les sept marqueurs de cristal sont vérifiés. Ce rapport s'arrête avant
l'entrée du boss 196 ; posséder la clé ne prouve pas tous ses usages.

Reproduction : `python tools/summarize_d8_thief_v0309.py`.
Voir le [rapport et ses empreintes](d8_thief_v0309_report.json).
Sources et recettes exécutées : `validation/v0309-d8-thief-sources`.
La fidélité globale SMS et les contenus optionnels restent à vérifier.
