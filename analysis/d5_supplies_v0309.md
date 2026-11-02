# Ravitaillement et seconde moitié de D5 sur v0309

Le parcours reprend la [sortie après les bottes](d5_progress_v0309.md).
Le programme du jeu reste la ROM v0309 inchangée, SHA-256
`7270576d6eeb2aee641776a3e364f2f3f320711d70bb91a566d7578161261049`.

| Étape | Image finale | Salle | PV | Cornes | Clés |
| --- | --- | --- | --- | --- | --- |
| Don A1 | 124513 | A1 | 60/64 | 46 | 0 |
| Don B4 | 125953 | B4 | 60/64 | 76 | 0 |
| Achat et soin | 127327 | 94 | 64/64 | 16 | 1 |
| Retour dans D5 | 130108 | 186 | 64/64 | 16 | 1 |
| Terre et portail | 136029 | 162 | 64/64 | 16 | 1 |
| Mécanisme et passage | 136995 | 172 | 64/64 | 16 | 1 |

Les deux donateurs donnent chacun 30 cornes, de 16 à 46 puis 76.
Le marchand prélève exactement 60 cornes pour la clé ; son soin gratuit
fait passer les PV de 60 à 64. Les commandes de dialogue et de sélection
sont normales, sans modification d'argent, de clés ou de PV par le test.

Au retour, Terre détruit le rocher 44 de 153 en consommant huit PM. Le vrai
portail conduit à 162. Le mécanisme de cette salle s'active par une commande
UP, avec l'option permettant son utilisation pendant le combat, et le héros
traverse vers 172. Les quatre cristaux, Feu, Terre, épée longue, bottes,
canoë et corde sont conservés ; la hache reste sélectionnée à ce point.

L'audit couvre les treize étapes depuis l'entrée initiale de D5, y compris
la clé, le premier passage Terre et les bottes déjà documentés. Chaque étape
a une relecture fixe depuis le démarrage, exacte sur les 65536 octets de RAM
et le PNG final. Le HUD physique après les bottes est également vérifié.

Les écritures de test restent les seules protections d'approche déclarées
sur `hero_hurt`. Aucun import de SRAM, ressource, possession, acteur ou
progression n'est utilisé. Le cinquième épisode attend toujours le boss de
163 ; ce rapport ne prétend pas avoir remporté son combat ni obtenu le cristal.

Voir le [rapport](d5_supplies_v0309_report.json) et
l'[audit reproductible](../tools/summarize_d5_supplies_v0309.py).
Les sources figées de cette étape utilisent
`validation/v0309-d5-sources/supplies_source_index.json` ; l'index original
de la préparation est conservé inchangé. La campagne ultérieure et la
fidélité globale SMS restent à vérifier.
