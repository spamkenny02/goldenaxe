"""Prepare normal D8 payment, entrance and unassisted intermediate after audited D7."""
import ast
from pathlib import Path
root=Path(__file__).resolve().parents[2];project=root/'validation/c0046-campaign01/isolated/project'
s=(root/'validation/pal318-d8-entry01/run.py').read_text().replace('pal318','palc0046').replace('pal_d7_campaign_v0318_report.json','palc0046_d7_report.json').replace("receipt['seventh_crystal_and_exterior_return']","receipt['actual_seventh_crystal_and_exterior']").replace("receipt['md_sha256']","receipt['rom_sha256']")
s=s.replace('EVIDENCE=Path(__file__).resolve().parent',"EVIDENCE=ROOT/'validation/palc0046-d8-entry-sources'")
s=s.replace('    global STREAM\n', '    EVIDENCE.mkdir(exist_ok=False)\n    global STREAM\n',1)
s=s.replace("STREAM=ReplayStream(EVIDENCE/'cold-stream')", "STREAM=ReplayStream(ROOT/'validation/palc0046-d8-entry-cold-stream01')")
s=s.replace("source = 'md-pal-palc0046-d7-02-exit01'", "source = Path(receipt['current_campaign_trace']).name\n        assert source=='md-pal-palc0046-d7-01-exit01'")
s=s.replace("'continue_d8_entry_v0317.py'", "'continue_d8_entry_palc0046.py'")
s=s.replace("COMMON = ['--pal','--assisted-prefix'", "COMMON = ['--pal','--wake-sentinels','--retry-isolated-foes','--isolated-retry-limit','12','--assisted-prefix'")
p=project/'tools/continue_d8_entry_palc0046.py';assert not p.exists();ast.parse(s);p.write_text(s)
print('PAL D8 entry controller prepared; requires actual seventh crystal and exterior audit before execution')
