# v0305 — Hache, fée et deuxième cristal

La ROM reste `83dfaf697521ce97597af259835eccae70bde055e70f321176caad34f93a23c7`.
Aucun code natif ou binaire n’est modifié par ce jalon. Le parcours poursuit
le premier cristal et le retour de la branche ayant récupéré l’huile à C7.

| Étape | Image finale | Salle | PV | Clés |
| --- | --- | --- | --- | --- |
| Retour pour la hache | 17678 | 1E4 | 28/32 | 0 |
| Clé de 1C5 | 21450 | 1C5 | 32/32 | 1 |
| Hache | 23234 | 1B6 | 32/32 | 0 |
| Sortie avec hache équipée | 24578 | B9 | 32/32 | 0 |
| Arrivée chez la fée | 25634 | AF | 32/32 | 0 |
| Don de vie et sortie | 26152 | C9 | 40/40 | 0 |
| Entrée D2 | 28313 | 171 | 40/40 | 0 |
| Clé de 160 | 29474 | 160 | 40/40 | 1 |
| Clé de 152 | 31486 | 152 | 40/40 | 2 |
| Clé de 131 | 35150 | 131 | 40/40 | 2 |
| Deuxième cristal | 38097 | 144 | 48/48 | 1 |
| Sortie D2 | 40562 | D6 | 31/48 | 1 |

La hache est obtenue dans son donjon, puis équipée par le menu. Trois
coupes réelles ouvrent le trajet vers la première fée C9. Le dialogue donne
l’augmentation de capacité de 32 à 40 PV et le soin complet, puis le héros
ressort normalement. Le deuxième donjon est atteint à 40/40 PV.

Les trois clés de 160, 152 et 131 sont récupérées par le jeu. Quatre essais
intermédiaires échouent et restent exclus des validations : combat bloqué,
traversée sans combat, essai de position devant une porte puis retour trop
précoce pendant l’apparition d’un acteur. La modification expérimentale de
position devant la porte a été retirée ; ses sources et résultats sont
conservés.

Le contrôleur dispose maintenant d’une option limitée à trois sorties et
rentrées lorsqu’aucune position d’attaque n’est accessible. Il attend que
les véritables rectangles d’attaque des ennemis soient initialisés et
utilise uniquement des déplacements normaux. L’essai réussi fait deux
rentrées dans la salle 151 et récupère ensuite la clé de 152. Aucun ennemi
n’est supprimé par l’outil et aucune porte n’est ouverte artificiellement.
Cette stratégie ne démontre pas une égalité du hasard entre SMS et MD.

La protection de test d’approche est retirée à l’image 36726. Le premier
combat du boss 63 commence à 36783 avec 40 PV et compteur de protection nul,
soit 57 images plus tard. Un coup normal à 36960 fait passer les PV de 40
à 32 ; le combat continue avec les dégâts ordinaires. Le cristal et son
soin terminent à 48/48 PV. La sortie finit en D6 à 31/48 PV et une clé.
Aucune écriture d’assistance ne reprend après 36726.

Les aides héritées et celles de cette approche ne modifient que `hero_hurt`
(valeurs 0 et 129). Aucun PV, inventaire, acteur, progression ou sauvegarde
n’est injecté. Le parcours conserve l’huile de C7 et le premier cristal.
Il n’est pas présenté comme une campagne entièrement sans assistance.

Douze relectures froides indépendantes reproduisent les 65 536 octets de RAM
et le PNG final. Les fenêtres du contrôleur de combat et de sortie ont une
égalité de RAM complète, sans import d’état secondaire dans le jeu principal.
Le profil de pile avant chaque instruction normale jusqu’à l’image 40562
observe 450 octets de marge : SP minimal 63426, frontière de tas maximale
62976, chaînes du tas valides. RAM et PNG du profil correspondent au retour
canonique. Cette observation ne couvre pas tous les chemins du jeu.

Un plan direct vers le maître du Feu E6 reste sans chemin sur la carte de
base, même avec la hache. Il ne constitue pas un parcours validé. Les
donjons suivants, la fin, les sauvegardes, le hasard SMS et sa phase globale,
ainsi que la fidélité vidéo/audio/matériel complète restent à traiter.
Les sept cristaux et la clé des voleurs de v0304 restent propres à v0304.

[Rapport et empreintes](d2_campaign_v0305_report.json). Reproduction locale :
`tools/summarize_d2_campaign_v0305.py`. Les captures sont archivées sans perte
par `tools/archive_d2_campaign_v0305.py`, vérifiées puis nettoyées ; les ROMs
numérotées et l’original SMS restent protégés.
