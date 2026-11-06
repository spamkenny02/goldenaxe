"""Publish the measured sprite-copy trial without replacing the stable ROM."""
import difflib
import json
from pathlib import Path
import shutil
import sys
sys.path.insert(0,'tools')
from archive_lossless_evidence import freeze,sha

ROOT=Path(__file__).resolve().parents[1]
work=ROOT/'validation/v318-clone-rows01'
timing=json.loads((work/'report.json').read_bytes())
sprites=json.loads((work/'physical-sprites.json').read_bytes())
ntsc=json.loads((work/'ntsc-profile-report.json').read_bytes())
assert sprites['passed'] and ntsc['passed']
rom=work/'out/release/rom.bin';raw=rom.read_bytes();digest=sha(raw)
candidate=next(r for r in timing['results'] if r['tag']=='candidate')
assert candidate['rom_sha256']==digest==sprites['md_sha256']
frames=candidate['simulation_frames']
dest=ROOT/f'versions/candidates/c0045-{digest[:8]}'
assert not dest.exists()
dest.mkdir(parents=True)
shutil.copyfile(rom,dest/'gaw-megadrive-c0045.bin')
shutil.copyfile(work/'out/release/symbol.txt',dest/'symbol.txt')
old=(ROOT/'megadrive/src/main.c').read_text();new=(work/'src/main.c').read_text()
(dest/'source.patch').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/megadrive/src/main.c',tofile='b/megadrive/src/main.c')))
paths=[ROOT/'validation/build_sprite_clone_rows_trial.py',Path(__file__).resolve(),work/'source.patch',work/'build.log',work/'report.json',work/'physical-sprites.json',work/'ntsc-profile-report.json']
paths += [work/n for n in ['timing.py','physical_sprites.py','ntsc_prefix.py']]
for tag in ['baseline','candidate']:
    paths += list((work/tag).glob('*'))
physical=ROOT/'validation/sprite-mask-cache-gameplay-clone-rows01'
paths += [p for p in physical.rglob('*') if p.is_file()]
meta=dict(candidate='c0045',rom_sha256=digest,pal_simulation_frames=frames,
          first_game_state_difference=timing['first_difference_frames'][:1],
          physical_sprite_frames=sum(c['physical_sprite_frames'] for c in sprites['cases']),
          ntsc_opening_exact=ntsc['passed'],stable_rom_unchanged=True,
          additional_pal_updates_over_c0044=False,
          limits=['Controlled sprite fixtures and recorded PAL/NTSC inputs; complete adaptive campaign and general SMS timing remain unverified.'])
freeze(ROOT,ROOT/'analysis/c0045-clone-rows',paths,meta,[work,physical])
check=int.from_bytes(raw[0x18e:0x190],'big')
recovered=', '.join(str(f) for f in [80001,80003] if f in frames) or 'aucune'
(dest/'README.md').write_text(f'''# c0045 — Copie des lignes de sprites

Aperçu de développement de 2 Mio, basé sur c0044. Le choix entre RAM et
VDP se fait une seule fois pour les huit lignes ; les lignes RAM masquées
ne sont plus lues. Les lectures VDP restent effectuées dans leur ordre.

Sur la salve PAL mesurée, mises à jour récupérées parmi 80 001 et 80 003 :
{recovered}. Aucune mise à jour supplémentaire par rapport à c0044 :
le saut à 80 001 reste présent. Premier écart des champs de jeu avec la V318 :
{timing['first_difference_frames'][:1]}. Un écart de chronologie ne prouve
pas à lui seul la fidélité à la Master System.

Les 108 images de sprites physiques des douze scénarios contrôlés
concordent avec la V318. Le début NTSC jusqu’à 7 710 concorde sur les champs
de jeu comparés. Parcours complet et fidélité audio/vidéo restent à vérifier.
La V318 reste la version de référence.

Checksum : {check:04X}. SHA-256 : `{digest}`.

- [ROM c0045](gaw-megadrive-c0045.bin)
- [Patch source](source.patch)
- [Mesures et captures](../../../analysis/c0045-clone-rows/manifest.json)
''')
readme=ROOT/'README.md';s=readme.read_text()
anchor='<!-- ROM-RELEASE:END -->'
s=s.replace(anchor,anchor+f'\n\nNouvel aperçu [c0045]({dest.relative_to(ROOT).as_posix()}/README.md) :\ncopie des lignes de sprites optimisée, mesures ciblées disponibles ;\nla V318 reste la version de référence.',1)
readme.write_text(s)
print(json.dumps(meta,indent=2),flush=True)
print(dest.relative_to(ROOT).as_posix(),flush=True)
