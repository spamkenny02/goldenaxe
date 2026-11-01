"""Verify and freeze D7 intermediate/ship evidence before capture cleanup."""
import json
from run_core import ROOT
from archive_lossless_evidence import freeze,sha
from rebase_natural_campaign import evidence
from summarize_d7_midboss_v0306 import main as intermediate
from summarize_d7_ship_v0306 import main as ship

def main():
 intermediate();ship()
 reports=[ROOT/'analysis'/n for n in ['d7_midboss_v0306_report.json','d7_ship_v0306_report.json']];before_reports={p:p.read_bytes() for p in reports};summaries=[json.loads(before_reports[p]) for p in reports]
 assert all(r['passed'] and not r['full_game_validated'] for r in summaries) and summaries[0]['intermediate_defeated'] and summaries[1]['ship_acquired']
 protected=[ROOT/'input/original.sms',ROOT/'gaw-megadrive.bin',ROOT/'gaw-title-megadrive.bin',*sorted((ROOT/'versions').glob('*/*.bin'))];assert len(protected)==309
 before={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected}
 roots=[]
 for pattern in ['md-auto-v0306-d7-key03*','md-auto-v0306-d7-earth1b9-*','md-auto-v0306-d7-guard-release*','md-auto-v0306-d7-contact1b9-*','md-auto-v0306-d7-midboss*','md-auto-v0306-d7-approach-resume*','md-auto-v0306-d7-south*','md-auto-v0306-d7-remote1e6-*','md-auto-v0306-d7-ship*']:
  roots += [p for p in (ROOT/'validation/natural-dungeon-combat').glob(pattern) if p.is_dir()]
 roots += [ROOT/'validation/v0306-d7-progress-sources'];assert roots and all(p.exists() and p.resolve().is_relative_to(ROOT/'validation') for p in roots)
 paths=[p for folder in roots for p in folder.rglob('*') if p.is_file()];inherited=[]
 for report in summaries:
  for name,digest in report['evidence'].items():
   p=ROOT/name;assert sha(evidence(p))==digest
   if p.exists():paths.append(p)
   else:inherited.append(dict(path=name,sha256=digest))
 prefix=json.loads((ROOT/'analysis/d7_progress_v0306_worklog_prefix.json').read_bytes());assert sha((ROOT/'analysis/world_next.md').read_bytes()[:prefix['prefix_bytes']])==prefix['prefix_sha256']
 paths += reports+[ROOT/name for name in ['README.md','analysis/world_next.md','analysis/d7_progress_v0306.md','analysis/d7_progress_v0306_worklog_prefix.json','analysis/d7_midboss_v0306_selection.json','tools/summarize_d7_midboss_v0306.py','tools/summarize_d7_ship_v0306.py','tools/archive_d7_progress_v0306.py','tools/close_assisted_approach.py','tools/resume_after_intermediate.py','tools/unassisted_dungeon_continuation.py','tools/rebase_natural_campaign.py']]
 paths += [p for p in (ROOT/'validation').iterdir() if p.is_file() and p.name.startswith(('v0306-d7-','md-v0306-d7-','md-auto-v0306-d7-')) and p.name not in ['v0306-d7-archive.log','v0306-d7-progress-archive.log']]
 ready=[]
 for r in summaries:
  p=ROOT/r['current_campaign_trace'];c=json.loads((p/'capture.json').read_bytes());p=p/f"ram_{c['frames']:05d}.bin";ready.append((p,p.read_bytes()))
 freeze(ROOT,ROOT/'analysis/d7-progress-v0306',paths,dict(version=306,md_sha256=summaries[1]['md_sha256'],protected_sha256=before,inherited_evidence=inherited,worklog_prefix=prefix,ordinary_south_death_not_promoted=True,missing_original_terminal_recovered_without_state_import=True),roots,cleanup=True)
 for p,raw in ready:p.write_bytes(raw)
 assert before=={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected}
 intermediate();ship();assert all(p.read_bytes()==raw for p,raw in before_reports.items())
 print('309 original/ROM files unchanged; two D7 reports identical; intermediate and ship RAM retained')
if __name__=='__main__':main()
