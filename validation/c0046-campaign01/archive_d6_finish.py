"""Archive the sixth source-stat boss, crystal and exterior return."""
import json
from pathlib import Path
import sys
sys.path.insert(0,'tools')
from run_core import ROOT
from archive_lossless_evidence import freeze,sha
work=Path(__file__).resolve().parent;project=work/'isolated/project'
report=ROOT/'analysis/d6_campaign_c0046_report.json'
r=json.loads(report.read_bytes())
assert r['passed'] and r['sixth_crystal_and_exterior_return'] and r['owned_crystal_markers']==6
assert r['candidate']=='c0046' and not r['full_game_validated']
paths={Path(__file__).resolve(),work/'prepare_d6_finish.py',report,project/'tools/summarize_d6_campaign_c0046.py'}
for name,h in r['evidence'].items():
    p=ROOT/name;assert sha(p.read_bytes())==h;paths.add(p)
snapshot=project/'validation/c0046-d6-finish-sources'
paths.update(p for p in snapshot.iterdir() if p.is_file())
for name,h in json.loads((snapshot/'source_index.json').read_bytes()).items():assert sha((snapshot/Path(name).name).read_bytes())==h
stream=snapshot/'cold-stream/completed.json'
s=json.loads(stream.read_bytes())
assert s['passed'] and s['cold_boot_count']==1 and s['rom_sha256']==r['md_sha256'] and len(s['checkpoints'])==3
assert all(p['whole_ram_png_exact'] for p in s['checkpoints'])
paths.add(stream)
freeze(ROOT,ROOT/'analysis/c0046-d6-campaign',paths,r,[work])
print('Sixth boss, crystal and exterior return archived',flush=True)
