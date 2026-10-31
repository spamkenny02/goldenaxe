"""Lossless D6 capture archive, verified cleanup and protected numbered ROMs."""
import json
from run_core import ROOT
from archive_lossless_evidence import freeze, sha
from rebase_natural_campaign import evidence
from summarize_d6_progress_v0306 import main as progress
from summarize_d6_campaign_v0306 import main as campaign


def main():
    progress()
    campaign()
    reports = [ROOT / 'analysis' / name for name in ['d6_progress_v0306_report.json', 'd6_campaign_v0306_report.json']]
    old = {p: p.read_bytes() for p in reports}
    p_report, c_report = [json.loads(old[p]) for p in reports]
    assert c_report['passed'] and c_report['sixth_crystal_and_exterior_exit'] and not c_report['full_game_validated']
    protected = [ROOT / 'input/original.sms', ROOT / 'gaw-megadrive.bin', ROOT / 'gaw-title-megadrive.bin',
                 *sorted((ROOT / 'versions').glob('*/*.bin'))]
    assert len(protected) == 309
    before = {p.relative_to(ROOT).as_posix(): sha(p.read_bytes()) for p in protected}
    roots = []
    for family, pattern in [('natural-service-route', 'md-v0306-d6-*'),
                            ('natural-dungeon-route', 'md-v0306-d6-*'),
                            ('natural-dungeon-combat', 'md-auto-v0306-d6-*')]:
        roots += [p for p in (ROOT / 'validation' / family).glob(pattern) if p.is_dir()]
    roots += [ROOT / 'validation/v0306-d6-sources', ROOT / 'validation/stack-v0306-d6-all']
    assert roots and all(p.exists() and p.resolve().is_relative_to(ROOT / 'validation') for p in roots)
    paths = [p for folder in roots for p in folder.rglob('*') if p.is_file()]
    inherited = []
    for report in [p_report, c_report]:
        for name, digest in report['evidence'].items():
            p = ROOT / name
            assert sha(evidence(p)) == digest
            if p.exists():
                paths.append(p)
            else:
                inherited.append(dict(path=name, sha256=digest))
    prefix = json.loads((ROOT / 'analysis/d6_campaign_v0306_worklog_prefix.json').read_bytes())
    assert sha((ROOT / 'analysis/world_next.md').read_bytes()[:prefix['prefix_bytes']]) == prefix['prefix_sha256']
    paths += [ROOT / name for name in [
        'README.md', 'analysis/world_next.md', 'analysis/d6_campaign_v0306.md',
        'analysis/d6_campaign_v0306_worklog_prefix.json', 'tools/natural_weapon_selection.py',
        'tools/summarize_d6_progress_v0306.py', 'tools/summarize_d6_campaign_v0306.py',
        'tools/archive_d6_campaign_v0306.py', 'tools/rebase_natural_campaign.py']]
    paths += reports
    paths += [p for p in (ROOT / 'validation').iterdir() if p.is_file() and
              p.name.startswith(('v0306-d6-', 'md-v0306-d6-', 'md-auto-v0306-d6-')) and
              p.name != 'v0306-d6-archive.log']
    ready = []
    for relative in [p_report['ready_trace'], c_report['current_campaign_trace']]:
        p = ROOT / relative
        c = json.loads((p / 'capture.json').read_bytes())
        p = p / f"ram_{c['frames']:05d}.bin"
        ready.append((p, p.read_bytes()))
    freeze(ROOT, ROOT / 'analysis/d6-campaign-v0306', paths,
           dict(version=306, md_sha256=c_report['md_sha256'], protected_sha256=before,
                inherited_evidence=inherited, worklog_prefix=prefix,
                rejected_route_attempts_not_promoted=True), roots, cleanup=True)
    for p, raw in ready:
        p.write_bytes(raw)
    assert before == {p.relative_to(ROOT).as_posix(): sha(p.read_bytes()) for p in protected}
    progress()
    campaign()
    assert all(p.read_bytes() == raw for p, raw in old.items())
    print('309 original/ROM files unchanged; both D6 reports identical; two ready RAM states retained')


if __name__ == '__main__':
    main()
