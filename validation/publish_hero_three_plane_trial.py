"""Publish c0046 with measured cost and explicit campaign divergence limits."""
import difflib
import json
from pathlib import Path
import shutil
import sys
sys.path.insert(0,'tools')
from archive_lossless_evidence import freeze,sha

ROOT=Path(__file__).resolve().parents[1]
work=ROOT/'validation/v318-hero-three-plane02'
load=lambda name:json.loads((work/name).read_bytes())
timing=load('report.json');cost=load('hero_pattern_cost_report.json')
sprites=load('physical-sprites.json');walking=load('ground_walk_report.json')
ntsc=load('ntsc-fault-report.json')
raw=(work/'out/release/rom.bin').read_bytes();digest=sha(raw)
assert cost['passed'] and sprites['passed'] and len(walking['cases'])==16
assert cost['md_sha256']==sprites['md_sha256']==walking['md_sha256']==digest
candidate=next(r for r in timing['results'] if r['tag']=='candidate')
assert candidate['rom_sha256']==digest
assert all(f in candidate['simulation_frames'] for f in [80001,80003])
assert ntsc['first_differences'][0]['frame']==3396
assert all(case['hero_pose_and_packed_pixels_exact'] for case in cost['cases'])
dest=ROOT/f'versions/candidates/c0046-{digest[:8]}';assert not dest.exists()
dest.mkdir(parents=True)
(dest/'gaw-megadrive-c0046.bin').write_bytes(raw)
shutil.copyfile(work/'out/release/symbol.txt',dest/'symbol.txt')
old=(ROOT/'megadrive/src/main.c').read_text();new=(work/'src/main.c').read_text()
(dest/'source.patch').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/megadrive/src/main.c',tofile='b/megadrive/src/main.c')))
paths=[ROOT/'validation/build_hero_three_plane_trial.py',Path(__file__).resolve()]
paths += [p for p in work.iterdir() if p.is_file() and p.suffix in ['.py','.json','.patch']]
for name in ['baseline','candidate','ntsc-fault-v0318','ntsc-fault-dungeon-patterns']:
    paths += [p for p in (work/name).glob('*') if p.is_file()]
additional=[ROOT/'validation/sprite-mask-cache-gameplay-hero-three-plane02',
            ROOT/'validation/hero-three-plane-pattern-cost-01']
additional += list((ROOT/'validation').glob('hero-three-plane-ground-walk-*'))
for folder in additional:
    paths += [p for p in folder.rglob('*') if p.is_file() and p.suffix not in ['.out']]
meta=dict(candidate='c0046',rom_sha256=digest,hero_pattern_cost_reduction_percent=44.79,
    pal_updates_recovered=[80001,80003],physical_sprite_frames=108,
    hero_pose_pattern_frames_per_region=561,sms_ground_walk_cases=16,
    ntsc_first_game_field_divergence=3396,pal_first_game_field_divergence=timing['first_difference_frames'][0],
    stable_rom_unchanged=True,full_candidate_campaign_verified=False,
    limits=['Old campaign inputs diverge after additional simulation updates. PAL burst endpoints are not the same actor trajectory as the old recording. Complete natural SMS timing, audio and candidate campaign remain open.'])
freeze(ROOT,ROOT/'analysis/c0046-hero-three-plane',paths,meta,[work,*additional])
checksum=int.from_bytes(raw[0x18e:0x190],'big')
(dest/'README.md').write_text(f'''# c0046 — Préparation des motifs du héros

Aperçu de développement de 2 Mio, basé sur c0044. Les petites copies de
trois octets dans la préparation des motifs du héros deviennent des
écritures directes. L’atlas RAM des ennemis de c0044 reste présent.

Le coût médian des nouvelles poses passe de 123060 à 67942 cycles maîtres,
soit une réduction de 44,79 %, dans les deux régions. Les poses et motifs
concordent sur 561 images par région ; 108 images de sprites physiques
concordent aussi. Les 16 essais de marche contrôlés face à la Master System
passent : quatre directions, vitesse normale et bottes, PAL et NTSC.

L’ancien rejeu PAL exécute désormais la simulation à 80001 et 80003,
deux images sautées par la V318. Sa première divergence de champs de jeu
se situe toutefois à {timing['first_difference_frames'][0]}, avant cette
salve : on ne prétend pas conserver l’ancienne trajectoire des acteurs.
En NTSC, la première divergence est à 3396 : c0046 exécute la simulation
alors que la V318 la saute. Les anciennes commandes de campagne doivent
être adaptées. Le parcours complet de c0046 et la fidélité générale SMS
ne sont pas validés. La V318 reste la référence.

Checksum : {checksum:04X}. SHA-256 : `{digest}`.

- [ROM c0046](gaw-megadrive-c0046.bin)
- [Patch source](source.patch)
- [Mesures, pilotes et captures](../../../analysis/c0046-hero-three-plane/manifest.json)
- [Profil qui motive le changement](../../../analysis/c0044_burst_stages.md)
''')
readme=ROOT/'README.md';text=readme.read_text();anchor='<!-- ROM-RELEASE:END -->'
text=text.replace(anchor,anchor+f'\n\nNouvel aperçu [c0046]({dest.relative_to(ROOT).as_posix()}/README.md) :\npréparation des motifs du héros mesurée 44,79 % moins coûteuse ;\nmarche contrôlée conforme SMS, parcours complet de cet aperçu à valider.',1)
readme.write_text(text)
print(dest.relative_to(ROOT).as_posix(),flush=True)
print(json.dumps(meta,indent=2),flush=True)
