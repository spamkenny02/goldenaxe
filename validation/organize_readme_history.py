"""Separate current instructions from preserved, dated development notes."""
from pathlib import Path

root=Path(__file__).resolve().parents[1]
path=root/'README.md';history=root/'HISTORIQUE_PORTAGE.md'
text=path.read_text(encoding='utf-8')
marker='## État du portage\n'
assert text.count(marker)==1 and not history.exists()
head,tail=text.split(marker,1)
history.write_text('# Historique du portage\n\n'
    'Ces notes décrivent les versions au moment de leurs tests. Les mentions de\n'
    '« version courante » ou de travail restant ci-dessous sont historiques.\n'
    'Consulter le [README](README.md) pour les ROMs et résultats actuels.\n\n'
    +marker+tail,encoding='utf-8')
current="""## État du portage

La logique du jeu est portée en code natif 68000. SGDK fournit notamment
le démarrage et les accès vidéo ; les ressources et les tables proviennent
de la ROM Master System. Le lecteur audio est également natif.
Sources principales : [boucle et transitions](megadrive/src/main.c),
[acteurs](megadrive/src/actors.c), [générateur source](megadrive/src/source_rng.c).

Les résultats de la V318 et des aperçus sont distincts. La V318 reste la
référence ; c0047 contient l’optimisation des motifs du héros et poursuit
sa propre campagne. Un numéro de version ne constitue pas un statut de finale.

## Campagne et travail restant

| Binaire | Parcours vérifié | Limite |
| --- | --- | --- |
| V318 NTSC | Neuf cristaux, palais, Death Adder, générique et retour à l’intro ; 393707 états comparés au parcours V317 | Ce rejeu ne prouve pas une identité globale avec la SMS. |
| V318 PAL | Nouvelle partie jusqu’à la victoire et au générique, avec rejeux indépendants RAM/image | La comparaison audiovisuelle source reste ciblée. |
| c0047 NTSC | Cinq cristaux et retours, canoë, Feu, épée longue, bottes, achat de clé et soin | Sixième donjon en cours ; fin de campagne et sauvegarde à revalider sur cet aperçu. |
| c0047 PAL | Premier cristal et retour extérieur | Les autres donjons restent à vérifier sur cet aperçu. |

Les contrôles V318 couvrent aussi l’intro et le titre, la saisie du nom,
des bruitages de menu, six restaurations de décor après inventaire et les
défilements entre cartes. Une vraie sauvegarde V318 est écrite puis rechargée
en PAL ; la compatibilité d’une sauvegarde V317 à neuf cristaux est contrôlée.
Les rapports et leurs périmètres sont liés plus haut.

La récurrence du hasard SMS est intégrée, mais son fournisseur de registre R
utilise encore SGDK : la phase globale R/IRQ reste à porter.
[Adaptateur actuel](megadrive/src/source_rng_runtime.c).
Des écarts restent dans des révélations partielles et des fondus.
Les comparaisons de registres audio ne certifient ni toutes les formes d’onde
PCM ni tous les bruitages de toutes les scènes. La fidélité globale et les
essais sur console réelle ne sont pas déclarés validés.

## ROMs et compilation

Chaque ROM différente conserve son numéro et son SHA-256 dans
[l’index des versions](versions/index.json). Les deux fichiers racine,
`gaw-megadrive.bin` et `gaw-title-megadrive.bin`, contiennent la V318.
Les aperçus gardent leur binaire et leur patch dans `versions/candidates`.
Toutes les anciennes ROMs numérotées sont conservées.

Depuis ce répertoire, avec la ROM source dans `input/original.sms`,
SGDK, Java et Python disponibles :

```powershell
.\u005cbuild.ps1
python tools/verify_git_roms.py
```

`build.ps1` accepte `-Sgdk` et `-Java` pour leurs emplacements. Il compile
les sources de référence, complète la ROM à 2 Mio, recalcule le checksum
et numérote les nouveaux binaires. Le vérificateur Git compare les ROMs
aux objets du dernier commit ; il s’exécute après l’enregistrement de la livraison.

Le [module de démarrage SGDK](megadrive/src/gaw_sgdk_sys.c) conserve
l’[attribution MIT](megadrive/SGDK-license.txt).
Les preuves volumineuses sont archivées sans perte et relues avant tout
nettoyage des doublons générés. Les ROMs numérotées restent conservées.

## Historique et reprise

- [Notes détaillées des versions précédentes](HISTORIQUE_PORTAGE.md).
- [Reprise du projet et processus courant](REPRISE_CODEX.md).
- [ROMs numérotées](versions/README.md).
"""
path.write_text(head+current,encoding='utf-8')
print('Current README separated from preserved historical notes')
