# v0310 : don d'argent et apprentissage de Terre

Le [rapport vérifié](earth_learning_v0310_report.json) poursuit la même partie
à trois cristaux. Le héros reçoit normalement 50 cornes en F4 : argent2->52.
Il rejoint ensuite le maître en A3 avec la corde déjà acquise, coupe l'obstacle
A3:4A avec la hache et achète Terre pour50 : argent52->2, niveau0->1,
magie et capacité24->48. Le héros conserve46/56PV,huile,corde et trois cristaux.

Les quatre étapes se terminent aux images69600,70043,71785 et72795.
Elles ont chacune leur relecture froide indépendante par commandes fixes :
RAM65536octets et PNG final exacts. Les128mots physiques du HUD correspondent
après chacun des deux services ; l'image finale chez le maître a été inspectée.

La protection d'approche est consignée et retirée avant les boss. Aucun objet,
argent,PV,PM,acteur ou progression n'est injecté. Les deux services rejouent
seulement les anciennes écritures de blessures,sans en ajouter. Aucun import
SRAM ou état principal. Le premier essai de route vers le maître s'arrête avant
émulation : le pilote omettait l'option de corde ;le second utilise réellement
la corde acquise et vérifie la coupe requise. Aucun bug de ROM n'en est déduit.

Ce rapport ne prouve pas encore le quatrième donjon. La ROM restev310 ;
les écarts globaux R/IRQ et la suite du parcours restent ouverts.
