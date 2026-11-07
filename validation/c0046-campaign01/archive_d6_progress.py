"""Archive source-checked D6 keys, mechanisms, Earth and actual Ice Bell."""
import json
from pathlib import Path
import sys
sys.path.insert(0,'tools')
from run_core import ROOT
from archive_lossless_evidence import freeze,sha
work=Path(__file__).resolve().parent;project=work/'isolated/project'
report=ROOT/'analysis/d6_progress_c0046_report.json'
r=json.loads(report.read_bytes())
assert r['passed'] and r['ice_bell_acquired'] and len(r['stages'])==17
assert r['candidate']=='c0046' and not r['sixth_boss_entered'] and not r['full_game_validated']
paths={Path(__file__).resolve(),work/'prepare_d6.py',work/'prepare_d6_audit.py',
       work/'native_sources_setup.json',report,project/'tools/summarize_d6_progress_c0046.py'}
for name,h in r['evidence'].items():
    p=ROOT/name;assert sha(p.read_bytes())==h;paths.add(p)
snapshot=project/'validation/c0046-d6-sources02'
paths.update(p for p in snapshot.iterdir() if p.is_file())
for name,h in json.loads((snapshot/'source_index.json').read_bytes()).items():assert sha((snapshot/Path(name).name).read_bytes())==h
stream=snapshot/'cold-stream/completed.json'
s=json.loads(stream.read_bytes())
assert s['passed'] and s['cold_boot_count']==1 and s['rom_sha256']==r['md_sha256'] and len(s['checkpoints'])==17
assert all(p['whole_ram_png_exact'] for p in s['checkpoints'])
paths.add(stream)
freeze(ROOT,ROOT/'analysis/c0046-d6-progress',paths,r,[work])
print('D6 Ice Bell, real casts, keys and mechanisms archived',flush=True)
