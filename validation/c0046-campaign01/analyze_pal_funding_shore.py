"""Explain funds10 using captured collision RAM, without running or modifying a game."""
import importlib.util
import gzip
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[2]
project = root / 'validation/c0046-campaign01/isolated/project'
sys.path.insert(0, str(project / 'tools'))
from archive_lossless_evidence import sha
from natural_combat_aim import contact

driver = project / 'validation/palc0046-d9-guarded-funding06/funding_controller.py'
spec = importlib.util.spec_from_file_location('funding_shore_reference', driver)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
folder = project / 'validation/natural-dungeon-combat/md-pal-palc0046-d9-funds10'
report = json.loads((folder / 'report.json').read_bytes())
ram_path = folder / 'ram_261460.bin'
if ram_path.exists():
    ram = ram_path.read_bytes()
else:
    archive = root / 'analysis/palc0046-d9-funding-failures10-11'
    manifest = json.loads((archive / 'manifest.json').read_bytes())
    item = manifest['compressed'][ram_path.relative_to(root).as_posix()]
    encoded = (archive / item['stored']).read_bytes()
    assert sha(encoded) == item['stored_sha256']
    ram = gzip.decompress(encoded)
    assert sha(ram) == item['raw_sha256'] and len(ram) == item['raw_bytes']
sy = module.symbols(project / 'megadrive/out/release/symbol.txt')
data = lambda address, size: bytes(ram[(address + i) ^ 1] for i in range(size))
tilemap = data(sy['sms_vram'] + 0x3800, 1536)
loot = data(sy['world_loot_state'], 48)
coin = dict(type=loot[0], x=loot[19], y=loot[17], contact_box=loot[28])
module.CANOE_OWNED = module.SHIP_OWNED = True
path = module.walk(tilemap, (40, 120), lambda point: contact(point, coin))
assert report['passed'] is False and report['failure'] == 'gold_goal_not_reached'
assert coin == dict(type=9, x=40, y=144, contact_box=2)
assert path is None
assert module.walk(tilemap, (40, 120), lambda point: point == (40, 128)) == [1]
assert not contact((40, 128), coin) and contact((40, 136), coin)
result = dict(
    passed=True, diagnostic_only=True, funding_succeeded=False,
    capture_sha256=sha(ram), capture_frame=261460, coin=coin,
    hero_start=[40, 120], reachable_near_shore=[40, 128],
    contact_at_near_shore=False, contact_at_unreachable_point=[40, 136],
    collision_reference_path_to_pickup=None,
    cartridge_modified=False,
    scope='Explains a failed controller trial using its live collision map and source contact boxes. '
          'No successful funding or global gameplay claim. The next trial uses room3A instead of '
          'shooting from the boat toward inaccessible shore enemies in room2B.')
output = root / 'analysis/palc0046_d9_funding_shore_report.json'
if output.exists():
    assert json.loads(output.read_bytes()) == result
else:
    output.write_text(json.dumps(result, indent=2) + '\n')
print('Verified: five-piece coin exists, but its pickup rectangle is unreachable from the boat.')
