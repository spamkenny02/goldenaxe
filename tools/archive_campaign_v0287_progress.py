"""Losslessly archive v287 campaign proofs before generated-data cleanup."""
import json
from run_core import ROOT
from archive_lossless_evidence import freeze,sha

def main():
 report=json.loads((ROOT/'analysis/campaign_v0287_progress_report.json').read_bytes());assert report['passed'] and report['md_sha256']==sha((ROOT/'gaw-megadrive.bin').read_bytes())
 prefix=json.loads((ROOT/'analysis/campaign_v0287_worklog_prefix.json').read_bytes());assert sha((ROOT/'analysis/world_next.md').read_bytes()[:prefix['bytes']])==prefix['sha256']
 protected=[ROOT/'input/original.sms',ROOT/'gaw-megadrive.bin',ROOT/'gaw-title-megadrive.bin',*sorted((ROOT/'versions').glob('*/*.bin'))];assert len(protected)==290
 before={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected};roots=[]
 for family,patterns in [('natural-dungeon-route',['*v0287-fairy*','*v0287-d2*']),('natural-service-route',['*v0287-fairy*']),('natural-dungeon-combat',['*v0287-d2*','*v0287-source-d3*']),('natural-rope-route',['*v0287*'])]:
  for pattern in patterns:roots.extend(p for p in (ROOT/'validation'/family).glob(pattern) if p.is_dir())
 roots.append(ROOT/'validation/stack-v0287-d2-all');paths=[p for d in roots for p in d.rglob('*') if p.is_file()]
 paths.extend(ROOT/n for n in report['evidence'] if (ROOT/n).exists())
 paths.extend(p for p in (ROOT/'validation').glob('*.log') if any(t in p.name for t in ['v0287-d2','v0287-fairy','v0287-source','stack-v0287-d2']))
 paths.extend(ROOT/'megadrive/out/release'/n for n in ['rom.bin','rom.out','symbol.txt'])
 paths.extend(ROOT/'megadrive/src'/n for n in ['main.c','actors.c','source_magic_rope.c','source_magic_rope.h'])
 paths.extend(ROOT/'tools'/n for n in ['assisted_prefix.py','assisted_boss_route.py','natural_dungeon_combat.py','natural_rope_route.py','natural_boss_cautious_planner.py','natural_boss_side_planner.py','natural_boss_escape_planner.py','natural_combat_navigation.py','natural_combat_beam.py','natural_combat_lookahead.py','natural_boss_lookahead.py','summarize_campaign_v0287_progress.py','archive_campaign_v0287_progress.py','profile_playable_stack.py','rebase_natural_campaign.py','run_core.py'])
 paths.extend(ROOT/n for n in ['README.md','analysis/world_next.md','analysis/campaign_v0287_progress.md','analysis/campaign_v0287_progress_report.json','analysis/campaign_v0287_worklog_prefix.json'])
 manifest=freeze(ROOT,ROOT/'analysis/campaign-v0287-progress',paths,dict(md_sha256=report['md_sha256'],full_game_validated=False,numbered_roms_preserved=287,protected_sha256=before),roots,cleanup=True)
 for name,digest in before.items():assert sha((ROOT/name).read_bytes())==digest
 from summarize_campaign_v0287_progress import main as summarize
 raw=(ROOT/'analysis/campaign_v0287_progress_report.json').read_bytes();summarize();assert (ROOT/'analysis/campaign_v0287_progress_report.json').read_bytes()==raw
 print('Verified generated cleanup bytes:',sum(r['bytes'] for r in manifest['removed_verified_generated']))
if __name__=='__main__':main()
