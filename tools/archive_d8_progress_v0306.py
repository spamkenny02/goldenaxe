"""Archive D8 coastal entry and ordinary intermediate victory with verified cleanup."""
import json
from run_core import ROOT
from archive_lossless_evidence import freeze,sha
from rebase_natural_campaign import evidence
from summarize_d8_entry_v0306 import main as entry
from summarize_d8_midboss_v0306 import main as combat

def main():
 entry();combat()
 reports=[ROOT/'analysis'/n for n in ['d8_entry_v0306_report.json','d8_midboss_v0306_report.json']];before_reports={p:p.read_bytes() for p in reports};summaries=[json.loads(before_reports[p]) for p in reports]
 assert all(r['passed'] and not r['full_game_validated'] for r in summaries) and summaries[1]['intermediate_defeated']
 protected=[ROOT/'input/original.sms',ROOT/'gaw-megadrive.bin',ROOT/'gaw-title-megadrive.bin',*sorted((ROOT/'versions').glob('*/*.bin'))];assert len(protected)==309
 before={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected};roots=[]
 for family,patterns in [('natural-dungeon-route',['md-v0306-d8-paid3c-route*','md-v0306-d8-entry*']),('natural-service-route',['md-v0306-d8-paid3c-service*']),('natural-dungeon-combat',['md-auto-v0306-d8-mini-ready*','md-auto-v0306-d8-guard-release*','md-auto-v0306-d8-midboss*'])]:
  for pattern in patterns:roots += [p for p in (ROOT/'validation'/family).glob(pattern) if p.is_dir()]
 roots += [ROOT/'validation/v0306-d8-entry-sources',ROOT/'validation/v0306-d8-progress-sources'];assert roots and all(p.exists() and p.resolve().is_relative_to(ROOT/'validation') for p in roots)
 paths=[p for folder in roots for p in folder.rglob('*') if p.is_file()];inherited=[]
 for report in summaries:
  for name,digest in report['evidence'].items():
   p=ROOT/name;assert sha(evidence(p))==digest
   if p.exists():paths.append(p)
   else:inherited.append(dict(path=name,sha256=digest))
 prefix=json.loads((ROOT/'analysis/d8_progress_v0306_worklog_prefix.json').read_bytes());assert sha((ROOT/'analysis/world_next.md').read_bytes()[:prefix['prefix_bytes']])==prefix['prefix_sha256']
 paths += reports+[ROOT/name for name in ['README.md','analysis/world_next.md','analysis/d8_progress_v0306.md','analysis/d8_progress_v0306_worklog_prefix.json','analysis/d8_midboss_v0306_selection.json','tools/summarize_d8_entry_v0306.py','tools/summarize_d8_midboss_v0306.py','tools/archive_d8_progress_v0306.py','tools/rebase_natural_campaign.py']]
 paths += [p for p in (ROOT/'validation').iterdir() if p.is_file() and p.name.startswith(('v0306-d8-','md-v0306-d8-','md-auto-v0306-d8-')) and p.name!='v0306-d8-progress-archive.log']
 ready=[]
 for relative in ['validation/natural-dungeon-combat/md-auto-v0306-d8-guard-release01',summaries[1]['current_campaign_trace']]:
  p=ROOT/relative;c=json.loads((p/'capture.json').read_bytes());p=p/f"ram_{c['frames']:05d}.bin";ready.append((p,p.read_bytes()))
 freeze(ROOT,ROOT/'analysis/d8-progress-v0306',paths,dict(version=306,md_sha256=summaries[1]['md_sha256'],protected_sha256=before,inherited_evidence=inherited,worklog_prefix=prefix,rejected_first_approach_not_promoted=True),roots,cleanup=True)
 for p,raw in ready:p.write_bytes(raw)
 assert before=={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected}
 entry();combat();assert all(p.read_bytes()==raw for p,raw in before_reports.items())
 print('309 original/ROM files unchanged; two D8 reports identical; pre-intermediate and victory RAM retained')
if __name__=='__main__':main()
