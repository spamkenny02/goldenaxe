"""Verify the v0314 ship, main D7 combat, and exterior return on one run."""
import argparse
import json

from archive_lossless_evidence import sha
from assisted_prefix import recording
from rebase_natural_campaign import evidence
from run_core import ROOT
from validate_playable_sprite_limit import symbols
from validate_reward_hud_restore import translated


CASES = ('south01', 'remote01', 'ship01', 'north01', 'warp01', 'approach01',
         'main-release01', 'boss01', 'return-earth01', 'exit01')


def verify_hud(data, read, folder, frame, original, crystals):
    sms = data('sms_vram', 16384)
    vram = read(folder / f'vram_{frame:05d}.bin')
    regs = read(folder / f'vdp_regs_{frame:05d}.bin')
    base = (regs[2] & 56) << 10
    width = [32, 64, 32, 128][regs[16] & 3]
    for index in range(128):
        offset = base + ((index // 32 + 22) * width + index % 32) * 2
        word = int.from_bytes(sms[0x3d00 + 2 * index:0x3d02 + 2 * index], 'little')
        assert int.from_bytes(vram[offset:offset + 2], 'little') == translated(word)
    for index in range(crystals):
        tile, offset = original[0x1edc + 2 * index:0x1ede + 2 * index]
        assert sms[0x3d00 + offset:0x3d02 + offset] == bytes([tile, 0x59])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--through-ship', action='store_true')
    args = parser.parse_args()
    hashes = {}

    def read(path):
        raw = evidence(path)
        hashes[path.relative_to(ROOT).as_posix()] = sha(raw)
        return raw

    def load(path):
        return json.loads(read(path))

    previous_proof = load(ROOT / 'analysis/d7_midboss_v0314_report.json')
    digest = sha((ROOT / 'gaw-megadrive.bin').read_bytes())
    assert previous_proof['passed'] and previous_proof['md_sha256'] == digest
    assert previous_proof['intermediate_defeated'] and not previous_proof['intermediate_assistance']
    previous = ROOT / previous_proof['stages'][-1]['trace']
    capture = load(previous / 'capture.json')
    prior_aid, writes = recording(previous, capture)
    assert prior_aid['boss_room'] == 0x179 and prior_aid['release_write_frame'] is None
    sy = symbols(ROOT / 'megadrive/out/release/symbol.txt')
    original = read(ROOT / 'input/original.sms')
    assert original[0x3234e + 0x179 * 8] == 0x67
    names=load(ROOT/'validation/run-v0314-d7-finish-02/source_index.json')
    index={name.split('/')[-1]:sha(read(ROOT/name)) for name in names}
    for name,h in names.items():assert index[name.split('/')[-1]]==h==sha(read(ROOT/'validation/run-v0314-d7-finish-02'/name.split('/')[-1]))
    stages = []
    release_frame = first_combat = boss_damage = None
    for name in CASES[:3] if args.through_ship else CASES:
        folder = previous.with_name('md-auto-v0314-d7-02-' + name)
        prior_frame, prior_writes = capture['frames'], writes
        capture, result = load(folder / 'capture.json'), load(folder / 'report.json')
        aid, writes = recording(folder, capture)
        assert capture['rom_sha256'] == result['rom_sha256'] == digest and capture['sram_input'] is None
        assert result['failure'] is None and not result['deaths'] and not aid['primary_state_imports']
        assert result['prefix_end'] == prior_frame and result['recorded_new_game_prefix'] == previous.name
        assert aid['boss_room'] == 0x179 and len(aid['episodes']) == 8 and aid['episodes'][:-1] == prior_aid['episodes'][:-1]
        assert writes[:len(prior_writes)] == prior_writes and all(address == sy['hero_hurt'] for _, address, _ in writes)
        frame = capture['frames']
        assert frame > prior_frame
        proof_dir = folder.with_name(f'{folder.name}-assisted-fixed-replay-{frame}')
        proof = load(proof_dir / 'replay_report.json')
        assert proof['passed'] and proof['rom_sha256'] == digest and proof['whole_ram_bytes'] == 65536
        assert proof['final_png_exact'] and not proof['feedback_reads']
        for filename, expected in proof['evidence'].items():
            assert sha(read(folder / filename)) == expected
        filename = f'frame_{frame:05d}.png'
        assert read(folder / filename) == read(proof_dir / filename)
        filename = f'ram_{frame:05d}.bin'
        raw = read(folder / filename)
        assert raw == read(proof_dir / filename)

        def data(symbol, size):
            return bytes(raw[(sy[symbol] + i) ^ 1] for i in range(size))

        def word(symbol):
            return int.from_bytes(data(symbol, 2), 'big')

        won = name in ('boss01', 'return-earth01', 'exit01')
        crystals = 7 if won else 6
        assert data('game_save_state', 0x28)[0x1f:] == bytes([128] * crystals + [0] * (9 - crystals))
        ship = name not in ('south01', 'remote01')
        assert data('hero_items', 17)[16] == ship and word('hero_health') > 0 and not word('sound_unhandled_command')
        if won:
            assert result['unassisted_extension'] and not result['new_assistance_writes'] and writes == prior_writes
            assert result['guard_release_frame'] == release_frame and result['extension_guard_checks_through_frame'] == frame
            assert result['unassisted_controller_sha256'] == index['unassisted_dungeon_continuation.py']
            assert word('hero_max_health') == 88 and aid['first_boss_combat']
        else:
            assert aid['first_boss_entry'] is None and word('hero_max_health') == 80
        if name == 'south01':
            assert result['room_cleared'] and word('room_id') == 0x1d6
        elif name == 'remote01':
            assert result['contact_route_passed'] and result['contact_coordinate'] == 332 and not result['contact_state_writes']
            save = data('game_save_state', 592)
            assert save[0x50 + 0xe6] & 4 and save[0x50 + 0xd6] & 0x40 and save[0x50 + 0xd5] & 0x80
        elif name == 'ship01':
            assert result['item_acquisition_passed'] and not result['item_acquisition_state_writes']
            assert word('room_id') == 0x1d5 and not word('item_reward_active')
            assert result['item_acquisition_first']['owned'] == 0 and result['item_acquisition_last']['owned'] == 1
        elif name in ('warp01', 'return-earth01'):
            assert result['earth_route_passed'] and not result['earth_state_writes']
            assert result['earth_cell'] == (0x34 if name == 'warp01' else 0x57)
            assert result['earth_before']['magic'] - result['earth_opened']['magic'] == 8
        elif name == 'main-release01':
            assert word('room_id') == 0x189 and word('hero_hurt') == 0 and aid['closed_before_room'] == 0x179
            assert writes == prior_writes + [(frame, sy['hero_hurt'], b'\0\0')]
            release_frame = frame
        elif name == 'boss01':
            assert result['arrival_checked_on_every_entry'] and result['arrival_controller_sha256']==index['unassisted_arrival_prediction.py']
            first_combat = result['first_intermediate_combat']
            assert first_combat['room'] == 0x179 and release_frame < first_combat['frame'] and first_combat['hurt'] <= 128
            assert any(actor['kind'] == 0x67 and actor['hp'] == 60 for actor in first_combat['actors'])
            assert result['room_cleared'] and not word('item_reward_active')
            assert result['full_ram_prediction_matches'] == result['verified_persistent_prediction_windows'] > 0
            assert not result['stack_only_difference_windows']
            boss_damage = aid['first_boss_damage']
        elif name == 'exit01':
            assert result['full_dungeon_cleared'] and word('room_id') == 0x1b and not word('world_dungeon_number')
        if name in ('boss01','exit01'):
            assert result['secondary_video_suppressed'] and not result['primary_video_suppressed']
            assert result['prediction_video_wrapper_sha256'] == index['unassisted_fast_prediction.py']
            assert result['prediction_video_adapter_sha256'] == index['prediction_video_skip.py']
            assert result['full_ram_prediction_matches'] == result['verified_persistent_prediction_windows']
            assert not result['stack_only_difference_windows']
        if name in ('ship01', 'boss01', 'exit01'):
            verify_hud(data, read, folder, frame, original, crystals)
        stages.append(dict(trace=folder.relative_to(ROOT).as_posix(), frame=frame, room=word('room_id'),
                           health=word('hero_health'), max_health=word('hero_max_health'), magic=word('hero_magic'),
                           gold=word('hero_gold'), keys=word('hero_keys'), crystals=crystals, ship_owned=ship,
                           whole_ram_png_exact=True))
        previous = folder

    if not args.through_ship:
        cold=load(ROOT/'validation/run-v0314-d7-finish-02/cold-stream/completed.json')
        assert cold['passed'] and cold['rom_sha256']==digest and not cold['primary_state_imports'] and cold['cold_boot_count']==1
        assert [(x['trace'],x['frames']) for x in cold['checkpoints']]==[(x['trace'].removeprefix('validation/'),x['frame']) for x in stages]
    report = dict(passed=True, version=314, md_sha256=digest, stages=stages, ship_acquired=True,
                  intermediate_assistance=False, seventh_crystal_and_exterior_return=not args.through_ship,
                  release_frame=release_frame, first_boss_combat=first_combat, first_boss_damage=boss_damage,
                  full_game_validated=False, production_rom_unchanged=True, controller_sha256=index, evidence=hashes)
    suffix = 'ship' if args.through_ship else 'campaign'
    (ROOT / f'analysis/d7_{suffix}_v0314_report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(f'D7 {suffix} verified on v0314')


if __name__ == '__main__':
    main()
