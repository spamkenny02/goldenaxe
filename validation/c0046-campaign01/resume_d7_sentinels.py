"""Prepare a fresh D7 continuation that wakes source52 floor ambushers."""
from pathlib import Path
root=Path(__file__).resolve().parents[2]
project=root/'validation/c0046-campaign01/isolated/project'
source=project/'tools/continue_d7_finish_c0046.py'
text=source.read_text().replace('continue_d7_finish_c0046.py','resume_d7_finish_c0046.py')
text=text.replace('run-c0046-d7-finish-02','run-c0046-d7-finish-03')
text=text.replace("stage('south01'","stage('south02'")
before="['--equip-axe','--avoid-portal-rooms','0x1b7'],True,'room_cleared')"
after="['--equip-axe','--avoid-portal-rooms','0x1b7','--wake-sentinels','--retry-isolated-foes'],True,'room_cleared')"
assert text.count(before)==1;text=text.replace(before,after)
target=project/'tools/resume_d7_finish_c0046.py';assert not target.exists();target.write_text(text)
audit=project/'tools/summarize_d7_campaign_c0046.py';text=audit.read_text()
assert text.count("CASES = ('south01'")==1
text=text.replace("'south01'","'south02'").replace('run-c0046-d7-finish-02','run-c0046-d7-finish-03')
audit.write_text(text)
print('Fresh D7 continuation prepared with ordinary floor-ambusher search')
