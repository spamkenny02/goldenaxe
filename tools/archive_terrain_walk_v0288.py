"""Freeze historical D3 discovery and v288 movement fix before verified cleanup."""
import json
from run_core import ROOT
from archive_lossless_evidence import freeze,sha

def main():
 report=json.loads((ROOT/'analysis/terrain_walk_v0288_report.json').read_bytes());old=json.loads((ROOT/'analysis/d3_rope_v0287_report.json').read_bytes());assert report['passed'] and old['passed'] and report['md_sha256']==sha((ROOT/'gaw-megadrive.bin').read_bytes())
 prefix=json.loads((ROOT/'analysis/terrain_walk_v0288_worklog_prefix.json').read_bytes());assert sha((ROOT/'analysis/world_next.md').read_bytes()[:prefix['bytes']])==prefix['sha256']
 protected=[ROOT/'input/original.sms',ROOT/'gaw-megadrive.bin',ROOT/'gaw-title-megadrive.bin',*sorted((ROOT/'versions').glob('*/*.bin'))];assert len(protected)==291
 before={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected};roots=[]
 for family,patterns in [('natural-dungeon-route',['*v0287-d3*','*v0287-source-d4*','*v0288*']),('natural-dungeon-combat',['*v0287-d3*','*v0287-source-d4*','*v0288*']),('natural-rope-route',['md-v0287-rope41*'])]:
  for pattern in patterns:roots.extend(p for p in (ROOT/'validation'/family).glob(pattern) if p.is_dir())
 for pattern in ['v0287-d3-build','terrain-walk-v0288*','rope-motion-v0287*','rope-motion-v0288*','stack-v0287-d3-rope-all','stack-v0288-d1-all']:
  roots.extend(p for p in (ROOT/'validation').glob(pattern) if p.is_dir())
 roots=sorted(set(roots));paths=[p for d in roots for p in d.rglob('*') if p.is_file()]
 for r in [report,old]:paths.extend(ROOT/n for n in r['evidence'] if (ROOT/n).exists())
 paths.extend(p for p in (ROOT/'validation').glob('*.log') if any(v in p.name for v in ['v0287-d3','v0287-source-d4','v0287-md-rope','v0288','rope-motion-v0287']))
 paths.extend(ROOT/'megadrive/out/release'/n for n in ['rom.bin','rom.out','symbol.txt'])
 paths.extend(ROOT/'megadrive/src'/n for n in ['main.c','hero_walk_tables.c','source_magic_rope.c','source_magic_rope.h'])
 names=['assisted_boss_route.py','natural_dungeon_route.py','natural_rope_route.py','natural_boss_evasive_planner.py','natural_exit_planner.py','profile_rope_traversal.py','generate_hero_walk_tables.py','validate_terrain_walk_game.py','validate_rope_motion_game.py','summarize_d3_rope_v0287.py','summarize_terrain_walk_v0288.py','archive_terrain_walk_v0288.py','summarize_campaign_v0287_progress.py','rebase_natural_campaign.py','run_core.py','profile_playable_stack.py']
 paths.extend(ROOT/'tools'/n for n in names)
 paths.extend(ROOT/n for n in ['build.ps1','README.md','analysis/world_next.md','analysis/d3_rope_v0287.md','analysis/d3_rope_v0287_report.json','analysis/rope_motion_v0287_report.json','analysis/terrain_walk_v0288.md','analysis/terrain_walk_v0288_report.json','analysis/terrain_walk_v0288_worklog_prefix.json','analysis/terrain_walk_v0288_game_report.json','analysis/rope_motion_v0288_game_report.json'])
 manifest=freeze(ROOT,ROOT/'analysis/terrain-walk-v0288',paths,dict(md_sha256=report['md_sha256'],historical_md_sha256=old['md_sha256'],full_game_validated=False,numbered_roms_preserved=288,protected_sha256=before),roots,cleanup=True)
 for name,digest in before.items():assert sha((ROOT/name).read_bytes())==digest
 from summarize_d3_rope_v0287 import main as summarize_old
 from summarize_terrain_walk_v0288 import main as summarize_new
 for path,fn in [(ROOT/'analysis/d3_rope_v0287_report.json',summarize_old),(ROOT/'analysis/terrain_walk_v0288_report.json',summarize_new)]:
  raw=path.read_bytes();fn();assert path.read_bytes()==raw
 print('Verified generated cleanup bytes:',sum(v['bytes'] for v in manifest['removed_verified_generated']))
if __name__=='__main__':main()
