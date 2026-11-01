# Passage du palais — v0308

Le script SMS de la salle8B appelle6560,puis6911. Le portage executait la porte
du sixieme donjon mais omettait la seconde routine. Elle exige les neuf bits80
des cristaux et un heros actif,memorise C0F8=1 et le bit0 persistant de la salle.

La secousse comporte un premier VBlank,puis neuf amplitudes8 a0 pendant32
images chacune. Le signe suit C02F bit1,le bruit9E est demande sur DE06 toutes
les quatre images. Le decor et la scene de sprites se deplacent ensemble ; les
acteurs ne simulent pas pendant l'effet. Le HUD reste fixe. Le demi-plan cache
Mega Drive reprend les32 colonnes SMS pour reproduire le bouclage des bords.
Les transferts sont regroupes dans VBlank,avant le lecteur PSG.

Le test controle utilise une transition ordinaire9B->8B apres demarrage jouable,
avec huit ou neuf cristaux comme fixture explicite. SMS et MD memorisent
l'evenement a2834 et ouvrent a3123 :289 images. Chaque changement de decalage
est identique ; toutes les amplitudes durent32 images. Le cas huit cristaux
reste ferme. Le controle continue jusqu'a3500 sans relancer l'evenement.
Rapport : palace_gate_v0308_report.json ; outil : tools/probe_palace_gate.py.

La v0307 est une compilation intermediaire conservee. La v0308 retablit aussi
la bonne file sonore DE06 pour9E. Le passage est valide dans ce scenario isole,
pas encore dans le parcours reel. La campagne neuf cristaux est toujours
prouvee sur v0306 : ne pas attribuer son RAM/PNG a la nouvelle ROM. Il reste
la relecture,la hache doree,le dernier boss,la fin et les validations globales.
