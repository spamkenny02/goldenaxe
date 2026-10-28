"""Lossless v295 evidence archive; protect every original and numbered ROM."""
import json
from pathlib import Path
from run_core import ROOT
from archive_lossless_evidence import freeze, sha


def main():
    report = json.loads((ROOT/'analysis/variant_7c_v0295_report.json').read_bytes())
    assert report['passed'] and report['version'] == 295 and report['native_two_crystals']
    assert not report['burst_cadence_complete']
    protected = [ROOT/'input/original.sms',ROOT/'gaw-megadrive.bin',
                 ROOT/'gaw-title-megadrive.bin',*sorted((ROOT/'versions').glob('*/*.bin'))]
    assert len(protected) == 298
    before = {p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected}
    roots = [ROOT/'validation'/n for n in ['stack-v0295-d2-all','v0295-sources','burst-variant-7c-v0295']]
    for family in ['natural-dungeon-combat','natural-dungeon-route']:
        roots += [p for p in (ROOT/'validation'/family).iterdir()
                  if p.is_dir() and p.name.startswith(('md-auto-v0295-d2-','md-v0295-d3-'))]
    roots += [p for p in (ROOT/'validation').iterdir() if p.is_dir() and p.name.startswith(('v0295-burst-boss-gameplay-','v0294-baseline-burst-boss-gameplay-'))]
    assert all(p.exists() and p.resolve().is_relative_to(ROOT/'validation') for p in roots)
    paths = [p for root in roots for p in root.rglob('*') if p.is_file()]
    paths += [ROOT/name for name in report['evidence']]
    paths += [p for p in (ROOT/'analysis').iterdir() if p.is_file() and 'v0295' in p.name]
    paths += [ROOT/'analysis/burst_variant_7c_v0294_baseline_diagnostic.json',
              ROOT/'README.md',ROOT/'analysis/world_next.md',
              ROOT/'tools/archive_variant_7c_v0295.py',ROOT/'tools/rebase_natural_campaign.py']
    paths += [p for p in (ROOT/'validation').iterdir() if p.is_file() and p.name.startswith(('v0295-','v0294-baseline-','v0294-burst-diagnostic'))]
    # Retain a small ready-to-continue checkpoint locally; never import it into a game.
    latest = ROOT/'validation/natural-dungeon-route/md-v0295-d3-entry02/ram_40308.bin'
    ready = latest.read_bytes()
    prefix = json.loads((ROOT/'analysis/variant_7c_v0295_worklog_prefix.json').read_bytes())
    assert sha((ROOT/'analysis/world_next.md').read_bytes()[:prefix['prefix_bytes']]) == prefix['prefix_sha256']
    freeze(ROOT,ROOT/'analysis/variant-7c-v0295',paths,
           dict(version=295,md_sha256=report['md_sha256'],protected_sha256=before,
                burst_cadence_remains_open=True,worklog_prefix=prefix),roots,cleanup=True)
    latest.write_bytes(ready)
    assert before == {p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected}
    from summarize_variant_7c_v0295 import main as summary
    prior = (ROOT/'analysis/variant_7c_v0295_report.json').read_bytes()
    summary()
    assert (ROOT/'analysis/variant_7c_v0295_report.json').read_bytes() == prior
    assert prior == (ROOT/'versions/v0295-b71a6bc6/variant_7c_v0295_report.json').read_bytes()
    print('All298 original/ROM files unchanged; summary identical after cleanup; D3 final RAM retained for planning')


if __name__ == '__main__': main()
