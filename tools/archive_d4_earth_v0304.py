"""Archive closed D4 Earth runs; retain the verified pre-thief continuation RAM."""
import json
from run_core import ROOT
from archive_lossless_evidence import freeze, sha
from rebase_natural_campaign import evidence


def main():
    report=json.loads((ROOT/'analysis/d4_earth_v0304_report.json').read_bytes())
    assert report['passed'] and not report['fourth_crystal_validated']
    protected=[ROOT/'input/original.sms',ROOT/'gaw-megadrive.bin',ROOT/'gaw-title-megadrive.bin',
               *sorted((ROOT/'versions').glob('*/*.bin'))]
    assert len(protected)==307
    before={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected}
    roots=[]
    for stage in report['stages']:
        p=ROOT/'validation'/stage['trace']
        proof=p.with_name(p.name+f"-assisted-fixed-replay-{stage['frames']}")
        assert json.loads((proof/'replay_report.json').read_bytes())['passed']
        roots.extend([p,proof])
    failed=ROOT/report['next_issue']['trace']
    roots.extend([failed,failed.with_name(failed.name+'-thief-diagnostic'),ROOT/'validation/thief-lethal-capture-source-v0304'])
    assert all(p.exists() and p.resolve().is_relative_to(ROOT/'validation') for p in roots)
    paths=[p for root in roots for p in root.rglob('*') if p.is_file()]
    inherited=[]
    for name,expected in report['evidence'].items():
        p=ROOT/name
        assert sha(evidence(p))==expected
        if p.exists():paths.append(p)
        else:inherited.append(dict(path=name,sha256=expected))
    prefix=json.loads((ROOT/'analysis/d4_earth_v0304_worklog_prefix.json').read_bytes())
    assert sha((ROOT/'analysis/world_next.md').read_bytes()[:prefix['prefix_bytes']])==prefix['prefix_sha256']
    paths += [ROOT/n for n in ['README.md','analysis/world_next.md','analysis/d4_earth_v0304_report.json',
                              'analysis/d4_earth_v0304.md','analysis/d4_earth_v0304_worklog_prefix.json',
                              'tools/archive_d4_earth_v0304.py','tools/rebase_natural_campaign.py']]
    paths += [p for p in (ROOT/'validation').iterdir() if p.is_file() and p.name.startswith(
        ('v0304-gold','v0304-earth','v0304-d4'))]
    ready=ROOT/'validation/natural-dungeon-combat/md-auto-v0304-d4-earth01/ram_67098.bin'
    raw=ready.read_bytes()
    freeze(ROOT,ROOT/'analysis/d4-earth-v0304',paths,
           dict(version=304,md_sha256=report['md_sha256'],protected_sha256=before,
                inherited_evidence=inherited,worklog_prefix=prefix),roots,cleanup=True)
    ready.write_bytes(raw)
    assert before=={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected}
    from summarize_d4_earth_v0304 import main as summarize
    previous=(ROOT/'analysis/d4_earth_v0304_report.json').read_bytes()
    summarize()
    assert (ROOT/'analysis/d4_earth_v0304_report.json').read_bytes()==previous
    assert (ROOT/'versions/v0304-b7b4e150/d4_earth_v0304_report.json').read_bytes()==previous
    print('307 original/current/numbered ROMs unchanged; report identical after cleanup; verified Earth prefix RAM retained')


if __name__=='__main__':
    main()
