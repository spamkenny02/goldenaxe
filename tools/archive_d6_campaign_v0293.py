"""Freeze terminal D6 combat/exit evidence; retain the D7 starting captures."""
import json
from run_core import ROOT
from archive_lossless_evidence import freeze, sha


def main():
    names = ['analysis/d6_boss_v0293_report.json', 'analysis/d6_campaign_v0293_report.json', 'analysis/d7_entry_v0293_report.json']
    reports = [json.loads((ROOT/n).read_bytes()) for n in names]
    assert all(r['passed'] and r['md_sha256'] == sha((ROOT/'gaw-megadrive.bin').read_bytes()) for r in reports)
    protected = [ROOT/'input/original.sms', ROOT/'gaw-megadrive.bin', ROOT/'gaw-title-megadrive.bin', *sorted((ROOT/'versions').glob('*/*.bin'))]
    assert len(protected) == 296
    before = {p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected}
    base = ROOT/'validation/natural-dungeon-combat'
    stems = ['md-auto-v0293-d6-'+s for s in ['boss02','boss03','boss04','boss05','exit01','exit02','exit03']]
    roots = [p for p in base.iterdir() if p.is_dir() and any(p.name == s or p.name.startswith(s+'-assisted-fixed-replay-') for s in stems)]
    roots += [ROOT/'validation'/s for s in ['stack-v0293-d6-exit-all', 'stack-v0293-d6-exit-all02']]
    assert all(p.exists() and p.resolve().is_relative_to(ROOT/'validation') and 'd7' not in p.name for p in roots)
    paths = [p for folder in roots for p in folder.rglob('*') if p.is_file()]
    for report in reports:
        paths += [ROOT/n for n in report['evidence'] if (ROOT/n).exists()]
    paths += [p for p in (ROOT/'validation').iterdir() if p.is_file() and p.name.startswith(('v0293-d6-boss','v0293-d6-exit','v0293-d6-stack'))]
    paths += [ROOT/n for n in names+['README.md','analysis/world_next.md','analysis/d6_campaign_v0293.md','analysis/d6_campaign_v0293_worklog_prefix.json','megadrive/out/release/symbol.txt']]
    paths += [ROOT/'tools'/n for n in ['archive_d6_campaign_v0293.py','summarize_d6_boss_v0293.py','summarize_d6_campaign_v0293.py','summarize_d7_entry_v0293.py','natural_exit_planner.py','natural_dungeon_combat.py','natural_dungeon_route.py','assisted_boss_route.py','rebase_natural_campaign.py','replay_assisted_prefix.py','profile_playable_stack.py']]
    prefix=json.loads((ROOT/'analysis/d6_campaign_v0293_worklog_prefix.json').read_bytes())
    assert sha((ROOT/'analysis/world_next.md').read_bytes()[:prefix['prefix_bytes']]) == prefix['prefix_sha256']
    freeze(ROOT, ROOT/'analysis/d6-campaign-v0293', paths,
           dict(version=293, md_sha256=reports[0]['md_sha256'], dungeon6_completed=True,
                dungeon7_entered=True, dungeon7_captures_retained=True,
                protected_sha256=before, worklog_prefix=prefix), roots, cleanup=True)
    assert before == {p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected}
    from summarize_d6_boss_v0293 import main as boss
    from summarize_d6_campaign_v0293 import main as campaign
    from summarize_d7_entry_v0293 import main as entry
    for name, fn in zip(names, [boss,campaign,entry]):
        p=ROOT/name;raw=p.read_bytes();fn();assert p.read_bytes()==raw
    print('All296 original/ROM files preserved; three summaries exact after cleanup; D7 captures retained')


if __name__ == '__main__':
    main()
