"""Losslessly archive Fire/Long Sword/D5-entry evidence before generated cleanup."""
import json
from run_core import ROOT
from archive_lossless_evidence import freeze, sha
from rebase_natural_campaign import evidence
from summarize_fire_sword_v0306 import STAGES, main as summarize


def main():
    summarize()
    report_path = ROOT / 'analysis/fire_sword_v0306_report.json'
    old = report_path.read_bytes()
    report = json.loads(old)
    assert report['passed'] and report['d5_entrance_reached'] and not report['full_game_validated']
    protected = [ROOT / 'input/original.sms', ROOT / 'gaw-megadrive.bin', ROOT / 'gaw-title-megadrive.bin',
                 *sorted((ROOT / 'versions').glob('*/*.bin'))]
    assert len(protected) == 309
    before = {p.relative_to(ROOT).as_posix(): sha(p.read_bytes()) for p in protected}
    roots = []
    for family, name, _ in STAGES:
        root = ROOT / 'validation' / family / name
        c = json.loads((root / 'capture.json').read_bytes())
        roots.extend([root, root.with_name(root.name + f"-assisted-fixed-replay-{c['frames']}")])
    roots += [ROOT / 'validation' / n for n in [
        'v0306-equipment-sources', 'stack-v0306-fire-sword-all',
        'spell-teacher-game-v0306-fire-learn', 'canoe-house-v0306-entry01',
        'natural-dungeon-route/md-v0306-armor2-entry02']]
    assert all(p.exists() and p.resolve().is_relative_to(ROOT / 'validation') for p in roots)
    paths = [p for folder in roots for p in folder.rglob('*') if p.is_file()]
    inherited = []
    for name, digest in report['evidence'].items():
        p = ROOT / name
        assert sha(evidence(p)) == digest
        if p.exists():
            paths.append(p)
        else:
            inherited.append(dict(path=name, sha256=digest))
    prefix = json.loads((ROOT / 'analysis/fire_sword_v0306_worklog_prefix.json').read_bytes())
    assert sha((ROOT / 'analysis/world_next.md').read_bytes()[:prefix['prefix_bytes']]) == prefix['prefix_sha256']
    paths += [ROOT / n for n in [
        'README.md', 'analysis/world_next.md', 'analysis/fire_sword_v0306.md',
        'analysis/fire_sword_v0306_report.json', 'analysis/fire_sword_v0306_worklog_prefix.json',
        'tools/natural_house_quest.py', 'tools/validate_canoe_house_entry.py',
        'tools/summarize_fire_sword_v0306.py', 'tools/archive_fire_sword_v0306.py',
        'tools/rebase_natural_campaign.py']]
    paths += [p for p in (ROOT / 'validation').glob('*.log') if p.name.startswith(
        ('v0306-fire-', 'v0306-sword2-', 'v0306-armor', 'v0306-canoe-house-', 'v0306-d5-entry'))]
    proposals = ROOT / 'validation/v0306-equipment-entry-proposals.json'
    if proposals.exists():
        paths.append(proposals)
    ready = []
    for relative, frame in [('natural-service-route/md-v0306-sword2-gift01', 96309),
                            ('natural-dungeon-route/md-v0306-d5-entry01', 100808)]:
        p = ROOT / 'validation' / relative / f'ram_{frame:05d}.bin'
        ready.append((p, p.read_bytes()))
    freeze(ROOT, ROOT / 'analysis/fire-sword-v0306', paths,
           dict(version=306, md_sha256=report['md_sha256'], protected_sha256=before,
                inherited_evidence=inherited, worklog_prefix=prefix,
                rejected_armor_attempt_not_promoted=True), roots, cleanup=True)
    for p, raw in ready:
        p.write_bytes(raw)
    assert before == {p.relative_to(ROOT).as_posix(): sha(p.read_bytes()) for p in protected}
    summarize()
    assert report_path.read_bytes() == old
    print('309 original/ROM files unchanged; report identical; two ready RAM endpoints retained')


if __name__ == '__main__':
    main()
