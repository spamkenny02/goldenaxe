# v0304 : troisième cristal et retour extérieur

La ROM reste `b7b4e150` (2 Mio), sans modification du programme 68000.
Après les deux cristaux déjà prouvés, le troisième donjon et sa corde
sont rejoués depuis le démarrage. Le trajet vers le boss ramasse normalement
un objet de vie : le héros entre dans le combat à 39 PV, sans soin injecté.

La dernière écriture de protection est zéro à 48776. Le premier combat
ordinaire commence à 48810, à 39 PV et compteur de protection nul, soit
34 images après le retrait. Le premier segment s'arrête volontairement
après 1800 images de combat, à 39 PV et 18 PV de boss. C'est une étape
partielle, pas une victoire. Sa relecture indépendante est exacte.

La continuation rejoue ce préfixe entier depuis le démarrage, puis poursuit
le même combat avec des commandes d'esquive ordinaires. Aucun état capturé
ni remise à zéro de vie n'est importé. À 51735, le héros subit un vrai coup
de 39 à 31 PV. Le boss 69 est vaincu ; le troisième cristal et le soin normal
de récompense se terminent à 56/56 PV en 52469 images. Les 149 fenêtres de
prédiction de cette continuation correspondent aux 65536 octets de RAM.

Le retour traverse les couloirs et le téléporteur inverse, sans nouvelle
protection. Le héros ressort en 62 à 46/56 PV en 53755 images, hache équipée
et corde conservée. Les 31 fenêtres de prédiction du retour sont exactes.
Combat et sortie ont chacun leur relecture froide indépendante : toute la
RAM de 65536 octets et le PNG final correspondent. Les écritures d'aide
s'arrêtent à 48776 dans les trois enregistrements.

La pile est observée à chaque instruction normale depuis l'image14 jusqu'à
cette sortie : minimum F7F0, limite du tas F600, marge observée496 octets ;
le tas reste valide. Ce contrôle ne couvre pas les futurs parcours.

La campagne conserve les aides historiques d'approche. Les boss et leurs
retours n'en reçoivent aucune ; aucun soin, équipement, clé ou progression
n'est injecté. Les trois cristaux et retours sont maintenant prouvés sur
la v304. Le quatrième donjon et la suite, la fin, les sauvegardes, la
comparaison de campagne SMS et la fidélité globale vidéo/audio restent
à valider.

[Rapport et empreintes](d3_campaign_v0304_report.json).


Erratum2026-10-30 : la marge de496 octets citee ci-dessus concerne les points instrumentes. Le minimum avant chaque instruction est478 octets sur les parcours D1-D6. Voir la [correction de mesure](stack_minimum_v0304_erratum.md).
