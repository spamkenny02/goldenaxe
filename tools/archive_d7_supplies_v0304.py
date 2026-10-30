"""Lossless readback before cleanup of terminal D7 resupply evidence."""
import json
from run_core import ROOT
from archive_lossless_evidence import freeze, sha
from rebase_natural_campaign import evidence


def main():
    report = json.loads((ROOT/'analysis/d7_supplies_v0304_report.json').read_bytes())
    assert report['passed'] and report['first_dungeon_key_acquired'] and not report['seventh_boss_entered']
    protected = [ROOT/'input/original.sms', ROOT/'gaw-megadrive.bin', ROOT/'gaw-title-megadrive.bin',
                 *sorted((ROOT/'versions').glob('*/*.bin'))]
    assert len(protected) == 307
    before = {p.relative_to(ROOT).as_posix(): sha(p.read_bytes()) for p in protected}
    roots = []
    for stage in report['stages']:
        p = ROOT/'validation'/stage['trace']
        proof = p.with_name(p.name+f"-assisted-fixed-replay-{stage['frames']}")
        assert json.loads((proof/'replay_report.json').read_bytes())['passed']
        roots.extend([p, proof])
    roots += [ROOT/'validation'/n for n in [
        'natural-dungeon-route/md-v0304-d7-entry01',
        'natural-dungeon-route/md-v0304-d7-entry01-assisted-fixed-replay-156221',
        'natural-dungeon-combat/md-auto-v0304-d7-key01',
        'natural-dungeon-route/md-v0304-d7-gold5d-route01']]
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
    prefix = json.loads((ROOT/'analysis/d7_supplies_v0304_worklog_prefix.json').read_bytes())
    assert sha((ROOT/'analysis/world_next.md').read_bytes()[:prefix['prefix_bytes']]) == prefix['prefix_sha256']
    paths += [ROOT/n for n in ['README.md', 'analysis/world_next.md', 'analysis/d7_supplies_v0304_report.json',
                              'analysis/d7_supplies_v0304.md', 'analysis/d7_supplies_v0304_worklog_prefix.json',
                              'tools/archive_d7_supplies_v0304.py', 'tools/rebase_natural_campaign.py']]
    paths += [p for p in (ROOT/'validation').iterdir() if p.is_file() and p.name.startswith('v0304-d7-')]
    paths += list((ROOT/'validation/natural-dungeon-route').glob('plan-door*-v0304-d7*.json'))
    stage = report['stages'][-1]
    ready = ROOT/'validation'/stage['trace']/f"ram_{stage['frames']:05d}.bin"
    raw = ready.read_bytes()
    freeze(ROOT, ROOT/'analysis/d7-supplies-v0304', paths,
           dict(version=304, md_sha256=report['md_sha256'], protected_sha256=before,
                inherited_evidence=inherited, worklog_prefix=prefix), roots, cleanup=True)
    ready.write_bytes(raw)
    assert before == {p.relative_to(ROOT).as_posix(): sha(p.read_bytes()) for p in protected}
    from summarize_d7_supplies_v0304 import main as summarize
    old = (ROOT/'analysis/d7_supplies_v0304_report.json').read_bytes()
    summarize()
    assert (ROOT/'analysis/d7_supplies_v0304_report.json').read_bytes() == old
    assert (ROOT/'versions/v0304-b7b4e150/d7_supplies_v0304_report.json').read_bytes() == old
    print('All307 original/ROM files unchanged;D7 supply report identical after cleanup;room1CB RAM retained')


if __name__ == '__main__':
    main()
