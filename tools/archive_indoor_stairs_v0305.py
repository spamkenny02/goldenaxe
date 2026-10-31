"""Lossless archive of closed stair checks and diagnostic historical replays."""
import json
from run_core import ROOT
from archive_lossless_evidence import freeze,sha
from rebase_natural_campaign import evidence


def main():
    report=json.loads((ROOT/'analysis/indoor_stairs_v0305_report.json').read_bytes())
    assert report['passed'] and report['version']==305 and report['natural_oil_and_exterior_return']
    protected=[ROOT/'input/original.sms',ROOT/'gaw-megadrive.bin',ROOT/'gaw-title-megadrive.bin',
               *sorted((ROOT/'versions').glob('*/*.bin'))]
    assert len(protected)==308
    before={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected}
    names=['indoor-stairs-v0304-baseline01','indoor-stairs-v0304-baseline02','indoor-boot-probe01',
           'v0304-before-indoor-fix','v0305-indoor-sources','indoor-stairs-v0305-fix01',
           'indoor-stairs-v0305-fix01-pal','stack-v0305-oil-all','v0305-fixed-rebase-prototype',
           'v0304-earth-door-prototype',
           'natural-dungeon-route/md-v0305-oil-route01','natural-dungeon-route/md-v0305-oil-route01-fixed-replay',
           'natural-service-route/md-v0305-oil-stairs01','natural-service-route/md-v0305-oil-stairs02',
           'natural-service-route/md-v0305-oil-stairs02-fixed-replay',
           'natural-service-route/md-v0305-d8-rebase-return3c01',
           'natural-dungeon-combat/md-auto-v0305-d8-rebase-dynamic01',
           'natural-dungeon-combat/md-auto-v0304-d8-boss01']
    for family,name in [('natural-dungeon-combat','md-auto-v0304-d8-resupply-exit01'),
                        ('natural-dungeon-route','md-v0304-d8-return1a-route01'),
                        ('natural-service-route','md-v0304-d8-return1a-service01')]:
        p=ROOT/'validation'/family/name
        c=json.loads((p/'capture.json').read_bytes())
        proof=p.with_name(p.name+f"-assisted-fixed-replay-{c['frames']}")
        assert json.loads((proof/'replay_report.json').read_bytes())['passed']
        names.extend([family+'/'+name,proof.relative_to(ROOT/'validation').as_posix()])
    roots=[(ROOT/'validation'/name).resolve() for name in names]
    assert all(p.exists() and p.is_relative_to(ROOT/'validation') for p in roots)
    paths=[p for root in roots for p in root.rglob('*') if p.is_file()]
    inherited=[]
    for name,digest in report['evidence'].items():
        p=ROOT/name;assert sha(evidence(p))==digest
        if p.exists():paths.append(p)
        else:inherited.append(dict(path=name,sha256=digest))
    prefix=json.loads((ROOT/'analysis/indoor_stairs_v0305_worklog_prefix.json').read_bytes())
    assert sha((ROOT/'analysis/world_next.md').read_bytes()[:prefix['prefix_bytes']])==prefix['prefix_sha256']
    paths += [ROOT/n for n in ['README.md','analysis/world_next.md','analysis/indoor_stairs_v0305.md',
              'analysis/indoor_stairs_v0305_report.json','analysis/indoor_stairs_v0305_worklog_prefix.json',
              'analysis/readme_history_through_v0304.md','tools/archive_indoor_stairs_v0305.py',
              'tools/rebase_natural_campaign.py']]
    paths += [p for p in (ROOT/'validation').iterdir() if p.is_file() and p.name.startswith(
        ('v0305-','build-v0305','v0304-indoor-','v0304-d8-boss01','v0304-d8-resupply-exit',
         'v0304-d8-return1a'))]
    ready=ROOT/'validation/natural-service-route/md-v0305-oil-stairs02/ram_04677.bin'
    raw=ready.read_bytes()
    freeze(ROOT,ROOT/'analysis/indoor-stairs-v0305',paths,
           dict(version=305,md_sha256=report['md_sha256'],protected_sha256=before,
                inherited_evidence=inherited,worklog_prefix=prefix,
                historical_replays_promoted=False,unused_earth_door_prototype_preserved=True),roots,cleanup=True)
    ready.write_bytes(raw)
    assert before=={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected}
    from summarize_indoor_stairs_v0305 import main as summarize
    old=(ROOT/'analysis/indoor_stairs_v0305_report.json').read_bytes();summarize()
    assert (ROOT/'analysis/indoor_stairs_v0305_report.json').read_bytes()==old
    assert (ROOT/'versions/v0305-83dfaf69/indoor_stairs_v0305_report.json').read_bytes()==old
    print('All308 protected ROM/original files unchanged;stair report identical;natural Oil ready RAM retained')


if __name__=='__main__':main()
