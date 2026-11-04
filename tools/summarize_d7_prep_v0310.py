"""Bind the v0310 D7 keys and Earth obstacles to their cold replays."""
import json

from archive_lossless_evidence import sha
from assisted_prefix import recording
from rebase_natural_campaign import evidence
from run_core import ROOT
from validate_playable_sprite_limit import symbols


CASES = (
    ('key01', 0x1cb, 68, 24, 2, None),
    ('key03', 0x1b9, 80, 40, 3, None),
    ('earth01', 0x1b9, 80, 32, 3, 0x36),
    ('earth02', 0x1b9, 80, 24, 3, 0x2b),
)


def main():
    hashes = {}

    def read(path):
        raw = evidence(path)
        hashes[path.relative_to(ROOT).as_posix()] = sha(raw)
        return raw

    def load(path):
        return json.loads(read(path))

    prior = load(ROOT / 'analysis/d7_entry_v0310_report.json')
    digest = sha((ROOT / 'gaw-megadrive.bin').read_bytes())
    assert prior['passed'] and prior['md_sha256'] == digest and prior['whole_ram_png_exact']
    folder = ROOT / prior['trace']
    capture = load(folder / 'capture.json')
    assert capture['frames'] == prior['frames']
    _, writes = recording(folder, capture)
    symbol = symbols(ROOT / 'megadrive/out/release/symbol.txt')
    sources = ROOT / 'validation/v0310-d7-sources/healed-prep'
    index = load(sources / 'source_index.json')
    for name, digest_expected in index.items():
        assert sha(read(sources / name)) == digest_expected

    stages = []
    for trial, room, health, magic, keys, cell in CASES:
        previous_name, previous_frame, previous_writes = folder.name, capture['frames'], writes
        folder = ROOT / 'validation/natural-dungeon-combat' / ('md-auto-v0310-d7-healed-' + trial)
        capture = load(folder / 'capture.json')
        result = load(folder / 'report.json')
        aid, writes = recording(folder, capture)
        assert capture['rom_sha256'] == result['rom_sha256'] == digest and capture['sram_input'] is None
        assert result['failure'] is None and not result['deaths'] and not result['sram_checkpoint_injection']
        assert result['recorded_new_game_prefix'] == previous_name and result['prefix_end'] == previous_frame
        assert capture['frames'] > previous_frame and writes[:len(previous_writes)] == previous_writes
        assert all(frame > previous_frame and address == symbol['hero_hurt'] and value in (b'\0\0', b'\0\x81')
                   for frame, address, value in writes[len(previous_writes):])
        assert aid['boss_room'] == 0x1b8 and len(aid['episodes']) == 7
        assert aid['first_boss_entry'] is None and not aid['boss_assistance'] and not aid['health_refills']
        assert result['driver_sha256'] == index['natural_dungeon_combat.py']
        if cell is None:
            assert result['new_key_verified'] and result['room_cleared'] and result['target_entry_keys'] == keys - 1
        else:
            assert result['earth_controller_sha256'] == index['natural_earth_passage.py']
            assert result['earth_route_passed'] and result['earth_cell'] == cell and not result['earth_state_writes']
            assert result['earth_before']['magic'] - result['earth_opened']['magic'] == 8
            assert result['earth_before']['cell'] == 0x0b and result['earth_opened']['cell'] != 0x0b
            assert writes == previous_writes
            read(folder / 'earth_events.json')

        frame = capture['frames']
        replay_folder = folder.with_name(f'{folder.name}-assisted-fixed-replay-{frame}')
        replay = load(replay_folder / 'replay_report.json')
        assert replay['passed'] and replay['rom_sha256'] == digest and replay['whole_ram_bytes'] == 65536
        assert replay['final_png_exact'] and not replay['feedback_reads']
        for name, expected in replay['evidence'].items():
            assert sha(read(folder / name)) == expected
        name = f'frame_{frame:05d}.png'
        assert read(folder / name) == read(replay_folder / name)
        name = f'ram_{frame:05d}.bin'
        raw = read(folder / name)
        assert raw == read(replay_folder / name)

        def data(name, size):
            return bytes(raw[(symbol[name] + index) ^ 1] for index in range(size))

        def word(name):
            return int.from_bytes(data(name, 2), 'big')

        assert (word('room_id'), word('hero_health'), word('hero_magic'), word('hero_keys')) == (room, health, magic, keys)
        assert word('hero_selected_item') == 1 and not word('sound_unhandled_command')
        assert data('game_save_state', 0x28)[0x1f:] == bytes([128] * 6 + [0] * 3)
        stages.append(dict(trace=folder.relative_to(ROOT).as_posix(), frame=frame,
                           room=room, health=health, magic=magic, keys=keys,
                           earth_cell=cell, whole_ram_png_exact=True))

    report = dict(passed=True, version=310, md_sha256=digest, stages=stages,
                  original_crystals_retained=6, earth_casts=2, earth_magic_spent=16,
                  intermediate_boss_entered=False, full_game_validated=False, evidence=hashes)
    (ROOT / 'analysis/d7_prep_v0310_report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('D7 preparation verified on v0310')


if __name__ == '__main__':
    main()
