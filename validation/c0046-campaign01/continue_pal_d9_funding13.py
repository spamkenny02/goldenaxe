"""Replay the partial eight-piece detour, then continue ordinary dungeon pickups."""
import json
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[2]
project = root / 'validation/c0046-campaign01/isolated/project'
name = 'md-pal-palc0046-d9-funds12'
folder = project / 'validation/natural-dungeon-combat' / name
report = json.loads((folder / 'report.json').read_bytes())
capture = json.loads((folder / 'capture.json').read_bytes())
assert report['passed'] is False and report['failure'] == 'gold_goal_not_reached'
assert report['room_cleared'] and not report['deaths']
assert report['gold_events'][-1]['gold'] == 8 and not report['new_resource_writes']
assert report['last_state']['room'] == 0x1da and report['last_state']['health'] == 96
proof = folder.with_name(name + f'-assisted-fixed-replay-{capture["frames"]}')
if not proof.exists():
    subprocess.run([sys.executable, '-u', 'tools/replay_assisted_prefix.py',
                    '--trace', 'natural-dungeon-combat/' + name], cwd=project, check=True)
verified = json.loads((proof / 'replay_report.json').read_bytes())
assert verified['passed'] and verified['whole_ram_bytes'] == 65536 and verified['final_png_exact']
for stem, ext in [('ram', 'bin'), ('frame', 'png')]:
    filename = f'{stem}_{capture["frames"]:05d}.{ext}'
    assert (folder / filename).read_bytes() == (proof / filename).read_bytes()
print('Partial funding checkpoint reproduced exactly; eight pieces, goal still ten.', flush=True)
subprocess.run([sys.executable, '-u', 'validation/palc0046-d9-guarded-funding09/run.py',
                '--boss-room', '0x1ac', '--planner', 'ordinary', '--release-near-coins',
                '--pal', '--assisted-prefix', '--continuation', name,
                '--rooms', '0x1da,0x1ca,0x1c9,0x1c8', '--target-room', '0x1c8',
                '--frames', str(capture['frames'] + 18000), '--trial', 'palc0046-d9-funds13',
                '--max-deaths', '0', '--collision-aim', '--settle-attacks',
                '--doorway-ranges', '--ignore-inactive-actors', '--equip-basic',
                '--wake-sentinels'], cwd=project, check=True)
