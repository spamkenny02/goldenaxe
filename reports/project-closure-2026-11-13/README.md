# Clôture du projet — V328

Clôture demandée par l'utilisateur le 13 novembre 2026. La ROM acceptée
reste inchangée, SHA-256 `368c003f92e0860336c919005ec19f0ae620d6876b4bca8f436f83e682b59dcc`.

La compilation a été exécutée depuis une exportation des seuls fichiers de
l'index Git : aucune ROM Mega Drive précompilée, aucun ancien dossier de
validation ni objet natif généré n'était présent dans cette copie. La chaîne
complète des sources reproduit exactement la V328.

Le lecteur de runs portable livré avec son cœur Windows x64 atteint la fin
en PAL et NTSC sur la ROM reconstruite. Les protections d'approche sont
retirées avant les boss et leur absence durant ces combats est auditée.
Quatre chargements d'une sauvegarde valide passent dans la copie propre.
Le lecteur SMS est aussi lancé sur un préfixe de 3 000 images ; ce dernier
contrôle est court, distinct des preuves historiques de parcours SMS complet.

- [Compilation complète](source-build.json)
- [Run MD NTSC](run-ntsc.json)
- [Run MD PAL](run-pal.json)
- [Préfixe SMS](run-sms-smoke.json)
- [Chargements Continuer](continue.json)
- [Dépendances de compilation](dependencies.json)
- [Bilan du ménage local](cleanup.json)
- [Instructions de compilation et de débogage](../../BUILD_AND_DEBUG.md)

Les vidéos, captures et caches locaux non suivis sont abandonnés à la demande
de l'utilisateur. Le ménage préserve tous les fichiers suivis par Git et ne
traverse aucun lien ou jonction vers un autre dossier. Les rapports historiques
peuvent donc référencer des captures locales supprimées ; les procédures
V328 autonomes conservées permettent de produire de nouveaux runs.

Ménage effectué sans erreur : 571 333 fichiers régénérables supprimés,
99,8 Go de contenu logique retiré, environ 91,1 Go réellement récupérés
sur le disque. Tous les fichiers suivis sont conservés ; huit liens/jonctions
ont été ignorés pour préserver leurs cibles.
