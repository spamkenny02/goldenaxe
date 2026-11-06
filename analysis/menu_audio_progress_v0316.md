# Menus et audio — travail après v316

La production et les 316 ROMs numérotées restent inchangées. La v317 n’est
pas publiée : un contrôle plus complet a trouvé une régression de rendu
pendant quelques images de l’intro.

Les corrections du candidat08 sont mesurées sur la ROM SMS originale :

- Sortie du titre, chargement et fondu de Nouveau jeu / Continuer ; le
  curseur apparaît après le fondu et passe par la file d’envoi à l’IRQ.
- Fermeture du menu et révélation de l’entrée du nom ; les sprites du
  curseur sont publiés à l’IRQ suivante, sans apparition pendant le fondu.
- Répétition des directions traduite depuis 12C1 : compteur partagé,
  seuils 24/8, incrément même à l’état neutre, sans remise à zéro lorsque
  seule la direction change.
- Transfert de carte 0914 : interruption masquée puis lecture du statut
  VDP. La prévision utilise le travail réel du lecteur audio et le modèle
  de l’IRQ source. Les compteurs musicaux ne sont pas retouchés.
- Avance du curseur de saisie après le transfert ; validation du nom
  silencieuse, comme 125A. Le son AB ajouté par le portage est retiré.

Le candidat08 passe 210 cas naturels de premier caractère. Quatre états de
400 octets audio logiques sont comparés par cas. La demande sonore native
en attente représente DE08 avant sa consommation par l’IRQ ; sa valeur
réelle est enregistrée, et les différences physiques brutes sont gardées.
Le premier essai qui comparait ces deux stockages sans normalisation reste
conservé comme échec, pas effacé.

Huit démarrages avec des instants de sélection différents établissent la
phase du tempo jusqu’au premier écran. Les fenêtres contrôlées de musique
du menu et du premier écran correspondent aussi. Les bips du récit ont
encore des différences de déclenchement explicitement listées dans le
rapport ; cela ne prouve pas l’audio complet du jeu.

Les 270 images normalisées contrôlées des menus correspondent à la SMS.
La séquence de saisie du nom compare aussi positions, répétitions et
demandes/acceptations sonores. Quatre parcours Nouveau jeu / Continuer
valident les événements de sélection et confirmation. Six restaurations
d’inventaire, deux reprises d’une sauvegarde réelle à neuf cristaux et deux
nouveaux trajets au premier donjon passent sur ce candidat. Cela n’est pas
un nouveau parcours complet jusqu’au générique.

## Motif du maintien en candidat

Les états audio de l’intro et ses captures fixes restent identiques à
v316, mais les hachages du tampon de travail NTSC changent sur certaines
transitions. Un observateur vidéo a donc été ajouté au frontal libretro
pour comparer les images effectivement émises, sans milliers de PNG.

Le candidat08 change des images de l’intro : sa nouvelle condition dans
`world_vint` s’exécutait aussi hors des menus. Le candidat09 la déplace
dans un callback propre aux menus et rétablit le callback ordinaire pour
le jeu et le retour au titre. Cela réduit les différences, sans les fermer :
21 images NTSC et 9 images PAL sur 6500 images émises par région.

Les images concernées sont ensuite comparées à la SMS originale. Des
pixels du candidat09 sont meilleurs, mais d’autres sont moins fidèles ;
les neuf cas PAL incluent tous des pixels corrects sur v316 et incorrects
sur le candidat. Le contrôle n’est donc pas déclaré réussi. Les captures,
comptages et désassemblages sont conservés.

La routine de transfert `draw_map` et le dispatch DMA ont les mêmes
instructions normalisées dans les deux compilations examinées. Le code
de l’intro intégré à `main.isra.0` change avec l’optimisation globale ; la
suite doit résoudre sa publication et son cadencement à partir de la
source, sans masquer les écarts par un simple changement de critère.

Le [patch candidat09](menu_audio_candidate09_v0316_crlf.patch) est fourni pour
revue et reprise ; il n’est pas appliqué aux sources de production.
Le [rapport de travail](menu_audio_progress_v0316_report.json) distingue
le candidat08 validé pour les menus du candidat09 encore en développement.
Les artefacts clos sont archivés et relus avant nettoyage ; le binaire,
les symboles et le cache de compilation du candidat09 restent disponibles.

Le portage complet reste à valider : rendu et bips du récit, autres entrées
et modifications de nom, nouveau parcours complet, rafraîchissement/RNG
global et matériel physique ne sont pas couverts par ces seuls contrôles.

Un contrôle de reproductibilité compare deux démarrages de la même v316 :
les 6500 images sont identiques dans chaque région. Les écarts du candidat
ne viennent donc pas de variations aléatoires du frontal. Le profil des
entrées de transfert mesure des décalages variables ; il ne justifie pas
un décalage constant ajouté au rendu.
[Profil des entrées de transfert](menu_intro_raster_profile_v0316_report.json)
· [Patch CRLF vérifié](menu_audio_patch_review_v0316_report.json)
· [Nettoyage vérifié](menu_audio_progress_cleanup_v0316_report.json)
