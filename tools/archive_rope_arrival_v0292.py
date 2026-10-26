"""Freeze verified rope evidence before deleting only generated validation files."""
import json
from run_core import ROOT
from archive_lossless_evidence import freeze,sha

def main():
 report=json.loads((ROOT/'analysis/rope_arrival_v0292_report.json').read_bytes());assert report['passed'] and report['md_sha256']==sha((ROOT/'gaw-megadrive.bin').read_bytes())
 prefix=json.loads((ROOT/'analysis/rope_arrival_v0292_worklog_prefix.json').read_bytes());assert sha((ROOT/'analysis/world_next.md').read_bytes()[:prefix['bytes']])==prefix['sha256']
 protected=[ROOT/'input/original.sms',ROOT/'gaw-megadrive.bin',ROOT/'gaw-title-megadrive.bin',*sorted((ROOT/'versions').glob('*/*.bin'))];assert len(protected)==295
 before={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected};roots=[]
 for family in ['natural-dungeon-route','natural-dungeon-combat','natural-rope-route','natural-service-route']:
  roots.extend(p for p in (ROOT/'validation'/family).iterdir() if p.is_dir() and any(s in p.name for s in ['v0291','v0292']))
 roots.extend(p for p in (ROOT/'validation').iterdir() if p.is_dir() and (p.name.startswith(('rope-arrival-','stack-v0292','v0291-campaign-build'))))
 roots=sorted(set(roots));paths=[p for root in roots for p in root.rglob('*') if p.is_file()]
 paths.extend(ROOT/n for n in report['evidence'] if (ROOT/n).exists());paths.extend(p for p in (ROOT/'validation').iterdir() if p.is_file() and any(s in p.name for s in ['v0291','v0292']))
 paths.extend(ROOT/'megadrive/out/release'/n for n in ['rom.bin','rom.out','symbol.txt'])
 names=['rebase_assisted_campaign.py','profile_acquired_rope_climb.py','validate_rope_arrival.py','validate_rope_arrival_game.py','validate_rope_arrival_publication.py','summarize_rope_arrival_v0292.py','archive_rope_arrival_v0292.py','natural_dungeon_route.py','natural_dungeon_combat.py','natural_house_service.py','assisted_prefix.py','assisted_boss_route.py','replay_assisted_prefix.py','rebase_natural_campaign.py','replay_natural_campaign.py','profile_playable_stack.py','archive_lossless_evidence.py','run_core.py']
 paths.extend(ROOT/'tools'/n for n in names)
 paths.extend(ROOT/n for n in ['README.md','build.ps1','analysis/world_next.md','analysis/rope_arrival_v0292.md','analysis/rope_arrival_v0292_report.json','analysis/rope_arrival_v0292_worklog_prefix.json'])
 freeze(ROOT,ROOT/'analysis/rope-arrival-v0292',paths,dict(version=292,rom_sha256=report['md_sha256'],protected=before,worklog_prefix=prefix),roots,cleanup=True)
 assert before=={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected}
 print('All295 protected original/ROM files unchanged')
if __name__=='__main__':main()
