# v0285 : pile et publication des dialogues

ROM de 2 Mio, SHA-256
`9961a313f9387dea5e088a475ae5734a230a7bb22c2992143e3ebe9904eca023`.
Checksum `3524`. Les v0281 à v0284 sont des étapes de compilation conservées,
pas des versions finales validées. Le portage complet reste en cours.

## Défaut mémoire confirmé

La v0280 descend à `$FFEF2C` sur le parcours enregistré. Cette adresse est
dans le buffer DMA alloué, sous la limite de pile `$FFF600`. Les en-têtes du
tas sont également écrasés. Ce résultat provient d'une observation de SP avant
chaque instruction exécutée, dans un émulateur séparé sans écriture dans le jeu.
Il ne prouve pas que tous les glitches historiques avaient cette cause.

Le jeu utilise maintenant le lecteur audio streaming sans les sauvegardes
imbriquées des canaux. Son espace de sortie est fourni par l'appelant.
Les deux buffers de dialogue quittent également la pile. Ils occupent
`scratch[$900..$CFF]`, et la sortie audio IRQ occupe `$D00..$F05`.
Les plus grands flux RLE de carte/titre mesurés occupent 912 octets ; les
métatuiles et cellules de pièce restent sous `$900`. Les effacements complets
du buffer ne conservent pas de données dans la zone audio après une IRQ.
Le masquage des sprites réutilise le tableau des événements de lignes après
son dernier usage, au lieu de garder deux tableaux simultanément sur la pile.

Sur les **18 020 frames** du démarrage normal, premier donjon, hache équipée,
premier cristal, sortie et fée C9, SP ne descend plus sous `$FFF79C` :
**412 octets de marge observée**. Le tas reste valide. La RAM entière et
l'image finales correspondent à l'émulateur officiel exécutant les mêmes
boutons. Cette marge concerne ce parcours NTSC, pas tous les chemins du jeu.

## Publication de la fenêtre

Le contrôle image par image a révélé une frame déchirée en NTSC sur la v0284 :
la carte de la nouvelle fenêtre était encore transférée pendant le balayage.
La v0285 publie ses sept lignes au VBlank avec les motifs du dialogue.
Le même contrôle ne trouve plus de frame incohérente en PAL ni en NTSC.
Il s'agit d'un test de cohérence de la zone de texte, avec position initiale
du héros contrôlée, pas d'une égalité globale de cadence avec la SMS.

## Autres preuves et limites

- Le parcours actuel obtient hache et cristal, puis la fée augmente la capacité
  à 40 et restaure la vie. Aucun décès ni erreur audio observé.
- Une relecture froide sans pilote reproduit les 65 536 octets de RAM et
  l'image finales. Les 256 indicateurs et 1 280 octets de carte à la sortie
  de la fée correspondent au parcours SMS archivé.
- Le lecteur audio conserve état, DE, travail source et commandes PSG sur
  25 644 vecteurs source. Les 28 644 cas incluant les mutations vérifient
  aussi l'API avec espace fourni et ses gardes mémoire. Le streaming rapide
  ne promet pas d'annuler l'état d'un canal rejeté ; l'API transactionnelle
  conserve son annulation complète.
- Les six parcours d'inventaire PAL/NTSC conservent fenêtres noires, HUD,
  fermeture silencieuse et reprise. Les 40 images normalisées et les cadences
  relatives du titre passent aussi.

Le pilote sait désormais déclencher le mécanisme de la salle `$151` avant
de combattre un ennemi inaccessible. Sur les traces **v0280** SMS et MD, il
obtient réellement une nouvelle clé dans `$152` : le contrôle compare le
compteur à celui de l'entrée, au lieu d'accepter une clé déjà possédée.
Les relectures fixes de ces deux traces reproduisent RAM et image finales.
Cela ne constitue pas une validation du deuxième cristal sur la v0285.

Le planificateur dans un second émulateur reste expérimental. Ses essais
échoués et divergences sont conservés ; ils ne prouvent aucune victoire.
La campagne entière, la phase R/IRQ globale, la fidélité audio analogique,
les échéances physiques générales et les essais matériel restent ouverts.

Les rapports, sources et captures sont liés par SHA dans
[le bilan exécutable](stack_release_v0285_report.json) et dans
`stack-release-v0285/manifest.json`. Le nettoyage ne supprime que des fichiers
générés après archivage gzip et relecture intégrale ; toutes les ROMs
numérotées sont conservées.
