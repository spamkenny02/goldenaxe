"""Archive the real thief key and eight verified approach endpoints."""
import json
from pathlib import Path
import sys
sys.path.insert(0,'tools')
from run_core import ROOT
from archive_lossless_evidence import freeze,sha
work=Path(__file__).resolve().parent;project=work/'isolated/project'
report=ROOT/'analysis/d8_approach_c0046_report.json';r=json.loads(report.read_bytes())
assert r['passed'] and r['candidate']=='c0046' and r['thief_key_acquired'] and len(r['stages'])==8
assert r['defeated_intermediate_not_respawned'] and not r['eighth_boss_entered'] and not r['eighth_crystal_obtained']
paths={Path(__file__).resolve(),work/'prepare_d8_finish.py',report,project/'tools/summarize_d8_approach_c0046.py'}
for name,h in r['evidence'].items():
    p=ROOT/name;assert sha(p.read_bytes())==h;paths.add(p)
snapshot=project/'validation/c0046-d8-sources/main-sources'
index=snapshot/'source_index.json';paths.add(index)
for name,h in json.loads(index.read_bytes()).items():
    p=snapshot/Path(name).name;assert sha(p.read_bytes())==h;paths.add(p)
stream=snapshot/'cold-stream/checkpoints.json';s=json.loads(stream.read_bytes())
assert s['cold_boot_count']==1 and s['rom_sha256']==r['md_sha256'] and len(s['checkpoints'])>=8
assert all(p['whole_ram_png_exact'] for p in s['checkpoints'][:8])
assert [p['frames'] for p in s['checkpoints'][:8]]==[p['frames'] for p in r['stages']]
paths.add(stream)
freeze(ROOT,ROOT/'analysis/c0046-d8-approach',paths,r,[work])
print('D8 thief key and main-boss approach archived; no eighth-crystal claim',flush=True)
