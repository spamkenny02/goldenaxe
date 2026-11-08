"""Prepare the remaining PAL palace from a verified, unassisted first giant."""
import ast
from pathlib import Path

root = Path(__file__).resolve().parents[2]
project = root / 'validation/c0046-campaign01/isolated/project'
s = (root / 'validation/pal318-palace-inner01/run.py').read_text().replace('pal318', 'palc0046')
s = s.replace('continue_d8_entry_v0317', 'continue_d8_entry_palc0046')
for phase in ('inner', 'guardian', 'final'):
    s = s.replace(f'continue_palace_{phase}_v0317', f'continue_palace_{phase}_c0046')
s = s.replace('work=Path(__file__).resolve().parent',
              "work=ROOT/'validation/palc0046-pal-palace-inner-sources'")
s = s.replace("ROOT/'validation/palc0046-palace01/cold-stream/checkpoints.json'",
              "ROOT/'validation/palc0046-pal-palace-entry-sources/cold-stream/completed.json'")
marker = "    digest=sha((ROOT/'gaw-megadrive.bin').read_bytes())"
s = s.replace(marker, marker + """
    audited=json.loads((ROOT/'analysis/palc0046_palace_giant_report.json').read_bytes())
    assert audited['passed'] and audited['giant_defeated'] and audited['rom_sha256']==digest
""", 1)
s = s.replace("    assert proof['rom_sha256']==digest and proof['cold_boot_count']==1",
              "    assert proof['passed'] and proof['rom_sha256']==digest and proof['cold_boot_count']==1")
s = s.replace("'continue_d8_entry_palc0046.py','cold_replay_stream.py')",
              "'continue_d8_entry_palc0046.py','cold_replay_stream.py',"
              "'continue_pal_palace_inner_c0046.py','run_core.py')")
s = s.replace("    helper.STREAM=ReplayStream(work/'cold-stream')",
              "    work.mkdir(exist_ok=False)\n    helper.STREAM=ReplayStream(work/'cold-stream')")
target = project / 'tools/continue_pal_palace_inner_c0046.py'
assert not target.exists(), target
ast.parse(s)
target.write_text(s)
print('PAL palace interior prepared, gated on the audited first giant and completed cold stream.')
