"""Audit v314 D4 keys, Earth passages and the real canoe reward."""
import json
from pathlib import Path

from archive_lossless_evidence import sha
from assisted_prefix import prefix_writes, recording
from run_core import ROOT
from validate_playable_sprite_limit import symbols
from validate_reward_hud_restore import translated


def main():
    references = {}

    def read(name):
        raw = (ROOT / name).read_bytes()
        references[name] = sha(raw)
        return raw

    def load(name):
        return json.loads(read(name))

    digest = sha((ROOT / 'gaw-megadrive.bin').read_bytes())
    assert digest == 'c53381c459a1e6254a8c9f1cfad1b8cda482cc0614697ad566133b28335e07a7'
    prior = load('analysis/earth_learning_v0314_report.json')
    assert prior['passed'] and prior['md_sha256'] == digest
    cases = [('natural-dungeon-route/md-v0314-d4-entry01', 'entry'),
             ('natural-dungeon-combat/md-auto-v0314-d4-key01', 'key'),
             ('natural-dungeon-combat/md-auto-v0314-d4-earth01', 'earth'),
             ('natural-dungeon-combat/md-auto-v0314-d4-a1-key01', 'key'),
             ('natural-dungeon-combat/md-auto-v0314-d4-canoe01', 'canoe'),
             ('natural-dungeon-combat/md-auto-v0314-d4-warp01', 'earth'),
             ('natural-dungeon-combat/md-auto-v0314-d4-boss-key01', 'key')]
    sy = symbols(ROOT / 'megadrive/out/release/symbol.txt')
    stages, previous, earth_casts = [], None, []
    for relative, kind in cases:
        root = 'validation/' + relative
        capture = load(root + '/capture.json')
        report = load(root + ('/route_report.json' if kind == 'entry' else '/report.json'))
        end = capture['frames']
        replay = root + f'-assisted-fixed-replay-{end}'
        proof = load(replay + '/replay_report.json')
        assist, writes = recording(ROOT / root, capture)
        read(root + '/assistance.json')
        assert prefix_writes(ROOT / root, capture, True) == writes
        assert capture['rom_sha256'] == proof['rom_sha256'] == digest
        assert capture['sram_input'] is None and not assist['primary_state_imports']
        assert not assist['health_refills'] and not assist['boss_assistance']
        assert len(assist['episodes']) == 4 and assist['boss_room'] == 0x180
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
        save, items = data('game_save_state', 592), data('hero_items', 17)
        assert save[0x1f:0x28] == bytes([128] * 3 + [0] * 6)
        assert items[5] == items[8] == items[13] == 1
        assert word('hero_health') > 0 and word('hero_max_health') == 56
        assert word('hero_max_magic') == 48 and word('game_state') == 12
        assert word('hero_weapon_level') == word('hero_selected_item') == 1
        assert word('sound_unhandled_command') == 0
        if kind == 'entry':
            assert report['reached_entrance'] and report['directional_probe_succeeded']
            assert word('room_id') == 0x1f0
        elif kind == 'key':
            assert report['new_key_verified'] and word('hero_keys') > 0
        elif kind == 'earth':
            assert report['earth_route_passed'] and report['earth_passage_traversed']
            assert report['earth_state_writes'] == 0 and report['earth_passage_opened']
            before, opened = report['earth_before'], report['earth_opened']
            assert before['magic'] - opened['magic'] == 8 and opened['flags'] & 4
            earth_casts.append(dict(room=report['earth_passage_room'], cell=report['earth_cell'],
                                    before=before, opened=opened, normal_input=True))
        else:
            assert report['item_acquisition_passed'] and report['item_acquisition_state_writes'] == 0
            assert report['item_acquisition_first']['owned'] == 0 and items[12] == 1
            assert not report['last_state']['reward_active']
            sms = data('sms_vram', 16384)
            vram, regs = read(root + f'/vram_{end:05d}.bin'), read(root + f'/vdp_regs_{end:05d}.bin')
            base, width = (regs[2] & 56) << 10, [32, 64, 32, 128][regs[16] & 3]
            for n in range(128):
                at = base + ((n // 32 + 22) * width + n % 32) * 2
                assert int.from_bytes(vram[at:at+2], 'little') == translated(int.from_bytes(sms[0x3d00+n*2:0x3d02+n*2], 'little'))
        stages.append(dict(trace=root, kind=kind, frames=end, room=word('room_id'),
                           health=word('hero_health'), magic=word('hero_magic'),
                           keys=word('hero_keys'), canoe_owned=bool(items[12]),
                           whole_ram_bytes=65536, final_png_exact=True))
    assert len(earth_casts) == 2 and stages[-1]['canoe_owned']
    result = dict(passed=True, version=314, md_sha256=digest, stages=stages,
                  earth_casts=earth_casts, canoe_acquired=True, boss_approach_key_verified=True,
                  resource_writes=0, primary_state_imports=0, boss_assistance=False,
                  physical_canoe_reward_hud_words_exact=128, fourth_crystal_verified=False,
                  full_game_validated=False, evidence=references,
                  driver_sha256=sha(Path(__file__).read_bytes()),
                  limits=['One cold NTSC campaign with declared approach-only hurt writes; no resources, actors, progress, SRAM or primary states imported.',
                          'The selected key route uses normal movement and retains all actor records; no actor or production patch.',
                          'Optional B0 mechanism is deferred. D4 boss, fourth crystal, return and global source audiovisual/R/IRQ fidelity remain outside these checkpoints.'])
    (ROOT / 'analysis/d4_progress_v0314_report.json').write_bytes((json.dumps(result, indent=2) + '\n').encode())
    print('v314 D4 keys, two real Earth passages and canoe reward audited.')


if __name__ == '__main__':
    main()
