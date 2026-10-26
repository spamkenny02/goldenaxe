"""Freeze D5 approach/key/Earth/boots evidence before generated cleanup."""
import json
from run_core import ROOT
from archive_lossless_evidence import freeze,sha

def main():
 reports=[json.loads((ROOT/name).read_bytes()) for name in ['analysis/d5_approach_v0292_report.json','analysis/d5_progress_v0292_report.json']]
 assert all(r['passed'] and r['md_sha256']==sha((ROOT/'gaw-megadrive.bin').read_bytes()) for r in reports)
 protected=[ROOT/'input/original.sms',ROOT/'gaw-megadrive.bin',ROOT/'gaw-title-megadrive.bin',*sorted((ROOT/'versions').glob('*/*.bin'))]
 assert len(protected)==295
 before={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected}
 prefix=json.loads((ROOT/'analysis/d5_progress_v0292_worklog_prefix.json').read_bytes())
 assert sha((ROOT/'analysis/world_next.md').read_bytes()[:prefix['bytes']])==prefix['sha256']
 roots=[]
 for family in ['natural-dungeon-route','natural-dungeon-combat']:
  roots.extend(p for p in (ROOT/'validation'/family).iterdir() if p.is_dir() and 'v0292-d5-' in p.name)
 roots.append(ROOT/'validation/v0292-d5-drivers');assert all(p.is_dir() for p in roots)
 paths=[p for root in roots for p in root.rglob('*') if p.is_file()]
 for r in reports:paths.extend(ROOT/name for name in r['evidence'] if (ROOT/name).exists())
 paths.extend(p for p in (ROOT/'validation').iterdir() if p.is_file() and 'v0292-d5-' in p.name)
 paths.extend((ROOT/'validation/natural-dungeon-route').glob('plan-door5-v0292-d5-*.json'))
 names=['archive_d5_progress_v0292.py','summarize_d5_approach_v0292.py','summarize_d5_progress_v0292.py','natural_dungeon_route.py','natural_dungeon_combat.py','natural_earth_passage.py','movement_reference.py','assisted_boss_route.py','assisted_prefix.py','replay_assisted_prefix.py','rebase_natural_campaign.py','run_core.py','archive_lossless_evidence.py']
 paths.extend(ROOT/'tools'/name for name in names)
 paths.extend(ROOT/name for name in ['README.md','analysis/world_next.md','analysis/d5_progress_v0292.md','analysis/d5_approach_v0292_report.json','analysis/d5_progress_v0292_report.json','analysis/d5_progress_v0292_worklog_prefix.json','megadrive/out/release/symbol.txt','megadrive/src/main.c'])
 freeze(ROOT,ROOT/'analysis/d5-progress-v0292',paths,dict(version=292,md_sha256=reports[0]['md_sha256'],dungeon5_completed=False,boots_acquired=True,protected_sha256=before,worklog_prefix=prefix),roots,cleanup=True)
 assert before=={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected}
 from summarize_d5_approach_v0292 import main as approach
 from summarize_d5_progress_v0292 import main as progress
 for name,fn in [('analysis/d5_approach_v0292_report.json',approach),('analysis/d5_progress_v0292_report.json',progress)]:
  path=ROOT/name;raw=path.read_bytes();fn();assert path.read_bytes()==raw
 print('All295 original/ROM files unchanged; both D5 reports identical after verified cleanup')

if __name__=='__main__':main()
