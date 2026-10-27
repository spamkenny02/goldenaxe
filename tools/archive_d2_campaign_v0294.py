"""Freeze terminal v294 campaign evidence, including controller source variants."""
import json
from run_core import ROOT
from archive_lossless_evidence import freeze,sha


def main():
    names=['analysis/d1_campaign_v0294_report.json','analysis/d2_approach_v0294_report.json','analysis/d2_campaign_v0294_report.json']
    reports=[json.loads((ROOT/n).read_bytes()) for n in names]
    digest=sha((ROOT/'gaw-megadrive.bin').read_bytes())
    assert all(r['passed'] and r['md_sha256']==digest for r in reports) and reports[-1]['dungeon2_completed']
    protected=[ROOT/'input/original.sms',ROOT/'gaw-megadrive.bin',ROOT/'gaw-title-megadrive.bin',*sorted((ROOT/'versions').glob('*/*.bin'))];assert len(protected)==297
    before={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected}
    roots=[]
    for family in ['natural-dungeon-route','natural-dungeon-combat','natural-service-route']:
        roots += [p for p in (ROOT/'validation'/family).iterdir() if p.is_dir() and p.name.startswith(('md-v0294-d1-','md-v0294-d2-','md-v0294-fairy-','md-auto-v0294-d1-','md-auto-v0294-d2-'))]
    roots += [ROOT/'validation'/name for name in ['stack-v0294-d1-all','stack-v0294-d2-all','v0294-d2-sources']]
    assert all(p.exists() and p.resolve().is_relative_to(ROOT/'validation') for p in roots)
    paths=[p for folder in roots for p in folder.rglob('*') if p.is_file()]
    frozen=json.loads((ROOT/'analysis/d2_campaign_v0294_source_index.json').read_bytes())['sources'];aliases=[]
    for report in reports:
        for name,expected in report['evidence'].items():
            p=ROOT/name
            if not p.exists():continue
            actual=sha(p.read_bytes())
            if actual!=expected:
                match=next(v for v in frozen.values() if v['sha256']==expected)
                assert sha((ROOT/match['path']).read_bytes())==expected
                aliases.append(dict(original_path=name,expected_sha256=expected,frozen_path=match['path']))
            paths.append(p)
    paths += [ROOT/n for n in names+['README.md','analysis/world_next.md','analysis/d1_campaign_v0294.md','analysis/d2_approach_v0294.md','analysis/d2_campaign_v0294.md','analysis/d2_campaign_v0294_worklog_prefix.json','analysis/d2_campaign_v0294_source_index.json','analysis/actor_7c_v0294_pending.json']]
    paths += [ROOT/'tools'/name for name in ['archive_d2_campaign_v0294.py','summarize_d1_campaign_v0294.py','summarize_d2_approach_v0294.py','summarize_d2_campaign_v0294.py','clip_assisted_combat_prefix.py','natural_dungeon_combat.py','natural_fairy_service.py','rebase_natural_campaign.py','assisted_boss_route.py','replay_assisted_prefix.py','profile_playable_stack.py']]
    paths += [p for p in (ROOT/'validation').iterdir() if p.is_file() and p.name.startswith(('v0294-d1-','v0294-d2-','v0294-fairy-'))]
    prefix=json.loads((ROOT/'analysis/d2_campaign_v0294_worklog_prefix.json').read_bytes())
    assert sha((ROOT/'analysis/world_next.md').read_bytes()[:prefix['prefix_bytes']])==prefix['prefix_sha256']
    freeze(ROOT,ROOT/'analysis/d2-campaign-v0294',paths,dict(version=294,md_sha256=digest,native_two_crystals=True,protected_sha256=before,historical_source_aliases=aliases,older_summaries_frozen_not_recomputed=True,worklog_prefix=prefix),roots,cleanup=True)
    assert before=={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected}
    from summarize_d2_campaign_v0294 import main as summary
    p=ROOT/names[-1];raw=p.read_bytes();summary();assert p.read_bytes()==raw
    for name in names:assert (ROOT/name).read_bytes()==(ROOT/'versions/v0294-508642dc'/__import__('pathlib').Path(name).name).read_bytes()
    print('All297 original/ROM files unchanged; current D2 summary identical after cleanup; all three published records exact')


if __name__=='__main__':main()
