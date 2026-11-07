"""Prepare real D7 ship acquisition, main boss, seventh crystal and exterior return."""
import ast
from pathlib import Path
root=Path(__file__).resolve().parents[2];project=root/'validation/c0046-campaign01/isolated/project'
s=(root/'validation/pal318-d7-finish01/run.py').read_text().replace('pal318','palc0046').replace('pal_d7_midboss_v0318_report.json','palc0046_d7_midboss_report.json').replace("prior['md_sha256']","prior['rom_sha256']").replace("prefix='palc0046-d7-02-'","prefix='palc0046-d7-01-'")
s=s.replace("previous=prior['stages'][-1]['trace'].split('/')[-1]", "previous=Path(prior['current_campaign_trace']).name")
s=s.replace('out=Path(__file__).resolve().parent', "out=ROOT/'validation/palc0046-d7-finish-sources'\n    out.mkdir(exist_ok=False)").replace("'continue_d7_finish_v0317.py'","'continue_d7_finish_palc0046.py'")
s=s.replace("stream=ReplayStream(out/'cold-stream')", "stream=ReplayStream(ROOT/'validation/palc0046-d7-finish-cold-stream01')")
s=s.replace("common=['--pal','--assisted-prefix'", "common=['--pal','--wake-sentinels','--retry-isolated-foes','--isolated-retry-limit','12','--assisted-prefix'")
p=project/'tools/continue_d7_finish_palc0046.py';assert not p.exists();ast.parse(s);p.write_text(s)
print('D7 finish controller prepared; execution requires the audited unassisted intermediate victory')
