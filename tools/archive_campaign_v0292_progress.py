"""Freeze campaign evidence and prune only verified generated validation data."""
import json
from run_core import ROOT
from archive_lossless_evidence import freeze,sha

def main():
 report=json.loads((ROOT/'analysis/campaign_v0292_progress_report.json').read_bytes());assert report['passed'] and report['md_sha256']==sha((ROOT/'gaw-megadrive.bin').read_bytes())
 prefix=json.loads((ROOT/'analysis/campaign_v0292_worklog_prefix.json').read_bytes());assert sha((ROOT/'analysis/world_next.md').read_bytes()[:prefix['bytes']])==prefix['sha256']
 protected=[ROOT/'input/original.sms',ROOT/'gaw-megadrive.bin',ROOT/'gaw-title-megadrive.bin',*sorted((ROOT/'versions').glob('*/*.bin'))];assert len(protected)==295
 before={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected};roots=[]
 for family in ['natural-dungeon-route','natural-dungeon-combat','natural-rope-route','natural-service-route']:
  roots.extend(p for p in (ROOT/'validation'/family).iterdir() if p.is_dir() and 'v0292' in p.name)
 roots.extend(p for p in (ROOT/'validation').iterdir() if p.is_dir() and p.name=='v0292-progress-drivers');roots=sorted(set(roots));paths=[p for root in roots for p in root.rglob('*') if p.is_file()]
 paths.extend(ROOT/name for name in report['evidence'] if (ROOT/name).exists())
 cross=json.loads((ROOT/'analysis/campaign_earth_v0292_report.json').read_bytes());paths.extend(ROOT/name for name in cross['evidence'] if (ROOT/name).exists())
 paths.extend(p for p in (ROOT/'validation').iterdir() if p.is_file() and 'v0292' in p.name)
 paths.extend(ROOT/'megadrive/out/release'/n for n in ['rom.bin','rom.out','symbol.txt'])
 names=['run_core.py','assisted_boss_route.py','assisted_prefix.py','natural_dungeon_combat.py','natural_dungeon_route.py','natural_house_service.py','natural_earth_passage.py','rebase_assisted_campaign.py','rebase_natural_campaign.py','replay_assisted_prefix.py','validate_campaign_input_scheduler.py','validate_campaign_earth_v0292.py','summarize_campaign_v0292_progress.py','archive_campaign_v0292_progress.py','archive_lossless_evidence.py']
 paths.extend(ROOT/'tools'/n for n in names)
 paths.extend(ROOT/n for n in ['megadrive/src/main.c','README.md','analysis/world_next.md','analysis/campaign_v0292_progress.md','analysis/campaign_v0292_progress_report.json','analysis/campaign_v0292_worklog_prefix.json','analysis/campaign_v0292_input_scheduler_report.json','analysis/campaign_earth_v0292_report.json'])
 freeze(ROOT,ROOT/'analysis/campaign-v0292-progress',paths,dict(version=292,md_sha256=report['md_sha256'],full_game_validated=False,protected_sha256=before,worklog_prefix=prefix),roots,cleanup=True)
 assert before=={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected}
 print('All295 original/ROM files unchanged')
 from validate_campaign_earth_v0292 import main as earth
 from summarize_campaign_v0292_progress import main as summarize
 for name,fn in [('analysis/campaign_earth_v0292_report.json',earth),('analysis/campaign_v0292_progress_report.json',summarize)]:
  path=ROOT/name;raw=path.read_bytes();fn();assert path.read_bytes()==raw
 print('Consolidated evidence identical after verified cleanup')
if __name__=='__main__':main()
