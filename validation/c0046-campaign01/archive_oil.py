"""Archive the independently audited real c0046 oil gift."""
import json,sys
from pathlib import Path
sys.path.insert(0,'tools')
from run_core import ROOT
from archive_lossless_evidence import freeze,sha
work=Path(__file__).resolve().parent
project=work/'isolated/project'
report=ROOT/'analysis/oil_service_c0046_report.json'
result=json.loads(report.read_bytes())
assert result['passed'] and result['real_oil_gift'] and result['physical_hud_words_exact']==128
assert result['resource_writes']==result['primary_state_imports']==result['new_test_writes']==0
paths={report,Path(__file__).resolve(),project/'tools/continue_oil_c0046.py',project/'tools/summarize_oil_service_c0046.py'}
for name,digest in result['evidence'].items():
    path=ROOT/name;assert sha(path.read_bytes())==digest
    paths.add(path)
snapshot=project/'validation/c0046-oil-sources'
paths.update(p for p in snapshot.iterdir() if p.is_file())
index=json.loads((snapshot/'source_index.json').read_bytes())
for name,digest in index.items():assert sha((snapshot/Path(name).name).read_bytes())==digest
freeze(ROOT,ROOT/'analysis/c0046-oil-service',paths,result,[work])
print('Oil gift, stairs, preserved resources and HUD archived',flush=True)
