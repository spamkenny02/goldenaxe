"""Prepare the PAL palace route from the audited ninth crystal, without importing state."""
import ast
from pathlib import Path

root = Path(__file__).resolve().parents[2]
project = root / 'validation/c0046-campaign01/isolated/project'
source = root / 'validation/pal318-palace01/run.py'
s = source.read_text().replace('pal318', 'palc0046')
s = s.replace('continue_d8_entry_v0317', 'continue_d8_entry_palc0046')
s = s.replace('continue_after_d9_v0317', 'continue_after_d9_c0046')
s = s.replace('continue_palace_giant_v0317', 'continue_palace_giant_c0046')
s = s.replace('work=Path(__file__).resolve().parent',
              "work=ROOT/'validation/palc0046-pal-palace-entry-sources'")
s = s.replace("ROOT/'validation/palc0046-d9-finish01/finish-cold-stream/checkpoints.json'",
              "ROOT/'validation/palc0046-d9-funded-finish-cold-stream01/completed.json'")
marker = "    digest=sha((ROOT/'gaw-megadrive.bin').read_bytes())"
assert marker in s
s = s.replace(marker, marker + """
    audited=json.loads((ROOT/'analysis/palc0046_d9_report.json').read_bytes())
    published=json.loads((ROOT/'analysis/pal_d9_v0319_report.json').read_bytes())
    assert audited['passed'] and audited['actual_ninth_crystal_and_exterior']
    assert audited['rom_sha256']==digest and published['passed']
    assert published['pal_crystals_and_exterior_returns_verified']==9
""", 1)
s = s.replace("    assert receipt['rom_sha256']==digest and receipt['cold_boot_count']==1",
              "    assert receipt['passed'] and receipt['rom_sha256']==digest and receipt['cold_boot_count']==1")
s = s.replace("'continue_d8_entry_palc0046.py','cold_replay_stream.py')",
              "'continue_d8_entry_palc0046.py','cold_replay_stream.py',"
              "'continue_pal_palace_entry_c0046.py','run_core.py')")
s = s.replace("    helper.STREAM=ReplayStream(work/'cold-stream')",
              "    work.mkdir(exist_ok=False)\n    helper.STREAM=ReplayStream(work/'cold-stream')")
target = project / 'tools/continue_pal_palace_entry_c0046.py'
assert not target.exists(), target
ast.parse(s)
target.write_text(s)
print('PAL palace approach prepared; requires actual ninth-crystal and V319 replay receipts.')
