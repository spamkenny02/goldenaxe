"""Freeze closed supply/mechanism runs; never include the separate live boss."""
import json
from run_core import ROOT
from archive_lossless_evidence import freeze,sha
from rebase_natural_campaign import evidence


def main():
    report=json.loads((ROOT/'analysis/d5_supplies_v0304_report.json').read_bytes())
    assert report['passed'] and report['scope_ends_before_boss'] and not report['fifth_crystal_validated']
    protected=[ROOT/'input/original.sms',ROOT/'gaw-megadrive.bin',ROOT/'gaw-title-megadrive.bin',
               *sorted((ROOT/'versions').glob('*/*.bin'))]
    assert len(protected)==307
    before={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected}
    roots=[ROOT/'validation/v0304-d5-supplies-sources']
    for stage in report['stages']:
        p=ROOT/stage['trace'];proof=p.with_name(p.name+f"-assisted-fixed-replay-{stage['frames']}")
        assert json.loads((proof/'replay_report.json').read_bytes())['passed']
        roots.extend([p,proof])
    roots += [ROOT/'validation'/name for name in [
        'natural-dungeon-route/md-v0304-d5-goldb4-route01','natural-dungeon-route/md-v0304-d5-goldb4-route02',
        'natural-dungeon-combat/md-auto-v0304-d5-contact01']]
    assert all(p.exists() and p.resolve().is_relative_to(ROOT/'validation') for p in roots)
    assert all('d5-boss01' not in p.name for p in roots)
    paths=[p for root in roots for p in root.rglob('*') if p.is_file()]
    inherited=[]
    for name,expected in report['evidence'].items():
        p=ROOT/name;assert sha(evidence(p))==expected
        if p.exists():paths.append(p)
        else:inherited.append(dict(path=name,sha256=expected))
    prefix=json.loads((ROOT/'analysis/d5_supplies_v0304_worklog_prefix.json').read_bytes())
    assert sha((ROOT/'analysis/world_next.md').read_bytes()[:prefix['prefix_bytes']])==prefix['prefix_sha256']
    paths += [ROOT/n for n in ['README.md','analysis/world_next.md','analysis/d5_supplies_v0304_report.json',
                              'analysis/d5_supplies_v0304.md','analysis/d5_supplies_v0304_source_index.json',
                              'analysis/d5_supplies_v0304_worklog_prefix.json',
                              'tools/archive_d5_supplies_v0304.py','tools/rebase_natural_campaign.py']]
    log_prefixes=('v0304-d5-golda1-','v0304-d5-goldb4-','v0304-d5-merchant94-',
                  'v0304-d5-keys94-','v0304-d5-return-','v0304-d5-warp01','v0304-d5-contact')
    paths += [p for p in (ROOT/'validation').iterdir() if p.is_file() and p.name.startswith(log_prefixes)]
    ready=ROOT/'validation/natural-dungeon-combat/md-auto-v0304-d5-contact02/ram_112233.bin'
    raw=ready.read_bytes()
    freeze(ROOT,ROOT/'analysis/d5-supplies-v0304',paths,
           dict(version=304,md_sha256=report['md_sha256'],protected_sha256=before,
                inherited_evidence=inherited,worklog_prefix=prefix,
                excluded_live_trace='natural-dungeon-combat/md-auto-v0304-d5-boss01'),roots,cleanup=True)
    ready.write_bytes(raw)
    assert before=={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected}
    from summarize_d5_supplies_v0304 import main as summarize
    old=(ROOT/'analysis/d5_supplies_v0304_report.json').read_bytes();summarize()
    assert (ROOT/'analysis/d5_supplies_v0304_report.json').read_bytes()==old
    assert (ROOT/'versions/v0304-b7b4e150/d5_supplies_v0304_report.json').read_bytes()==old
    print('All307 original/ROM files unchanged;supplies report identical after cleanup;live boss excluded;ready172 RAM retained')


if __name__=='__main__':main()
