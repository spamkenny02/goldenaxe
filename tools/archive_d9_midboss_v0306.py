"""Freeze D9 first intermediate evidence before verified generated cleanup."""
import json
from run_core import ROOT
from archive_lossless_evidence import freeze, sha
from rebase_natural_campaign import evidence
from summarize_d9_midboss_v0306 import main as audit


def main():
    audit()
    report = ROOT/'analysis/d9_midboss_v0306_report.json'
    before_report = report.read_bytes(); summary = json.loads(before_report)
    assert summary['passed'] and not summary['full_game_validated']
    protected = [ROOT/'input/original.sms',ROOT/'gaw-megadrive.bin',ROOT/'gaw-title-megadrive.bin',*sorted((ROOT/'versions').glob('*/*.bin'))]
    assert len(protected) == 309
    before = {p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected}
    roots = []
    for family in ['natural-dungeon-combat']:
        roots += [p for p in (ROOT/'validation'/family).glob('*v0306-d9-*') if p.is_dir()]
    roots += [ROOT/'validation/v0306-d9-first-mini-sources']
    assert roots and all(p.exists() and p.resolve().is_relative_to(ROOT/'validation') for p in roots)
    paths = [p for folder in roots for p in folder.rglob('*') if p.is_file()]
    inherited = []
    for name, digest in summary['evidence'].items():
        p=ROOT/name; assert sha(evidence(p)) == digest
        if p.exists(): paths.append(p)
        else: inherited.append(dict(path=name,sha256=digest))
    prefix=json.loads((ROOT/'analysis/d9_midboss_v0306_worklog_prefix.json').read_bytes())
    assert sha((ROOT/'analysis/world_next.md').read_bytes()[:prefix['prefix_bytes']]) == prefix['prefix_sha256']
    paths += [ROOT/name for name in ['README.md','REPRISE_CODEX.md','analysis/world_next.md','analysis/d9_midboss_v0306.md','analysis/d9_midboss_v0306_worklog_prefix.json','analysis/d9_midboss_v0306_selection.json','tools/natural_earth_then_contact.py','tools/summarize_d9_midboss_v0306.py','tools/archive_d9_midboss_v0306.py','tools/rebase_natural_campaign.py']]
    paths += [report]
    paths += [p for p in (ROOT/'validation').iterdir() if p.is_file() and p.name.startswith('v0306-d9-') and p.name not in ['v0306-d9-entry-archive.log','v0306-d9-midboss-archive.log']]
    ready=[]
    for relative in [summary['current_campaign_trace'], next(s['trace'] for s in summary['stages'] if s['kind']=='close')]:
        p=ROOT/relative;c=json.loads((p/'capture.json').read_bytes());p=p/f"ram_{c['frames']:05d}.bin";ready.append((p,p.read_bytes()))
    freeze(ROOT,ROOT/'analysis/d9-midboss-v0306',paths,dict(version=306,md_sha256=summary['md_sha256'],protected_sha256=before,inherited_evidence=inherited,worklog_prefix=prefix),roots,cleanup=True)
    for p,raw in ready: p.write_bytes(raw)
    assert before == {p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected}
    audit(); assert report.read_bytes() == before_report
    print('309 original/ROM files unchanged; D9 first-intermediate report identical; pre-fight and current RAM retained')

if __name__ == '__main__':
    main()
