# v0310 : Terre, canoë, quatrième cristal et retour

Le [bilan vérifié](d4_campaign_v0310_report.json) prolonge la même partie
depuis D3 : don normal de 50 cornes, achat de Terre, puis quatrième donjon.
Le héros récupère le canoë, obtient le quatrième cristal et ressort en salle
10 à **62/64 PV**. La ROM reste v310, sans changement de binaire.

Les deux passages avec Terre consomment chacun huit PM. Le canoë est obtenu
par la récompense du jeu ; la relecture observe 33 images de déplacement
effectif sur l'eau avec cet objet acquis.

La protection d'approche est retirée à l'image 93294. Le combat contre le
boss **type6A, 30 PV**, commence à 93358 avec 56 PV et compteur de blessures
nul. Aucun dégât n'est reçu pendant ce combat ; le cristal porte ensuite
la vie à 64/64. Aucun nouvel apport de protection pendant le combat ou le
retour. La sortie termine à l'image 103398 avec 62 PV.

Les quinze étapes ont une relecture depuis le démarrage par commandes fixes :
65 536 octets de RAM et image finale identiques. Les 211 fenêtres de prédiction
du combat et les quinze du retour correspondent à toute la RAM. Le HUD physique
de 128 mots et les marqueurs de cristal sont contrôlés après le canoë, le boss
et la sortie ; ces trois images ont été inspectées.

Le premier essai de retour `exit01` s'arrête parce que le pilote cherche le
mécanisme facultatif B0. `exit02` écarte cet objectif de son itinéraire, comme
sur le parcours historique, et atteint la sortie. Ce mécanisme reste hors
couverture de ce parcours ; aucun correctif natif n'est déduit de cet arrêt.

Les seules écritures de test sont les compteurs de blessures autorisés sur
les approches. Aucun objet, ressource, acteur ou progression n'est injecté ;
aucun état principal ou SRAM n'est importé. Quatre cristaux sont validés sur
v310 ; la suite de cette campagne, la phase globale R/IRQ et la fidélité
temporelle et audiovisuelle complète restent ouvertes.
