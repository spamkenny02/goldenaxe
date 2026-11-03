# v0310 : premier cristal et retour depuis Nouveau Jeu

Le [bilan vérifié](d1_campaign_v0310_report.json) confirme un nouveau parcours
sur la v310 avec son générateur raccordé : démarrage normal, première clé,
boss 68 en 175, premier cristal, puis retour en extérieur B9 à **28/32 PV**.
Le parcours conserve l'arme de départ. Aucun import SRAM ou RAM historique,
aucune écriture de vie, argent, clé, équipement ou progression.

| Étape | Image finale | Résultat |
| --- | --- | --- |
| Entrée du donjon | 4237 | 1E4, 14 PV, sans aide |
| Première clé | 4989 | 1E5, 14 PV, une clé, sans aide |
| Boss et cristal | 14551 | 175, 32/32 PV, cristal acquis |
| Retour | 16254 | B9, 28/32 PV, cristal conservé |

L'approche après 4989 utilise le garde de blessures de test autorisé. Sa
**dernière écriture est à 13546** ; le combat commence à 13617, à 10 PV avec
compteur de blessures nul. Un coup normal retire quatre PV à 13709. Aucun
garde ne reprend pendant le combat ou le retour. Le soin du cristal est celui
du jeu. Les 32 prédictions du combat et les 16 du retour correspondent à la RAM.

Chaque étape a une relecture froide indépendante par commandes fixes :
65 536 octets de RAM et PNG final exacts. Le HUD physique de 128 mots et le
premier marqueur de cristal sont contrôlés après acquisition puis à la sortie.
Les deux images finales ont aussi été inspectées.

Deux essais antérieurs sont conservés comme diagnostics. Gem01 remettait le
compteur de blessures à zéro sur les pointes : les PV tombaient de 14 à zéro
sur quatre images consécutives, à cause du pilote. Gem02 conserve le délai
naturel mais meurt pendant le vrai combat, sans garde. Gem03 choisit une conduite
plus prudente et réussit. Le pilote préserve désormais le délai de terrain par
défaut ; `--no-preserve-floor-hurt` permet de reproduire les anciens diagnostics.
Les pilotes effectivement exécutés sont conservés avec leurs traces, même
lorsque leur fichier courant est ensuite amélioré.

La ROM reste v310 `32fe75a6…` : ce jalon modifie le pilote et les preuves,
pas le binaire public. Les autres donjons v310, la phase globale R/IRQ, les
contenus optionnels et le matériel restent à vérifier. La campagne complète
précédemment terminée reste une preuve **v309**, distincte de ce parcours NTSC.

L'examen du groupe de projectiles déjà plein confirme aussi une limite ouverte :
A82D écrit via l'ancien IY si toutes les allocations échouent. Sa valeur dépend
des instructions précédentes, dont le parcours des contacts 2346 ; elle ne peut
pas être remplacée arbitrairement par le dernier projectile du groupe.
Aucune correction native spéculative n'a été ajoutée pour ce cas.
