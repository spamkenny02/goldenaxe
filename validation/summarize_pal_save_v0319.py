"""Attach the public PAL game-written save/Continue proof to the unchanged numbered ROM."""
import json
import hashlib
from pathlib import Path

root = Path(__file__).resolve().parents[1]
reference = root / 'analysis/c0047_pal_real_save_report.json'
r = json.loads(reference.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
assert r['passed'] and r['candidate'] == 'c0047' and r['region'] == 'pal'
assert r['game_written_save'] and not r['synthetic_sram_fixture'] and not r['writer_initial_sram']
assert not r['writer_primary_state_imports'] and r['writer_whole_ram_bytes_exact'] == 65536 and r['writer_final_png_exact']
assert r['raw_sram_exact_to_c0046'] and r['reload_from_own_game_written_sram']
assert r['reload_primary_sram_imports'] == 1 and r['reload_ram_writes'] == 0
assert r['reload_whole_ram_bytes_exact'] == 65536 and r['reload_final_png_exact']
assert r['source_crystal_markers_exact'] == 9 and r['physical_hud_words_exact'] == 128
numbered = root / 'versions/v0319-d3ea2a83/gaw-megadrive-v0319.bin'
assert sha(root / 'gaw-megadrive.bin') == sha(numbered) == r['rom_sha256']
result = dict(passed=True, version=319, region='pal', md_sha256=r['rom_sha256'],
              game_written_save=True, save_slot=0, normal_continue_and_movement=True,
              writer_initial_sram=False, reload_from_own_game_written_sram=True,
              reload_primary_sram_imports=1, reload_ram_writes=0,
              writer_and_loader_whole_ram_bytes_exact=65536, final_images_exact=True,
              source_report=reference.relative_to(root).as_posix(), source_report_sha256=sha(reference),
              full_game_validated=False,
              scope='PAL slot0 real SRAM write and normal Continue on unchanged V319. '
                    'Both writer and loader match the candidate on whole RAM and final image. '
                    'Other slots/refusals, global SMS fidelity and hardware remain outside this proof.')
output = root / 'analysis/pal_save_v0319_report.json'
assert not output.exists(), output
output.write_text(json.dumps(result, indent=2) + '\n')
print('V319 PAL save/Continue receipt verified.')
