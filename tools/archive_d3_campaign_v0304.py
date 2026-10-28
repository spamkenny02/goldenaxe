"""Freeze terminal third-crystal/return proof; retain the ready exterior prefix."""
import json
from run_core import ROOT
from archive_lossless_evidence import freeze,sha
from rebase_natural_campaign import evidence


def main():
    report=json.loads((ROOT/'analysis/d3_campaign_v0304_report.json').read_bytes())
    assert report['passed'] and report['three_crystals_and_exterior_exit'] and not report['full_game_validated']
    protected=[ROOT/'input/original.sms',ROOT/'gaw-megadrive.bin',ROOT/'gaw-title-megadrive.bin',*sorted((ROOT/'versions').glob('*/*.bin'))]
    assert len(protected)==307
    before={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected}
    roots=[ROOT/'validation/stack-v0304-d3-all']
    for name in ['boss02','exit01']:
        p=ROOT/('validation/natural-dungeon-combat/md-auto-v0304-d3-'+name)
        capture=json.loads((p/'capture.json').read_bytes());proof=p.with_name(p.name+f"-assisted-fixed-replay-{capture['frames']}")
        assert json.loads((proof/'replay_report.json').read_bytes())['passed']
        roots.extend([p,proof])
    assert all(p.exists() and p.resolve().is_relative_to(ROOT/'validation') for p in roots)
    paths=[p for root in roots for p in root.rglob('*') if p.is_file()]
    inherited=[]
    for name,expected in report['evidence'].items():
        p=ROOT/name;assert sha(evidence(p))==expected
        if p.exists():paths.append(p)
        else:inherited.append(dict(path=name,sha256=expected))
    paths += [ROOT/n for n in ['README.md','analysis/world_next.md','analysis/d2_campaign_v0304.md',
              'analysis/d3_campaign_v0304.md','analysis/d3_campaign_v0304_report.json',
              'analysis/d3_campaign_v0304_worklog_prefix.json','tools/archive_d3_campaign_v0304.py',
              'tools/rebase_natural_campaign.py']]
    paths += [p for p in (ROOT/'validation').iterdir() if p.is_file() and p.name.startswith(('v0304-d3-boss02','v0304-d3-exit','v0304-d3-stack'))]
    prefix=json.loads((ROOT/'analysis/d3_campaign_v0304_worklog_prefix.json').read_bytes())
    assert sha((ROOT/'analysis/world_next.md').read_bytes()[:prefix['prefix_bytes']])==prefix['prefix_sha256']
    latest=ROOT/'validation/natural-dungeon-combat/md-auto-v0304-d3-exit01/ram_53755.bin';ready=latest.read_bytes()
    freeze(ROOT,ROOT/'analysis/d3-campaign-v0304',paths,
           dict(version=304,md_sha256=report['md_sha256'],protected_sha256=before,
                three_crystals_verified=True,inherited_evidence=inherited,
                inherited_archive='analysis/d2-campaign-v0304/manifest.json',worklog_prefix=prefix),roots,cleanup=True)
    latest.write_bytes(ready)
    assert before=={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected}
    from summarize_d3_campaign_v0304 import main as summary
    old=(ROOT/'analysis/d3_campaign_v0304_report.json').read_bytes();summary()
    assert (ROOT/'analysis/d3_campaign_v0304_report.json').read_bytes()==old
    assert (ROOT/'versions/v0304-b7b4e150/d3_campaign_v0304_report.json').read_bytes()==old
    print('All307 original/ROM files unchanged; D3 report identical after cleanup; exterior62 RAM retained')


if __name__=='__main__':main()
