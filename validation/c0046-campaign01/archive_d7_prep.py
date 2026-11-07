"""Archive real D7 supplies and the first key and Earth mechanisms."""
import json
from pathlib import Path
import sys
sys.path.insert(0,'tools')
from run_core import ROOT
from archive_lossless_evidence import freeze,sha
work=Path(__file__).resolve().parent;project=work/'isolated/project'
report=ROOT/'analysis/d7_prep_c0046_report.json';r=json.loads(report.read_bytes())
assert r['passed'] and r['candidate']=='c0046' and r['original_crystals_retained']==6
assert r['keys_bought']==1 and r['key_price'] in (40,60) and r['earth_magic_spent']==16
assert not r['intermediate_boss_entered'] and not r['full_game_validated']
paths={Path(__file__).resolve(),work/'prepare_d7.py',report,project/'tools/summarize_d7_prep_c0046.py'}
for name,h in r['evidence'].items():
    p=ROOT/name;assert sha(p.read_bytes())==h;paths.add(p)
snapshot=project/'validation/run-c0046-d7-02'
paths.update(p for p in snapshot.iterdir() if p.is_file())
for name,h in json.loads((snapshot/'source_index.json').read_bytes()).items():assert sha((snapshot/Path(name).name).read_bytes())==h
stream=snapshot/'cold-stream/completed.json';s=json.loads(stream.read_bytes())
assert s['passed'] and s['cold_boot_count']==1 and s['rom_sha256']==r['md_sha256'] and len(s['checkpoints'])==len(r['stages'])
assert all(p['whole_ram_png_exact'] for p in s['checkpoints'])
paths.add(stream)
freeze(ROOT,ROOT/'analysis/c0046-d7-prep',paths,r,[work])
print('D7 ordinary supplies and preparation archived',flush=True)
