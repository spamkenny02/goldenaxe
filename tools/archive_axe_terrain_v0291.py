"""Freeze source/native axe fixtures and natural first-teacher/gold routes."""
import json
from run_core import ROOT
from archive_lossless_evidence import freeze,sha

def main():
 report=json.loads((ROOT/'analysis/axe_terrain_v0291_report.json').read_bytes());assert report['passed'] and report['md_sha256']==sha((ROOT/'gaw-megadrive.bin').read_bytes())
 prefix=json.loads((ROOT/'analysis/axe_terrain_v0291_worklog_prefix.json').read_bytes());assert sha((ROOT/'analysis/world_next.md').read_bytes()[:prefix['bytes']])==prefix['sha256']
 protected=[ROOT/'input/original.sms',ROOT/'gaw-megadrive.bin',ROOT/'gaw-title-megadrive.bin',*sorted((ROOT/'versions').glob('*/*.bin'))];assert len(protected)==294
 before={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected};roots=[]
 for family in ['natural-dungeon-route','natural-service-route']:roots.extend(p for p in (ROOT/'validation'/family).glob('*v0291*') if p.is_dir())
 for pattern in ['axe-terrain*','stack-v0291*','v0290-historical-build']:roots.extend(p for p in (ROOT/'validation').glob(pattern) if p.is_dir())
 roots=sorted(set(roots));paths=[p for d in roots for p in d.rglob('*') if p.is_file()];paths.extend(ROOT/n for n in report['evidence'] if (ROOT/n).exists())
 paths.extend(p for p in (ROOT/'validation').glob('*') if p.is_file() and ('v0291' in p.name or 'axe-terrain' in p.name))
 paths.extend(ROOT/'megadrive/out/release'/n for n in ['rom.bin','rom.out','symbol.txt'])
 paths.extend(ROOT/'megadrive/src'/n for n in ['main.c','source_axe_terrain.c','source_axe_terrain.h','axe_terrain_data.c'])
 names=['generate_axe_terrain.py','validate_axe_terrain_probes.py','validate_axe_terrain_game.py','validate_axe_terrain_publication.py','summarize_axe_terrain_v0291.py','archive_axe_terrain_v0291.py','natural_dungeon_route.py','natural_house_service.py','replay_natural_campaign.py','rebase_natural_campaign.py','run_core.py','profile_playable_stack.py','archive_lossless_evidence.py']
 paths.extend(ROOT/'tools'/n for n in names)
 paths.extend(ROOT/n for n in ['build.ps1','README.md','analysis/world_next.md','analysis/axe_terrain_v0291.md','analysis/axe_terrain_v0291_report.json','analysis/axe_terrain_v0291_worklog_prefix.json','analysis/axe_terrain_probes_v0291_report.json','analysis/axe_terrain_game_v0291-02_report.json','analysis/axe_terrain_game_v0290-baseline_report.json','analysis/axe_terrain_publication_v0291_report.json'])
 manifest=freeze(ROOT,ROOT/'analysis/axe-terrain-v0291',paths,dict(md_sha256=report['md_sha256'],full_game_validated=False,numbered_roms_preserved=291,protected_sha256=before,large_observations_cleanup_threshold_bytes=1048576),roots,cleanup=True)
 for name,digest in before.items():assert sha((ROOT/name).read_bytes())==digest
 from validate_axe_terrain_publication import main as publication
 from summarize_axe_terrain_v0291 import main as summarize
 for path,fn in [(ROOT/'analysis/axe_terrain_publication_v0291_report.json',publication),(ROOT/'analysis/axe_terrain_v0291_report.json',summarize)]:
  raw=path.read_bytes();fn();assert path.read_bytes()==raw
 print('Verified generated cleanup bytes:',sum(v['bytes'] for v in manifest['removed_verified_generated']))
if __name__=='__main__':main()
