"""Prepare D8 mechanisms, ordinary thief key, source-strength main boss and exit."""
import ast
from pathlib import Path
root=Path(__file__).resolve().parents[2];project=root/'validation/c0046-campaign01/isolated/project'
s=(root/'validation/pal318-d8-finish01/run.py').read_text().replace('pal318','palc0046').replace('continue_d8_entry_v0317','continue_d8_entry_palc0046').replace('pal_d8_midboss_v0318_report.json','palc0046_d8_midboss_report.json')
s=s.replace('helper.EVIDENCE=Path(__file__).resolve().parent',"helper.EVIDENCE=helper.ROOT/'validation/palc0046-d8-finish-sources'")
s=s.replace("COMMON=['--pal','--assisted-prefix'", "COMMON=['--pal','--wake-sentinels','--retry-isolated-foes','--isolated-retry-limit','12','--assisted-prefix'")
s=s.replace("    snapshot=EVIDENCE/'main-sources';snapshot.mkdir()", "    assert receipt['rom_sha256']==sha((ROOT/'gaw-megadrive.bin').read_bytes())\n    EVIDENCE.mkdir(exist_ok=False)\n    snapshot=EVIDENCE/'main-sources';snapshot.mkdir()")
s=s.replace("'continue_d8_finish_v0317.py'", "'continue_d8_finish_palc0046.py'")
s=s.replace("STREAM=ReplayStream(snapshot/'cold-stream')", "STREAM=ReplayStream(ROOT/'validation/palc0046-d8-finish-cold-stream01')")
s=s.replace("for s in args]+['--pal']", "for s in args]+['--pal','--wake-sentinels','--retry-isolated-foes','--isolated-retry-limit','12']")
p=project/'tools/continue_d8_finish_palc0046.py';assert not p.exists();ast.parse(s);p.write_text(s)
print('D8 finish controller prepared; requires audited unassisted intermediate and immutable candidate ROM')
