# Scripts de test Golden Axe Warrior — SMS et Mega Drive

Les tests historiques utilisent **Genesis Plus GX/libretro avec Python**.
`bizhawk/gaw_test.lua` est une adaptation fournie pour BizHawk, et non le
script ayant servi à valider les campagnes précédentes.

## Ce qui est fourni

| Fichier | Couverture réelle |
| --- | --- |
| `routes/md_ntsc.csv` | Parcours MD enregistré : 403488 images, neuf cristaux, fin, crédits, retour intro |
| `routes/md_pal.csv` | Même objectif en PAL : 382208 images |
| `routes/sms_intro_ntsc.csv`, `sms_intro_pal.csv` | Intro/titre SMS, 7600 images ; **pas une campagne complète** |
| `replay_libretro.py` | Relecture automatisée avec le moteur utilisé pour les tests |
| `bizhawk/gaw_test.lua` | Suivi du jeu SMS/MD, enregistrement et relecture CSV dans BizHawk |

Les parcours MD utilisent une protection de test pendant les approches,
retirée avant les combats de boss : 190764 écritures NTSC et 196493 PAL sur
le compteur de blessure uniquement. Aucun import de sauvegarde, inventaire,
progression ou recharge de vie. Désactiver cette aide peut invalider le parcours.

**Il n’existe pas dans ce kit de parcours SMS complet validé de A à Z.**
Le mode suivi/enregistrement sert à réaliser ce parcours sur SMS, puis à
le rejouer. Les trajets SMS et MD ne sont pas interchangeables.

## BizHawk : lancement

1. Extraire tout le dossier ; conserver `bizhawk`, `routes` et `logs` ensemble.
2. Ouvrir la ROM correcte dans BizHawk et régler sa région PAL ou NTSC.
   Utiliser une manette SMS standard ou Mega Drive à trois boutons.
3. Pour une relecture, repartir d’une ouverture de ROM à froid, image 0,
   sans savestate ni sauvegarde SRAM existante. Mettre en pause à l’image 0.
4. Ouvrir **Tools > Lua Console**, puis charger :

   - `bizhawk/lecture_md_ntsc.lua` ou `lecture_md_pal.lua` pour la campagne MD ;
   - `bizhawk/intro_sms_ntsc.lua` ou `intro_sms_pal.lua` pour l’introduction SMS ;
   - `bizhawk/gaw_test.lua` pour jouer librement avec suivi ;
   - `bizhawk/enregistrer_sms_md.lua` pour enregistrer ses propres entrées.

Les fichiers `logs/*-route.csv` enregistrés peuvent être copiés dans `routes`.
Créer un lanceur identique aux exemples avec le nom de ce CSV, sans extension,
commençant par `sms_` ou `md_`. Pour une relecture depuis l’allumage,
l’enregistrement doit lui-même avoir commencé à l’image 0.

Le script affiche salle, vie, cristaux et compteur d’images. Les journaux
CSV enregistrent ces états ; **ils ne valident pas automatiquement les images
ou le son**. Les relectures MD vérifient aussi la fin attendue. Un échec ou une
désynchronisation n’est jamais présenté comme une campagne réussie.

La protection est activée par les lanceurs MD avec `assistance=true`.
Le mode suivi et l’enregistrement ne modifient aucune mémoire.
Le script refuse les ROMs autres que la SMS fournie et les MD V320/V321.
Le domaine RAM est détecté ; en cas d’ambiguïté, ajouter `domain="68K RAM"`
ou le nom exact de la RAM SMS dans `GAW_CONFIG` du lanceur.

**Limite BizHawk :** syntaxe Lua et logique testées avec une API simulée.
Aucune campagne complète n’a été exécutée dans BizHawk pour certifier cette
adaptation. Le coeur, la région, la SRAM et l’alignement des images peuvent
désynchroniser des entrées issues de libretro. Arrêter si le héros se bloque
ou meurt ; conserver le journal pour trouver le premier écart.

API vérifiée dans la [documentation officielle BizHawk](https://tasvideos.org/BizHawk/LuaFunctions).
Le code source officiel des coeurs est dans [TASEmulators/BizHawk](https://github.com/TASEmulators/BizHawk).

## Lecteur réellement utilisé : Python/libretro

Windows 64 bits, Python et Pillow :

```powershell
python -m pip install -r requirements.txt
python replay_libretro.py --rom "D:/chemin/gaw-megadrive-v0321.bin" --route md_ntsc --core "D:/chemin/genesis_plus_gx_libretro.dll" --out "D:/tests/gaw-ntsc-01"
python replay_libretro.py --rom "D:/chemin/gaw-megadrive-v0321.bin" --route md_pal --core "D:/chemin/genesis_plus_gx_libretro.dll" --out "D:/tests/gaw-pal-01"
python replay_libretro.py --rom "D:/chemin/Golden Axe Warrior.sms" --route sms_intro_ntsc --core "D:/chemin/genesis_plus_gx_libretro.dll" --out "D:/tests/gaw-sms-intro-01"
```

Dans le projet local, le coeur utilisé se trouve dans
`../../work/libretro/genesis_plus_gx_libretro.dll` depuis la racine du dépôt.
SHA-256 : `d17f2392115b3cd54258a1fa6c4195ddadc19b0805ebcca400db5162b1793516`.
Les ROMs et le coeur ne sont pas inclus dans l’archive. Une autre version du
coeur peut désynchroniser le parcours. Le coeur provient de
[Genesis Plus GX](https://github.com/ekeeke/Genesis-Plus-GX).

Le dossier de sortie doit être nouveau. Le lecteur produit `result.json`,
l’image finale et des données de diagnostic. `--frames 5000` lance seulement
un préfixe, sans déclarer une campagne complète réussie.
`--without-assistance` retire les écritures de protection mais ne constitue
pas une preuve que le trajet reste jouable sans aide.

Les hashes de ROM et de CSV sont vérifiés. `manifest.json` contient la
provenance des contrôles et de l’aide de test. `verification.json` indique
quelles versions et régions ont effectivement terminé avec ce kit.

## Contrôles visuels à faire pendant le parcours

- Intro, guerrier, cape, logo et menu Nouveau/Continuer.
- Déplacements, attaques, monstres et transitions dans les quatre directions.
- Marchands et PNJ ; ouverture/fermeture de l’inventaire depuis une maison.
- Objets, sorts, passages et neuf donjons ; protection retirée avant chaque boss.
- Death Adder, crédits jusqu’au bout, retour intro puis nouvelle partie.

Atteindre la fin ne prouve ni toutes les quêtes facultatives, ni une fidélité
graphique/sonore à 100 %, ni le fonctionnement sur console réelle.
