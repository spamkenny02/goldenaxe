# Point 5 — audit des entrées du moteur de texte

L’audit rapproche 157 enregistrements vérifiés de 36 couples entrée/adresse de retour observés. Les préfixes de démarrage communs sont comptés plusieurs fois ; ce nombre ne représente pas des conversations distinctes.

Les appels directs possibles vers 050C, 0524, 6277, 7444 et 779B sont inventoriés sur les 256 Kio. Les correspondances brutes peuvent être des données ou commencer au milieu d’une instruction. Elles restent des candidats à analyser, pas des appels exécutables certifiés.

Les 11 appels littéraux vers 050C dans les deux banques fixes ont tous leur adresse de retour observée en exécution. Cela couvre ces sites d’appel, sans prouver toutes les valeurs possibles de leur argument ni éliminer les appels indirects.

| Entrée | Retour pile | Textes sélectionnés distincts |
| --- | --- | --- |
| 050C | 6064 | 911E |
| 050C | 61E2 | 8BCD |
| 050C | 627A | 8BEA, 8E5C, 8E94, 8ED9, 8FE3, 9021, 9035, 905B, 90BF, 9181, 91BF, 91E3, 9247, 92A8, 92C6, 930A, 9357, 93B8, 941B, 946B, 94DE, 951E, 95CC, 9611, 969D, 96EC, 9740, 9848, 9891, 9921, 9945, 99A9, 99F1, 9ACC, 9B3D, 9B72, 9BC5, 9BFE, 9C09, 9C5A, 9CE4, 9D34, 9DDA, 9E0C, 9E78, 9F1C, 9F95, 9FDE, A03F, A077, A17F, A1A3, A202, A244, A2CE, A35C, A3CA, A451, A4A1, A4AE, A4C1, A52F, A568, A5C0, A621, A670, A6A5, A6FF, A79C, A7CE, A852, A887, A8FC, A937, A996, A9EF, AA29, AA61, AAC3, AB0D, AC1E, AC65, ACB5, ACE3, B930, B94D, B9D7, BA20 |
| 050C | 64D0 | 8E30 |
| 050C | 6505 | 8DF6 |
| 050C | 6663 | A0E6 |
| 050C | 66CD | B90E |
| 050C | 683E | B95F |
| 050C | 685E | B982 |
| 050C | 6883 | B9BF |
| 050C | 6893 | BA8E |
| 0524 | 6064 | 911E |
| 0524 | 61E2 | 8BCD |
| 0524 | 627A | 8BEA, 8E5C, 8E94, 8ED9, 8FE3, 9021, 9035, 905B, 90BF, 9181, 91BF, 91E3, 9247, 92A8, 92C6, 930A, 9357, 93B8, 941B, 946B, 94DE, 951E, 95CC, 9611, 969D, 96EC, 9740, 9848, 9891, 9921, 9945, 99A9, 99F1, 9ACC, 9B3D, 9B72, 9BC5, 9BFE, 9C09, 9C5A, 9CE4, 9D34, 9DDA, 9E0C, 9E78, 9F1C, 9F95, 9FDE, A03F, A077, A17F, A1A3, A202, A244, A2CE, A35C, A3CA, A451, A4A1, A4AE, A4C1, A52F, A568, A5C0, A621, A670, A6A5, A6FF, A79C, A7CE, A852, A887, A8FC, A937, A996, A9EF, AA29, AA61, AAC3, AB0D, AC1E, AC65, ACB5, ACE3, B930, B94D, B9D7, BA20 |
| 0524 | 64D0 | 8E30 |
| 0524 | 6505 | 8DF6 |
| 0524 | 6663 | A0E6 |
| 0524 | 66CD | B90E |
| 0524 | 683E | B95F |
| 0524 | 685E | B982 |
| 0524 | 6883 | B9BF |
| 0524 | 6893 | BA8E |
| 0524 | 73F1 | 8D70 |
| 0524 | 7402 | 8DA7 |
| 0524 | 7447 | 8CC7, 8CF5, 8DB6, 8DDD, AB68, AD89, AE39, AF95, AFD6, B04A, B333, B35D, B3E5, B457, B621, B747, B77E, B8CA |
| 0524 | 7483 | 8BEA, 8C01, 8C45 |
| 0524 | 74B8 | 8BC2 |
| 0524 | 74C4 | 8BCD |
| 0524 | 755F | 8BEA |
| 0524 | 7575 | 8FE3 |
| 0524 | 7604 | 8C45 |
| 0524 | 7615 | 8FFD |
| 0524 | 76AB | 8C7B, 8D3F |
| 0524 | 78D6 | 8B98, 8BAC |
| 0524 | 7A73 | B06F |
| 0524 | 7A9E | B233 |

Aucun des trois textes DA58, DA7C ou ED3C n’est déclenché dans ces enregistrements. Le point 5 reste ouvert : le flux indirect et les pointeurs calculés ne sont pas encore entièrement prouvés. Aucun dialogue ou état de quête n’est ajouté à la ROM sur cette seule absence.

[Données, octets et contextes de désassemblage](sms_text_frontend_sources.json).
