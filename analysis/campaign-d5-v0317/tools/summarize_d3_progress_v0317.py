"""Audit v317 D3 entry, rope, contact mechanism and key from cold boot."""
import json
from pathlib import Path

from archive_lossless_evidence import sha
from assisted_prefix import prefix_writes, recording
from run_core import ROOT
from validate_playable_sprite_limit import symbols


def main():
    digest = sha((ROOT / 'gaw-megadrive.bin').read_bytes())
    assert digest == '7694654ec85dd6626c0e17ff1834e5893d4eb35481400a4725eac6b6f3503294'
    evidence = {}

    def read(path):
        raw = (ROOT / path).read_bytes()
        evidence[path] = sha(raw)
        return raw

    def load(path):
        return json.loads(read(path))

    prior = load('analysis/oil_service_v0317_report.json')
    assert prior['passed'] and prior['md_sha256'] == digest
    sy = symbols(ROOT / 'megadrive/out/release/symbol.txt')
    stages, previous = [], None
    cases = [('natural-dungeon-route/md-v0317-d3-entry01', 'entry'),
             ('natural-dungeon-combat/md-auto-v0317-d3-rope01', 'rope'),
             ('natural-dungeon-combat/md-auto-v0317-d3-switch01', 'switch'),
             ('natural-dungeon-combat/md-auto-v0317-d3-key01', 'key')]
    for relative, kind in cases:
        root = 'validation/' + relative
        capture = load(root + '/capture.json')
        report = load(root + ('/route_report.json' if kind == 'entry' else '/report.json'))
        end = capture['frames']
        replay = root + f'-assisted-fixed-replay-{end}'
        proof = load(replay + '/replay_report.json')
        assist, writes = recording(ROOT / root, capture)
        read(root + '/assistance.json')
        read(root + '/controls.json')
        assert prefix_writes(ROOT / root, capture, True) == writes
        assert capture['rom_sha256'] == proof['rom_sha256'] == digest
        assert capture['sram_input'] is None and not assist['primary_state_imports']
        assert not assist['health_refills'] and not assist['boss_assistance']
        assert len(assist['episodes']) == 3 and assist['boss_room'] == (0x195 if kind == 'entry' else 0x1c3)
        assert assist['first_boss_entry'] is None
        assert all(address == sy['hero_hurt'] for _, address, _ in writes)
        if previous is not None:
            assert writes[:len(previous)] == previous
        previous = writes
        assert report['failure'] is None and not report.get('deaths', 0)
        assert proof['passed'] and proof['whole_ram_bytes'] == 65536
        assert proof['final_png_exact'] and not proof['feedback_reads']
        for name, expected in proof['evidence'].items():
            assert sha(read(root + '/' + name)) == expected
        for stem, extension in [('ram', 'bin'), ('frame', 'png')]:
            name = f'/{stem}_{end:05d}.{extension}'
            assert read(root + name) == read(replay + name)
        raw = read(root + f'/ram_{end:05d}.bin')
        data = lambda name, size: bytes(raw[(sy[name] + i) ^ 1] for i in range(size))
        word = lambda name: int.from_bytes(data(name, 2), 'big')
        items, save = data('hero_items', 17), data('game_save_state', 592)
        assert items[8] == 1 and save[0x1f:0x28] == bytes([128, 128] + [0] * 7)
        assert word('hero_max_health') == 48 and word('hero_health') > 0
        assert word('hero_selected_item') == word('hero_weapon_level') == 1
        assert not word('sound_unhandled_command') and word('game_state') == 12
        if kind == 'entry':
            assert report['reached_entrance'] and report['directional_probe_succeeded']
            assert word('room_id') == 0x1f8 and items[13] == 0
        elif kind == 'rope':
            assert report['item_acquisition_passed'] and report['item_acquisition_state_writes'] == 0
            assert report['item_acquisition_first']['owned'] == 0 and items[13] == 1
            assert not report['last_state']['reward_active']
        elif kind == 'switch':
            assert items[13] == 1 and report['contact_route_passed']
            assert report['contact_state_writes'] == 0 and report['contact_opened']['active_enemies']
            assert report['contact_opened']['flags'] & 4 and word('room_id') == 0x1e3
        else:
            assert items[13] == 1 and report['new_key_verified']
            assert word('room_id') == 0x1d2 and word('hero_keys') == 1
        stages.append(dict(kind=kind, trace=root, frame=end, room=word('room_id'),
                           health=word('hero_health'), max_health=word('hero_max_health'),
                           rope=items[13], oil=items[8], whole_ram_bytes=65536,
                           final_png_exact=True, no_initial_sram=True))
    result = dict(passed=True, version=317, md_sha256=digest,
                  stages=stages, rope_acquired=True, contact_mechanism_opened=True,
                  new_key_acquired=True,
                  boss_assistance=False, primary_state_imports=0, resource_writes=0,
                  third_crystal_verified=False, full_game_validated=False,
                  evidence=evidence, driver_sha256=sha(Path(__file__).read_bytes()),
                  limits=['One cold NTSC campaign with declared approach-only hurt writes; bosses remain unprotected.',
                          'Rope and mechanism are real game actions. The mechanism is opened with live enemies; this report does not claim that room is cleared.',
                          'The world entry preserves the preceding still-unreached target195; the rope controller retargets only pending test bookkeeping to the source boss1C3. No game state is imported.',
                          'D3 boss, whole-game R/IRQ and audiovisual fidelity, optional paths and hardware are outside these checkpoints.'])
    (ROOT / 'analysis/d3_progress_v0317_report.json').write_bytes((json.dumps(result, indent=2) + '\n').encode())
    print('v317 D3 entry, rope, live-enemy contact mechanism and key audited.')


if __name__ == '__main__':
    main()
