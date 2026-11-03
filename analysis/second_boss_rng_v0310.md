# Boss à satellites : branche de production et hasard en v0310

[Rapport](second_boss_rng_v0310_report.json) : 732 cas distincts en NTSC,
puis les mêmes en PAL, soit 1 464 comparaisons. La branche type65 est extraite
sans changement de `actors.c`, puis compilée avec le véritable adaptateur de
graine et la routine native du boss. Les instructions SMS du boss, du choix de
direction, des limites et de l'orbite exécutent leurs calculs d'origine.
Le banc contrôle les entrées aléatoires, sans prétendre reconstruire leur phase.

Les contrôles comparent les **768 octets d'acteurs**, la graine après la
branche et le nombre exact de lectures du fournisseur. Ils couvrent tous les
256 résultats du seuil 04E1, les cinq états du boss, les gardes des compteurs,
la fin du décompte de 20 déplacements, les deux chemins du choix de direction,
les limites de durée de pause et plusieurs occupations du groupe de satellites.
Aucun dépassement de la séquence de lectures préparée n'est admis.

Le seuil A921 appelle 04E1 et conserve bien ses huit bits. A935 lit R pour la
durée de pause, tandis que 4ED5 et 4EBE servent au choix de direction. Les cas
vérifient que les lectures inutiles ne sont pas consommées, notamment lorsque
le compteur impose un retour, quand le mouvement est imposé, ou quand une
direction vers le héros évite le deuxième tirage. Les sources et résultats
bruts sont figés dans `validation/v0310-second-boss-rng-sources`.

Le premier lancement du pilote s'est arrêté avant compilation : le répertoire
parent du générateur SMS privé n'existait pas. L'essai02 crée ce parent et
termine avec succès. Aucune modification de la ROM publique n'a été nécessaire.

Limites : c'est un banc isolé du fragment de dispatch et de la routine du boss.
Les contacts/dégâts et la fin commune de la boucle d'acteurs sont hors de ce
contrôle. Les lectures R et la sortie 04E1 SMS sont remplacées par des entrées
contrôlées ; côté MD, la graine initiale et le fournisseur sont contrôlés.
Ce résultat ne prouve ni la phase naturelle R/IRQ, ni un combat naturel, ni les
pixels, l'audio ou le matériel. La campagne complète reste prouvée sur v309.
