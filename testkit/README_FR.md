# Scripts de test Golden Axe Warrior — SMS et Mega Drive

**Livraison finale V328 :** le lecteur Python accepte son empreinte et applique
automatiquement les décalages du splash (NTSC 277, PAL 231). Le cœur Windows x64,
sa licence et une sauvegarde de test valide sont inclus. Voir les commandes
autonomes dans [BUILD_AND_DEBUG.md](../BUILD_AND_DEBUG.md). Les parcours V328
PAL/NTSC sont vérifiés avec le lecteur portable ; BizHawk reste une adaptation
à valider dans l'émulateur. Les descriptions historiques ci-dessous sont conservées.

Les tests historiques utilisent **Genesis Plus GX/libretro avec Python**.
`bizhawk/gaw_test.lua` est une adaptation fournie pour BizHawk, et non le
script ayant servi à valider les campagnes précédentes.

## Ce qui est fourni

| Fichier | Couverture réelle |
| --- | --- |
| `routes/md_ntsc.csv` | Parcours MD enregistré : 403488 images, neuf cristaux, fin, crédits, retour intro |
| `routes/md_pal.csv` | Même objectif en PAL : 382208 images |
| `routes/sms_full_ntsc.csv` | Campagne SMS NTSC : 436161 images, neuf cristaux, hache d’or, Death Adder, générique et retour intro |
| `routes/sms_intro_ntsc.csv`, `sms_intro_pal.csv` | Intro/titre SMS, 7600 images ; **pas une campagne complète** |
| `replay_libretro.py` | Relecture automatisée avec le moteur utilisé pour les tests |
| `bizhawk/gaw_test.lua` | Suivi du jeu SMS/MD, enregistrement et relecture CSV dans BizHawk |

Les campagnes utilisent la protection autorisée pendant les approches,
retirée avant chaque boss. La route SMS comporte 210005 écritures d'un seul
octet sur le compteur de blessure (offset RAM 0x305). Les routes MD emploient
190764 écritures NTSC et 196493 PAL sur leur compteur natif. Aucun import de
sauvegarde, d'inventaire, de progression ou de recharge de vie. Le trajet peut
se désynchroniser si cette aide est retirée.

**La campagne SMS NTSC est terminée et rejouée sur Genesis Plus GX/libretro.**
Le CSV exporté reproduit les 8192 octets de RAM et l'image finale de référence ;
les 169 étapes de construction ont aussi leurs relectures indépendantes.
La couverture de tous les PNJ et de toutes les quêtes reste ouverte. Cette
route n'est pas validée en PAL ni dans BizHawk. Les anciens CSV SMS d'intro
restent distincts ; les trajets SMS et MD ne sont pas interchangeables.

## BizHawk : lancement

1. Extraire tout le dossier ; conserver `bizhawk`, `routes` et `logs` ensemble.
2. Ouvrir la ROM correcte dans BizHawk et régler sa région PAL ou NTSC.
   Utiliser une manette SMS standard ou Mega Drive à trois boutons.
3. Pour une relecture, repartir d’une ouverture de ROM à froid, image 0,
   sans savestate ni sauvegarde SRAM existante. Mettre en pause à l’image 0.
4. Ouvrir **Tools > Lua Console**, puis charger :

   - `bizhawk/lecture_md_ntsc.lua` ou `lecture_md_pal.lua` pour la campagne MD ;
   - `bizhawk/lecture_sms_ntsc.lua` pour l’adaptation du parcours SMS complet, **non validée dans BizHawk** ;
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

La protection est activée par les lanceurs des campagnes MD et SMS avec `assistance=true`.
Le mode suivi et l’enregistrement ne modifient aucune mémoire.
Le script refuse les ROMs autres que la SMS fournie et les MD V320/V321 et la V322 de développement SHA1421abe4.
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
python replay_libretro.py --rom "D:/chemin/Golden Axe Warrior.sms" --route sms_full_ntsc --core "D:/chemin/genesis_plus_gx_libretro.dll" --out "D:/tests/gaw-sms-complet-01"
python replay_libretro.py --rom "D:/chemin/Golden Axe Warrior.sms" --route sms_extended_ntsc --core "D:/chemin/genesis_plus_gx_libretro.dll" --out "D:/tests/gaw-sms-etendu-01"
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
quelles versions et régions ont effectivement terminé avec ce kit. La route
SMS complète compare aussi la RAM et les pixels finaux avec les références
du dossier `references`. Les deux trajets de campagne visitent certains PNJ,
sans couvrir exhaustivement leurs variantes ou les quêtes secondaires.

## Contrôles visuels à faire pendant le parcours

- Intro, guerrier, cape, logo et menu Nouveau/Continuer.
- Déplacements, attaques, monstres et transitions dans les quatre directions.
- Marchands et PNJ ; ouverture/fermeture de l’inventaire depuis une maison.
- Objets, sorts, passages et neuf donjons ; protection retirée avant chaque boss.
- Death Adder, crédits jusqu’au bout, retour intro puis nouvelle partie.

Atteindre la fin ne prouve ni toutes les quêtes facultatives, ni une fidélité
graphique/sonore à 100 %, ni le fonctionnement sur console réelle.

`sms_extended_ntsc` contient 564131 images : 65 contextes ordinaires connus,
enseignements 2/2/2/1, capacités vie/magie 128/128, bouclier de dragon,
pomme de J9, huile cachée de Kari-Kari et corrosion/remède réels, puis la fin.
Les branches séparées (autres variantes, services, jeux et revisites) restent
hors de ce CSV. Le lanceur `bizhawk/lecture_sms_extended_ntsc.lua` est fourni
avec la même réserve de validation BizHawk que les autres lanceurs.

## V322 de développement, pas une RC validée — 12 novembre 2026

Les deux campagnes ont été rejouées jusqu’au générique sur le SHA V322 du manifeste. Le compteur de protection a été contrôlé sur chaque image : aucune superposition avec un boss vivant. Les limites BizHawk et tous PNJ ci-dessus restent applicables. Rapports locaux : `../validation/rc1-campaign-ntsc01/report.json` et `../validation/rc1-campaign-pal01/report.json`. Les annexes SMS restent à rejouer sur MD avant RC.
