# Réconciliation des trois textes signalés

Les chaînes SMS DA58, DA7C et ED3C existent bien. Leur absence littérale des ressources MD avait été constatée ; aucun nouveau déclencheur n'est inventé pour les rendre visibles.

Le PNJ de FB/8F sélectionne 99F1, dont le texte se termine juste avant DA58. Le formateur retourne alors HL=9A58. Le code original 6277–6286 appelle le formateur une seule fois, attend une commande, puis saute à 1DE2 : il n'affiche pas la chaîne suivante. DA7C suit DA58, mais aucune de ces deux chaînes n'est sélectionnée par ce PNJ. Le simple voisinage dans la banque de texte ne définit donc pas une quête Terre supplémentaire chez lui.

Le troisième PNJ de Halls (CE/02, position 0344) sélectionne A887 avant le neuvième cristal et ACE3 après. Son code 6624–6633 ne lit aucun état de cloche et rejoint le même affichage unique. ED3C suit physiquement le texte ACE3 : le retour HL=AD3C observé après celui-ci n'est pas une nouvelle entrée de dialogue.

Les relevés d'exécution distinguent les appels 050C/0524 des retours du formateur et du wrapper. Le JSON associé conserve les octets de code vérifiés, les contextes et les relevés retenus. Les trois adresses ne figurent ni dans les 65 sélections ordinaires exportées ni dans les neuf variantes conditionnelles connues.

Conclusion limitée : les PNJ voisins et le pointeur de retour ne sont pas des déclencheurs de ces trois textes. Cela écarte cette explication d'un dialogue manquant dans le portage. L'inutilisation globale dans toute la ROM n'est pas encore démontrée ; ce point reste ouvert jusqu'à une preuve complète de flux ou un déclenchement réel.
