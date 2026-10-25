# v0287 historique — troisième donjon et corde acquise

ROM : `58068350382a19ddc73a62eb747e42d978c36a1daf3c87f819e921f391b0065d`.
Ces preuves appartiennent à la v0287 ; la v0288 corrige ensuite la vitesse
sur les terrains spéciaux.

Le héros récupère la corde en 1F4, presse le passage en 1E3, fait le détour
par 1D2, puis rejoint le boss 1C3. La protection d'approche finit à la frame
47235, avant le combat à 47270, compteur nul. Une recherche trop agressive
meurt ; celle qui conserve des chemins d'esquive complets gagne sans perte
de PV. Le cristal porte la capacité à 56. La sortie réussie atteint 62 à
56/56 PV, frame 51924, sans nouvelle écriture d'aide après le boss.

L'entrée, l'objet, les deux segments de combat et la sortie ont chacun une
relecture froide officielle : toute la RAM et le PNG finals correspondent.
Le premier segment de combat s'arrête à sa limite de diagnostic avec 12 PV
au boss et 48 au héros ; le suivant rejoue ses commandes avant de poursuivre.
Les prédictions n'importent des états que dans le cœur secondaire de recherche.

Depuis la sortie, la corde réellement acquise est utilisée en 41, en (104,88).
Dix rangées de deux tuiles se dessinent une par frame, puis le héros avance
sur la corde. Les indicateurs (256 octets), la carte (1 280) et les objets
possédés (17) correspondent à la SMS, à la sortie et après ce parcours.
Le nombre de clés, l'or, les rencontres et toute la sauvegarde ne sont pas
présentés comme identiques. Chaque système a sa propre relecture RAM/PNG.

L'observation de pile à chaque instruction jusqu'à la corde (52 989 frames)
donne F6FE face à la limite F600 : 254 octets de marge observée, tas valide.
La valeur de 412 octets mesurée précédemment ne couvrait pas ce nouveau trajet.

Les échecs de sortie sont conservés : ennemis dans une zone inaccessible,
puis mortalité d'un contrôleur trop exposé. Exit04 a réussi dans le jeu,
mais une assertion d'enregistrement contenait un nom de variable erroné ;
sa récupération de métadonnées et sa relecture sont explicites. Le jalon
retenu est exit05, une nouvelle exécution propre après correction, guidée
par les vrais points de porte et de portail. Elle n'ajoute aucune aide.

L'enquête sur le mouvement a ensuite révélé que la v0287 emploie cinq ticks
sur la corde au lieu des douze de la SMS. La v0288 sélectionne les tables
complètes de terrain pour corriger cet écart ; les dix rangées graphiques
étaient déjà correctes. Le préfixe d'observation de l'outil a été accéléré
sans changer ses commandes, sa RAM ou son PNG finals.

La référence SMS atteint aussi l'entrée du quatrième donjon avec la carte
réelle du préfixe de corde ; la relecture passe. Les essais vers le canoë
restent bloqués dans les partitions internes. Aucun quatrième boss, canoë
acquis ou portage complet n'est annoncé.

Rapport : `d3_rope_v0287_report.json`.
