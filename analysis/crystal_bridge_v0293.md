# v0293 : pont du cinquieme cristal et acces au sixieme donjon

ROM : v0293, 2 Mio, checksum3549, SHA-256 `878a7f44afb53997dfeeb25351b5c34370944cf98836ae2c687180c8a33ec735`.

Le script original de la carte49 (AF4A) traite la porte du cinquieme donjon puis saute en698B. Cette derniere routine etait absente du portage. Elle attend un etat du heros non nul et le bit7 du cinquieme cristal C0D3. La routine193D positionne le bit de transformation de la carte avant de tester sa valeur precedente. Une seule nouvelle activation demande le sonA8 et le redessin5E8B. La transformation20 deja portee ouvre les cellules4A et5A en0A et6B. La correction native raccorde exactement cette decision apres la porte, uniquement sur la carte exterieure49. Aucun etat du parcours n'est injecte par le code distribue.

L'absence du pont est reproduite sur la v0292. Le calcul des chemins ne pouvait pas relier la partie occidentale et orientale de49. Avec le vrai pont ouvert par le cinquieme cristal, une proposition de227 etapes conduit de49 vers4A,4B,5B,6B,7B,7C,8C,9C,9B et8B. Le jeu execute ce parcours et entre dans la salle187 du sixieme donjon, a72/72 PV. Les bottes permettent le deplacement d'essai de16 pixels. La nouvelle aide d'approche est consignee pour le boss196 ; ce checkpoint s'arrete avant de l'atteindre.

Preuves :

- 5120 situations executent le Z80 original698B/193D et la decision C compilee : heros0/1/5/9, cristal0/1/7F/80/FF et toutes les256 valeurs du drapeau. Seul le puits de redessin/son5E8B est intercepte dans ce banc.
- 12 situations dans les vrais jeux comparent160 cellules,1280 octets de carte logicielle, drapeau, cristal, salle, etat et position en PAL/NTSC. Les quatre cas positifs concernes restent bloques sur la v0292 et passent sur la v0293.
- Les huit mots VDP du passage ouvert et les pixels des tuiles referencees correspondent dans quatre situations PAL/NTSC, soit32 mots compares.
- Le premier donjon est rejoue sans aide jusqu'a32/32 PV. Le parcours natif acquiert les cinq cristaux et sort a72/72 PV. Une troisieme preuve prolonge cette campagne jusqu'a l'entree du sixieme donjon. Chaque etape a une relecture froide independante par commandes fixes, RAM entiere65536 octets et PNG final identiques.
- L'observateur de pile avant chaque instruction normale68000, a partir de l'image14 jusqu'a117215, retrouve408 octets de marge observee et des en-tetes de tas valides ; RAM/image finales identiques au coeur officiel.

Le [rapport consolide](crystal_bridge_v0293_report.json) lie les controles aux ROMs, sources et captures par SHA-256. Reproduction : `tools/summarize_crystal_bridge_v0293.py`.

Les cases controles ne prouvent pas une equivalence de toutes les images, de la latence physique du redessin ni des ondes audio. Les parcours aides le declarent explicitement ; les gardes sont retirees avant les boss et aucun equipement, argent ou soin n'est ajoute par fixture dans la campagne. Une victoire dans la campagne SMS complete n'est pas revendiquee. Les donjons6-10, la fin et la fidelite globale restent a verifier.
