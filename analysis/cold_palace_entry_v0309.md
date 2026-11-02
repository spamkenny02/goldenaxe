# Entrée froide du palais après les neuf cristaux sur v0309

Cette étape poursuit la même partie depuis Nouveau Jeu, après l'usage réel
du ballon. Elle utilise la ROM v0309 inchangée et ne charge aucune SRAM
synthétique. La protection d'approche autorisée reprend après la sortie D9
vérifiée ; elle devra être retirée avant chaque gardien.

Le héros traverse le monde depuis EB jusqu'à l'accès du palais. En 8B,
le mécanisme des neuf cristaux est réellement observé : les cellules sont
encore 35/35/35 à l'image 305511, puis deviennent 30/31/1F à 305800,
soit 289 images entre ces deux observations. Aucun terrain, objet ou état
de progression n'est écrit par le pilote.

La porte 10 mène à 18D. À l'image 306434, le héros est contrôlable à
102/104 PV, 64 PM, 32 pièces et deux clés, avec le ballon, le navire et la
clé des voleurs. La relecture fixe depuis le démarrage est exacte sur les
65536 octets de RAM et le PNG final. Les 128 mots physiques du HUD et les
neuf marqueurs sont vérifiés ; l'image d'entrée a été inspectée.

Le premier essai de reprise s'arrêtait avant l'émulation, car le pilote
monde exigeait une salle nettoyée au lieu d'une action terminée. Le mode
explicite `--prefix-completed-action` accepte maintenant une action assistée
validée par sa relecture canonique, sans import ni nouvelle écriture, et lit
la position directement dans la RAM capturée. Les contrôles habituels des
préfixes de combat restent en place. Un mode incompatible est refusé avant
l'émulation. La mesure de cette entrée est liée au pilote figé dans ses
sources ; les préconditions ajoutées ensuite resserrent les métadonnées
acceptées sans changer l'exécution du jeu.

Reproduction : `python tools/summarize_cold_palace_entry_v0309.py`.
Voir le [rapport et ses empreintes](cold_palace_entry_v0309_report.json).
Sources figées : `validation/v0309-cold-palace-entry02-sources`.
Commandes exécutées : `validation/run_cold_palace_entry02.py`.

Cette entrée ne prouve pas la fin du palais. Il reste à combattre 15E/7B,
11E/7C et 14C/6D sans protection, et à acquérir réellement la hache de niveau 2
en 11D avant le dernier combat. L'ancien scénario contrôlé avec SRAM
synthétique ne remplace pas cette campagne. La fidélité globale SMS, le
hasard, les sauvegardes, les autres contenus optionnels et le matériel restent ouverts.
