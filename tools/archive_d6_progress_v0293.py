"""Freeze fifteen completed D6 approach stages; leave the live boss run alone."""
import json
from run_core import ROOT
from archive_lossless_evidence import freeze,sha
from summarize_d6_progress_v0293 import STAGES

def main():
 names=['analysis/d6_prefix_optimization_v0293_report.json','analysis/d6_progress_v0293_report.json'];reports=[json.loads((ROOT/n).read_bytes()) for n in names]
 assert all(r['passed'] and r['md_sha256']==sha((ROOT/'gaw-megadrive.bin').read_bytes()) for r in reports) and reports[-1]['official_cold_replays']==15
 protected=[ROOT/'input/original.sms',ROOT/'gaw-megadrive.bin',ROOT/'gaw-title-megadrive.bin',*sorted((ROOT/'versions').glob('*/*.bin'))];assert len(protected)==296
 before={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected}
 prefix=json.loads((ROOT/'analysis/d6_progress_v0293_worklog_prefix.json').read_bytes());assert sha((ROOT/'analysis/world_next.md').read_bytes()[:prefix['prefix_bytes']])==prefix['prefix_sha256']
 suffixes=[s for s,_ in STAGES]+['key01','key05','contact01','torches01','torches02','earth135-01','warp02','bell01','bell02','boss01']
 base=ROOT/'validation/natural-dungeon-combat';roots=[]
 for suffix in suffixes:
  stem='md-auto-v0293-d6-'+suffix
  roots.extend(p for p in base.iterdir() if p.is_dir() and (p.name==stem or p.name.startswith(stem+'-assisted-fixed-replay-')))
 roots.append(ROOT/'validation/v0293-d6-drivers');assert all(p.exists() for p in roots) and all('boss02' not in p.name for p in roots)
 paths=[p for folder in roots for p in folder.rglob('*') if p.is_file()]
 for r in reports:paths.extend(ROOT/n for n in r['evidence'] if (ROOT/n).exists())
 paths.extend(p for p in (ROOT/'validation').iterdir() if p.is_file() and p.name.startswith('v0293-d6-') and not p.name.startswith('v0293-d6-boss02'))
 tools=['archive_d6_progress_v0293.py','summarize_d6_progress_v0293.py','summarize_d6_prefix_optimization_v0293.py','natural_dungeon_combat.py','natural_contact_passage.py','natural_earth_passage.py','natural_combat_aim.py','assisted_boss_route.py','assisted_prefix.py','replay_assisted_prefix.py','rebase_natural_campaign.py','run_core.py','archive_lossless_evidence.py']
 paths.extend(ROOT/'tools'/n for n in tools)
 paths.extend(ROOT/n for n in names+['README.md','analysis/world_next.md','analysis/d6_progress_v0293.md','analysis/d6_progress_v0293_worklog_prefix.json','analysis/contact_script_reference.json','analysis/room_puzzles_reference.json','analysis/item_rewards_reference.json','megadrive/out/release/symbol.txt','megadrive/src/main.c'])
 freeze(ROOT,ROOT/'analysis/d6-progress-v0293',paths,dict(version=293,md_sha256=reports[0]['md_sha256'],scope_ends_before_boss=True,dungeon6_completed=False,live_boss_run_excluded=True,protected_sha256=before,worklog_prefix=prefix),roots,cleanup=True)
 assert before=={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected}
 from summarize_d6_prefix_optimization_v0293 import main as optimization
 from summarize_d6_progress_v0293 import main as progress
 for name,fn in zip(names,[optimization,progress]):
  p=ROOT/name;raw=p.read_bytes();fn();assert p.read_bytes()==raw
 print('All296 original/ROM files unchanged; both D6 summaries identical after verified cleanup; live boss02 untouched')

if __name__=='__main__':main()
