"""Verify that the v0310 D7 guard ends before 1B8 and resumes only after victory."""
import json

from archive_lossless_evidence import sha
from assisted_prefix import recording
from rebase_natural_campaign import evidence
from run_core import ROOT
from validate_playable_sprite_limit import symbols


PREFIX = 'md-auto-v0310-d7-healed-'
CASES = ('release01', 'contact01', 'midboss01', 'resume01')


def main():
    hashes = {}

    def read(path):
        raw = evidence(path)
        hashes[path.relative_to(ROOT).as_posix()] = sha(raw)
        return raw

    def load(path):
        return json.loads(read(path))

    prep = load(ROOT / 'analysis/d7_prep_v0310_report.json')
    digest = sha((ROOT / 'gaw-megadrive.bin').read_bytes())
    assert prep['passed'] and prep['md_sha256'] == digest
    directory = ROOT / 'validation/v0310-d7-sources/healed-midboss'
    index = load(directory / 'source_index.json')
    for name, expected in index.items():
        assert sha(read(directory / name)) == expected
    original = read(ROOT / 'input/original.sms')
    assert original[0x3234e + 0x1b8 * 8] == 0x78
    descriptor = 0x320ea + (0x78 - 0x20) * 4
    assert original[descriptor:descriptor + 4] == bytes([30, 12, 4, 32])

    previous = ROOT / prep['stages'][-1]['trace']
    capture = load(previous / 'capture.json')
    _, writes = recording(previous, capture)
    sy = symbols(ROOT / 'megadrive/out/release/symbol.txt')
    stages, results = [], {}
    release_frame = None
    for name in CASES:
        folder = previous.with_name(PREFIX + name)
        previous_frame, previous_writes = capture['frames'], writes
        capture = load(folder / 'capture.json')
        result = load(folder / 'report.json')
        aid, writes = recording(folder, capture)
        assert capture['rom_sha256'] == result['rom_sha256'] == digest
        assert capture['sram_input'] is None and not aid['primary_state_imports']
        assert result['failure'] is None and not result['deaths']
        assert result['prefix_end'] == previous_frame and result['recorded_new_game_prefix'] == previous.name
        frame = capture['frames']
        assert frame > previous_frame
        replay_dir = folder.with_name(f'{folder.name}-assisted-fixed-replay-{frame}')
        proof = load(replay_dir / 'replay_report.json')
        assert proof['passed'] and proof['rom_sha256'] == digest and proof['whole_ram_bytes'] == 65536
        assert proof['final_png_exact'] and not proof['feedback_reads']
        for filename, expected in proof['evidence'].items():
            assert sha(read(folder / filename)) == expected
        filename = f'frame_{frame:05d}.png'
        assert read(folder / filename) == read(replay_dir / filename)
        filename = f'ram_{frame:05d}.bin'
        raw = read(folder / filename)
        assert raw == read(replay_dir / filename)

        def data(symbol, length):
            return bytes(raw[(sy[symbol] + i) ^ 1] for i in range(length))

        def word(symbol):
            return int.from_bytes(data(symbol, 2), 'big')

        assert data('game_save_state', 0x28)[0x1f:] == bytes([128] * 6 + [0] * 3)
        assert not word('sound_unhandled_command') and word('hero_health') > 0
        assert not data('hero_items', 17)[16]
        if name == 'release01':
            assert word('room_id') == 0x1b9 and word('hero_hurt') == 0 and aid['closed_before_room'] == 0x1b8
            assert frame == previous_frame + 1 and writes == previous_writes + [(frame, sy['hero_hurt'], b'\0\0')]
            release_frame = frame
        elif name == 'resume01':
            assert aid['boss_room'] == 0x179 and aid['first_boss_entry'] is None
            assert result['resumed_after_verified_intermediate'] and result['new_assistance_writes'] == 1
            assert word('hero_hurt') == 129 and result['driver_sha256'] == index['resume_after_intermediate.py']
            assert frame == previous_frame + 1 and writes == previous_writes + [(frame, sy['hero_hurt'], b'\0\x81')]
            assert result['first_intermediate_combat']['frame'] == results['midboss01']['first_intermediate_combat']['frame']
        else:
            assert word('room_id') == 0x1b8 and aid['boss_room'] == 0x1b8
            assert result['unassisted_extension'] and result['guard_release_frame'] == release_frame
            assert writes == previous_writes and not result['new_assistance_writes']
            assert result['extension_guard_checks_through_frame'] == frame
            assert result['unassisted_controller_sha256'] == index['unassisted_dungeon_continuation.py']
            if name == 'contact01':
                assert result['contact_route_passed'] and not result['contact_state_writes']
            else:
                assert result['room_cleared']
                actors = data('world_actor_state', 768)
                assert not any(actors[i] == 0x78 and actors[i + 24] for i in range(0, len(actors), 48))
                assert result['full_ram_prediction_matches'] == result['verified_persistent_prediction_windows'] > 0
                assert not result['stack_only_difference_windows']
        stages.append(dict(trace=folder.relative_to(ROOT).as_posix(), frames=frame, room=word('room_id'),
                           health=word('hero_health'), magic=word('hero_magic'), keys=word('hero_keys'),
                           whole_ram_png_exact=True))
        results[name] = result
        previous = folder

    fight = results['midboss01']
    first = fight['first_intermediate_combat']
    assert first == results['contact01']['first_intermediate_combat']
    assert first['room'] == 0x1b8 and first['hurt'] == 0 and first['health'] == 80
    assert first['frame'] > release_frame and any(a['kind'] == 0x78 and a['hp'] == 30 for a in first['actors'])
    report = dict(passed=True, version=310, md_sha256=digest, stages=stages, intermediate_defeated=True,
                  intermediate_assistance=False, guard_release_frame=release_frame, first_intermediate_combat=first,
                  first_extension_damage=fight['first_extension_damage'], full_ram_prediction_matches=fight['full_ram_prediction_matches'],
                  main_boss_entered=False, seventh_crystal_validated=False, full_game_validated=False, evidence=hashes)
    (ROOT / 'analysis/d7_midboss_v0310_report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('D7 intermediate victory and approach restart verified on v0310')


if __name__ == '__main__':
    main()
