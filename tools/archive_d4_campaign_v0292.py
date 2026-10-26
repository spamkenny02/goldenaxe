"""Lossless D4 evidence freeze, with readback before generated cleanup."""
import json
from run_core import ROOT
from archive_lossless_evidence import freeze,sha

def main():
 report=json.loads((ROOT/'analysis/d4_campaign_v0292_report.json').read_bytes());canoe=json.loads((ROOT/'analysis/canoe_campaign_v0292_report.json').read_bytes());assert report['passed'] and canoe['passed'] and report['md_sha256']==canoe['md_sha256']==sha((ROOT/'gaw-megadrive.bin').read_bytes())
 prefix=json.loads((ROOT/'analysis/d4_campaign_v0292_worklog_prefix.json').read_bytes());assert sha((ROOT/'analysis/world_next.md').read_bytes()[:prefix['bytes']])==prefix['sha256']
 protected=[ROOT/'input/original.sms',ROOT/'gaw-megadrive.bin',ROOT/'gaw-title-megadrive.bin',*sorted((ROOT/'versions').glob('*/*.bin'))];assert len(protected)==295;before={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected}
 roots=[]
 for p in (ROOT/'validation/natural-dungeon-combat').iterdir():
  if p.is_dir() and 'v0292' in p.name and any(label in p.name for label in ['d4-a1-key','d4-canoe','d4-warp','d4-boss','d4-crystal','d4-exit']):roots.append(p)
 roots.extend(ROOT/'validation'/name for name in ['stack-v0292-d4-crystal-all','v0292-d4-drivers']);roots=sorted(set(roots));assert all(p.is_dir() for p in roots)
 paths=[p for root in roots for p in root.rglob('*') if p.is_file()]
 for proof in [report,canoe]:paths.extend(ROOT/name for name in proof['evidence'] if (ROOT/name).exists())
 paths.extend(p for p in (ROOT/'validation').iterdir() if p.is_file() and ('v0292' in p.name and any(s in p.name for s in ['d4','canoe'])))
 paths.extend(ROOT/'megadrive/out/release'/name for name in ['rom.bin','rom.out','symbol.txt'])
 names=['archive_d4_campaign_v0292.py','summarize_d4_campaign_v0292.py','validate_canoe_campaign_v0292.py','movement_reference.py','natural_dungeon_combat.py','natural_earth_passage.py','natural_combat_navigation.py','natural_combat_lookahead.py','natural_combat_beam.py','natural_boss_lookahead.py','natural_boss_side_planner.py','natural_boss_escape_planner.py','natural_boss_evasive_planner.py','natural_boss_cautious_planner.py','natural_exit_planner.py','assisted_boss_route.py','assisted_prefix.py','replay_assisted_prefix.py','rebase_natural_campaign.py','profile_playable_stack.py','archive_lossless_evidence.py','run_core.py']
 paths.extend(ROOT/'tools'/name for name in names)
 paths.extend(ROOT/name for name in ['README.md','megadrive/src/main.c','analysis/world_next.md','analysis/d4_campaign_v0292.md','analysis/d4_campaign_v0292_report.json','analysis/d4_campaign_v0292_worklog_prefix.json','analysis/canoe_campaign_v0292_report.json'])
 freeze(ROOT,ROOT/'analysis/canoe-campaign-v0292',paths,dict(version=292,md_sha256=report['md_sha256'],native_dungeon4_completed=True,source_boss_victory_validated=False,full_game_validated=False,protected_sha256=before,worklog_prefix=prefix),roots,cleanup=True)
 assert before=={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected}
 print('All295 original/ROM files unchanged')
 from validate_canoe_campaign_v0292 import main as validate
 from summarize_d4_campaign_v0292 import main as summarize
 for name,fn in [('analysis/canoe_campaign_v0292_report.json',validate),('analysis/d4_campaign_v0292_report.json',summarize)]:
  path=ROOT/name;raw=path.read_bytes();fn();assert path.read_bytes()==raw
 print('Canoe and D4 reports identical after verified cleanup')
if __name__=='__main__':main()
