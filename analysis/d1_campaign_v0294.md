# v0294 : premier cristal et retour a l'exterieur confirmes

Une nouvelle conduite adaptative termine le premier donjon sur la v0294, avec l'arme de depart. Le boss68 de175 est vaincu, le cristal et son soin sont termines a32/32 PV, puis le heros ressort enB9 a28/32 PV. Ce jalon ne modifie pas la ROM.

Le debut jusqu'a5045 et la premiere cle sont sans aide. Ensuite, le garde de blessures de test protege seulement l'approche. Sa derniere ecriture est a12338, pendant la transition ; le combat commence a12409 avec20 PV et un compteur de blessures nul, soit71 images plus tard. Un coup ordinaire fait passer le heros de20 a16 PV a12493. Aucun soin,cle,equipement ou instantane n'est injecte. Le retour n'ajoute aucune aide. Ce parcours est assiste pendant l'approche et n'est pas une campagne entierement sans aide.

| Etape | Trace | Fin | Resultat |
| --- | --- | --- | --- |
| Boss et cristal | md-auto-v0294-d1-assisted03 |13325|32/32 PV, premier cristal|
| Retour | md-auto-v0294-d1-exit01 |15025|exterieurB9,28/32 PV|

Les deux segments ont leur relecture froide independante par commandes fixes :65536 octets de RAM et PNG final exacts. Le controleur de retour predit23 fenetres completes de RAM, toutes identiques a l'execution principale. Le controle de pile avant chaque instruction normale du68000, apres l'initialisation a partir de l'image14 et jusqu'a15025, observeF798 au-dessus du tasF600 :408 octets de marge. Les en-tetes de l'allocateur restent valides ; RAM et image finales correspondent aussi au retour canonique.

Les essais precedents sont conserves comme diagnostics. Les anciennes commandes fixes meurent enD1. Une conduite fraiche avec8 PV meurt avant le boss. Un essai avec garde quitte la premiere salle de cle avant l'activation des ennemis ; un autre omet la cle193 pour la meme raison. L'option qui ignore les acteurs inactifs est retiree des nouveaux parcours D1 : ils attendent leur vraie activation et recuperent les cles. Une branche distincte obtient ensuite la cle1C5 et la hache1B6, mais son essai de boss a8 PV echoue ; cette branche ne remplace pas le parcours reussi ci-dessus.

[Rapport et empreintes](d1_campaign_v0294_report.json). Reproduction : `tools/summarize_d1_campaign_v0294.py`. Les captures sont generees par le jeu depuis le demarrage, sans import de sauvegarde ou de RAM historique.

Limites : ce rapport confirme le premier cristal et sa sortie sur la compilation courante. L'acquisition de la hache pour la suite, les autres donjons, la fin et la campagne SMS equivalente restent des etapes distinctes. Les images intermediaires, les ondes audio, la cadence globale, le materiel reel et les autres chemins ne sont pas prouves par les comparaisons de RAM finale ou par cette marge de pile observee.
