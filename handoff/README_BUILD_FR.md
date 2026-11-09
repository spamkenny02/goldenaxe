# Golden Axe Warrior — V320 prête à compiler

Paquet autonome pour **Windows x64**. Il contient les sources, SGDK, un runtime
OpenJDK et la ROM de référence. Aucun téléchargement, Python ou historique Git
n’est nécessaire à la compilation de ce paquet.

1. Extraire tout le ZIP dans un chemin sans espace, par exemple `C:\gaw-v320`.
2. Dans PowerShell, à la racine extraite :

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\BUILD_V320.ps1
```

Résultat : `dist/gaw-megadrive-v0320.bin`. Le script reconstruit les sources
68000, assemble le correctif du générique et vérifie le SHA-256 final :

`9e5b0abed80678ce864a0bb796c17e97047d1d34e5227a5275bf9336129ceaff`

Taille : 2097152 octets. Checksum Mega Drive : `B0A2`.
Le journal est dans `build/compile.log` ; ce dossier temporaire est recréé à
chaque compilation. La ROM fournie dans `reference/` est uniquement la V320.

## Pour l’autre LLM

Lire `PASSATION_LLM.md` avant de modifier le projet. Les ressources C sont déjà
générées : le build ne dépend pas des anciens répertoires de validation.
Les outils embarqués sont des exécutables Windows. Dans un environnement Linux,
il faut adapter la chaîne de compilation ; ce paquet ne prétend pas fournir
une compilation Linux vérifiée.

SGDK et OpenJDK sont fournis avec leurs notices et licences dans `toolchain/`.
La ROM SMS source fournie par l’utilisateur est dans `input/original.sms`.
