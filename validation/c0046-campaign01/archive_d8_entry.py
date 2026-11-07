"""Archive actual paid passage and the unassisted eighth-dungeon intermediate."""
import json
from pathlib import Path
import sys
sys.path.insert(0,'tools')
from run_core import ROOT
from archive_lossless_evidence import freeze,sha
work=Path(__file__).resolve().parent;project=work/'isolated/project'
report=ROOT/'analysis/d8_midboss_c0046_report.json';r=json.loads(report.read_bytes())
assert r['passed'] and r['candidate']=='c0046' and r['intermediate_defeated'] and r['paid_horns']==10
assert not r['intermediate_assistance'] and not r['full_game_validated'] and not r['eighth_crystal_validated']
assert len(r['stages']) in (6,8) and r['prediction_windows']>0
paths={Path(__file__).resolve(),work/'prepare_d8_entry.py',report,project/'tools/summarize_d8_midboss_c0046.py'}
for name,h in r['evidence'].items():
    p=ROOT/name;assert sha(p.read_bytes())==h;paths.add(p)
snapshot=project/'validation/c0046-d8-sources/d8-entry-and-intermediate'
paths.update(p for p in snapshot.iterdir() if p.is_file())
for name,h in json.loads((snapshot/'source_index.json').read_bytes()).items():assert sha((snapshot/name).read_bytes())==h
stream=snapshot.parent/'cold-stream/completed.json';s=json.loads(stream.read_bytes())
assert s['passed'] and s['cold_boot_count']==1 and s['rom_sha256']==r['md_sha256'] and len(s['checkpoints'])==len(r['stages'])
assert all(p['whole_ram_png_exact'] for p in s['checkpoints'])
paths.add(stream)
freeze(ROOT,ROOT/'analysis/c0046-d8-midboss',paths,r,[work])
print('D8 paid passage and intermediate archived',flush=True)
