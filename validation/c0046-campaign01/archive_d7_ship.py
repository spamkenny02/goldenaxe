"""Archive the successful ambusher route, remote mechanism and real ship reward."""
import json
from pathlib import Path
import sys
sys.path.insert(0,'tools')
from run_core import ROOT
from archive_lossless_evidence import freeze,sha
work=Path(__file__).resolve().parent;project=work/'isolated/project'
report=ROOT/'analysis/d7_ship_c0046_report.json';r=json.loads(report.read_bytes())
assert r['passed'] and r['candidate']=='c0046' and r['ship_acquired'] and len(r['stages'])==3
assert not r['seventh_crystal_and_exterior_return'] and not r['full_game_validated']
paths={Path(__file__).resolve(),work/'resume_d7_sentinels.py',report,project/'tools/summarize_d7_campaign_c0046.py'}
for name,h in r['evidence'].items():
    p=ROOT/name;assert sha(p.read_bytes())==h;paths.add(p)
snapshot=project/'validation/run-c0046-d7-finish-03'
# The command journal continues while the immutable source snapshot stays fixed.
for name,h in json.loads((snapshot/'source_index.json').read_bytes()).items():
    p=snapshot/Path(name).name;assert sha(p.read_bytes())==h;paths.add(p)
paths.add(snapshot/'source_index.json')
stream=snapshot/'cold-stream/checkpoints.json';s=json.loads(stream.read_bytes())
assert s['cold_boot_count']==1 and s['rom_sha256']==r['md_sha256'] and len(s['checkpoints'])>=3
assert all(p['whole_ram_png_exact'] for p in s['checkpoints'][:3])
assert [p['frames'] for p in s['checkpoints'][:3]]==[p['frame'] for p in r['stages']]
paths.add(stream)
failed=project/'validation/natural-dungeon-combat/md-auto-c0046-d7-02-south01/report.json'
f=json.loads(failed.read_bytes());assert f['failure']=='controller_stalled' and not f['deaths']
paths.add(failed)
freeze(ROOT,ROOT/'analysis/c0046-d7-ship',paths,r,[work])
print('D7 actual ship and source52 ambusher recovery archived',flush=True)
