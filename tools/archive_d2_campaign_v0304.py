"""Freeze closed D2 milestones; exclude the live D3 continuation explicitly."""
import json
from run_core import ROOT
from archive_lossless_evidence import freeze,sha


def main():
    report=json.loads((ROOT/'analysis/d2_campaign_v0304_report.json').read_bytes())
    assert report['passed'] and report['second_crystal_and_exterior_exit'] and not report['full_game_validated']
    protected=[ROOT/'input/original.sms',ROOT/'gaw-megadrive.bin',ROOT/'gaw-title-megadrive.bin',*sorted((ROOT/'versions').glob('*/*.bin'))]
    assert len(protected)==307
    before={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected}
    roots=[]
    for stage in report['stages']:
        root=ROOT/stage['trace'];roots.extend([root,root.with_name(root.name+f"-assisted-fixed-replay-{stage['frames']}")])
    roots += [ROOT/'validation/stack-v0304-d2-all',ROOT/'validation/v0304-d2-sources',
              ROOT/'validation/natural-dungeon-combat/md-auto-v0304-d2-boss01']
    # This bounded combat is terminal and independently replayed; it is an alive
    # partial prefix, not a third-boss victory. boss02 may still be running.
    partial=ROOT/'validation/natural-dungeon-combat/md-auto-v0304-d3-boss01'
    capture=json.loads((partial/'capture.json').read_bytes());failed=json.loads((partial/'report.json').read_bytes())
    proof=json.loads(partial.with_name(partial.name+f"-assisted-fixed-replay-{capture['frames']}").joinpath('replay_report.json').read_bytes())
    assert failed['failure']=='frame_limit' and failed['last_state']['health']==39 and not failed['room_cleared'] and proof['passed']
    roots.extend([partial,partial.with_name(partial.name+f"-assisted-fixed-replay-{capture['frames']}")])
    assert all(p.exists() and p.resolve().is_relative_to(ROOT/'validation') for p in roots)
    assert all('md-auto-v0304-d3-boss02' not in p.as_posix() for p in roots)
    paths=[p for root in roots for p in root.rglob('*') if p.is_file()]
    paths += [ROOT/name for name in report['evidence']]
    paths += [ROOT/n for n in ['README.md','analysis/world_next.md','analysis/burst_cadence_v0304.md',
              'analysis/d2_campaign_v0304.md','analysis/d2_campaign_v0304_report.json',
              'analysis/d2_campaign_v0304_source_index.json','analysis/d2_campaign_v0304_worklog_prefix.json',
              'tools/archive_d2_campaign_v0304.py','tools/rebase_natural_campaign.py']]
    prefixes=['v0304-d1-return-axe','v0304-d1-axe','v0304-fairy','v0304-d2-','v0304-d3-entry','v0304-d3-rope','v0304-d3-boss01-']
    paths += [p for p in (ROOT/'validation').iterdir() if p.is_file() and any(p.name.startswith(n) for n in prefixes)]
    latest=ROOT/'validation/natural-dungeon-combat/md-auto-v0304-d3-rope01/ram_44800.bin';ready=latest.read_bytes()
    prefix=json.loads((ROOT/'analysis/d2_campaign_v0304_worklog_prefix.json').read_bytes())
    assert sha((ROOT/'analysis/world_next.md').read_bytes()[:prefix['prefix_bytes']])==prefix['prefix_sha256']
    freeze(ROOT,ROOT/'analysis/d2-campaign-v0304',paths,
           dict(version=304,md_sha256=report['md_sha256'],protected_sha256=before,
                two_crystals_verified=True,live_d3_continuation_excluded=True,worklog_prefix=prefix),roots,cleanup=True)
    latest.write_bytes(ready)
    assert before=={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected}
    from summarize_d2_campaign_v0304 import main as summary
    old=(ROOT/'analysis/d2_campaign_v0304_report.json').read_bytes();summary()
    assert (ROOT/'analysis/d2_campaign_v0304_report.json').read_bytes()==old
    assert (ROOT/'versions/v0304-b7b4e150/d2_campaign_v0304_report.json').read_bytes()==old
    print('All307 original/ROM files unchanged; summary identical after cleanup; D3 boss02 untouched')


if __name__=='__main__':main()
