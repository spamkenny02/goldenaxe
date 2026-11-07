"""Archive the actual reverse paid passage with eight crystals preserved."""
import json,sys
from pathlib import Path
sys.path.insert(0,'tools')
from run_core import ROOT
from archive_lossless_evidence import freeze,sha
work=Path(__file__).resolve().parent;project=work/'isolated/project'
report=ROOT/'analysis/d9_south_c0046_report.json';r=json.loads(report.read_bytes())
assert r['passed'] and r['candidate']=='c0046' and r['paid_south_return'] and r['real_price']==10
assert r['eight_crystals_preserved'] and len(r['stages'])==2 and not r['full_game_validated']
paths={Path(__file__).resolve(),work/'prepare_d9_south.py',report}
for name,h in r['evidence'].items():
    p=ROOT/name;assert sha(p.read_bytes())==h;paths.add(p)
base=project/'validation/c0046-d9-south-sources'
for name,h in json.loads((base/'source_index.json').read_bytes()).items():
    p=base/name;assert sha(p.read_bytes())==h;paths.add(p)
paths.add(base/'source_index.json')
done=base/'cold-stream/completed.json';s=json.loads(done.read_bytes())
assert s['passed'] and s['rom_sha256']==r['md_sha256'] and s['cold_boot_count']==1 and len(s['checkpoints'])==2
paths.add(done)
freeze(ROOT,ROOT/'analysis/c0046-d9-south',paths,r,[work])
print('Eight-crystal ordinary paid southern return archived',flush=True)
