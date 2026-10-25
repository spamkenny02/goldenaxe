# Deuxième donjon et assistance de test, v0285

La ROM reste la v0285, SHA-256
`9961a313f9387dea5e088a475ae5734a230a7bb22c2992143e3ebe9904eca023`.
Ces changements concernent les outils d’essai et la documentation.

Le parcours depuis un démarrage à froid termine la salle 151, puis la salle
152 et récupère une nouvelle clé : compteur de 1 à 2, 32/40 points de vie,
aucun décès. Les commandes fixes reproduisent les 65 536 octets de RAM et
l’image finale sur le cœur officiel, sans injection. Les 256 indicateurs
persistants et les 1 280 octets de carte correspondent au parcours SMS
archivé. L’observation de chaque instruction jusqu’à la frame 25 280 retrouve
le minimum SP `$FFF79C` et reproduit aussi la RAM et l’image finales.

À la demande de l’utilisateur, un outil distinct permet maintenant de rendre
le héros invincible sur le trajet d’approche, puis de retirer cette aide avant
le boss. Il agit sur la RAM de l’émulateur de test ; il ne modifie pas la ROM.
Il conserve les points de vie existants et ne recharge pas la santé.

L’essai `md-auto-v0285-d2-assisted-boss03` atteint la salle du boss du deuxième
donjon à la frame 31 649 avec 32 points de vie. La dernière écriture de test,
à la frame 31 650, remet le compteur d’invulnérabilité à zéro. Le jeu reprend
le combat à la frame 31 707 avec ce compteur à zéro. Aucun accès en écriture
de test ne suit. À la frame 31 884, le boss inflige des dégâts : 32 → 16 points
de vie, avec le compteur de blessure normal à 47.

La relecture officielle à commandes et écritures d’approche fixes reproduit
toute la RAM et l’image à la frame 31 885, sans lecture de retour pour piloter
le jeu. Ce résultat valide la coupure de l’aide et le retour des dégâts. Le
pilote meurt ensuite et le boss conserve ses 30 points de vie : le deuxième
cristal et le combat victorieux restent à valider. Ce parcours assisté ne
constitue pas une preuve de campagne naturelle.

Le premier essai d’aide permanente empêchait aussi le ramassage d’une clé :
le passage de contact sert aux objets comme aux dégâts. L’outil relâche donc
le compteur lorsqu’il n’y a plus d’acteur dangereux. Le routage ignore les
contacts pendant l’approche assistée, puis retrouve ses règles normales au
boss. Les deux essais préalables restent conservés comme diagnostics.

Les prévisions de commandes utilisent un cœur secondaire. Son instantané
restaure aussi la phase `m68k.refresh_cycles`, absente du format de sauvegarde
standard du cœur utilisé. Les getters/setters supplémentaires restent dans
un cœur de recherche distinct. Les résultats retenus passent ensuite une
relecture indépendante avec le cœur officiel. Cela ne change pas les horloges
ni le générateur aléatoire de la ROM jouable.

Preuves : [rapport vérifiable](d2_progress_v0285_report.json),
[outil d’assistance](../tools/assisted_boss_route.py),
[relecture assistée](../tools/replay_assisted_boss.py).
Les captures lourdes sont archivées localement sans perte avec vérification
SHA-256 avant nettoyage ; le manifeste est versionné. Le jeu complet,
la campagne PAL, les horloges source et le matériel restent à valider.
