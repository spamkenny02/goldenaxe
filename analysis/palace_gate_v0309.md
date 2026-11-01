# v0309 — travail video du palais

La scene6911-698A ajoutee en v0308 utilise maintenant la file world_video_pending
existante : bit2 pour la secousse,bit4 pour le miroir initial des32 colonnes.
Le chemin IRQ sans travail video conserve son test precedent. Aucun tampon
ou global supplementaire n'est reserve pour cette scene.

Le test controle huit/neuf cristaux SMS/MD reproduit exactement les289 images
et tous les changements de decalage. Les amplitudes8 a0 durent32 images
chacune ; avec huit cristaux,le passage reste ferme jusqu'a3500. Les transferts
se font avant le lecteur PSG. Rapport : palace_gate_v0309_report.json.
Commandes : tools/probe_palace_gate.py v0309-01,puis tools/validate_palace_gate.py
--trial v0309-01 --report analysis/palace_gate_v0309_report.json.

La reprise actuelle jusqu'au deuxieme donjon est controlee depuis le demarrage,
avec une relecture froide independante RAM65536/PNG. Le rejeu historique
complet et les prototypes de retiming echouent et ne sont pas credites.
Voir palace_rebase_v0309_report.json. La preuve des neuf cristaux reste v0306.
