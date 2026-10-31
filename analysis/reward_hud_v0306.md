# v0306 — Restauration du HUD et marqueurs de cristal

ROM : `3a12380b86c193148d1cbd29d68a880901860cfb1c276aa96d61d2da16ac2c01`,
2 097 152 octets, checksum Mega Drive `343B`.

## Défaut reproduit et correction native

La v0305 restaurait les mots du HUD en RAM après les fenêtres d’acquisition,
puis `redraw_current_room` ne transférait que les 20 lignes du terrain au VDP.
Les quatre lignes inférieures gardaient donc une partie de la fenêtre. La
capture naturelle après le canoë présente 128 mots physiques incorrects sur
128, malgré une copie RAM restaurée. L’égalité d’une relecture RAM/PNG ne
suffisait pas à prouver que cette image était correcte face à la SMS.

Un second écart apparaissait lors des cristaux : les marqueurs de propriété
du chandelier n’étaient pas ajoutés. L’original `1EB5..1EDB` utilise neuf
paires de tuile/décalage, table `1EDC..1EED`, à partir des bits de propriété
des neuf cristaux. Chaque fenêtre de cristal du contrôle révèle ce marqueur
manquant dans la copie logicielle du HUD de v0305.

La seule source de production modifiée est `megadrive/src/main.c` :

- Le redessin traduit les quatre lignes du HUD dans le buffer `md_map`
  existant et transfère les 24 lignes, conformément à la chaîne `1DE2`.
- Les marqueurs sont préparés après redessin et lors de la construction du
  HUD initial/repris, avec les 18 octets de la table SMS vérifiés exactement.
- Aucun nouveau buffer permanent n’est ajouté ; les anciennes ROMs sont
  conservées. Les routines de jeu, objets et règles de combat restent celles
  de la version précédente.

## Comparaison avec la SMS

Deux scripts d’objet réels, hache et canoë, et les neuf fenêtres de cristal
sont exécutés dans les boucles SMS et MD, en PAL et NTSC : 22 scénarios et
44 images stabilisées après confirmation. Les positions de pièce, acteurs,
contact et statistiques sont des fixtures explicites pour isoler la fenêtre ;
ces comparaisons ne sont pas présentées comme une campagne naturelle.

La référence v0305 reproduit les mots physiques obsolètes et le marqueur
manquant. Sur v0306, les 5 632 mots du HUD après fermeture et les pixels des
tuiles utilisées concordent avec la SMS, sans exclusion d’une case du HUD.
Les mots et tuiles des 22 fenêtres avant fermeture sont aussi comparés :
3 300 mots de fenêtre inchangés et conformes. Trois premiers diagnostics
de fixture sont conservés, mais seule la référence complète `baseline04`
est utilisée comme preuve de référence.

## Campagne sur la ROM actuelle

Les commandes historiques v0305 sont réexécutées sur v0306 depuis le démarrage,
avec génération des seules protections d’approche et libération détectée sur
les transitions actuelles. Le jeu obtient l’huile, la hache, la fée de vie,
la corde, Terre, le canoë et les quatre premiers cristaux, puis ressort en
10 à 50/64 PV, neuf cornes, sans clé, en 86 364 images.

La relecture indépendante à commandes fixes reproduit les 65 536 octets de
RAM et le PNG final. Les quatre protections d’approche sont retirées avant
chaque combat principal et aucune aide ne reprend au retour du quatrième.
Aucun PV, MP, objet, corne, acteur, progression ou sauvegarde n’est injecté.
La campagne conserve les aides d’approche déclarées et ne constitue pas un
parcours entièrement sans assistance.

Le HUD physique final correspond à sa copie logicielle sur ses 128 mots,
avec les quatre marqueurs de cristal. La capture finale a également été
inspectée visuellement. Le profil de pile avant chaque instruction normale,
après l’initialisation à partir de l’image 14, observe SP minimal 63418,
frontière de tas maximale 62976 et marge 442 octets. Les chaînes du tas sont
valides ; RAM et PNG finaux concordent avec la relecture canonique.
Cette observation reste propre à ce parcours.

## Limites et conservation

La suite de campagne, la fin, les sauvegardes, le hasard SMS et sa phase
globale, la fidélité complète vidéo/audio et le matériel réel restent non
validés. Le contrôle de la construction initiale des marqueurs ne constitue
pas une validation complète du système de sauvegarde.

[Rapport et empreintes](reward_hud_v0306_report.json). Le vérificateur
`tools/summarize_reward_hud_v0306.py` contrôle les sources, les anciennes ROMs,
les VRAM SMS/MD, la relecture et la pile. L’archive sans perte
`analysis/reward-hud-v0306` est vérifiée avant nettoyage ; l’original SMS,
les 306 ROMs numérotées et les deux alias sont protégés. La RAM de fin de
parcours reste disponible pour la suite.
