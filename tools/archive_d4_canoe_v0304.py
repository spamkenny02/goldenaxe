"""Freeze completed canoe evidence only; exclude the separately running boss."""
import json
from run_core import ROOT
from archive_lossless_evidence import freeze,sha
from rebase_natural_campaign import evidence


def main():
    report=json.loads((ROOT/'analysis/d4_canoe_v0304_report.json').read_bytes())
    assert report['passed'] and report['canoe_acquired'] and not report['fourth_crystal_validated']
    protected=[ROOT/'input/original.sms',ROOT/'gaw-megadrive.bin',ROOT/'gaw-title-megadrive.bin',
               *sorted((ROOT/'versions').glob('*/*.bin'))]
    assert len(protected)==307
    before={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected}
    roots=[]
    for stage in report['stages']:
        p=ROOT/stage['trace'];proof=p.with_name(p.name+f"-assisted-fixed-replay-{stage['frames']}")
        assert json.loads((proof/'replay_report.json').read_bytes())['passed']
        roots.extend([p,proof])
    assert all(p.exists() and p.resolve().is_relative_to(ROOT/'validation') for p in roots)
    assert all('d4-boss01' not in p.name for p in roots)
    paths=[p for root in roots for p in root.rglob('*') if p.is_file()]
    inherited=[]
    for name,expected in report['evidence'].items():
        p=ROOT/name;assert sha(evidence(p))==expected
        if p.exists():paths.append(p)
        else:inherited.append(dict(path=name,sha256=expected))
    prefix=json.loads((ROOT/'analysis/d4_canoe_v0304_worklog_prefix.json').read_bytes())
    assert sha((ROOT/'analysis/world_next.md').read_bytes()[:prefix['prefix_bytes']])==prefix['prefix_sha256']
    paths += [ROOT/n for n in ['README.md','analysis/world_next.md','analysis/d4_canoe_v0304_report.json',
                              'analysis/d4_canoe_v0304.md','analysis/d4_canoe_v0304_worklog_prefix.json',
                              'tools/archive_d4_canoe_v0304.py','tools/rebase_natural_campaign.py']]
    paths += [p for p in (ROOT/'validation').iterdir() if p.is_file() and p.name.startswith(
        ('v0304-d4-a1-key02','v0304-d4-canoe01','v0304-d4-warp01','v0304-d4-boss-key01'))]
    ready=ROOT/'validation/natural-dungeon-combat/md-auto-v0304-d4-boss-key01/ram_76662.bin'
    raw=ready.read_bytes()
    freeze(ROOT,ROOT/'analysis/d4-canoe-v0304',paths,
           dict(version=304,md_sha256=report['md_sha256'],protected_sha256=before,
                inherited_evidence=inherited,worklog_prefix=prefix,excluded_live_trace='natural-dungeon-combat/md-auto-v0304-d4-boss01'),
           roots,cleanup=True)
    ready.write_bytes(raw)
    assert before=={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected}
    from summarize_d4_canoe_v0304 import main as summarize
    old=(ROOT/'analysis/d4_canoe_v0304_report.json').read_bytes();summarize()
    assert (ROOT/'analysis/d4_canoe_v0304_report.json').read_bytes()==old
    assert (ROOT/'versions/v0304-b7b4e150/d4_canoe_v0304_report.json').read_bytes()==old
    print('All307 ROM files unchanged;canoe report identical after cleanup;live boss excluded;key-prefix RAM retained')


if __name__=='__main__':main()
