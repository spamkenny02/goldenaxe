"""Audit the real-coin D8 detour and exterior return, without claiming D9 complete."""
import json
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[2]
project = root / 'validation/c0046-campaign01/isolated/project'
sys.path.insert(0, str(project / 'tools'))
from assisted_prefix import recording
from archive_lossless_evidence import freeze, sha
from validate_playable_sprite_limit import symbols

paths = {Path(__file__).resolve()}
def read(path):
    paths.add(path)
    return path.read_bytes()
def load(path):
    return json.loads(read(path))

prior = load(root / 'analysis/palc0046_d8_report.json')
assert prior['passed'] and prior['actual_eighth_crystal_and_exterior']
digest = sha(read(project / 'gaw-megadrive.bin'))
assert digest == prior['rom_sha256']
sy = symbols(project / 'megadrive/out/release/symbol.txt')
previous = root / prior['current_campaign_trace']
old_cap = load(previous / 'capture.json')
_, old_writes = recording(previous, old_cap)
previous_frame = old_cap['frames']
assert previous_frame == prior['campaign_frames']
assert sha(read(previous / f'ram_{previous_frame:05d}.bin')) == prior['final_ram_sha256']
stages = []
spec = [('natural-dungeon-route', 'md-pal-palc0046-d9-funding-d8-reentry01', 0x1ea, 7),
        ('natural-dungeon-combat', 'md-pal-palc0046-d9-funds12', 0x1da, 8),
        ('natural-dungeon-combat', 'md-pal-palc0046-d9-funds13', 0x1ca, 14),
        ('natural-dungeon-combat', 'md-pal-palc0046-d9-funding-d8-exit01', 0x29, None)]
for family, name, expected_room, expected_gold in spec:
    folder = project / 'validation' / family / name
    c = load(folder / 'capture.json')
    frame = c['frames']
    r = load(folder / ('route_report.json' if family == 'natural-dungeon-route' else 'report.json'))
    # funds12 reached an exact, useful eight-piece checkpoint, but failed its ten-piece goal.
    if name.endswith('funds12'):
        assert r['passed'] is False and r['failure'] == 'gold_goal_not_reached' and r['room_cleared']
    else:
        assert r['failure'] is None
    if name.endswith('funds13'):
        assert r['passed'] and r['ordinary_gold_goal_reached'] and not r['new_resource_writes']
        assert [(e['frame'], e['gold']) for e in r['gold_events']] == [
            (260859, 7), (261406, 8), (262300, 9), (262688, 14)]
    assert not r.get('deaths', 0) and r['prefix_end'] == previous_frame
    assert previous.name in (r.get('recorded_new_game_prefix'), r.get('recorded_combat_prefix'))
    assert c['rom_sha256'] == digest and c['sram_input'] is None and frame > previous_frame
    assert c['core_options']['genesis_plus_gx_region_detect'] == 'pal'
    aid, writes = recording(folder, c)
    assert writes[:len(old_writes)] == old_writes
    assert not aid['boss_assistance'] and not aid['health_refills'] and not aid['primary_state_imports']
    assert aid['boss_room'] == 0x1ac and aid['first_boss_entry'] is None
    assert aid['episodes'][-1]['activation_after_frame'] == prior['campaign_frames']
    assert all(address == sy['hero_hurt'] and value in (b'\0\0', b'\0\x81')
               for _, address, value in writes)
    proof = folder.with_name(name + f'-assisted-fixed-replay-{frame}')
    if not proof.exists():
        assert name.endswith('funding-d8-exit01'), 'Earlier checkpoints must already be proven'
        subprocess.run([sys.executable, '-u', 'tools/replay_assisted_prefix.py',
                        '--trace', family + '/' + name], cwd=project, check=True)
    v = load(proof / 'replay_report.json')
    assert v['passed'] and v['whole_ram_bytes'] == 65536 and v['final_png_exact'] and not v['feedback_reads']
    for filename, expected in v['evidence'].items():
        assert sha(read(folder / filename)) == expected
    for stem, ext in [('ram', 'bin'), ('frame', 'png')]:
        filename = f'{stem}_{frame:05d}.{ext}'
        assert read(folder / filename) == read(proof / filename)
    raw = read(folder / f'ram_{frame:05d}.bin')
    data = lambda name, size: bytes(raw[(sy[name] + i) ^ 1] for i in range(size))
    word = lambda name: int.from_bytes(data(name, 2), 'big')
    assert word('room_id') == expected_room and word('hero_health') > 0
    assert word('hero_max_health') == 96 and word('hero_keys') == 2 and not word('sound_unhandled_command')
    assert data('game_save_state', 592)[0x1f:0x28] == bytes([128] * 8 + [0])
    if expected_gold is not None:
        assert word('hero_gold') == expected_gold
    else:
        assert r['dungeon_exit_verified'] and r['room_cleared'] and word('hero_gold') >= 10
    stages.append(dict(trace=folder.relative_to(root).as_posix(), frames=frame, room=expected_room,
                       gold=word('hero_gold'), health=word('hero_health'),
                       whole_ram_bytes_exact=65536, final_png_exact=True))
    for path in folder.iterdir():
        if path.is_file(): read(path)
    previous, previous_frame, old_writes = folder, frame, writes

for n in ('08', '09'):
    for path in (project / f'validation/palc0046-d9-guarded-funding{n}').glob('*.py'): read(path)
for name in ('continue_pal_d9_funding13.py', 'continue_pal_d9_funded_exit.py'): read(Path(__file__).with_name(name))
archive = root / 'analysis/palc0046-d9-funding-return'
result = dict(passed=True, candidate='c0046', region='pal', rom_sha256=digest,
              stages=stages, current_campaign_trace=stages[-1]['trace'], campaign_frames=previous_frame,
              final_ram_sha256=sha(raw), actual_eighth_crystal_and_exterior=True,
              ordinary_coin_collection=True, gold_before=7, gold_after=stages[-1]['gold'],
              resource_or_actor_writes=0, primary_state_imports=0, approach_protection=True,
              ninth_crystal_obtained=False, full_game_validated=False,
              archive_manifest=(archive / 'manifest.json').relative_to(root).as_posix(),
              scope='Real D8 detour after eight crystals: ordinary coin pickups and exterior return. '
                    'Hurt-only approach protection is declared; no currency, resource, actor, SRAM or progression imports. '
                    'Four cold whole-RAM/PNG endpoints; not a D9 combat or fidelity milestone.')
freeze(root, archive, paths, result, [project / 'validation'])
(root / 'analysis/palc0046_d9_funding_return_report.json').write_text(json.dumps(result, indent=2) + '\n')
print('Real funding and return audited, archived and available for the ten-piece toll.', flush=True)
