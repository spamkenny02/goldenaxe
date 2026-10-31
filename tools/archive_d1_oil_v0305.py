"""Freeze completed current-ROM Oil/first-crystal campaign evidence."""
import json
from run_core import ROOT
from archive_lossless_evidence import freeze,sha
from rebase_natural_campaign import evidence


def main():
    report=json.loads((ROOT/'analysis/d1_oil_v0305_report.json').read_bytes())
    assert report['passed'] and report['version']==305 and report['first_crystal_and_exterior_return']
    protected=[ROOT/'input/original.sms',ROOT/'gaw-megadrive.bin',ROOT/'gaw-title-megadrive.bin',
               *sorted((ROOT/'versions').glob('*/*.bin'))]
    assert len(protected)==308
    before={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected}
    roots=[]
    for stage in report['stages']:
        p=ROOT/stage['trace'];c=json.loads((p/'capture.json').read_bytes())
        suffix=f"-assisted-fixed-replay-{c['frames']}" if c['test_ram_writes'] else '-fixed-replay'
        roots.extend([p,p.with_name(p.name+suffix)])
    roots.append(ROOT/'validation/stack-v0305-d1-oil-all')
    assert all(p.exists() and p.resolve().is_relative_to(ROOT/'validation') for p in roots)
    paths=[p for root in roots for p in root.rglob('*') if p.is_file()]
    inherited=[]
    for name,digest in report['evidence'].items():
        p=ROOT/name;assert sha(evidence(p))==digest
        if p.exists():paths.append(p)
        else:inherited.append(dict(path=name,sha256=digest))
    prefix=json.loads((ROOT/'analysis/d1_oil_v0305_worklog_prefix.json').read_bytes())
    assert sha((ROOT/'analysis/world_next.md').read_bytes()[:prefix['prefix_bytes']])==prefix['prefix_sha256']
    paths += [ROOT/n for n in ['README.md','analysis/world_next.md','analysis/d1_oil_v0305.md',
              'analysis/d1_oil_v0305_report.json','analysis/d1_oil_v0305_worklog_prefix.json',
              'tools/archive_d1_oil_v0305.py','tools/rebase_natural_campaign.py']]
    paths += [p for p in (ROOT/'validation').glob('v0305-d1-*.log')]
    ready=ROOT/(report['stages'][-1]['trace']+f"/ram_{report['stack_frames']:05d}.bin")
    raw=ready.read_bytes()
    freeze(ROOT,ROOT/'analysis/d1-oil-v0305',paths,
           dict(version=305,md_sha256=report['md_sha256'],protected_sha256=before,
                inherited_evidence=inherited,worklog_prefix=prefix),roots,cleanup=True)
    ready.write_bytes(raw)
    assert before=={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected}
    from summarize_d1_oil_v0305 import main as summarize
    old=(ROOT/'analysis/d1_oil_v0305_report.json').read_bytes();summarize()
    assert (ROOT/'analysis/d1_oil_v0305_report.json').read_bytes()==old
    assert (ROOT/'versions/v0305-83dfaf69/d1_oil_v0305_report.json').read_bytes()==old
    print('All308 original/ROM files unchanged;report identical;exterior ready RAM retained')


if __name__=='__main__':main()
