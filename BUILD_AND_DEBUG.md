# V328 — compilation et débogage après clôture

Le projet est clôturé à la demande de l'utilisateur le 13 novembre 2026.
La livraison conservée est la V328, 2 097 152 octets, SHA-256 :
`368c003f92e0860336c919005ec19f0ae620d6876b4bca8f436f83e682b59dcc`.
Le démarrage, les noms de sauvegarde et les bordures ont été acceptés sur
Mega Drive 1 / flashkit 2 Mo + SRAM 32 Ko. Les limites de fidélité historiques
restent documentées ; la clôture ne les transforme pas en certification à 100 %.

## Recompiler depuis les sources

Environnement vérifié : Windows x64, PowerShell, Python 3.15, Java JDK 25.0.1
et SGDK au commit `ee6870a6010b1e341ca36078f581a68a26c9a543`
(GCC 68000 13.2.0). La compilation finale n'utilise aucun paquet Python tiers.
La ROM SMS et les ressources converties sont déjà versionnées.
Le dépôt SGDK contient ses outils Windows ; installer Java séparément.

```powershell
git clone https://github.com/spamkenny02/goldenaxe.git
git clone https://github.com/Stephane-D/SGDK.git C:/dev/sgdk
git -C C:/dev/sgdk checkout ee6870a6010b1e341ca36078f581a68a26c9a543
cd goldenaxe
powershell -NoProfile -ExecutionPolicy Bypass -File BUILD_FINAL.ps1 -Sgdk C:/dev/sgdk -Java C:/chemin/jdk-25.0.1/bin/java.exe
```

Adapter le chemin Java. `-Python C:/chemin/python.exe` est également accepté.
La sortie est `dist/gaw-megadrive-v0328.bin`, avec un rapport et les symboles.
Le script refuse toute différence avec l'empreinte V328 et ne remplace pas
les ROMs publiées ni leur numérotation.

La chaîne compile le moteur V319, puis les corrections générique/titre/dialogue,
Konami, et enfin le splash et la validation des noms SRAM. Les adresses des
corrections sont fixes : `megadrive/rebuild-base/save.inc` préserve le module
de base à compiler ; la logique actualisée de `megadrive/src/save.inc` est
appliquée à cette base via `megadrive/overlays/save_name_guard.*`.
Les assembleurs et scripts vérifient les octets et empreintes intermédiaires.
Une compilation générale par l'ancien `build.ps1` ne produit pas la V328 :
utiliser **BUILD_FINAL.ps1** pour reconstruire la livraison acceptée.

Les sources du moteur sont dans `megadrive/src`, les correctifs dans
`megadrive/overlays`, et les ressources de présentation dans
`megadrive/presentation`. Les graphismes/sons convertis sont conservés pour
ne pas imposer une reconversion dépendant d'outils multimédias.

## Rejouer les runs PAL/NTSC ou SMS

Installer Pillow avec le même Python x64 que celui utilisé pour les scripts :

```powershell
python -m pip install -r testkit/requirements.txt
python testkit/replay_libretro.py --rom gaw-megadrive.bin --route md_ntsc --out validation/mon-run-ntsc
python testkit/replay_libretro.py --rom gaw-megadrive.bin --route md_pal --out validation/mon-run-pal
python testkit/replay_libretro.py --rom input/original.sms --route sms_full_ntsc --out validation/mon-run-sms
```

Chaque sortie doit être un nouveau dossier. Ajouter `--frames 8000` pour
un parcours court : ce nombre concerne la route, hors splash. Les décalages
de démarrage de la V328 sont appliqués automatiquement : NTSC 277, PAL 231.
Le lecteur vérifie l'empreinte de la ROM et des CSV, produit une image finale,
la RAM, les entrées rejouées et `result.json`. Les runs complets MD atteignent
la fin avec neuf cristaux. Les protections d'approche enregistrées sont
annoncées et auditées ; elles sont retirées avant les boss. Le paramètre
`--without-assistance` les supprime, mais la route fixe peut alors échouer.

Le cœur Windows x64 est fourni dans `testkit/runtime`, avec sa licence,
son empreinte et sa provenance. `--core chemin.dll` permet d'en choisir un
autre, dont le comportement devra être revalidé. Les routes SMS étendues,
scripts BizHawk de surveillance/enregistrement/rejeu et leurs limites sont
décrits dans [testkit/README_FR.md](testkit/README_FR.md). L'adaptation BizHawk
accepte la V328 et ses décalages ; elle n'est pas certifiée par un parcours
complet dans BizHawk.

## Débogage ciblé

`megadrive/debug/symbol.txt` contient les symboles natifs utilisés par la V328.
Les adresses RAM et symboles du moteur restent ceux de la base ; les ELF des
correctifs sont régénérés dans `validation/final-build-*/konami` et `final`.
`dist/base-rom.out` est l'ELF de la base, pas une image liée contenant les
correctifs : associer ses symboles à la ROM finale avec cette distinction.

Pour les contrôles visuels de démarrage, installer aussi NumPy :

```powershell
python -m pip install numpy
python tools/validate_presentation_boot.py --rom gaw-megadrive.bin --out validation/controle-boot
python tools/validate_clean_presentation_planes.py --rom gaw-megadrive.bin --out validation/controle-bordures --offset-ntsc 277 --offset-pal 231
python tools/validate_konami_continue.py --rom gaw-megadrive.bin --label mon-continue --offset-ntsc 277 --offset-pal 231
```

La sauvegarde de test valide et son état attendu sont conservés dans
`testkit/fixtures/continue`. Les captures/SRAM produites par les tests sont
des fichiers de travail ; elles ne remplacent pas une sauvegarde utilisateur.

Les anciennes vidéos, captures volumineuses et caches locaux ne sont pas
nécessaires à ces commandes et sont supprimés lors de la clôture. Certaines
expériences historiques référencent ces anciennes captures : utiliser les
commandes de ce document pour les contrôles autonomes de la V328.
