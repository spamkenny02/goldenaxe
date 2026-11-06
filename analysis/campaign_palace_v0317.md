# v317 — palais et fin

Le parcours continue sur le binaire publié
`7694654ec85dd6626c0e17ff1834e5893d4eb35481400a4725eac6b6f3503294`.
Les résultats ci-dessous ne modifient pas la ROM.

## Ballon et entrée du palais vérifiés

Le ballon réellement obtenu au D9 est sélectionné et activé par les boutons
normaux. La vue d'ensemble commence à 300748, devient prête à 301244 puis
revient au jeu à 301335. Le point final 301527 conserve 74/104 PV, les
ressources et les neuf cristaux. La hache est resélectionnée normalement.
Les 768 mots de carte/HUD et les neuf marqueurs de cristal sont contrôlés,
en plus des données de décor, cellules et métadonnées restaurées.

Le trajet rejoint ensuite la porte du palais. Son ouverture réelle est
observée à 304085 : les trois cellules 35 deviennent 30, 31 et 1F. Aucun
terrain ou état de progression n'est importé. Le héros arrive dans la salle
18D du palais au point 304719, avec 74/104 PV, 72 MP, 6 pièces et deux clés.
Le HUD physique et ses neuf cristaux sont contrôlés.

Les deux points reproduisent les 65536 octets de RAM et le PNG final avec
un lecteur indépendant démarré à froid et partagé entre étapes. L'usage du
ballon n'ajoute aucune écriture d'aide. Une nouvelle protection d'approche
est déclarée après la sortie D9 vérifiée ; elle devra être retirée avant
chaque gardien et Death Adder. Aucun PV, MP, or, objet, acteur, état de
progression, SRAM ou état primaire n'est importé.

## Premier gardien vérifié

Le premier essai de contrôleur a atteint sa limite en 16D, avec deux ennemis
dans une zone séparée. Il reste conservé comme échec. Le trajet retenu
actionne le mécanisme pendant le combat, comme le permet le jeu : son
drapeau passe de 16 à 20 à 307403, sans écriture d'état par le test. Le point
307503 conserve les ennemis et ne revendique pas le nettoyage de la salle.

Le mécanisme de 16E est franchi au point 314018, à 90/104 PV. La protection
est retirée à 314019. Un piège de cette salle inflige ensuite 2 PV à 314031.
Le combat commence à 314096 : gardien source 7B à 60 PV, héros à 88 PV et
compteur de blessure normal de 18, sans protection de test. Le héros reçoit
un coup de 20 PV à 320313. La victoire est observée à 320348 ; le point
final 320499 termine à 92/104 PV après les gains ordinaires du jeu.

Les 195 fenêtres de prédiction correspondent à la RAM persistante principale.
Les quatre nouveaux points reproduisent la RAM complète et le PNG final.
Ils conservent les pièges permanents et n'ajoutent aucune écriture d'aide
après le retrait en 16E. Le HUD physique et ses neuf cristaux sont contrôlés.
La protection d'approche reprend à 320500, après la victoire vérifiée.

## Mécanismes intérieurs et Golden Axe

Le premier trajet vers 14E a atteint sa limite en 16D en cherchant à combattre
les ennemis de la zone séparée. Le trajet retenu emprunte la sortie déjà
ouverte et réutilise le point de reprise vérifié après le gardien. Il atteint
14E à 326775, franchit les passages Terre de 14E et de 11A, puis active le
mécanisme de 129. Le point 334385 revient en 12A à 104/104 PV.

Après le mécanisme de 12C, la protection est retirée en 12E à 341533. Le
gardien 7C apparaît à 341635 avec 60 PV, face à un héros à 104 PV et sans
protection. Deux coups de 24 PV ramènent le héros à 56 PV. La victoire est
confirmée au point 355421 et les 426 fenêtres de prédiction correspondent
à la RAM persistante du jeu. La protection d'approche reprend après la
victoire. Le héros reçoit la Golden Axe en 11D et termine sa récompense à
357747 avec 88/104 PV. Les cinq points des mécanismes intérieurs et les six
points du gardien et de la récompense reproduisent la RAM et le PNG final.

Le trajet vers Death Adder est en cours. Le générique, la sauvegarde de
cette partie et les écarts de fidélité à la SMS restent ouverts.

- [Ballon et retour au décor](owned_overview_v0317_report.json)
- [Porte et entrée réelle du palais](cold_palace_entry_v0317_report.json)
- [Mécanismes et premier gardien](cold_palace_giant_v0317_report.json)
- [Passages Terre et mécanismes intérieurs](cold_palace_inner_v0317_report.json)
- [Second gardien et Golden Axe](cold_palace_guardian_v0317_report.json)
