# v304 : correction de la mesure minimale de pile

Les anciennes syntheses annoncaient496 octets comme marge minimale. Ce nombre utilise les points instrumentes (entrees de fonctions), alors que les profils avaient aussi conserve le minimum avant chaque instruction normale du68000.

Le minimum aux points instrumentes est63472 ; le minimum par instruction est63454. La limite du tas est62976. La marge observee correcte est donc **478 octets**, soit18 de moins que la synthese precedente. Les en-tetes du tas sont valides sur ces parcours.

| Parcours termine | Frames | Marge aux points instrumentes | Marge par instruction |
| --- | ---: | ---: | ---: |
| D1 | 14583 | 496 | 478 |
| D2 | 37005 | 496 | 478 |
| D3 | 53755 | 496 | 478 |
| D4 | 86158 | 496 | 478 |
| D5 | 121051 | 496 | 478 |
| D6 | 153868 | 496 | 478 |

Les profils bruts et anciens rapports restent conserves avec leurs empreintes. Le [rapport d'audit](stack_minimum_v0304_erratum_report.json) lie les six mesures et leurs hashes. Le profileur courant utilise maintenant le minimum par instruction lorsque ce releve est disponible et expose separement le minimum des points instrumentes.

Il s'agit d'une correction de verification et de documentation. La ROM ne change pas. Cette marge observee ne prouve pas la securite de tous les chemins futurs ; aucun chevauchement avec le tas n'est observe dans ces six parcours.
