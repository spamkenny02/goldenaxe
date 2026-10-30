"""Freeze completed D7 combat/return evidence before generated-file cleanup."""
import json
from run_core import ROOT
from archive_lossless_evidence import freeze, sha
from rebase_natural_campaign import evidence


def main():
    report = json.loads((ROOT/'analysis/d7_campaign_v0304_report.json').read_bytes())
    assert report['passed'] and report['seventh_crystal_and_exterior_exit']
    protected = [ROOT/'input/original.sms', ROOT/'gaw-megadrive.bin', ROOT/'gaw-title-megadrive.bin',
                 *sorted((ROOT/'versions').glob('*/*.bin'))]
    assert len(protected) == 307
    before = {p.relative_to(ROOT).as_posix(): sha(p.read_bytes()) for p in protected}
    roots = [ROOT/'validation/stack-v0304-d7-all']
    for suffix in ['boss01', 'boss02', 'boss03', 'return-earth01', 'exit01', 'exit02']:
        p = ROOT/'validation/natural-dungeon-combat'/('md-auto-v0304-d7-'+suffix)
        capture = json.loads((p/'capture.json').read_bytes())
        result = json.loads((p/'report.json').read_bytes())
        roots.append(p)
        if suffix == 'exit01':
            assert result['failure'] == 'frame_limit' and not result['dungeon_exit_verified']
        else:
            proof = p.with_name(p.name+f"-assisted-fixed-replay-{capture['frames']}")
            assert json.loads((proof/'replay_report.json').read_bytes())['passed']
            roots.append(proof)
    assert all(p.exists() and p.resolve().is_relative_to(ROOT/'validation') for p in roots)
    paths = [p for root in roots for p in root.rglob('*') if p.is_file()]
    inherited = []
    for name, expected in report['evidence'].items():
        p = ROOT/name
        assert sha(evidence(p)) == expected
        if p.exists():
            paths.append(p)
        else:
            inherited.append(dict(path=name, sha256=expected))
    prefix = json.loads((ROOT/'analysis/d7_campaign_v0304_worklog_prefix.json').read_bytes())
    assert sha((ROOT/'analysis/world_next.md').read_bytes()[:prefix['prefix_bytes']]) == prefix['prefix_sha256']
    paths += [ROOT/n for n in ['README.md', 'analysis/world_next.md', 'analysis/d7_campaign_v0304_report.json',
                              'analysis/d7_campaign_v0304.md', 'analysis/d7_campaign_v0304_worklog_prefix.json',
                              'tools/archive_d7_campaign_v0304.py', 'tools/rebase_natural_campaign.py']]
    paths += [p for p in (ROOT/'validation').iterdir() if p.is_file() and p.name.startswith(
        ('v0304-d7-boss', 'v0304-d7-exit', 'v0304-d7-return-earth', 'v0304-d7-stack'))]
    stage = report['stages'][-1]
    ready = ROOT/stage['trace']/f"ram_{stage['frames']:05d}.bin"
    raw = ready.read_bytes()
    freeze(ROOT, ROOT/'analysis/d7-campaign-v0304', paths,
           dict(version=304, md_sha256=report['md_sha256'], protected_sha256=before,
                inherited_evidence=inherited, worklog_prefix=prefix,
                excluded_alternatives=['md-auto-v0304-d7-boss02', 'md-auto-v0304-d7-exit01']), roots, cleanup=True)
    ready.write_bytes(raw)
    assert before == {p.relative_to(ROOT).as_posix(): sha(p.read_bytes()) for p in protected}
    from summarize_d7_campaign_v0304 import main as summarize
    old = (ROOT/'analysis/d7_campaign_v0304_report.json').read_bytes()
    summarize()
    assert (ROOT/'analysis/d7_campaign_v0304_report.json').read_bytes() == old
    assert (ROOT/'versions/v0304-b7b4e150/d7_campaign_v0304_report.json').read_bytes() == old
    print('All307 ROM/original files unchanged;D7 report identical;outside1B ready RAM retained')


if __name__ == '__main__':
    main()
