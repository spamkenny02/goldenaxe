"""Archive only completed D8 passage trials, preserving a ready RAM copy."""
import json
from run_core import ROOT
from archive_lossless_evidence import freeze, sha
from rebase_natural_campaign import evidence


def main():
    report = json.loads((ROOT/'analysis/d8_passages_v0304_report.json').read_bytes())
    assert report['passed'] and report['ready_room'] == 0x1eb and not report['eighth_boss_entered']
    protected = [ROOT/'input/original.sms', ROOT/'gaw-megadrive.bin', ROOT/'gaw-title-megadrive.bin',
                 *sorted((ROOT/'versions').glob('*/*.bin'))]
    assert len(protected) == 307
    before = {p.relative_to(ROOT).as_posix(): sha(p.read_bytes()) for p in protected}
    roots = [ROOT/'validation'/n for n in ['v0304-d8-contact-sources']]
    for stage in report['stages']:
        p = ROOT/stage['trace']
        proof = p.with_name(p.name+f"-assisted-fixed-replay-{stage['frames']}")
        assert json.loads((proof/'replay_report.json').read_bytes())['passed']
        roots += [p, proof]
    for suffix in ['key01', 'switch1ec-01']:
        p = ROOT/'validation/natural-dungeon-combat'/('md-auto-v0304-d8-'+suffix)
        assert json.loads((p/'report.json').read_bytes())['failure'] == 'controller_stalled'
        roots.append(p)
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
    prefix = json.loads((ROOT/'analysis/d8_passages_v0304_worklog_prefix.json').read_bytes())
    assert sha((ROOT/'analysis/world_next.md').read_bytes()[:prefix['prefix_bytes']]) == prefix['prefix_sha256']
    paths += [ROOT/n for n in ['README.md', 'analysis/world_next.md', 'analysis/d8_passages_v0304_report.json',
                              'analysis/d8_passages_v0304.md', 'analysis/d8_passages_v0304_worklog_prefix.json',
                              'tools/archive_d8_passages_v0304.py', 'tools/rebase_natural_campaign.py']]
    paths += [p for p in (ROOT/'validation').iterdir() if p.is_file() and p.name.startswith(
        ('v0304-d8-west', 'v0304-d8-key', 'v0304-d8-switch1eb', 'v0304-d8-switch1ec'))]
    stage = report['stages'][-1]
    ready = ROOT/stage['trace']/f"ram_{stage['frames']:05d}.bin"
    raw = ready.read_bytes()
    freeze(ROOT, ROOT/'analysis/d8-passages-v0304', paths,
           dict(version=304, md_sha256=report['md_sha256'], protected_sha256=before,
                inherited_evidence=inherited, worklog_prefix=prefix), roots, cleanup=True)
    ready.write_bytes(raw)
    assert before == {p.relative_to(ROOT).as_posix(): sha(p.read_bytes()) for p in protected}
    from summarize_d8_passages_v0304 import main as summarize
    old = (ROOT/'analysis/d8_passages_v0304_report.json').read_bytes()
    summarize()
    assert (ROOT/'analysis/d8_passages_v0304_report.json').read_bytes() == old
    assert (ROOT/'versions/v0304-b7b4e150/d8_passages_v0304_report.json').read_bytes() == old
    print('All307 ROM/original files unchanged;D8 passages report identical;ready1EB RAM retained')


if __name__ == '__main__':
    main()
