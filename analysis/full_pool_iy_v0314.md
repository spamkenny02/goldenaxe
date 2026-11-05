# Cas limite IY des tirs, v314

Le corps natif du boss et son allocateur reproduisent les768 octets du cas
SMS contrôlé avec IY en ROM. Un IY arbitrairement imposé sur une adresse RAM
peut produire une écriture supplémentaire dans la SMS ; cette possibilité
ne constitue pas une preuve d’un défaut accessible en jouant.

Le cœur de trace lit IY sans changer les instructions ni leurs cycles. Le
contrôle initial reproduit les8192 octets de RAM du cœur officiel. Les douze
premiers contextes couvraient repos, épée, Feu et Terre. Les cibles RAM vues
dans ces cas étaient déjà à zéro avant et après le tir.

La série corrigée ajoute33 contextes : mouvements de hache aux deux niveaux,
deuxième épée, remède, soin, potion, sélection de lanterne/cloche, sort d’écran
et hache lancée sur l’eau, à trois phases.27 activations sont vérifiées ;
les six sélections lanterne/cloche ne revendiquent pas leur effet contextuel.
Le sort d’écran est actif mais aucun tir n’apparaît pendant ses trois fenêtres.

Dans les30 cas où un tir se produit avec les huit places occupées, IY vaut
2550/2558 en ROM, ou C4B0. Les16 cas RAM écrivent dans C4BA, déjà nul et
encore nul à la fin du même cadre. Aucune différence nette sur cette cible
ne justifie donc un changement de production dans les scénarios mesurés.
Cela ne démontre pas l’invariant pour tous les appels ou une rencontre
naturelle. La ROM publiée reste identique.

Le premier essai de cette série utilisait à tort C08F pour le remède et
seulement24 PM pour le sort d’écran, qui en demande32. La seconde série
corrige C0BF et le budget magique ; les anciennes données restent archivées
mais ne sont pas des preuves d’activation de ces deux actions.

Voir [comparaison native](full_pool_iy_native_comparison_v0314_report.json),
[appelant original](full_pool_iy_callers_v0314_report.json),
[mesures corrigées](iy_item_contexts_corrected_v0314_report.json) et
[cibles avant/après](iy_item_context_target_v0314_report.json).
