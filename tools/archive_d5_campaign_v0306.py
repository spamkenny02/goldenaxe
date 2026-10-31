"""Preserve all D5 evidence, then clean only fully verified generated captures."""
import json
from run_core import ROOT
from archive_lossless_evidence import freeze, sha
from rebase_natural_campaign import evidence
from summarize_d5_supplies_v0306 import STAGES as SUPPLIES, main as supplies
from summarize_d5_campaign_v0306 import STAGES as FIGHTS, main as campaign


def main():
    supplies()
    campaign()
    reports = [ROOT / 'analysis' / n for n in ['d5_supplies_v0306_report.json', 'd5_campaign_v0306_report.json']]
    old = {p: p.read_bytes() for p in reports}
    r = json.loads(old[reports[-1]])
    assert r['passed'] and r['fifth_crystal_and_exterior_exit'] and not r['full_game_validated']
    protected = [ROOT / 'input/original.sms', ROOT / 'gaw-megadrive.bin', ROOT / 'gaw-title-megadrive.bin',
                 *sorted((ROOT / 'versions').glob('*/*.bin'))]
    assert len(protected) == 309
    before = {p.relative_to(ROOT).as_posix(): sha(p.read_bytes()) for p in protected}
    roots = []
    traces = [(f, n) for f, n, _ in SUPPLIES] + [('natural-dungeon-combat', n) for n in FIGHTS]
    traces += [('natural-dungeon-combat', 'md-auto-v0306-d5-boss01')]
    for family, name in traces:
        p = ROOT / 'validation' / family / name
        c = json.loads((p / 'capture.json').read_bytes())
        roots.extend([p, p.with_name(p.name + f"-assisted-fixed-replay-{c['frames']}")])
    roots += [ROOT / 'validation' / n for n in [
        'v0306-d5-sources', 'stack-v0306-d5-all', 'natural-dungeon-combat/md-auto-v0306-d5-key01']]
    assert all(p.exists() and p.resolve().is_relative_to(ROOT / 'validation') for p in roots)
    paths = [p for folder in roots for p in folder.rglob('*') if p.is_file()]
    inherited = []
    for report in reports:
        for name, digest in json.loads(old[report])['evidence'].items():
            p = ROOT / name
            assert sha(evidence(p)) == digest
            if p.exists():
                paths.append(p)
            else:
                inherited.append(dict(path=name, sha256=digest))
    prefix = json.loads((ROOT / 'analysis/d5_campaign_v0306_worklog_prefix.json').read_bytes())
    assert sha((ROOT / 'analysis/world_next.md').read_bytes()[:prefix['prefix_bytes']]) == prefix['prefix_sha256']
    paths += [ROOT / n for n in [
        'README.md', 'analysis/world_next.md', 'analysis/d5_campaign_v0306.md',
        'analysis/d5_campaign_v0306_worklog_prefix.json',
        'tools/natural_dungeon_combat.py', 'tools/assisted_boss_coarse_route.py',
        'tools/summarize_d5_supplies_v0306.py', 'tools/summarize_d5_campaign_v0306.py',
        'tools/archive_d5_campaign_v0306.py', 'tools/rebase_natural_campaign.py']]
    paths += reports
    paths += [p for p in (ROOT / 'validation').iterdir() if p.is_file() and p.name.startswith(('v0306-d5-', 'md-v0306-d5-', 'md-auto-v0306-d5-'))]
    ready = []
    for relative in ['natural-dungeon-combat/md-auto-v0306-d5-contact01',
                     'natural-dungeon-combat/md-auto-v0306-d5-exit01']:
        p = ROOT / 'validation' / relative
        c = json.loads((p / 'capture.json').read_bytes())
        p = p / f"ram_{c['frames']:05d}.bin"
        ready.append((p, p.read_bytes()))
    freeze(ROOT, ROOT / 'analysis/d5-campaign-v0306', paths,
           dict(version=306, md_sha256=r['md_sha256'], protected_sha256=before,
                inherited_evidence=inherited, worklog_prefix=prefix,
                rejected_short_budget_and_threshold_stall_not_promoted=True), roots, cleanup=True)
    for p, raw in ready:
        p.write_bytes(raw)
    assert before == {p.relative_to(ROOT).as_posix(): sha(p.read_bytes()) for p in protected}
    supplies()
    campaign()
    assert all(p.read_bytes() == data for p, data in old.items())
    print('309 original/ROM files unchanged; both reports identical; two ready RAM states retained')


if __name__ == '__main__':
    main()
