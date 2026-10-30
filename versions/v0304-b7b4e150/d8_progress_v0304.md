# v304 : clé des voleurs et approche du huitième boss

La ROM reste inchangée : SHA-256 `b7b4e15008a6f0a913c9ad43f15386abcdfbb719e5a575873d92712ba52503a8`. Ce parcours continue les [mécanismes de D8](d8_passages_v0304.md).

Le héros traverse réellement le sol transformé de 1C8 et rejoint 1E8 par 1D8. Terre est sélectionnée par le menu normal : un lancer UP depuis (136,112) transforme la cellule58 de0B en0C et consomme huit points de magie, de48 à40. Le téléporteur ainsi accessible mène à 1AA.

La salle 1A9 donne ensuite la clé des voleurs, objet15, selon le mécanisme d’origine de la coordonnée856. L’objet apparaît en RAM à la frame215559 ; sa présentation se termine en215859 et la capture finale en215959 conserve la hache équipée. Tous les ennemis de cette salle ont alors disparu. Les soins ramassés pendant le trajet portent la vie de40 à64/88 PV, sans ajout de vie par le test.

Le mécanisme de 19A, UP en (72,40), ouvre la sortie ouest de 1D8 et l’entrée est de 1D7. Le héros retourne physiquement en 1AA, utilise le téléporteur vers 1E8, passe par 1D8 et 1D7, puis utilise son portail vers 1A6. Les ennemis de cette dernière salle sont vaincus après leurs apparitions normales. Une clé supplémentaire y est ramassée en221554.

| Étape | Frame finale | Salle | PV | Clés | Magie | Clé des voleurs |
| --- | ---: | --- | ---: | ---: | ---: | --- |
| Terre et téléporteur1E8 | 209630 | 1AA | 40/88 | 2 | 40 | non |
| Objet et présentation terminée | 215959 | 1A9 | 64/88 | 2 | 40 | oui |
| Mécanisme19A et retour | 218065 | 1AA | 64/88 | 2 | 40 | oui |
| Salle avant le boss nettoyée | 222496 | 1A6 | 64/88 | 3 | 40 | oui |

Les quatre étapes ont chacune une relecture indépendante à commandes fixes depuis le démarrage : les65536 octets de RAM et le PNG final sont identiques. Aucun état secondaire n’est importé et aucune écriture de test ne porte sur les objets, la vie, l’argent ou la progression. La protection d’approche est déclarée sur hero_hurt. Le combat intermédiaire7A reste assisté ; le boss principal196/type6B n’est pas encore entré dans ce checkpoint.

Les tables SMS identifient ce boss par `50100240` :80 PV, attaque16, armure2, drapeau boss40. Le [rapport reproductible](d8_progress_v0304_report.json) lie les sources, les captures et les relectures. Il ne prouve pas encore son combat, le huitième cristal, son retour ou l’utilisation de la clé des voleurs sur une porte ultérieure. La mesure de pile reste celle du retour D7 ; ce point ne l’étend pas.

Les routines d’acteurs utilisent encore le générateur SGDK. La fidélité du hasard SMS et de sa phase, les donjons suivants, la fin, les sauvegardes et la fidélité vidéo/audio complète restent à terminer ou vérifier.
