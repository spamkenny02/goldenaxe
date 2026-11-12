# Golden Axe Warrior — préparation V322 RC1, NON VALIDÉE

**Publication suspendue : les branches SMS doivent encore être rejouées et filmées sur MD. Le point 6 reste ouvert.** Les contrôles ci-dessous portent sur le binaire de développement V322 SHA1421abe4 ; ils ne suffisent pas à qualifier la RC demandée. Ce document est préparatoire.

## Changement par rapport à la V321

Correction du retour à la ligne vide du dialogue de Saylun, maison C7/1F : une première phrase pouvait disparaître. La routine native vérifie désormais les segments vides dans ce contexte précis. Le bitmap final de 1040 octets correspond exactement à celui observé sur SMS, en PAL et NTSC ; acquittement, sortie et déplacement sont vérifiés puis rejoués à froid indépendamment.

La correction occupe 76 octets à `0x1F0200`, avec deux branchements dans le code natif et la mise à jour du checksum. Tous les autres octets de la V321 sont conservés, dont les corrections du titre et du générique. Les autres maisons et le récit d’ouverture gardent leur comportement antérieur. Aucun changement de progression, d’inventaire ou de combat n’est intégré à la ROM.

## Contrôles de publication

| Contrôle exécuté sur cette ROM | Résultat |
| --- | --- |
| Reconstruction propre depuis les sources | Identité SHA-256 |
| Reconstruction indépendante avec SGDK/Java du paquet autonome | Même ROM, sans historique Git ni binaire de base |
| Campagne MD NTSC, 403488 images | Neuf cristaux, fin et générique, zéro mort |
| Campagne MD PAL, 382208 images | Neuf cristaux, fin et générique, zéro mort |
| Audit de la protection d’approche, chaque image | Aucun chevauchement avec un boss vivant dans les deux régions |
| Lecteur sonore pendant les campagnes | Aucune commande non prise en charge signalée |
| Continuer depuis de vraies sauvegardes antérieures, PAL/NTSC | Inventaire, cristaux, jauges, HUD et déplacement restaurés |
| Dialogue corrigé, PAL/NTSC | Bitmap SMS exact, acquittement et mouvement ; RAM complète/image finale exactes au rejeu |
| Vidéo MD de cette RC | Introduction puis campagne continue, décodage vidéo et audio intégral |
| Montage SMS retenu et annexes | Décodage intégral, synchronisation, 350 images aux raccords exactes |

Les rapports JSON joints contiennent les SHA, durées, états et bornes de chaque contrôle. Les tests des sauvegardes vérifient ici la lecture normale du slot 0 de sauvegardes réellement écrites sur des versions précédentes ; ils ne sont pas un nouvel audit exhaustif des écritures des trois slots de la RC.

## Point 6 : preuves et parcours retenus

La vidéo SMS dure **4 h 26 min 57 s** : campagne étendue continue jusqu’à la fin, puis branches distinctes annoncées par cartons et chapitres. Les 70 vidéos annexes couvrent les 145 preuves sélectionnées des points 3 et 4 ; les 17 redémarrages Continuer utilisent des sauvegardes effectivement écrites par le jeu. Les acquisitions, retours, refus et conditions annexes restent identifiables ; ils ne sont pas présentés comme une seule partie continue.

La vidéo MD de la **V322 RC1** dure environ **1 h 54 min 06 s** : une capture de l’introduction et une capture de campagne depuis Nouvelle partie jusqu’au générique, assemblées sans accélérer le jeu. Elle ne reprend pas toutes les branches PNJ SMS. Les vidéos restent locales ; elles ne sont pas envoyées sur YouTube.

Les deux campagnes MD et le parcours SMS utilisent la protection d’approche autorisée, retirée avant les boss. Les deux essais monétaires SMS séparés sont signalés à l’écran. Les entrées sont enregistrées/rejouées automatiquement ; il ne s’agit pas d’une performance manette en main. Aucun TAS public n’est utilisé.

## Limites conservées pour les essais RC

- Les trois chaînes SMS `0xDA58`, `0xDA7C`, `0xED3C` n’ont toujours pas de déclencheur légitime démontré. L’enquête code/guide/jeu reste disponible ; elles ne sont pas déclarées inutilisées et aucun déclenchement artificiel n’est ajouté au portage.
- La couverture globale de tous les PNJ, variantes de quêtes et comparaisons physiques SMS/MD n’est pas terminée. Les preuves SMS ne sont pas assimilées à des preuves MD.
- De petits écarts connus du raster du titre, des révélations et des fondus restent documentés. La fidélité graphique et les animations ne sont pas certifiées à 100 %.
- Les contrôles de logique sonore/PSG ne prouvent pas une identité de toutes les formes d’onde PCM. Aucune nouvelle distorsion n’est déduite de cette seule différence ; le correctif de dialogue ne modifie aucun octet audio.
- Les campagnes MD sont vérifiées en PAL et NTSC sur Genesis Plus GX/libretro. Le parcours SMS étendu est NTSC ; ni le matériel réel ni une campagne BizHawk complète ne sont certifiés.

Aucun blocage de progression, plantage ou défaut sonore de commande n’a été observé dans les contrôles de publication exécutés. Les limites ci-dessus sont conservées explicitement pour les essais externes, sans promesse d’absence de tout bug.

## Compilation et fichiers

ROM de **2 Mio**, SHA-256 : `1421abe47de95ac104a03e2fb1be7001f70aeca1fbb6a9b35669aa6e98b7d9a4`.

Dans le dépôt : `powershell -ExecutionPolicy Bypass -File BUILD_RC.ps1 -Sgdk chemin/sgdk -Java chemin/java.exe`.

Le ZIP autonome `handoff/gaw-v0322-rc1-ready-to-build-windows.zip` contient SGDK et Java avec leurs licences. Python 3.10+ et PowerShell sont nécessaires ; aucune dépendance Python externe n’est utilisée pour compiler. Lire son fichier `LIRE_AVANT_COMPILATION.md` et lancer `BUILD_RC.ps1`. Le paquet ne contient pas les gros caches, les anciennes ROMs ou les MP4.

Le rapport de décision RELEASE.json ne sera généré qu’après validation des branches MD. Vidéos locales : [MD RC1](../../videos/v0322-rc1/README.md), [SMS et annexes](../../videos/sms/parcours-et-annexes-2026-11-12/README.md).
