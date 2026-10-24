"""Lossless natural fairy/D2 evidence cleanup; every cartridge stays intact."""
import gzip,json,subprocess
from run_core import ROOT
from archive_lossless_evidence import freeze,sha

def main():
 report=json.loads((ROOT/'analysis/fairy_campaign_v0280_report.json').read_bytes());assert report['passed'] and not report['full_game_validated'] and report['md_sha256']==sha((ROOT/'gaw-megadrive.bin').read_bytes())
 prefix=json.loads((ROOT/'analysis/fairy_campaign_v0280_worklog_prefix.json').read_bytes());assert sha((ROOT/'analysis/world_next.md').read_bytes()[:prefix['bytes']])==prefix['sha256']
 protected=[ROOT/'input/original.sms',ROOT/'gaw-megadrive.bin',ROOT/'gaw-title-megadrive.bin',*sorted((ROOT/'versions').glob('*/*.bin'))]
 before={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected};assert len(protected)==283
 roots=[]
 for family,pattern in [('natural-dungeon-route','*v0280-fairy-c9-01'),('natural-dungeon-route','*v0280-d2-after-fairy01'),('natural-service-route','*v0280-fairy-c9-01*'),('natural-dungeon-combat','*-auto-v0280-d2-fairy-*')]:roots += [p for p in (ROOT/'validation'/family).glob(pattern) if p.is_dir()]
 roots += [p for p in (ROOT/'validation').glob('natural-v0280-fairy*-baseline') if p.is_dir()]
 failed=[p for p in roots if p.parent.name=='natural-dungeon-combat' and json.loads((p/'report.json').read_bytes())['failure']]
 paths=[p for folder in roots for p in folder.rglob('*') if p.is_file()]
 paths += [ROOT/'tools'/n for n in ['natural_dungeon_route.py','natural_dungeon_combat.py','natural_combat_aim.py','natural_fairy_service.py','summarize_fairy_campaign_v0280.py','archive_fairy_campaign_v0280.py','replay_natural_campaign.py','run_core.py']]
 paths += [ROOT/'analysis'/n for n in ['fairy_campaign_v0280.md','fairy_campaign_v0280_report.json','fairy_campaign_v0280_worklog_prefix.json','world_next.md','fairy_reference.json','room_puzzles_reference.json']]
 paths += [ROOT/'README.md',ROOT/'megadrive/src/main.c',ROOT/'megadrive/src/actors.c',ROOT/'megadrive/out/release/symbol.txt']
 out=ROOT/'analysis/fairy-campaign-v0280';m=freeze(ROOT,out,paths,dict(release=280,protected_sha256=before,purpose='Natural SMS/MD C9 life capacity and fixed replays;negative D2 trials retained',whole_campaign_complete=False),roots,cleanup=True)
 tracked=set(subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0'))
 # Large failed-trial button/capture manifests and PNGs are also recoverable.
 # Retain each report as an index; successful prefixes remain usable directly.
 for folder in failed:
  folder=folder.resolve();assert folder.is_relative_to(ROOT/'validation/natural-dungeon-combat')
  for path in sorted(folder.rglob('*')):
   if not path.is_file() or path.name=='report.json' or path.suffix not in ['.json','.png']:continue
   resolved=path.resolve();assert resolved.is_relative_to(folder);name=resolved.relative_to(ROOT).as_posix();assert name not in tracked
   item=m['compressed'][name];encoded=(out/item['stored']).read_bytes();raw=resolved.read_bytes();assert sha(encoded)==item['stored_sha256'] and sha(raw)==item['raw_sha256'] and gzip.decompress(encoded)==raw
   resolved.unlink();m['removed_verified_generated'].append(dict(path=name,bytes=len(raw)))
 for name,digest in before.items():assert sha((ROOT/name).read_bytes())==digest
 m['removed_verified_generated_bytes']=sum(v['bytes'] for v in m['removed_verified_generated']);(out/'manifest.json').write_bytes((json.dumps(m,indent=2)+'\n').encode())
 original=(ROOT/'analysis/fairy_campaign_v0280_report.json').read_bytes()
 import summarize_fairy_campaign_v0280
 summarize_fairy_campaign_v0280.main();assert (ROOT/'analysis/fairy_campaign_v0280_report.json').read_bytes()==original
 print('280 numbered ROMs unchanged;verified raw bytes removed:',m['removed_verified_generated_bytes'])

if __name__=='__main__':main()
