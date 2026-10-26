# v0292 : canoë, téléporteur et quatrième donjon terminé sur Mega Drive

Le binaire reste la v0292 :
`6eeb56086a81c230c75b154f51cafab72167a1eec42c691aed9bf317fd19dd82`,
checksum `2BF8`, 2 Mio. Cette étape améliore les contrôleurs et la validation,
sans changement du programme 68000 ni nouveau numéro de ROM.

## Acquisition et comparaison avec la SMS

Les deux campagnes reprennent leur propre parcours depuis le démarrage.
La salle A1 est nettoyée et fournit la clé supplémentaire : le compteur
passe de un à deux. Les observations de relecture voient deux captures par
les voleurs et deux libérations vivantes sur chaque système. Le contrôleur
alterne les directions comme l'attend le jeu ; aucun état de héros n'est forcé.

Le coffre de A2 accorde réellement le canoë, inventaire 12 à 1, et devient
la cellule de coffre ouvert 4C. Sur MD, des ennemis ont apparu au-delà de
l'eau : le contrôleur récupère d'abord le coffre quand l'attaque est
inaccessible, puis utilise les règles de collision de l'équipement acquis
pour nettoyer le reste de la salle. Cette priorité est une décision du
contrôleur, pas une modification de l'apparition ou des ennemis du jeu.

Une relecture fixe observe le canoë acquis et le drapeau réel d'eau peu
profonde 20 dans la carte : 30 frames de marche sur SMS et 71 sur MD.
Les parcours et leurs durées ne sont pas déclarés identiques. Le classement
de terrain est enregistré tel quel ; le contexte 3 concerne le bateau et
ne sert pas de présomption pour reconnaître l'eau du canoë.

Le héros traverse vers A3, sélectionne Terre dans le vrai inventaire et
détruit le rocher 5C. Le sort coûte 8 unités de magie, révèle la cellule de
téléporteur 0C et permet le transfert vers 192. Les 160 cellules, la carte
logicielle de 1 280 octets et l'inventaire de 17 octets correspondent entre
les deux jeux pour le coffre puis le téléporteur. Les quatre mots VDP du
coffre et les quatre du téléporteur correspondent aussi ; les indices de
couleur des tuiles statiques du coffre sont identiques. Les pixels animés
du téléporteur, les acteurs, PV, cornes, horloges, audio et images complètes
ne sont pas inclus dans cette comparaison entre systèmes.

Ces six segments ont chacun une seconde exécution depuis le démarrage,
avec toute la RAM et le PNG finals identiques. Voir le
[rapport du canoë](canoe_campaign_v0292_report.json).

## Combat et retour natifs

Une seconde clé est obtenue en 182. Le passage vers le boss suit 192, 191,
190 puis 180 : l'entrée réelle est au sud du boss. Le précédent trajet par
181 tentait une frontière sans porte ; c'était une proposition de route erronée.
Le contrôleur évite aussi de remarcher involontairement sur le téléporteur
réciproque de 192 pendant les combats.

La dernière écriture de protection est zéro à la frame 79 684. Le combat
commence à 79 729 avec 56 PV et un délai de protection nul, soit 45 frames
après son retrait. La prise de dégâts observée ensuite, 56 vers 32 PV,
confirme que le héros subit les attaques ordinaires. Le boss est vaincu à la
hache, sans import d'état dans la partie primaire. Les 261 fenêtres de
prédiction du contrôleur reproduisent les 65 536 octets de RAM primaire.

Le budget du premier essai s'arrête dans la boucle normale de remplissage
de vie, à 62/64 PV, après réception du cristal. Une continuation ordinaire
termine cette récompense à 64/64 PV. La sortie traverse les vraies pièces,
le téléporteur inverse et l'eau, sans nouvelle aide. Le héros ressort en 10
à 62/64 PV, avec les quatre drapeaux de cristal à 80, le canoë et la corde.
Les 110 fenêtres de prédiction du retour reproduisent aussi toute la RAM.

Le combat partiel, la récompense terminée et la sortie ont chacun une
relecture indépendante depuis le démarrage, RAM et PNG finals identiques.
Aucune garde n'est ajoutée après la libération précédant le boss. L'aide
d'approche est explicitement conservée dans les enregistrements ; la campagne
entière n'est pas qualifiée de parcours sans aide.

## Mémoire et limites

Le contrôle de pile à chaque instruction couvre le démarrage jusqu'au
cristal, soit 82 483 frames. Minimum observé : F798, au-dessus de la limite
du tas F600, soit 408 octets. Ses en-têtes restent valides ; la RAM entière
et le PNG final correspondent à l'exécution normale. Cela ne borne pas
encore toutes les routes des donjons suivants.

Le [rapport consolidé](d4_campaign_v0292_report.json) rassemble les preuves
et leurs empreintes. Le combat original SMS contre ce boss reste non validé :
l'essai ordinaire meurt, les recherches suivantes atteignent leur budget avec
le boss vivant. Ces diagnostics sont conservés et ne prouvent ni victoire
source ni égalité des timings de combat entre SMS et MD.

Les six donjons suivants, la fin, le matériel, les timings globaux, le RNG
et l'équivalence complète du son et de l'image restent à établir.
