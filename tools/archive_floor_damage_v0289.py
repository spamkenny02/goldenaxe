"""Freeze v289 dangerous-floor fixtures and natural D1 proof before cleanup."""
import json
from run_core import ROOT
from archive_lossless_evidence import freeze,sha

def main():
 report=json.loads((ROOT/'analysis/floor_damage_v0289_report.json').read_bytes());assert report['passed'] and report['md_sha256']==sha((ROOT/'gaw-megadrive.bin').read_bytes())
 prefix=json.loads((ROOT/'analysis/floor_damage_v0289_worklog_prefix.json').read_bytes());assert sha((ROOT/'analysis/world_next.md').read_bytes()[:prefix['bytes']])==prefix['sha256']
 protected=[ROOT/'input/original.sms',ROOT/'gaw-megadrive.bin',ROOT/'gaw-title-megadrive.bin',*sorted((ROOT/'versions').glob('*/*.bin'))];assert len(protected)==292
 before={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected};roots=[]
 for family in ['natural-dungeon-route','natural-dungeon-combat']:
  roots.extend(p for p in (ROOT/'validation'/family).glob('*v0289*') if p.is_dir())
 for pattern in ['floor-damage-v0289*','terrain-walk-v0289*','rope-motion-v0289*','stack-v0289-d1-all']:
  roots.extend(p for p in (ROOT/'validation').glob(pattern) if p.is_dir())
 roots=sorted(set(roots));paths=[p for d in roots for p in d.rglob('*') if p.is_file()]
 paths.extend(ROOT/n for n in report['evidence'] if (ROOT/n).exists())
 paths.extend(p for p in (ROOT/'validation').glob('*.log') if 'v0289' in p.name)
 paths.extend(ROOT/'megadrive/out/release'/n for n in ['rom.bin','rom.out','symbol.txt'])
 paths.extend(ROOT/'megadrive/src'/n for n in ['main.c','hero_walk_tables.c'])
 names=['validate_floor_damage_game.py','validate_terrain_walk_game.py','validate_rope_motion_game.py','summarize_floor_damage_v0289.py','archive_floor_damage_v0289.py','rebase_natural_campaign.py','run_core.py','profile_playable_stack.py','archive_lossless_evidence.py']
 paths.extend(ROOT/'tools'/n for n in names)
 paths.extend(ROOT/n for n in ['build.ps1','README.md','analysis/world_next.md','analysis/floor_damage_v0289.md','analysis/floor_damage_v0289_report.json','analysis/floor_damage_v0289_worklog_prefix.json','analysis/floor_damage_v0289_game_report.json','analysis/terrain_walk_v0289_game_report.json','analysis/rope_motion_v0289_game_report.json'])
 manifest=freeze(ROOT,ROOT/'analysis/floor-damage-v0289',paths,dict(md_sha256=report['md_sha256'],full_game_validated=False,numbered_roms_preserved=289,protected_sha256=before),roots,cleanup=True)
 for name,digest in before.items():assert sha((ROOT/name).read_bytes())==digest
 from summarize_floor_damage_v0289 import main as summarize
 path=ROOT/'analysis/floor_damage_v0289_report.json';raw=path.read_bytes();summarize();assert path.read_bytes()==raw
 print('Verified generated cleanup bytes:',sum(v['bytes'] for v in manifest['removed_verified_generated']))
if __name__=='__main__':main()
