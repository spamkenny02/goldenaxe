"""Archive the real gold gift, paid Earth lesson and shared cold replay."""
import json
from pathlib import Path
import sys
sys.path.insert(0,'tools')
from run_core import ROOT
from archive_lossless_evidence import freeze,sha
work=Path(__file__).resolve().parent;project=work/'isolated/project'
report=ROOT/'analysis/earth_learning_c0046_report.json'
r=json.loads(report.read_bytes())
assert r['passed'] and r['real_gold_gift']==r['real_earth_price']==50
assert r['earth_level']==1 and r['magic_capacity']==48
assert r['resource_writes']==r['primary_state_imports']==r['new_service_assistance_writes']==0
paths={Path(__file__).resolve(),report}
for name,h in r['evidence'].items():
    p=ROOT/name;assert sha(p.read_bytes())==h;paths.add(p)
snapshot=project/'validation/c0046-earth-learning-sources'
paths.update(p for p in snapshot.iterdir() if p.is_file())
index=json.loads((snapshot/'source_index.json').read_bytes())
for name,h in index.items():assert sha((snapshot/Path(name).name).read_bytes())==h
stream=project/'validation/c0046-earth-cold-stream/checkpoints.json'
s=json.loads(stream.read_bytes())
assert s['cold_boot_count']==1 and s['rom_sha256']==r['md_sha256'] and len(s['checkpoints'])==4
assert all(p['whole_ram_png_exact'] for p in s['checkpoints'])
paths.add(stream)
freeze(ROOT,ROOT/'analysis/c0046-earth-learning',paths,r,[work])
print('Earth purchase, real payment, HUD and cold replay archived',flush=True)
