"""Freeze terminal D7 diagnostics and alias tests; keep current D1 starting data."""
import json
from run_core import ROOT
from archive_lossless_evidence import freeze,sha


def main():
    names=['analysis/d7_passage_v0293_report.json','analysis/first_boss_alias_v0294_report.json','analysis/first_boss_alias_game_v0294_report.json','analysis/first_boss_variants_v0294_report.json']
    reports=[json.loads((ROOT/n).read_bytes()) for n in names]
    assert reports[0]['passed'] and reports[-1]['passed'] and reports[-1]['md_sha256']==sha((ROOT/'gaw-megadrive.bin').read_bytes())
    protected=[ROOT/'input/original.sms',ROOT/'gaw-megadrive.bin',ROOT/'gaw-title-megadrive.bin',*sorted((ROOT/'versions').glob('*/*.bin'))];assert len(protected)==297
    before={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected}
    roots=[ROOT/'validation/first-boss-alias-v0294',ROOT/'validation/natural-dungeon-combat/md-auto-v0294-d7-rebase01']
    roots += [p for p in (ROOT/'validation').iterdir() if p.is_dir() and p.name.startswith('first-boss-alias-v0294-')]
    for family in ['natural-dungeon-route','natural-dungeon-combat']:
        roots += [p for p in (ROOT/'validation'/family).iterdir() if p.is_dir() and (p.name.startswith('md-v0293-d7-') or p.name.startswith('md-auto-v0293-d7-'))]
    assert all(p.exists() and p.resolve().is_relative_to(ROOT/'validation') and 'v0294-d1' not in p.name for p in roots)
    paths=[p for folder in roots for p in folder.rglob('*') if p.is_file()]
    for report in [reports[0],reports[-1]]:paths += [ROOT/n for n in report['evidence'] if (ROOT/n).exists()]
    paths += [ROOT/n for n in names+['README.md','analysis/world_next.md','analysis/first_boss_variants_v0294.md','analysis/first_boss_variants_v0294_worklog_prefix.json','megadrive/out/release/symbol.txt']]
    paths += [ROOT/'tools'/n for n in ['archive_first_boss_variants_v0294.py','rebase_natural_campaign.py','rebase_assisted_campaign.py','natural_dungeon_combat.py','natural_earth_passage.py','assisted_boss_route.py','validate_first_boss.py','validate_first_boss_gameplay.py','first_boss_harness.c','first_boss_cases.inc','summarize_d7_passage_v0293.py','summarize_first_boss_variants_v0294.py']]
    paths += [p for p in (ROOT/'validation').iterdir() if p.is_file() and (p.name.startswith('v0293-d7-') or p.name.startswith('v0294-alias') or p.name in ['v0294-build.log','v0294-d7-rebase01.log'])]
    freeze(ROOT,ROOT/'analysis/first-boss-variants-v0294',paths,dict(version=294,md_sha256=reports[-1]['md_sha256'],protected_sha256=before,current_d1_starting_data_retained=True,full_game_validated=False),roots,cleanup=True)
    assert before=={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected}
    from summarize_d7_passage_v0293 import main as passage
    from summarize_first_boss_variants_v0294 import main as variants
    for name,fn in [(names[0],passage),(names[-1],variants)]:
        p=ROOT/name;raw=p.read_bytes();fn();assert p.read_bytes()==raw
    print('All297 original/ROM files unchanged; D7 and v294 summaries exact after cleanup; D1 start retained')


if __name__=='__main__':main()
