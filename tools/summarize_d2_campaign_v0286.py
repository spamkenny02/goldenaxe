"""Bind D2 victories and exits on unchanged SMS/native v286 to explicit assistance."""
import json
from run_core import ROOT
from rebase_natural_campaign import evidence
from archive_lossless_evidence import sha
from validate_playable_sprite_limit import symbols


def main():
    refs = {}

    def raw(name):
        value = evidence(ROOT / name)
        refs[name] = sha(value)
        return value

    def load(name):
        return json.loads(raw(name))

    digest = sha((ROOT / 'gaw-megadrive.bin').read_bytes())
    source_digest = sha((ROOT / 'input/original.sms').read_bytes())
    stages = {}
    final = {}
    for tag, expected, size in [('md', digest, 65536), ('sms', source_digest, 8192)]:
        stages[tag] = []
        for stage in ['key01', 'nav01', 'exit01']:
            folder = f'validation/natural-dungeon-combat/{tag}-auto-v0286-d2-assisted-{stage}'
            report = load(folder + '/report.json')
            capture = load(folder + '/capture.json')
            assist = load(folder + '/assistance.json')
            frame = capture['frames']
            replay = load(folder + f'-assisted-fixed-replay-{frame}/replay_report.json')
            assert report['rom_sha256'] == capture['rom_sha256'] == replay['rom_sha256'] == expected
            assert report['room_cleared'] and not report['deaths'] and report['failure'] is None
            assert replay['passed'] and replay['whole_ram_bytes'] == size and replay['final_png_exact']
            assert replay['assisted_route'] and not replay['natural_campaign_proof'] and not replay['feedback_reads']
            assert report['ram_injections'] and assist['health_refills'] == 0
            assert assist['rom_modifications'] is False and assist['boss_assistance'] is False
            for name, value in replay['evidence'].items():
                assert sha(raw(folder + '/' + name)) == value
            if stage == 'key01':
                assert report['new_key_verified'] and report['last_state']['keys'] == 2
                assert report['last_state']['health'] == 40 and assist['first_boss_combat'] is None
            else:
                assert assist['release_write_frame'] < assist['first_boss_combat']['frame']
                assert assist['first_boss_combat']['hurt'] == 0 and assist['first_boss_combat']['health'] == 40
                assert all(row['frame'] <= assist['release_write_frame'] for row in assist['writes'])
                assert assist['first_boss_damage']['after'] < assist['first_boss_damage']['before']
                assert report['last_state']['max_health'] == 48
            if stage == 'nav01':
                assert report['last_state']['progress'] == 128 and report['last_state']['health'] == 48
                assert report['verified_persistent_prediction_windows'] == report['full_ram_prediction_matches']
                assert report['stack_only_difference_windows'] == 0
            if stage == 'exit01':
                assert report['full_dungeon_cleared'] and report['last_state']['room'] == 0xd6
                assert report['last_state']['completed_dungeon_progress'] == 128
                final[tag] = raw(folder + f'/ram_{frame:05d}.bin')
            stages[tag].append(dict(stage=stage, trace=folder, frames=frame, state=report['last_state'],
                                    release_frame=assist['release_write_frame'],
                                    first_boss_combat=assist['first_boss_combat'],
                                    first_boss_damage=assist['first_boss_damage'],
                                    full_ram_prediction_windows=report.get('full_ram_prediction_matches')))
    sy = symbols(ROOT / 'megadrive/out/release/symbol.txt')
    data = lambda name, size: bytes(final['md'][(sy[name] + i) ^ 1] for i in range(size))
    assert data('game_save_state', 592)[0x50:0x150] == final['sms'][0x100:0x200]
    assert data('sms_vram', 16384)[0x3800:0x3d00] == final['sms'][0x1600:0x1b00]
    assert data('game_save_state', 592)[0x1f:0x21] == final['sms'][0xcf:0xd1] == b'\x80\x80'
    stack = load('validation/stack-v0286-d2-assisted-all/stack_report.json')
    assert stack['md_sha256'] == digest and stack['all_instructions'] and stack['read_only']
    assert stack['logged_assistance_replayed'] and not stack['invalid_heap_examples']
    minimum = min(row['sp'] for row in stack['instruction_minima'])
    boundary = max(row['end'] for row in stack['heap_changes']) + 2
    assert minimum > boundary and all(row['valid'] for row in stack['heap_changes'])
    end = stages['md'][-1]['frames']
    for stem, ext in [('ram', 'bin'), ('frame', 'png')]:
        filename = f'{stem}_{end:05d}.{ext}'
        assert raw('validation/stack-v0286-d2-assisted-all/' + filename) == raw(stages['md'][-1]['trace'] + '/' + filename)
    cadence = load('validation/boss-cadence-v0286-nav01/cadence_report.json')
    assert cadence['rom_sha256'] == digest and cadence['ram_and_png_match_recording']
    result = dict(passed=True, md_sha256=digest, source_sha256=source_digest, version=286,
                  game_binary_changed=False, second_crystal_verified=True, assisted_approach=True,
                  boss_assistance=False, exit_assistance=False, health_refills=0, deaths=0,
                  stages=stages, source_exit_flags_exact_bytes=256, source_exit_map_exact_bytes=1280,
                  minimum_sp=minimum, stack_boundary=boundary, observed_stack_margin=minimum-boundary,
                  heap_valid=True, stack_observer_whole_ram_and_png_exact=True,
                  boss_cadence=dict(first=cadence['first_frame'], last=cadence['last_frame'],
                                    ticks=cadence['observed_ticks'], gaps=cadence['gaps']),
                  full_game_validated=False, evidence=refs,
                  limits=['Approach assistance writes only the hero hurt counter. It ends before the boss; combat and exit are not assisted. Each trace is independently replayed cold, without SRAM/state imports or feedback.',
                          'Individual full-RAM/PNG replay equality is within each system. Cross-system equality here covers persistent flags and the final map, not encounters, remaining health, global R/IRQ, all frame pixels, waveform or hardware.',
                          'Historical SMS planner read C302 as its facing heuristic; corrected to C30A after the successful trace. Its original driver bytes are preserved. Recorded actual buttons and full RAM/PNG replays remain authoritative.',
                          'Three native tick gaps over this boss segment remain. Different encounters/inputs prevent interpreting their count as an old/new FPS comparison. PAL campaign and the rest of the game remain unvalidated.'])
    (ROOT / 'analysis/d2_campaign_v0286_report.json').write_text(json.dumps(result, indent=2) + '\n')
    print({key: value for key, value in result.items() if key not in ['evidence', 'stages', 'limits']})


if __name__ == '__main__':
    main()
