"""Archive closed navigation/cache checks; exclude the live main-boss attempt."""
import json
from run_core import ROOT
from archive_lossless_evidence import freeze, sha
from rebase_natural_campaign import evidence


def main():
    report = json.loads((ROOT/'analysis/d7_navigation_v0304_report.json').read_bytes())
    assert report['passed'] and not report['seventh_boss_entered'] and report['ready_room'] == 0x189
    protected = [ROOT/'input/original.sms', ROOT/'gaw-megadrive.bin', ROOT/'gaw-title-megadrive.bin',
                 *sorted((ROOT/'versions').glob('*/*.bin'))]
    assert len(protected) == 307
    before = {p.relative_to(ROOT).as_posix(): sha(p.read_bytes()) for p in protected}
    roots = [ROOT/'validation'/n for n in ['v0304-d7-navigation-sources', 'v0304-d7-sentinel-sources',
                                         'ship-controller-v0304-01']]
    for stage in report['stages']:
        p = ROOT/stage['trace']
        proof = p.with_name(p.name+f"-assisted-fixed-replay-{stage['frames']}")
        assert json.loads((proof/'replay_report.json').read_bytes())['passed']
        roots.extend([p, proof])
    roots += [ROOT/'validation/natural-dungeon-combat'/('md-auto-v0304-d7-'+suffix)
              for suffix in ['north-return01', 'approach01', 'approach02']]
    assert all(p.exists() and p.resolve().is_relative_to(ROOT/'validation') and 'd7-boss' not in p.name for p in roots)
    paths = [p for root in roots for p in root.rglob('*') if p.is_file()]
    inherited = []
    for name, expected in report['evidence'].items():
        p = ROOT/name
        assert sha(evidence(p)) == expected
        if p.exists():
            paths.append(p)
        else:
            inherited.append(dict(path=name, sha256=expected))
    prefix = json.loads((ROOT/'analysis/d7_navigation_v0304_worklog_prefix.json').read_bytes())
    assert sha((ROOT/'analysis/world_next.md').read_bytes()[:prefix['prefix_bytes']]) == prefix['prefix_sha256']
    paths += [ROOT/n for n in ['README.md', 'analysis/world_next.md', 'analysis/d7_navigation_v0304_report.json',
                              'analysis/d7_navigation_v0304.md', 'analysis/d7_navigation_v0304_worklog_prefix.json',
                              'analysis/stack_minimum_v0304_erratum.md', 'analysis/stack_minimum_v0304_erratum_report.json',
                              'analysis/stack_minimum_v0304_worklog_prefix.json',
                              'tools/archive_d7_navigation_v0304.py', 'tools/rebase_natural_campaign.py']]
    erratum = json.loads((ROOT/'analysis/stack_minimum_v0304_erratum_report.json').read_bytes())
    for row in erratum['profiles']:
        assert sha(evidence(ROOT/row['profile'])) == row['profile_sha256']
        paths.append(ROOT/row['profile'])
    paths += [p for p in (ROOT/'validation').iterdir() if p.is_file() and p.name.startswith(
        ('v0304-ship-controller01', 'v0304-d7-north-return', 'v0304-d7-approach', 'v0304-d7-warp1a8'))]
    stage = report['stages'][-1]
    ready = ROOT/stage['trace']/f"ram_{stage['frames']:05d}.bin"
    raw = ready.read_bytes()
    freeze(ROOT, ROOT/'analysis/d7-navigation-v0304', paths,
           dict(version=304, md_sha256=report['md_sha256'], protected_sha256=before,
                inherited_evidence=inherited, worklog_prefix=prefix,
                excluded_boss_attempt='md-auto-v0304-d7-boss01'), roots, cleanup=True)
    ready.write_bytes(raw)
    assert before == {p.relative_to(ROOT).as_posix(): sha(p.read_bytes()) for p in protected}
    from summarize_d7_navigation_v0304 import main as summarize
    old = (ROOT/'analysis/d7_navigation_v0304_report.json').read_bytes()
    summarize()
    assert (ROOT/'analysis/d7_navigation_v0304_report.json').read_bytes() == old
    assert (ROOT/'versions/v0304-b7b4e150/d7_navigation_v0304_report.json').read_bytes() == old
    print('All307 ROM/original files unchanged;navigation report identical;ready189 RAM retained;boss attempt excluded')


if __name__ == '__main__':
    main()
