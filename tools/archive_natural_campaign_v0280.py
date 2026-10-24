"""Archive current campaign attempts losslessly, preserving all numbered ROMs."""
import json
from run_core import ROOT
from archive_lossless_evidence import freeze,sha

def main():
 report=json.loads((ROOT/'analysis/natural_campaign_v0280_report.json').read_bytes());assert report['passed'] and not report['full_game_validated']
 assert report['md_sha256']==sha((ROOT/'gaw-megadrive.bin').read_bytes())
 prefix=json.loads((ROOT/'analysis/natural_campaign_v0280_worklog_prefix.json').read_bytes());assert sha((ROOT/'analysis/world_next.md').read_bytes()[:prefix['bytes']])==prefix['sha256']
 protected=[ROOT/'input/original.sms',ROOT/'gaw-megadrive.bin',ROOT/'gaw-title-megadrive.bin',*sorted((ROOT/'versions').glob('*/*.bin'))]
 before={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected};assert len(protected)==283
 roots=[p for family in ['natural-dungeon-route','natural-dungeon-combat'] for p in (ROOT/'validation'/family).glob('*v0280*') if p.is_dir()]
 roots += [ROOT/'validation/natural-v0280-pilot-baseline',ROOT/'validation/natural-v0280-pilot-experiment02']
 paths=[p for folder in roots for p in folder.rglob('*') if p.is_file()]
 paths += [ROOT/'tools'/n for n in ['natural_dungeon_combat.py','natural_combat_aim.py','rebase_natural_campaign.py','summarize_natural_campaign_v0280.py','archive_natural_campaign_v0280.py','replay_natural_campaign.py','natural_dungeon_route.py','run_core.py']]
 paths += [ROOT/'analysis'/n for n in ['natural_campaign_v0280.md','natural_campaign_v0280_report.json','natural_campaign_v0280_worklog_prefix.json','world_next.md']]
 paths += [ROOT/'README.md',ROOT/'megadrive/src/main.c',ROOT/'megadrive/src/actors.c',ROOT/'megadrive/out/release/symbol.txt']
 out=ROOT/'analysis/natural-campaign-v0280'
 m=freeze(ROOT,out,paths,dict(release=280,protected_sha256=before,purpose='Current first-dungeon axe/crystal/exit and exact fixed replay; unsuccessful source/MD D2 controller trials retained',whole_campaign_complete=False,second_crystal_verified=False),roots,cleanup=True)
 for name,digest in before.items():assert sha((ROOT/name).read_bytes())==digest
 original=(ROOT/'analysis/natural_campaign_v0280_report.json').read_bytes()
 import summarize_natural_campaign_v0280
 summarize_natural_campaign_v0280.main();assert (ROOT/'analysis/natural_campaign_v0280_report.json').read_bytes()==original
 print('280 numbered ROMs unchanged;verified raw bytes removed:',sum(v['bytes'] for v in m['removed_verified_generated']))

if __name__=='__main__':main()
