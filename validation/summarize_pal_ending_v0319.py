"""Bind the complete recorded PAL campaign/ending replay to the numbered V319 ROM."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
source = root / 'analysis/palc0046_palace_ending_report.json'
replay = root / 'analysis/c0047_pal_ending_report.json'
a = json.loads(source.read_bytes())
b = json.loads(replay.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert a['passed'] and a['candidate'] == 'c0046' and a['region'] == 'pal'
assert a['ending_complete'] and a['actual_golden_axe_acquired'] and len(a['stages']) == 22
assert a['fights']['final']['first']['hurt'] == 0 and a['fights']['final']['prediction_windows'] > 0
assert a['ending']['nine_gems_visible_frame'] < a['ending']['credits_started_frame']
assert a['ending']['credits_started_frame'] < a['ending']['credits_finished_frame'] < a['ending']['title_flow_return_frame']
assert b['passed'] and b['candidate'] == 'c0047' and b['region'] == 'pal' and b['milestone'] == 'ending'
assert b['whole_ram_bytes_exact'] == 65536 and b['final_png_exact'] and not b['initial_sram'] and not b['primary_state_imports']
assert b['source_report_sha256'] == sha(source) and b['frames'] == a['campaign_frames']
assert b['reference_rom_sha256'] == a['rom_sha256'] == '9e747d38e0c6fb2d69b7c1aa8c2b296a61e8b6af41171d14e543ed9a6cb49cf5'
numbered = root / 'versions/v0319-d3ea2a83/gaw-megadrive-v0319.bin'
assert sha(root / 'gaw-megadrive.bin') == sha(numbered) == b['rom_sha256']
result = dict(passed=True, version=319, region='pal', md_sha256=b['rom_sha256'],
              pal_campaign_from_new_game_to_intro_verified=True,
              actual_golden_axe_acquired=True, death_adder_defeated_without_test_protection=True,
              ending_complete=True, ending=a['ending'], frames=b['frames'],
              whole_ram_bytes_exact=65536, final_png_exact=True,
              initial_sram=False, primary_state_imports=0, full_game_validated=False,
              evidence={source.relative_to(root).as_posix(): sha(source), replay.relative_to(root).as_posix(): sha(replay)},
              scope='Complete recorded PAL New Game campaign through the nine crystals, Balloon, palace, '
                    'Golden Axe, Death Adder, full credits and intro return, replayed on unchanged V319. '
                    'Declared approach-only test protection ends before bosses. This does not certify '
                    'global SMS cycle/PCM equivalence, every input/side route or physical hardware.')
output = root / 'analysis/pal_ending_v0319_report.json'
assert not output.exists(), output
output.write_text(json.dumps(result, indent=2) + '\n')
print('V319 complete PAL recorded campaign and ending receipt verified.')
