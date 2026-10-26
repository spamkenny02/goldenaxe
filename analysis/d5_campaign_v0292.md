# Cinquieme donjon termine dans la campagne native, v0292

La ROM de production reste v0292, SHA-256 `6eeb56086a81c230c75b154f51cafab72167a1eec42c691aed9bf317fd19dd82`, checksum `2BF8`, 2 Mio. Les changements de ce jalon concernent les outils de parcours, les preuves et la documentation.

Depuis le [ravitaillement](d5_supplies_v0292.md), le heros traverse172 et173, utilise une des deux cles et entre dans la salle163. L'aide d'approche est retiree a112509 ; le combat commence a112535, avec le compteur de blessures a zero et64/64 PV. Le boss65 et ses satellites sont vaincus par commandes ordinaires, sans perte de vie. Sa mort est observee a115582. Le cristal est ramasse et son soin termine a116065 :72/72 PV, magie48/48 et aucune recompense encore active. La limite du test116135 intervient apres cette completion.

Le retour reste entierement sans nouvelle assistance. Une commande HAUT au mecanisme de173, position184,40, ouvre le passage vers174. Le teleporteur de174 mene en155, puis165,166,176,186 et dehors49. La sortie est verifiee a117065 et le trace finit a117215,72/72 PV, une cle restante, cinq cristaux, canoe, corde et bottes conserves.

| Etape | Trace | Fin | Preuve |
| --- | --- | --- | --- |
| Boss et cristal | md-auto-v0292-d5-boss03 |116135|RAM entiere et PNG final exacts depuis le demarrage|
| Mecanisme173 vers174 | md-auto-v0292-d5-return-contact01 |116483|RAM entiere et PNG final exacts depuis le demarrage|
| Sortie49 | md-auto-v0292-d5-exit01 |117215|RAM entiere et PNG final exacts depuis le demarrage|

Le controleur du combat predit381 fenetres completes de RAM. Le controleur de sortie en predit12. Seul le coeur secondaire utilise des instantanes pour rechercher les commandes ; l'execution principale demarre a froid et n'importe pas d'etat. Les ecritures historiques d'aide concernent uniquement le compteur de blessures pendant les approches et sont consignees. La ROM distribuee ne contient pas cette aide. Ce parcours n'est donc pas une campagne complete sans assistance.

Un observateur de pile avant chaque instruction normale du68000, depuis l'image14 jusqu'a116135, trouve un minimumF798, au-dessus de la limite du tasF600 :408 octets de marge observee. Les en-tetes de l'allocateur restent valides et RAM/image finales correspondent au trace canonique. Cette observation ne constitue pas une borne pour les parcours suivants.

Le [rapport reproductible](d5_campaign_v0292_report.json) lie par SHA-256 les trois relectures et leurs controles, les manifestes d'aide, les captures et les outils. Commande de synthese : `tools/summarize_d5_campaign_v0292.py`. Le [jalon precedent](d5_supplies_v0292_report.json) contient14 autres relectures ; la [comparaison des bottes](boots_timing_v0292_report.json) contient96 cas controles PAL/NTSC.

Limites : aucune victoire source SMS contre ce boss n'est revendiquee. Ces preuves ne comparent pas toutes les images ni l'audio ou le rythme global. Les donjons6-10, la fin du jeu et la fidelite complete restent ouverts. Un calcul de route statique vers l'entree6 en8B n'aboutit pas encore ; il faut analyser les acces et mecanismes reels avant de prolonger la campagne.
