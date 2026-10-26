"""Freeze current D5 campaign and movement evidence before verified cleanup."""
import json
from run_core import ROOT
from archive_lossless_evidence import freeze,sha

def main():
 report_names=['analysis/boots_timing_v0292_report.json','analysis/d5_supplies_v0292_report.json','analysis/d5_campaign_v0292_report.json']
 reports=[json.loads((ROOT/n).read_bytes()) for n in report_names]
 assert all(r['passed'] and r['md_sha256']==sha((ROOT/'gaw-megadrive.bin').read_bytes()) for r in reports)
 assert reports[-1]['native_dungeon5_completed']
 protected=[ROOT/'input/original.sms',ROOT/'gaw-megadrive.bin',ROOT/'gaw-title-megadrive.bin',*sorted((ROOT/'versions').glob('*/*.bin'))]
 assert len(protected)==295
 before={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected}
 prefix=json.loads((ROOT/'analysis/d5_supplies_v0292_worklog_prefix.json').read_bytes())
 assert sha((ROOT/'analysis/world_next.md').read_bytes()[:prefix['prefix_bytes']])==prefix['prefix_sha256']
 roots=[]
 for family in ['natural-dungeon-route','natural-dungeon-combat','natural-service-route']:
  roots.extend(p for p in (ROOT/'validation'/family).iterdir() if p.is_dir() and 'v0292-d5-' in p.name)
 roots.extend(ROOT/'validation'/name for name in ['v0292-d5-boss-drivers','terrain-walk-v0292-d5-boots01','stack-v0292-d5-crystal-all'])
 assert all(p.is_dir() for p in roots)
 paths=[p for folder in roots for p in folder.rglob('*') if p.is_file()]
 for r in reports:paths.extend(ROOT/n for n in r['evidence'] if (ROOT/n).exists())
 paths.extend(p for p in (ROOT/'validation').iterdir() if p.is_file() and 'v0292-d5-' in p.name)
 paths.extend((ROOT/'validation/natural-dungeon-route').glob('plan-*-v0292-d5-*.json'))
 names=['archive_d5_campaign_v0292.py','summarize_boots_timing_v0292.py','summarize_d5_supplies_v0292.py','summarize_d5_campaign_v0292.py','natural_dungeon_route.py','natural_dungeon_combat.py','natural_earth_passage.py','natural_contact_passage.py','natural_merchant_purchase.py','natural_house_service.py','natural_combat_navigation.py','natural_boss_evasive_planner.py','natural_boss_escape_planner.py','natural_boss_side_planner.py','natural_exit_planner.py','movement_reference.py','assisted_boss_route.py','assisted_prefix.py','replay_assisted_prefix.py','rebase_natural_campaign.py','run_core.py','archive_lossless_evidence.py','profile_playable_stack.py']
 paths.extend(ROOT/'tools'/n for n in names)
 paths.extend(ROOT/n for n in report_names+['README.md','analysis/world_next.md','analysis/d5_supplies_v0292.md','analysis/d5_campaign_v0292.md','analysis/d5_supplies_v0292_worklog_prefix.json','analysis/terrain_walk_v0292_game_report.json','megadrive/out/release/symbol.txt','megadrive/src/main.c'])
 freeze(ROOT,ROOT/'analysis/d5-campaign-v0292',paths,dict(version=292,md_sha256=reports[0]['md_sha256'],native_dungeon5_completed=True,source_boss_victory_validated=False,protected_sha256=before,worklog_prefix=prefix),roots,cleanup=True)
 assert before=={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected}
 from summarize_boots_timing_v0292 import main as boots
 from summarize_d5_supplies_v0292 import main as supplies
 from summarize_d5_campaign_v0292 import main as campaign
 for name,fn in zip(report_names,[boots,supplies,campaign]):
  p=ROOT/name;raw=p.read_bytes();fn();assert p.read_bytes()==raw
 print('All295 original/ROM files unchanged; all three new summaries identical after verified cleanup')

if __name__=='__main__':main()
