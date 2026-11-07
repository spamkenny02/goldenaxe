"""Prepare D9 giant, Balloon, main boss and ninth crystal from audited guardian victory."""
import ast
from pathlib import Path
root=Path(__file__).resolve().parents[2];project=root/'validation/c0046-campaign01/isolated/project'
s=(root/'validation/pal318-d9-finish01/run.py').read_text().replace('pal318','palc0046').replace('continue_d8_entry_v0317','continue_d8_entry_palc0046').replace('continue_d9_finish_v0317','continue_d9_finish_palc0046')
s=s.replace('helper.EVIDENCE=Path(__file__).resolve().parent',"helper.EVIDENCE=helper.ROOT/'validation/palc0046-d9-finish-sources'")
s=s.replace("ROOT / 'validation/palc0046-d9-entry02/cold-stream/checkpoints.json'", "ROOT / 'validation/palc0046-d9-entry-cold-stream01/completed.json'")
marker="    checkpoint = ROOT /"
s=s.replace(marker,"    audited=json.loads(evidence(ROOT/'analysis/palc0046_d9_midboss_report.json'))\n    assert audited['passed'] and audited['first_intermediate_defeated'] and not audited['intermediate_assistance'] and audited['rom_sha256']==sha((ROOT/'gaw-megadrive.bin').read_bytes())\n"+marker,1)
s=s.replace("helper.STREAM=ReplayStream(helper.EVIDENCE/'finish-cold-stream')", "helper.EVIDENCE.mkdir(exist_ok=False)\n    helper.STREAM=ReplayStream(ROOT/'validation/palc0046-d9-finish-cold-stream01')")
p=project/'tools/continue_d9_finish_palc0046.py';assert not p.exists();ast.parse(s);p.write_text(s)
print('D9 finish prepared; requires audited first guardian and current cold stream before emulation')
