# Campagne v0287 : deuxième donjon et référence de corde

La ROM reste `58068350382a19ddc73a62eb747e42d978c36a1daf3c87f819e921f391b0065d`
(v0287, 2 Mio, checksum DD1D). Aucun code jouable ni règle de combat n'a changé.

## Résultats natifs

La visite normale de la fée porte la capacité à 40 PV. L'approche du deuxième
donjon utilise ensuite uniquement la protection de blessure autorisée, sans
recharger les PV. Dernière écriture à la frame 28098 ; premier combat à 28155,
compteur de blessure nul. Le boss est vaincu sans perte de PV. Son cristal
porte la capacité à 48, et la sortie D6 est atteinte à 48/48 PV, frame 35662.
Le premier cristal et la hache équipée sont conservés.

Deux contrôleurs trop agressifs meurent alors que le boss n'a plus que 2 PV.
Un autre essai garde les chemins d'esquive complets à côté de la recherche
locale et privilégie la gauche : le boss finit par tomber sans dégât reçu.
Le premier segment s'arrête à sa limite de diagnostic, vivant avec 40 PV et
8 PV au boss. Le segment suivant le rejoue depuis le démarrage avant de
prolonger le combat. Aucun état n'est chargé dans le jeu principal.

Les quatre étapes clé/segment vivant/victoire/sortie ont chacune une relecture
froide indépendante sur le cœur officiel : les 64 Kio de RAM et le PNG finals
correspondent. Les 375 + 70 fenêtres de prédiction de huit frames correspondent
également à toute la RAM ; elles ne remplacent pas ces relectures officielles.

À la sortie, les 256 indicateurs, 1 280 octets de carte et 17 octets d'objets
correspondent à la référence SMS déjà validée. Cela ne compare pas tout le
fichier de sauvegarde, les compteurs de clés/or, les rencontres ou le RNG.
L'observation de pile à chaque instruction sur le parcours entier donne SP
minimal F79C, limite du tas F600 : 412 octets de marge observée et chaîne
valide. RAM et PNG correspondent aussi dans cette exécution observée.

## Référence SMS de la corde acquise

Le troisième donjon source est terminé, cristal puis sortie en 62. Le retour
emprunte 1C3→1D3→1E3→1E2, le portail réel vers 1E7, puis 1F7→1F8. Un premier
itinéraire qui supposait une liaison directe 1D3→1D2 est conservé comme échec.

Depuis cette sortie, le héros rejoint la falaise en 41, position (104,88),
avec la corde réellement acquise. Aucun objet, position, cellule, carte,
SRAM ou état n'est transplanté. Aucune nouvelle aide n'est écrite sur cette
extension ; le parcours complet garde néanmoins l'étiquette « assisté » à
cause des approches antérieures.

Dix rangées de deux tuiles se dessinent des frames 69833 à 69842, puis le héros
avance de y88 à y72. Les cellules de la colonne, les quatre octets de travail
et chaque rangée de carte sont contrôlés. Une relecture officielle reproduit
les 8 Kio de RAM et le PNG finals. Le nouvel outil, avec son code figé et son
SHA, retrouve les mêmes commandes, RAM et image que ce parcours vérifié.

Les premières tentatives du nouvel outil sont archivées : une erreur de cache
des boutons a empêché de rejouer le préfixe, puis un contrôle trop large des
256 octets a inclus trois octets transitoires hors des 160 cellules visibles.
Ces erreurs de diagnostic ne sont pas présentées comme des défauts du jeu.

## Suite et limites

La victoire du troisième boss MD et l'utilisation naturelle de la corde sur
MD restent à établir. La corde native est déjà testée en situations contrôlées
PAL/NTSC, mais la référence ci-dessus ne remplace pas un parcours MD équivalent.
Le reste de la campagne, le flux RNG/R/IRQ, la cadence globale, les mesures
audio et le matériel réel restent incomplets. Aucun pourcentage global n'est
déduit de ce seul jalon.

Les SHA et la portée des preuves sont dans `campaign_v0287_progress_report.json`.
