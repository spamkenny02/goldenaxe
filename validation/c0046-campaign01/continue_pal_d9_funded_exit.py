"""Prove real dungeon funding, then walk out with the acquired gold."""
import json
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[2]
project = root / 'validation/c0046-campaign01/isolated/project'
sys.path.insert(0, str(project / 'tools'))
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols

name = 'md-pal-palc0046-d9-funds13'
folder = project / 'validation/natural-dungeon-combat' / name
r = json.loads((folder / 'report.json').read_bytes())
c = json.loads((folder / 'capture.json').read_bytes())
assert r['passed'] and r['failure'] is None and r['ordinary_gold_goal_reached']
assert not r['deaths'] and not r['new_resource_writes'] and not r['primary_state_imports']
assert c['sram_input'] is None and c['core_options']['genesis_plus_gx_region_detect'] == 'pal'
sy = symbols(project / 'megadrive/out/release/symbol.txt')
raw = (folder / f'ram_{c["frames"]:05d}.bin').read_bytes()
data = lambda name, size: bytes(raw[(sy[name] + i) ^ 1] for i in range(size))
word = lambda name: int.from_bytes(data(name, 2), 'big')
assert word('hero_gold') == 14 and word('hero_health') == 96 and word('room_id') == 0x1ca
assert data('game_save_state', 592)[0x1f:0x28] == bytes([128] * 8 + [0])
aid, writes = recording(folder, c)
assert not aid['boss_assistance'] and not aid['primary_state_imports'] and not aid['health_refills']
assert aid['boss_room'] == 0x1ac and aid['first_boss_entry'] is None
assert all(address == sy['hero_hurt'] and value in (b'\0\0', b'\0\x81')
           for _, address, value in writes)
proof = folder.with_name(name + f'-assisted-fixed-replay-{c["frames"]}')
if not proof.exists():
    subprocess.run([sys.executable, '-u', 'tools/replay_assisted_prefix.py', '--trace',
                    'natural-dungeon-combat/' + name], cwd=project, check=True)
v = json.loads((proof / 'replay_report.json').read_bytes())
assert v['passed'] and v['whole_ram_bytes'] == 65536 and v['final_png_exact'] and not v['feedback_reads']
for stem, ext in [('ram', 'bin'), ('frame', 'png')]:
    filename = f'{stem}_{c["frames"]:05d}.{ext}'
    assert (folder / filename).read_bytes() == (proof / filename).read_bytes()
print('Fourteen real pieces reproduced exactly; leaving D8 through ordinary controls.', flush=True)
subprocess.run([sys.executable, '-u', 'tools/assisted_boss_route.py',
                '--pal', '--boss-room', '0x1ac', '--planner', 'ordinary', '--assisted-prefix',
                '--continuation', name, '--rooms', '0x1ca,0x1da,0x1ea', '--target-room', '0x29',
                '--exit-dungeon', '--exit-before-crystal', '--equip-axe', '--max-deaths', '0',
                '--collision-aim', '--settle-attacks', '--doorway-ranges',
                '--ignore-inactive-actors', '--wake-sentinels', '--retry-isolated-foes',
                '--isolated-retry-limit', '12', '--frames', str(c['frames'] + 12000),
                '--trial', 'palc0046-d9-funding-d8-exit01'], cwd=project, check=True)
