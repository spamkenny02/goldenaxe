"""Freeze terminal v296 render/campaign evidence before generated-file cleanup."""
import json
from run_core import ROOT
from archive_lossless_evidence import freeze,sha


def main():
    report=json.loads((ROOT/'analysis/sprite_cache_v0296_report.json').read_bytes())
    assert report['passed'] and report['version']==296 and report['acquired_rope'] and not report['burst_slowdown_fixed']
    # Both unsuccessful boss diagnostics must be terminal before touching their captures.
    for trial in ['boss01','boss02']:
        failed=json.loads((ROOT/f'validation/natural-dungeon-combat/md-auto-v0296-d3-{trial}/report.json').read_bytes())
        assert failed['failure']=='continuation_route_died' and failed['deaths']==1 and not failed['room_cleared']
    protected=[ROOT/'input/original.sms',ROOT/'gaw-megadrive.bin',ROOT/'gaw-title-megadrive.bin',*sorted((ROOT/'versions').glob('*/*.bin'))]
    assert len(protected)==299
    before={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected}
    roots=[p for p in (ROOT/'validation').iterdir() if p.is_dir() and p.name.startswith(('cost-v0295-burst-','cost-v0296-burst-','sprite-mask-cache-','stack-v0296-','v0296-sources'))]
    roots += [p for p in (ROOT/'validation/natural-dungeon-combat').iterdir() if p.is_dir() and p.name.startswith('md-auto-v0296-')]
    assert roots and all(p.resolve().is_relative_to(ROOT/'validation') for p in roots)
    paths=[p for root in roots for p in root.rglob('*') if p.is_file()]
    paths += [ROOT/n for n in report['evidence']]
    paths += [p for p in (ROOT/'analysis').iterdir() if p.is_file() and ('v0296' in p.name or 'cost-v0295' in p.name)]
    paths += [ROOT/'README.md',ROOT/'analysis/world_next.md',ROOT/'tools/archive_sprite_cache_v0296.py',ROOT/'tools/rebase_natural_campaign.py']
    paths += [p for p in (ROOT/'validation').iterdir() if p.is_file() and p.name.startswith(('v0296-','cost-v0295','cost-v0296'))]
    ready_paths=[ROOT/'validation/natural-dungeon-combat/md-auto-v0296-d3-rope01/ram_45394.bin',
                 ROOT/'validation/natural-dungeon-combat/md-auto-v0296-d3-boss02/ram_48875.bin']
    ready={p:p.read_bytes() for p in ready_paths}
    prefix=json.loads((ROOT/'analysis/sprite_cache_v0296_worklog_prefix.json').read_bytes())
    assert sha((ROOT/'analysis/world_next.md').read_bytes()[:prefix['prefix_bytes']])==prefix['prefix_sha256']
    freeze(ROOT,ROOT/'analysis/sprite-cache-v0296',paths,
           dict(version=296,md_sha256=report['md_sha256'],protected_sha256=before,
                burst_slowdown_still_open=True,third_boss_attempts_lost=2,worklog_prefix=prefix),roots,cleanup=True)
    for path,raw in ready.items():path.write_bytes(raw)
    assert before=={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected}
    from summarize_sprite_cache_v0296 import main as summary
    old=(ROOT/'analysis/sprite_cache_v0296_report.json').read_bytes();summary()
    assert (ROOT/'analysis/sprite_cache_v0296_report.json').read_bytes()==old
    assert (ROOT/'versions/v0296-3446f41f/sprite_cache_v0296_report.json').read_bytes()==old
    print('All299 original/ROM files unchanged; summary identical after cleanup; two final RAM files retained for planning')


if __name__=='__main__':main()
