# Préparation du sixième donjon sur v0309

Le parcours poursuit le [retour du cinquième donjon](d5_campaign_v0309.md),
depuis le même Nouveau Jeu sans import de SRAM. La ROM reste v0309,
SHA-256 `7270576d6eeb2aee641776a3e364f2f3f320711d70bb91a566d7578161261049`.
Le code du jeu n'a pas changé pendant ces vérifications.

| Étape | Image finale | Salle | PV | Clés | PM |
| --- | --- | --- | --- | --- | --- |
| Hache choisie par le menu | 146847 | Extérieur 49 | 72/72 | 0 | 72 |
| Entrée D6, pont débloqué utilisé | 148350 | 187 | 72/72 | 0 | 72 |
| Première clé | 150784 | 168 | 68/72 | 1 | 72 |
| Deuxième clé | 152914 | 148 | 72/72 | 2 | 64 |
| Troisième clé | 155740 | 146 | 72/72 | 3 | 64 |
| Quatrième acquisition de clé | 161576 | 116 | 72/72 | 2 | 72 |
| Cinquième acquisition de clé | 166970 | 113 | 72/72 | 3 | 40 |
| Cloche de glace acquise | 169528 | 112 | 72/72 | 1 | 40 |
| Dernier rocher dégagé | 171342 | 125 | 72/72 | 0 | 32 |

Les clés sont gagnées par les combats puis dépensées dans les portes normales.
Les six ouvertures Terre utilisent sept lancers avec un décrément réel de huit
PM par lancer. Les objets ramassés normalement peuvent restaurer la magie et
les PV ; aucune ressource n'est injectée pour poursuivre le trajet.

Les mécanismes de contact et les portails sont traversés avec les commandes
ordinaires. Le trajet contourne un combat non nécessaire dans 137, puis utilise
de vraies réentrées de salle lorsque des ennemis sont difficiles à atteindre.
Deux réentrées sont enregistrées sur le segment vers le mécanisme de 117.
Aucun acteur ni élément de carte n'est remplacé par un état de test.

La cloche passe réellement de 0 à 1. Le rocher 7B de 125 est détruit avec Terre
sans franchir la porte vers le boss de 115. Le héros conserve cinq cristaux,
Feu, Terre, épée longue, bottes, canoë et corde. La hache reste sélectionnée,
avec 27 cornes et l'armure de niveau 1 au dernier point de contrôle.

Les dix-sept étapes ont chacune une relecture fixe depuis le démarrage,
identique sur les 65536 octets de RAM et le PNG final. Les 128 mots de la
carte physique du HUD sont vérifiés après l'obtention de la cloche.
Les protections d'approche sont explicitement déclarées, uniquement via
`hero_hurt`. Le sixième épisode attend encore le boss ; ce rapport ne
prétend pas avoir obtenu son cristal.

Voir le [rapport et les empreintes des preuves](d6_progress_v0309_report.json)
et l'[audit reproductible](../tools/summarize_d6_progress_v0309.py).
Les sources exactes et les recettes effectivement exécutées sont figées dans
`validation/v0309-d6-sources`. Les recettes historiques servent de propositions ;
chaque point de contrôle décrit ici a été exécuté sur la ROM courante.
La campagne complète et la fidélité globale SMS restent à vérifier.
