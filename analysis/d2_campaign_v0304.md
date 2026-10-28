# v0304 : hache, deuxième cristal, sortie et corde

La ROM reste `b7b4e150` (2 Mio). Aucun changement de jeu ni nouveau binaire
n'est nécessaire pour ces preuves de campagne.

Après le premier cristal et son retour déjà vérifiés, le héros revient
dans le premier donjon, obtient la clé en 1C5 et la hache en 1B6, puis
l'équipe par le menu et ressort. Trois coupes à la hache permettent
le passage chez la fée de vie C9 : dialogue, capacité de 32 à 40 PV,
soin normal complet et sortie. Le deuxième donjon est atteint à 40/40 PV.
Ces sept étapes disposent chacune d'une relecture froide RAM/PNG exacte.

Les clés de 160, 152 et 131 sont ensuite acquises. Le premier essai contre
le boss 63 en 144 se termine par une défaite, conservée comme diagnostic.
La stratégie prudente suivante remporte le combat : la garde d'approche
est retirée à 33162, le premier combat ordinaire commence à 33219,
à 40 PV et compteur de protection nul. Un coup réel à 33485 fait passer
le héros de 40 à 32 PV. Aucune aide ne reprend pendant le combat.
Le cristal et le soin de récompense se terminent à 48/48 PV, en 34497 images.

Le retour traverse les vrais couloirs et portes. Il n'ajoute aucune écriture
d'aide et se termine en D6, à 31/48 PV, une clé et la hache équipée,
en 37005 images. Combat et retour ont chacun leur relecture indépendante :
65 536 octets de RAM et PNG final exacts. Le contrôle secondaire vérifie
78 fenêtres de combat et 16 de retour ; aucun état secondaire n'est importé
dans le jeu principal. La pile observée à chaque instruction normale depuis
l'image 14 atteint F7F0 pour une limite de tas F600, soit 496 octets de marge
jusqu'à cette sortie. Le tas reste valide.

Une nouvelle approche atteint le troisième donjon en 1F8 à 31/48 PV,
puis la corde est récupérée en 1F4 en 44800 images, toujours à 31/48 PV.
Ces deux étapes ont leurs relectures indépendantes exactes. Le rapport
ci-dessous ne valide pas le troisième boss ou son cristal.

Les aides de test ne touchent que le compteur de protection et restent
consignées. Aucun soin, objet, clé, équipement ou état capturé n'est injecté.
La campagne conserve les aides d'approche ; elle n'est pas présentée comme
un parcours entièrement sans assistance. La suite, la fin, la comparaison
de campagne SMS complète et la fidélité globale vidéo/audio restent à prouver.

[Rapport et empreintes](d2_campaign_v0304_report.json).
