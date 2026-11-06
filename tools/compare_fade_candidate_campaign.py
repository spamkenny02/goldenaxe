"""Compare the completed v317 campaign against the c0038 fade preview."""

import argparse
import contextlib
import hashlib
import io
import json
from pathlib import Path

from archive_lossless_evidence import sha
from assisted_prefix import recording
from rebase_natural_campaign import evidence
from run_core import ROOT, FrameWrites, run
from validate_playable_sprite_limit import symbols


BASE = '7694654ec85dd6626c0e17ff1834e5893d4eb35481400a4725eac6b6f3503294'
CANDIDATE = 'e7ee40cb477905b478d849d52a687ff4a319fc7217f29be5f138cbbcce8febeb'
FIRST_GAMEPLAY_FRAME = 2507
WORDS = (
    'room_id', 'game_state', 'hero_state', 'hero_x', 'hero_y', 'hero_health',
    'hero_max_health', 'hero_magic', 'hero_max_magic', 'hero_gold', 'hero_keys',
    'hero_hurt', 'hero_selected_item', 'hero_weapon_level', 'hero_direction',
    'hero_animation', 'hero_counter', 'hero_pending', 'hero_dx', 'hero_dy',
    'hero_flags', 'world_graphics_class', 'world_dungeon_number', 'hero_basic_level',
    'hero_armor_level', 'hero_shield_level', 'game_rng_seed', 'randbase',
    'transition_stage', 'transition_direction', 'transition_step',
    'ending_hero_descriptor', 'sound_unhandled_command',
)
FIELDS = dict.fromkeys(WORDS, 2) | {
    'world_actor_state': 768, 'world_loot_state': 336, 'game_save_state': 592,
    'hero_items': 17, 'sms_vram': 16384, 'sound_ram': 400,
}
BOSS_KINDS = set(range(0x63, 0x6E)) | set(range(0x78, 0x7D))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    assert out.is_relative_to(ROOT/'validation')

    audit_path = ROOT/'analysis/cold_palace_final_v0317_report.json'
    audit_bytes = evidence(audit_path)
    audit = json.loads(audit_bytes)
    assert audit['passed'] and audit['md_sha256'] == BASE and audit['ending_complete']
    assert audit['campaign_from_new_game_completed'] and not audit['final_boss_assistance']
    source = ROOT/audit['current_campaign_trace']
    capture_bytes = evidence(source/'capture.json')
    capture = json.loads(capture_bytes)
    assistance, writes = recording(source, capture)
    assert capture['rom_sha256'] == BASE and capture['sram_input'] is None
    assert not assistance['primary_state_imports'] and not assistance['boss_assistance']
    assert not assistance['health_refills']
    end = capture['frames']
    assert end == audit['campaign_frames']
    checkpoints = {
        audit['nine_gems_visible_frame'] + 1, audit['credits_started_frame'] + 1,
        audit['credits_finished_frame'] + 1, end,
    }
    assert min(checkpoints) > FIRST_GAMEPLAY_FRAME and max(checkpoints) == end

    controls_bytes = evidence(source/'controls.json')
    controls = json.loads(controls_bytes)
    presses = [tuple(row) for row in capture['presses']]
    for i, row in enumerate(controls):
        stop = controls[i+1]['frame']-1 if i+1 < len(controls) else end
        if row['frame'] <= end:
            presses.extend((row['frame'], min(stop, end), button) for button in row['buttons'])

    base_symbols = ROOT/'versions/v0317-7694654e/symbol.txt'
    base_hurt = symbols(base_symbols)['hero_hurt']
    assert all(address == base_hurt and value in (b'\0\0', b'\0\x81')
               for _, address, value in writes)
    preview = ROOT/'versions/candidates/c0038-e7ee40cb'
    builds = (
        ('v0317', ROOT/'versions/v0317-7694654e/gaw-megadrive-v0317.bin', base_symbols, BASE),
        ('c0038', preview/'gaw-megadrive-c0038.bin', preview/'symbol.txt', CANDIDATE),
    )
    out.mkdir(parents=True, exist_ok=False)
    hashes = bytearray()
    runs, first_differences = [], []
    difference_count = 0

    for tag, rom, symbol_file, digest in builds:
        assert sha(rom.read_bytes()) == digest
        sy = symbols(symbol_file)
        assert all(sy[name] % 2 == 0 for name in FIELDS)
        segments = [(sy[name], size & ~1, size & 1) for name, size in FIELDS.items()]
        remapped = FrameWrites((frame, sy['hero_hurt'], value) for frame, _, value in writes)
        boss_frames = checked = 0

        def observe(frame, raw):
            nonlocal boss_frames, checked, difference_count
            hurt = int.from_bytes(raw[sy['hero_hurt']:sy['hero_hurt']+2], 'little')
            actors = sy['world_actor_state']
            if any(raw[(actors+slot*48)^1] in BOSS_KINDS and raw[(actors+slot*48+24)^1]
                   for slot in range(16)):
                assert hurt <= 128, (tag, frame, 'Approach guard active during boss combat')
                boss_frames += 1
            assert raw[sy['sound_unhandled_command']:sy['sound_unhandled_command']+2] == b'\0\0'
            if frame < FIRST_GAMEPLAY_FRAME:
                return
            state = hashlib.sha256()
            for address, count, odd in segments:
                state.update(raw[address:address+count])
                if odd:
                    state.update(bytes([raw[(address+count)^1]]))
            result = state.digest()
            if tag == 'v0317':
                hashes.extend(result)
            elif result != hashes[checked*32:(checked+1)*32]:
                difference_count += 1
                if len(first_differences) < 20:
                    first_differences.append(frame)
            checked += 1

        folder = out/tag
        with contextlib.redirect_stdout(io.StringIO()):
            run(rom, end, folder, checkpoints.copy(), presses, skip_intro=False,
                ram_writes=remapped, ram_observer=observe, core_options=capture['core_options'])
        assert checked == end - FIRST_GAMEPLAY_FRAME + 1 and boss_frames > 0
        runs.append(dict(tag=tag, rom_sha256=digest, symbols_sha256=sha(symbol_file.read_bytes()),
                         capture_sha256=sha((folder/'capture.json').read_bytes()),
                         checked_frames=checked, live_boss_frames=boss_frames))
        print(tag, 'replayed through frame', end, flush=True)

    frame_name = f'frame_{end:05d}.png'
    assert (out/'v0317'/frame_name).read_bytes() == evidence(source/frame_name)
    images = {}
    for frame in sorted(checkpoints):
        name = f'frame_{frame:05d}.png'
        original = sha((out/'v0317'/name).read_bytes())
        candidate = sha((out/'c0038'/name).read_bytes())
        images[frame] = dict(v0317=original, c0038=candidate, exact=original == candidate)
    (out/'v0317-semantic-hashes.bin').write_bytes(hashes)
    report = dict(passed=not difference_count and all(row['exact'] for row in images.values()),
                  first_compared_frame=FIRST_GAMEPLAY_FRAME, last_compared_frame=end,
                  compared_fields=FIELDS, difference_count=difference_count,
                  first_difference_frames=first_differences, images=images, runs=runs,
                  input_trace=source.relative_to(ROOT).as_posix(), initial_sram=False,
                  primary_state_imports=0, approach_hurt_writes=len(writes),
                  evidence=dict(palace_audit_sha256=sha(audit_bytes),
                                capture_sha256=sha(capture_bytes), controls_sha256=sha(controls_bytes),
                                assistance_sha256=sha(evidence(source/'assistance.json'))),
                  driver_sha256=sha(Path(__file__).read_bytes()))
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print('Differing gameplay states:', difference_count, 'Ending images:', images, flush=True)
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
