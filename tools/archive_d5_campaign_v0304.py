"""Freeze terminal fifth-crystal evidence; keep the current D6-ready RAM."""
import json
from run_core import ROOT
from archive_lossless_evidence import freeze,sha
from rebase_natural_campaign import evidence


def main():
    report=json.loads((ROOT/'analysis/d5_campaign_v0304_report.json').read_bytes())
    assert report['passed'] and report['fifth_crystal_and_exterior_exit'] and not report['full_game_validated']
    protected=[ROOT/'input/original.sms',ROOT/'gaw-megadrive.bin',ROOT/'gaw-title-megadrive.bin',
               *sorted((ROOT/'versions').glob('*/*.bin'))]
    assert len(protected)==307
    before={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected}
    roots=[ROOT/'validation/stack-v0304-d5-all',ROOT/'validation/v0304-d5-boss-sources']
    for stage in report['stages']:
        p=ROOT/stage['trace'];proof=p.with_name(p.name+f"-assisted-fixed-replay-{stage['frames']}")
        assert json.loads((proof/'replay_report.json').read_bytes())['passed']
        roots.extend([p,proof])
    assert all(p.exists() and p.resolve().is_relative_to(ROOT/'validation') for p in roots)
    paths=[p for root in roots for p in root.rglob('*') if p.is_file()]
    inherited=[]
    for name,expected in report['evidence'].items():
        p=ROOT/name;assert sha(evidence(p))==expected
        if p.exists():paths.append(p)
        else:inherited.append(dict(path=name,sha256=expected))
    prefix=json.loads((ROOT/'analysis/d5_campaign_v0304_worklog_prefix.json').read_bytes())
    assert sha((ROOT/'analysis/world_next.md').read_bytes()[:prefix['prefix_bytes']])==prefix['prefix_sha256']
    paths += [ROOT/n for n in ['README.md','analysis/world_next.md','analysis/d5_campaign_v0304_report.json',
                              'analysis/d5_campaign_v0304.md','analysis/d5_campaign_v0304_source_index.json',
                              'analysis/d5_campaign_v0304_worklog_prefix.json',
                              'tools/archive_d5_campaign_v0304.py','tools/rebase_natural_campaign.py']]
    paths += [p for p in (ROOT/'validation').iterdir() if p.is_file() and p.name.startswith(
        ('v0304-d5-boss01','v0304-d5-boss02','v0304-d5-return-contact01','v0304-d5-exit01','v0304-d5-stack'))]
    ready=ROOT/'validation/natural-dungeon-combat/md-auto-v0304-d5-exit01/ram_121051.bin'
    raw=ready.read_bytes()
    freeze(ROOT,ROOT/'analysis/d5-campaign-v0304',paths,
           dict(version=304,md_sha256=report['md_sha256'],protected_sha256=before,
                inherited_evidence=inherited,worklog_prefix=prefix),roots,cleanup=True)
    ready.write_bytes(raw)
    assert before=={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected}
    from summarize_d5_campaign_v0304 import main as summarize
    old=(ROOT/'analysis/d5_campaign_v0304_report.json').read_bytes();summarize()
    assert (ROOT/'analysis/d5_campaign_v0304_report.json').read_bytes()==old
    assert (ROOT/'versions/v0304-b7b4e150/d5_campaign_v0304_report.json').read_bytes()==old
    print('All307 original/ROM files unchanged;D5 report identical after cleanup;exterior49 RAM retained')


if __name__=='__main__':main()
