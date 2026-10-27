"""Freeze source bridge correction and campaign proofs, then verified cleanup."""
import json
from run_core import ROOT
from archive_lossless_evidence import freeze,sha

def main():
 report=json.loads((ROOT/'analysis/crystal_bridge_v0293_report.json').read_bytes());assert report['passed'] and report['md_sha256']==sha((ROOT/'gaw-megadrive.bin').read_bytes())
 protected=[ROOT/'input/original.sms',ROOT/'gaw-megadrive.bin',ROOT/'gaw-title-megadrive.bin',*sorted((ROOT/'versions').glob('*/*.bin'))];assert len(protected)==296
 before={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected}
 prefix=json.loads((ROOT/'analysis/crystal_bridge_v0293_worklog_prefix.json').read_bytes());assert sha((ROOT/'analysis/world_next.md').read_bytes()[:prefix['prefix_bytes']])==prefix['prefix_sha256']
 roots=[p for p in (ROOT/'validation').iterdir() if p.is_dir() and (p.name.startswith('crystal-bridge-') and 'v0293' in p.name or p.name=='stack-v0293-d5-bridge-all')]
 for family in ['natural-dungeon-combat','natural-dungeon-route']:
  roots.extend(p for p in (ROOT/'validation'/family).iterdir() if p.is_dir() and 'v0293-' in p.name)
 paths=[p for folder in roots for p in folder.rglob('*') if p.is_file()]
 paths.extend(ROOT/n for n in report['evidence'] if (ROOT/n).exists())
 paths.extend(p for p in (ROOT/'validation').iterdir() if p.is_file() and p.name.startswith('v0293-'))
 paths.extend((ROOT/'validation/natural-dungeon-route').glob('plan-*-v0293-*.json'))
 names=['archive_crystal_bridge_v0293.py','summarize_crystal_bridge_v0293.py','validate_crystal_bridge_policy.py','validate_crystal_bridge_game.py','validate_crystal_bridge_publication.py','rebase_assisted_campaign.py','rebase_natural_campaign.py','replay_assisted_prefix.py','replay_natural_campaign.py','assisted_boss_route.py','assisted_prefix.py','natural_dungeon_route.py','run_core.py','profile_playable_stack.py','archive_lossless_evidence.py']
 paths.extend(ROOT/'tools'/n for n in names)
 paths.extend(ROOT/n for n in ['README.md','analysis/world_next.md','analysis/crystal_bridge_v0293.md','analysis/crystal_bridge_v0293_report.json','analysis/crystal_bridge_policy_v0293_report.json','analysis/crystal_bridge_game_v0293-current01_report.json','analysis/crystal_bridge_game_v0293-baseline01_report.json','analysis/crystal_bridge_publication_v0293_report.json','analysis/crystal_bridge_v0293_worklog_prefix.json','megadrive/src/main.c','megadrive/src/source_crystal_bridge.c','megadrive/src/source_crystal_bridge.h','megadrive/out/release/symbol.txt'])
 freeze(ROOT,ROOT/'analysis/crystal-bridge-v0293',paths,dict(version=293,md_sha256=report['md_sha256'],dungeon6_entrance_reached=True,dungeon6_completed=False,protected_sha256=before,worklog_prefix=prefix),roots,cleanup=True)
 assert before=={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected}
 from summarize_crystal_bridge_v0293 import main as summary
 p=ROOT/'analysis/crystal_bridge_v0293_report.json';raw=p.read_bytes();summary();assert p.read_bytes()==raw
 from validate_crystal_bridge_publication import main as publication
 p=ROOT/'analysis/crystal_bridge_publication_v0293_report.json';raw=p.read_bytes();publication();assert p.read_bytes()==raw
 print('All296 original/ROM files unchanged; summary and VDP report identical after verified cleanup')

if __name__=='__main__':main()
