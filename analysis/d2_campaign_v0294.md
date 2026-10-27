# v0294 : deuxieme cristal et retour a l'exterieur confirmes

Le deuxieme boss63 de144 est vaincu sur la v0294. Le cristal et le soin sont termines a48/48 PV, puis le heros revient enD6 a31/48 PV, avec une cle et la hache equipee. La ROM ne change pas dans ce jalon.

Les cles160,152 et131 sont obtenues par combat et ramassage ordinaires. L'aide de la deuxieme approche se termine a33281, avant le debut du combat a33338 :57 images d'avance, compteur de blessures nul et40 PV. Un premier coup ordinaire reduit la vie de40 a32 a33548. Aucun soin,objet,cle ou instantane n'est injecte ; les seuls changements de RAM de test restent les compteurs de blessures des approches.

Le premier essai de combat atteint2 PV restants au boss mais meurt. L'essai lateral suivant meurt avec10 PV au boss. Pour reprendre sans rejouer la meme fin perdante, l'outil execute a froid les commandes du premier essai jusqu'a33847 : le heros est alors vivant avec16 PV, son delai ordinaire de blessures vaut46 et le boss possede8 PV. Les65536 octets de RAM et le PNG correspondent a la capture originale a cette image. Ces fichiers servent seulement a la comparaison et ne sont jamais injectes dans le jeu. Ce prefixe raccourci a sa propre relecture froide independante.

Le controleur choisit ensuite de nouvelles commandes ordinaires depuis ce point. Ses19 fenetres de prediction correspondent toutes a la RAM entiere du coeur principal. Le boss est vaincu sans nouvelle aide, puis le soin du cristal s'acheve. Le retour suit144,143,133,132,131,121,120,130,140,150,151,161,171, puis l'exterieurD6 ; ses27 fenetres predites correspondent egalement. Les relectures froides du combat reussi et de la sortie retrouvent RAM entiere et PNG final exacts.

| Etape | Trace | Fin |
| --- | --- | --- |
| Cle160 | md-auto-v0294-d2-key01 |26780|
| Cle152 | md-auto-v0294-d2-key02 |28358|
| Cle131 | md-auto-v0294-d2-key03 |31534|
| Prefixe vivant rejoue a froid | md-auto-v0294-d2-prefix02 |33847|
| Boss et cristal | md-auto-v0294-d2-boss04 |34663|
| Retour enD6 | md-auto-v0294-d2-exit01 |37128|

Le controle de pile avant chaque instruction normale du68000, apres l'initialisation a partir de l'image14 et jusqu'a37128, conserveF798 au-dessus du tasF600 :408 octets de marge observee. Les en-tetes restent valides et RAM/image finales correspondent a la sortie canonique. Cette borne observee ne couvre pas les chemins suivants.

Un index de sources fige les variantes des controleurs utilisees. Le correctif de placement lateral fait avancer le heros dans l'arene avant de se decaler depuis la porte basse ; son essai n'est pas presente comme une victoire. Les essais morts et le prefixe trop tardif a33963 restent des diagnostics, distincts de la branche reussie.

[Rapport reproductible](d2_campaign_v0294_report.json), [index des sources figees](d2_campaign_v0294_source_index.json). Commande : `tools/summarize_d2_campaign_v0294.py`. Les [preparatifs avec hache et fee](d2_approach_v0294.md) couvrent sept autres relectures.

Limites : campagne native NTSC avec aides d'approche consignees, retirees avant chaque boss. Les donjons suivants, la fin, la campagne SMS equivalente et la fidelite globale restent a verifier. L'audit des tables a aussi identifie la variante7C en11E, dirigee vers54D3 dans la SMS mais encore absente de la distribution native ; ce manque fait l'objet d'une correction a venir. Les relectures finales ne prouvent pas toutes les images, les ondes audio ou la cadence physique du materiel.
