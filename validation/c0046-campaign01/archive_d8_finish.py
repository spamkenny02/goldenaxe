"""Archive both parts of the verified D8 main continuation."""
import json
from pathlib import Path
import sys
sys.path.insert(0,'tools')
from run_core import ROOT
from archive_lossless_evidence import freeze,sha
work=Path(__file__).resolve().parent;project=work/'isolated/project'
paths={Path(__file__).resolve(),work/'prepare_d8_finish.py'}
reports={}
for part in ['approach','campaign']:
    p=ROOT/f'analysis/d8_{part}_c0046_report.json';r=json.loads(p.read_bytes())
    assert r['passed'] and r['candidate']=='c0046' and not r['full_game_validated']
    reports[part]=r;paths.add(p);paths.add(project/f'tools/summarize_d8_{part}_c0046.py')
    for name,h in r['evidence'].items():
        p=ROOT/name;assert sha(p.read_bytes())==h;paths.add(p)
assert reports['approach']['thief_key_acquired'] and reports['campaign']['eighth_crystal_and_exterior_return']
snapshot=project/'validation/c0046-d8-sources/main-sources'
paths.update(p for p in snapshot.iterdir() if p.is_file())
for name,h in json.loads((snapshot/'source_index.json').read_bytes()).items():assert sha((snapshot/Path(name).name).read_bytes())==h
stream=snapshot/'cold-stream/completed.json';s=json.loads(stream.read_bytes())
assert s['passed'] and s['cold_boot_count']==1 and s['rom_sha256']==reports['campaign']['md_sha256'] and len(s['checkpoints'])==11
assert all(p['whole_ram_png_exact'] for p in s['checkpoints']);paths.add(stream)
freeze(ROOT,ROOT/'analysis/c0046-d8-campaign',paths,dict(passed=True,candidate='c0046',thief_key=True,eighth_crystal_and_exterior_return=True),[work])
print('D8 thief key, main boss and return archived',flush=True)
