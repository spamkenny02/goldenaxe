"""Freeze D7 navigation, seventh crystal, exterior return and stack evidence."""
import json
from run_core import ROOT
from archive_lossless_evidence import freeze,sha
from rebase_natural_campaign import evidence
from summarize_d7_navigation_v0306 import main as navigation
from summarize_d7_campaign_v0306 import main as campaign

def main():
 navigation();campaign()
 reports=[ROOT/'analysis'/n for n in ['d7_navigation_v0306_report.json','d7_campaign_v0306_report.json']];before_reports={p:p.read_bytes() for p in reports};summaries=[json.loads(before_reports[p]) for p in reports]
 assert all(r['passed'] and not r['full_game_validated'] for r in summaries) and summaries[1]['seventh_crystal_and_exterior_exit']
 protected=[ROOT/'input/original.sms',ROOT/'gaw-megadrive.bin',ROOT/'gaw-title-megadrive.bin',*sorted((ROOT/'versions').glob('*/*.bin'))];assert len(protected)==309
 before={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected};roots=[]
 for pattern in ['md-auto-v0306-d7-north-return*','md-auto-v0306-d7-warp1a8-*','md-auto-v0306-d7-approach03*','md-auto-v0306-d7-boss*','md-auto-v0306-d7-crystal*','md-auto-v0306-d7-return-earth*','md-auto-v0306-d7-exit*']:
  roots += [p for p in (ROOT/'validation/natural-dungeon-combat').glob(pattern) if p.is_dir()]
 roots += [ROOT/'validation/v0306-d7-navigation-sources',ROOT/'validation/stack-v0306-d7-all'];assert roots and all(p.exists() and p.resolve().is_relative_to(ROOT/'validation') for p in roots)
 paths=[p for folder in roots for p in folder.rglob('*') if p.is_file()];inherited=[]
 for report in summaries:
  for name,digest in report['evidence'].items():
   p=ROOT/name;assert sha(evidence(p))==digest
   if p.exists():paths.append(p)
   else:inherited.append(dict(path=name,sha256=digest))
 prefix=json.loads((ROOT/'analysis/d7_campaign_v0306_worklog_prefix.json').read_bytes());assert sha((ROOT/'analysis/world_next.md').read_bytes()[:prefix['prefix_bytes']])==prefix['prefix_sha256']
 paths += reports+[ROOT/name for name in ['README.md','analysis/world_next.md','analysis/d7_campaign_v0306.md','analysis/d7_campaign_v0306_worklog_prefix.json','analysis/d7_campaign_v0306_selection.json','tools/summarize_d7_navigation_v0306.py','tools/summarize_d7_campaign_v0306.py','tools/archive_d7_campaign_v0306.py','tools/rebase_natural_campaign.py']]
 paths += [p for p in (ROOT/'validation').iterdir() if p.is_file() and p.name.startswith(('v0306-d7-','md-v0306-d7-','md-auto-v0306-d7-')) and p.name not in ['v0306-d7-archive.log','v0306-d7-progress-archive.log','v0306-d7-campaign-archive.log']]
 ready=[]
 for relative in [summaries[0]['ready_trace'],summaries[1]['current_campaign_trace']]:
  p=ROOT/relative;c=json.loads((p/'capture.json').read_bytes());p=p/f"ram_{c['frames']:05d}.bin";ready.append((p,p.read_bytes()))
 freeze(ROOT,ROOT/'analysis/d7-campaign-v0306',paths,dict(version=306,md_sha256=summaries[1]['md_sha256'],protected_sha256=before,inherited_evidence=inherited,worklog_prefix=prefix),roots,cleanup=True)
 for p,raw in ready:p.write_bytes(raw)
 assert before=={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected}
 navigation();campaign();assert all(p.read_bytes()==raw for p,raw in before_reports.items())
 print('309 original/ROM files unchanged; two D7 campaign reports identical; preboss and exit RAM retained')
if __name__=='__main__':main()
