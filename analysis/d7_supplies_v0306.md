# Approvisionnement et entree du septieme donjon sur v0306

La ROM reste v0306, SHA-256 `3a12380b86c193148d1cbd29d68a880901860cfb1c276aa96d61d2da16ac2c01`. Aucun changement natif ni nouvelle version n'est revendique pour ces preuves.

Depuis la sortie du sixieme donjon, les huit etapes retenues obtiennent les dons de 30 pieces en 7D et AC, coupent l'obstacle AC/1C avec la hache equipee, achetent une cle au marchand 2E pour 60 pieces, ouvrent la porte verrouillee de 1DB et recuperent une cle en 1CB. Le parcours atteint 168,818 images, 72/80 PV, 27 pieces et 1 cle. Les six cristaux, la cloche de glace, le canoe, la corde et les bottes sont conserves.

Chaque etape est relue depuis une nouvelle partie avec les boutons enregistres : les 65 536 octets de RAM et le PNG final sont identiques. Aucun import SRAM ni injection de PV, argent, objet, acteur ou progression. La protection d'approche est declaree et ne constitue pas une partie sans assistance.

La premiere approche du marchand et son achat sont exclus : l'outil de test effacait le delai naturel des degats de terrain, ce qui faisait perdre 60 PV au lieu de 4. La branche corrigee utilise explicitement `--preserve-floor-hurt`, arrive avec 76 PV et sert de prefixe aux etapes suivantes. La tentative de retour interrompue est conservee sans promotion. La ROM n'est pas modifiee par cette correction de configuration du test.

Le combat intermediaire 1B8/type78 et le boss principal 179/type67 ne sont pas encore entres sur ce parcours. L'assistance devra etre retiree avant le combat intermediaire. La mesure de pile de 442 octets reste celle du parcours precedent jusqu'a 162574 images ; elle n'est pas etendue par ces preuves. Le bateau, le septieme cristal, la fin, les sauvegardes et la fidelite globale restent a verifier.

Preuves : `analysis/d7_supplies_v0306_report.json`. Reproduction : `python tools/summarize_d7_supplies_v0306.py`. Les propositions v0304 fournissent seulement les destinations et parametres ; aucun etat de jeu v0304 n'est importe.
