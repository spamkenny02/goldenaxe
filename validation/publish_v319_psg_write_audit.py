"""Publish corrected PSG evidence without changing frozen historical reports or ROMs."""
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'tools'))
from archive_lossless_evidence import sha

name = 'sms_psg_writes_v0319_report.json'
report = root / 'analysis' / name
data = json.loads(report.read_bytes())
assert data['audit_passed'] and not data['audio_timing_equivalence_passed']
release = root / 'versions/v0319-d3ea2a83'
assert sha((release / 'gaw-megadrive-v0319.bin').read_bytes()) == data['rom_sha256']
assert sha((root / 'gaw-megadrive.bin').read_bytes()) == data['rom_sha256']
(release / name).write_bytes(report.read_bytes())
index_path = root / 'versions/index.json'
index = json.loads(index_path.read_bytes())
entry = next(item for item in index if item['version'] == 319)
assert entry['sha256'] == data['rom_sha256']
assert not any(item['file'] == name for item in entry['reports'])
entry['reports'].append(dict(file=name, sha256=sha(report.read_bytes())))
index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
readme = root / 'README.md'
text = readme.read_text(encoding='utf-8')
before = '| Audio du démarrage | Huit registres PSG bruts identiques à la SMS sur 14000 frames par région, sans décalage | Instants d’écriture dans la frame, PCM et sons interactifs du reste du jeu |'
after = '| Audio du démarrage | Huit états PSG exposés identiques sur 14000 frames par région ; octets et ordre des écritures identiques dès le premier état sonore actif | Espacement des écritures différent dans la frame ; PCM et sons interactifs du reste du jeu |'
assert before in text
text = text.replace(before, after)
before = '- [PSG du démarrage face à la SMS](analysis/sms_psg_v0319_report.json) — 28000 frames comparées au total, sans écriture RAM ni import SRAM.'
after = '- [PSG et espacement des écritures face à la SMS](analysis/sms_psg_writes_v0319_report.json) — 28000 frames ; 31546 écritures musicales NTSC et 36915 PAL identiques par système. Les écarts d’initialisation et de timing restent documentés.'
assert before in text
text = text.replace(before, after)
needle = '\n## Sources et compilation\n'
addition = '''
Le relevé PSG initial appelait à tort les valeurs exposées « registres bruts » :
les volumes sont déjà décodés en amplitudes par l’émulateur. L’égalité des
huit états reste exacte ; le comptage corrigé donne 13739 frames actives
en NTSC et 13480 en PAL. Le nouveau relevé observe aussi les octets avant
décodage : quatre frames d’initialisation diffèrent par région, avant le
premier état actif. Ensuite les octets et leur ordre sont exacts, mais
l’espacement entre écritures diffère. Cette mesure confirme un travail
de synchronisation audio restant ; elle ne certifie pas les formes d’onde.
Le rapport historique est conservé, avec cet erratum explicite.
'''
assert needle in text
readme.write_text(text.replace(needle, '\n' + addition + needle), encoding='utf-8')
version_readme = release / 'README.md'
text = version_readme.read_text(encoding='utf-8')
text = text.replace('Les huit registres bruts correspondent à chaque frame de deux boucles',
                    'Les huit états PSG exposés correspondent à chaque frame de deux boucles')
text += '''
Erratum et mesure complémentaire : [octets PSG et espacement](../../analysis/sms_psg_writes_v0319_report.json).
Les volumes exposés sont des amplitudes décodées, zéro signifie muet ;
le précédent comptage d’activité était incorrect. Les états restent égaux.
Les octets et leur ordre correspondent dès la première frame sonore active
(23 NTSC, 20 PAL), avec quatre frames d’initialisation différentes par région.
L’espacement entre écritures reste différent : aucune équivalence PCM annoncée.
'''
version_readme.write_text(text, encoding='utf-8')
handoff = root / 'REPRISE_CODEX.md'
text = handoff.read_text(encoding='utf-8')
start = text.index('Dernière preuve : PSG du démarrage')
end = text.index('ÉTAT PRIORITAIRE :', start)
text = text[:start] + '''Dernière preuve : `analysis/sms_psg_writes_v0319_report.json`, archive
`analysis/v319-psg-write-spacing`. Observateur séparé avant décodage PSG,
aucune modification des cycles/états émulés ; ses 28000 états de fin de frame
reproduisent exactement ceux du précédent cœur. Aucun overflow. Les huit
états exposés SMS/MD restent égaux ; les volumes sont des amplitudes, pas
des nibbles d’atténuation. Erratum : ancien libellé « registres bruts » et
ancien comptage <15 incorrects ; le rapport historique est immuable.
Comptage corrigé :13739 frames actives NTSC,13480 PAL ; première23/20.
Quatre frames d’initialisation diffèrent dans chaque région, toutes avant
le premier état actif. Ensuite31546 écritures musicales NTSC et36915 PAL
par système : octets, nombre et ordre identiques chaque frame.
En revanche aucun des20028/23371 intervalles entre écritures consécutives
dans une même frame n’est exact. Médiane14980 ticks MD contre9405 SMS.
Les origines absolues ne sont pas alignées : ne pas appeler leur delta
un retard physique. Les intervalles dans la même frame annulent l’origine.
Ne pas retarder globalement la musique pour corriger une révélation vidéo.
Le reader natif calcule puis émet des listes par canal ; les intervalles
intercanaux sont souvent trop longs, ceux intraliste trop courts. Ajouter
seulement des attentes ne résoudra pas les deux. Étudier production anticipée
et livraison datée avec budget réel ; les APIs fast_timed existent mais
leur surcoût et workspace (~2560 octets) interdisent un remplacement aveugle
du workspace actuel scratch+D00..F05. Aucune ROM de production modifiée.
Scripts constructeurs et captures compressées archivés ; DLL diagnostic
locale sous work/genesis-plus-gx, hors dépôt. Job94890 terminal0.
Audit/archivage terminal0,7376066 octets générés supprimés après relecture,
6738531 nets libérés. Aucun ancien job à attendre.

''' + text[end:]
handoff.write_text(text, encoding='utf-8')
print('Corrected receipt attached; README/index/handoff updated; V319 ROM unchanged.')
