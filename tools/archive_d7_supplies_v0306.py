"""Archive verified D7 supply evidence before cleaning generated captures."""
import json
from run_core import ROOT
from archive_lossless_evidence import freeze,sha
from rebase_natural_campaign import evidence
from summarize_d7_supplies_v0306 import main as audit

def main():
 audit()
 report=ROOT/'analysis/d7_supplies_v0306_report.json'; original=report.read_bytes(); r=json.loads(original)
 assert r['passed'] and not r['full_game_validated']
 protected=[ROOT/'input/original.sms',ROOT/'gaw-megadrive.bin',ROOT/'gaw-title-megadrive.bin',*sorted((ROOT/'versions').glob('*/*.bin'))]
 assert len(protected)==309
 before={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected}
 roots=[]
 for family,pattern in [('natural-service-route','md-v0306-d7-*'),('natural-dungeon-route','md-v0306-d7-*'),('natural-dungeon-combat','md-auto-v0306-d7-*')]:
  roots += [p for p in (ROOT/'validation'/family).glob(pattern) if p.is_dir()]
 roots += [ROOT/'validation/v0306-d7-sources']
 assert roots and all(p.exists() and p.resolve().is_relative_to(ROOT/'validation') for p in roots)
 paths=[p for folder in roots for p in folder.rglob('*') if p.is_file()]; inherited=[]
 for name,digest in r['evidence'].items():
  p=ROOT/name; assert sha(evidence(p))==digest
  if p.exists():paths.append(p)
  else:inherited.append(dict(path=name,sha256=digest))
 prefix=json.loads((ROOT/'analysis/d7_supplies_v0306_worklog_prefix.json').read_bytes())
 assert sha((ROOT/'analysis/world_next.md').read_bytes()[:prefix['prefix_bytes']])==prefix['prefix_sha256']
 paths += [report,*[ROOT/name for name in ['README.md','analysis/world_next.md','analysis/d7_supplies_v0306.md','analysis/d7_supplies_v0306_worklog_prefix.json','tools/summarize_d7_supplies_v0306.py','tools/archive_d7_supplies_v0306.py','tools/rebase_natural_campaign.py']]]
 paths += [p for p in (ROOT/'validation').iterdir() if p.is_file() and p.name.startswith(('v0306-d7-','md-v0306-d7-','md-auto-v0306-d7-')) and p.name!='v0306-d7-archive.log']
 endpoint=ROOT/r['current_campaign_trace']; c=json.loads((endpoint/'capture.json').read_bytes()); ready=endpoint/f"ram_{c['frames']:05d}.bin"; raw=ready.read_bytes()
 freeze(ROOT,ROOT/'analysis/d7-supplies-v0306',paths,dict(version=306,md_sha256=r['md_sha256'],protected_sha256=before,inherited_evidence=inherited,worklog_prefix=prefix),roots,cleanup=True)
 ready.write_bytes(raw)
 assert before=={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected}
 audit(); assert report.read_bytes()==original
 print('309 original/ROM files unchanged; D7 supply report identical; ready RAM retained')
if __name__=='__main__':main()
