"""Freeze v289 D2 and v290 teacher evidence before verified generated cleanup."""
import json
from run_core import ROOT
from archive_lossless_evidence import freeze,sha

def main():
 report=json.loads((ROOT/'analysis/spell_teacher_v0290_report.json').read_bytes());old=json.loads((ROOT/'analysis/d2_campaign_v0289_report.json').read_bytes());assert report['passed'] and old['passed'] and report['md_sha256']==sha((ROOT/'gaw-megadrive.bin').read_bytes())
 prefix=json.loads((ROOT/'analysis/spell_teacher_v0290_worklog_prefix.json').read_bytes());assert sha((ROOT/'analysis/world_next.md').read_bytes()[:prefix['bytes']])==prefix['sha256']
 protected=[ROOT/'input/original.sms',ROOT/'gaw-megadrive.bin',ROOT/'gaw-title-megadrive.bin',*sorted((ROOT/'versions').glob('*/*.bin'))];assert len(protected)==293
 before={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected};roots=[]
 for family,patterns in [('natural-dungeon-route',['*v0289-fairy*','*v0289-d2*','*v0290*']),('natural-service-route',['*v0289-fairy*']),('natural-dungeon-combat',['*v0289-d2*'])]:
  for pattern in patterns:roots.extend(p for p in (ROOT/'validation'/family).glob(pattern) if p.is_dir())
 for pattern in ['spell-teacher*','stack-v0290-d1-all']:roots.extend(p for p in (ROOT/'validation').glob(pattern) if p.is_dir())
 roots=sorted(set(roots));paths=[p for d in roots for p in d.rglob('*') if p.is_file()]
 for r in [report,old]:paths.extend(ROOT/n for n in r['evidence'] if (ROOT/n).exists())
 paths.extend(p for p in (ROOT/'validation').glob('*') if p.is_file() and any(v in p.name for v in ['v0290','v0289-d2','v0289-fairy','spell-teacher']))
 paths.extend(ROOT/'megadrive/out/release'/n for n in ['rom.bin','rom.out','symbol.txt'])
 paths.extend(ROOT/'megadrive/src'/n for n in ['main.c','save.inc','source_spell_teacher.c','source_spell_teacher.h','spell_teacher.inc','spell_teacher_data.c'])
 names=['extract_spell_teacher.py','validate_spell_teacher_policy.py','validate_spell_teacher_game.py','summarize_spell_teacher_v0290.py','summarize_d2_campaign_v0289.py','archive_spell_teacher_v0290.py','assisted_boss_route.py','natural_dungeon_route.py','natural_dungeon_combat.py','natural_fairy_service.py','replay_natural_campaign.py','replay_assisted_prefix.py','replay_assisted_boss.py','rebase_natural_campaign.py','run_core.py','profile_playable_stack.py','archive_lossless_evidence.py']
 paths.extend(ROOT/'tools'/n for n in names)
 names=['build.ps1','README.md','analysis/world_next.md','analysis/spell_teacher_v0290.md','analysis/spell_teacher_v0290_report.json','analysis/spell_teacher_v0290_worklog_prefix.json','analysis/d2_campaign_v0289_report.json','analysis/spell_teacher_assets.json','analysis/spell_teacher_policy_report.json','analysis/spell_teacher_portraits_v0290_report.json']
 paths.extend(ROOT/n for n in names);paths.extend((ROOT/'analysis').glob('spell_teacher_game*_report.json'))
 manifest=freeze(ROOT,ROOT/'analysis/spell-teacher-v0290',paths,dict(md_sha256=report['md_sha256'],historical_md_sha256=old['md_sha256'],full_game_validated=False,numbered_roms_preserved=290,protected_sha256=before),roots,cleanup=True)
 for name,digest in before.items():assert sha((ROOT/name).read_bytes())==digest
 from summarize_d2_campaign_v0289 import main as summarize_old
 from summarize_spell_teacher_v0290 import main as summarize_new
 for path,fn in [(ROOT/'analysis/d2_campaign_v0289_report.json',summarize_old),(ROOT/'analysis/spell_teacher_v0290_report.json',summarize_new)]:
  raw=path.read_bytes();fn();assert path.read_bytes()==raw
 print('Verified generated cleanup bytes:',sum(v['bytes'] for v in manifest['removed_verified_generated']))
if __name__=='__main__':main()
