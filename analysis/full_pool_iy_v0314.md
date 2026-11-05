# Cas limite IY des tirs, v314

Les corps de production du boss et de l’allocateur, compilés sans modification
en68000 dans un projet isolé, reproduisent les768 octets du cas SMS avec IY
en ROM. Avec IY imposé sur un enregistrement RAM,la SMS écrit aussi zéro dans
IY+0A lorsque le réservoir de projectiles est plein ; ce cas supplémentaire
n’est pas reproduit par l’API C actuelle.

Le cœur de trace lit le registre sans changer l’instruction ou son coût émulé.
Son contrôle direct conserve les8192 octets SMS exactement. Dans la boucle du
jeu original observée,avec un boss et huit projectiles73 contrôlés,IY n’est
pas injecté :les cinq écritures utilisent2558,en ROM,et sont donc ignorées.
Cette observation ne prouve pas l’invariant pour tous les appels réels.

Aucun correctif de production n’est justifié par ces seules mesures. Il reste
à examiner la provenance de IY dans d’autres contextes,notamment après les
actions du héros,avant de déclarer un défaut accessible ou de modifier la ROM.
Les scénarios contrôlés ne remplacent pas une rencontre atteinte naturellement.

Voir [comparaison native](full_pool_iy_native_comparison_v0314_report.json)
et [appelant SMS observé](full_pool_iy_callers_v0314_report.json).
Le relevé aligné corrige le libellé actor5_direction du premier essai non aligné.
