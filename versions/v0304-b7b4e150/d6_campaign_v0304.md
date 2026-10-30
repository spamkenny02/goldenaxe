# v304 : sixieme cristal et retour hors du donjon

Le sixieme cristal est obtenu sur la ROM v304, SHA-256
`b7b4e15008a6f0a913c9ad43f15386abcdfbb719e5a575873d92712ba52503a8`.
Cette etape prolonge la [cloche de glace et les passages D6](d6_progress_v0304.md).
Le programme du jeu ne change pas pendant ces controles.

Le boss de la salle 115 est de type 64. Les donnees originales 3C140440
indiquent 60 PV, des degats de base de 20, une armure de 4 et le drapeau
de boss 40. La derniere ecriture de protection d'approche est a la frame
146 965. Le premier etat de combat normal est a 146 996 : 31 frames plus
tard, avec 72 PV et un compteur de blessures nul.

| Etape | Frame finale | Resultat |
| --- | ---: | --- |
| Combat partiel boss01 | 150 596 | Heros 72/72 PV ; boss encore a 40 PV |
| Victoire boss03 | 152 143 | Six cristaux, recompense terminee, 80/80 PV et 48/48 de magie |
| Sortie exit01 | 153 868 | Exterieur 8B, 80/80 PV, aucune cle |

Le combat partiel est rejoue independamment avant la continuation. Une
premiere continuation, boss02, perd le combat : heros a zero PV, boss a
10 PV. Cet essai reste un diagnostic et ne fait pas partie du parcours
reussi. Boss03 repart du segment boss01 verifie et emploie une conduite
plus prudente, sans importer la progression de boss02 ni reinitialiser le
combat. Les premiers degats ordinaires de cette branche sont observes a
150 687 : 72 vers 58 PV, compteur de blessures a 47. Le soin du cristal
porte ensuite normalement la vie et la capacite a 80.

Le retour traverse 115, 125, 124, 123, 113, 114, 138, 169, 168, 178, 177
et 187 avant l'exterieur 8B. Les contacts des teleporteurs sont accomplis
avec les commandes ordinaires. Cloche de glace, bottes, corde et canoe
restent acquis ; la hache reste equipee. Aucune nouvelle ecriture d'aide
n'est ajoutee pendant la continuation gagnante ou le retour.

Les trois etapes disposent chacune d'une relecture a commandes fixes
depuis le demarrage. Les 65 536 octets de RAM et le PNG final concordent.
Les 450, 104 et 82 fenetres de prediction concordent egalement avec toute
la RAM primaire. Les aides historiques sur les approches sont consignees :
ce parcours ne constitue pas une campagne entierement sans assistance.

Le [rapport reproductible](d6_campaign_v0304_report.json) relie les
commandes, les aides, les sources conservees et le profil de pile mesure
avant chaque instruction normale du 68000 jusqu'a la sortie. Le profil
verifie aussi les en-tetes du tas et la concordance de la RAM et du PNG
finaux. Sa marge observee ne borne pas les chemins futurs.

Six cristaux et leurs retours sont verifies sur cette ROM. Les donjons
suivants, la fin, les sauvegardes, le hasard global et la fidelite complete
video/audio/materiel restent ouverts. Le combat SMS equivalent contre ce
boss n'a pas encore ete compare.

Marge de pile observee sur ce parcours : **496 octets**, jusqu'a la frame
153 868. Aucun en-tete de tas invalide observe.


Erratum2026-10-30 : la marge de496 octets citee ci-dessus concerne les points instrumentes. Le minimum avant chaque instruction est478 octets sur les parcours D1-D6. Voir la [correction de mesure](stack_minimum_v0304_erratum.md).
