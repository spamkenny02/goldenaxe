"""Freeze completed v305 Earth/canoe/fourth-crystal evidence before cleanup."""
import json
from run_core import ROOT
from archive_lossless_evidence import freeze,sha
from rebase_natural_campaign import evidence


def main():
    report=json.loads((ROOT/'analysis/d4_campaign_v0305_report.json').read_bytes())
    assert report['passed'] and report['four_crystals_and_exterior_exit']
    protected=[ROOT/'input/original.sms',ROOT/'gaw-megadrive.bin',ROOT/'gaw-title-megadrive.bin',
               *sorted((ROOT/'versions').glob('*/*.bin'))]
    assert len(protected)==308
    before={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected}
    roots=[]
    for stage in report['stages']:
        p=ROOT/stage['trace'];c=json.loads((p/'capture.json').read_bytes())
        proof=p.with_name(p.name+f"-assisted-fixed-replay-{c['frames']}")
        assert json.loads((proof/'replay_report.json').read_bytes())['passed']
        roots.extend([p,proof])
    roots += [ROOT/'validation/natural-dungeon-combat'/('md-auto-v0305-d4-'+suffix)
              for suffix in ['earth01','a1-key01','warp01']]
    roots += [ROOT/'validation/stack-v0305-d4-all',ROOT/'validation/v0305-d4-sources']
    assert all(p.exists() and p.resolve().is_relative_to(ROOT/'validation') for p in roots)
    paths=[p for root in roots for p in root.rglob('*') if p.is_file()]
    inherited=[]
    for name,digest in report['evidence'].items():
        p=ROOT/name;assert sha(evidence(p))==digest
        if p.exists():paths.append(p)
        else:inherited.append(dict(path=name,sha256=digest))
    prefix=json.loads((ROOT/'analysis/d4_campaign_v0305_worklog_prefix.json').read_bytes())
    assert sha((ROOT/'analysis/world_next.md').read_bytes()[:prefix['prefix_bytes']])==prefix['prefix_sha256']
    paths += [ROOT/n for n in ['README.md','analysis/world_next.md','analysis/d4_campaign_v0305.md',
              'analysis/d4_campaign_v0305_report.json','analysis/d4_campaign_v0305_worklog_prefix.json',
              'tools/archive_d4_campaign_v0305.py','tools/rebase_natural_campaign.py']]
    paths += [p for p in (ROOT/'validation').glob('v0305-*.log') if p.name.startswith(
        ('v0305-gold-','v0305-gold50','v0305-earth-','v0305-d4-'))]
    ready=ROOT/(report['stages'][-1]['trace']+f"/ram_{report['stack_frames']:05d}.bin");raw=ready.read_bytes()
    freeze(ROOT,ROOT/'analysis/d4-campaign-v0305',paths,
           dict(version=305,md_sha256=report['md_sha256'],protected_sha256=before,
                inherited_evidence=inherited,worklog_prefix=prefix,failed_trials_promoted=False),roots,cleanup=True)
    ready.write_bytes(raw)
    assert before=={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected}
    from summarize_d4_campaign_v0305 import main as summarize
    old=(ROOT/'analysis/d4_campaign_v0305_report.json').read_bytes();summarize()
    assert (ROOT/'analysis/d4_campaign_v0305_report.json').read_bytes()==old
    assert (ROOT/'versions/v0305-83dfaf69/d4_campaign_v0305_report.json').read_bytes()==old
    print('All308 original/ROM files unchanged;D4 report identical;exterior ready RAM retained')


if __name__=='__main__':main()
