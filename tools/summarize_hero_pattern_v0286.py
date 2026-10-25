"""Bind the playable hero optimization to scoped pixels, cadence and campaign evidence."""
import json
from run_core import ROOT
from rebase_natural_campaign import evidence
from summarize_axe_campaign_v0274 import read as historical
from validate_playable_sprite_limit import symbols
from archive_lossless_evidence import sha
from finalize_md_rom import md_checksum


def main():
    rom = (ROOT / 'gaw-megadrive.bin').read_bytes()
    digest = sha(rom)
    refs = {}

    def raw(name):
        value = evidence(ROOT / name)
        refs[name] = sha(value)
        return value

    def load(name):
        return json.loads(raw(name))

    hero = load('validation/hero_pattern_fast_v0286_report.json')
    assert hero['passed'] and hero['md_sha256'] == digest
    assert all(case['hero_pose_and_packed_pixels_exact'] and case['reduction_percent'] > 0 for case in hero['cases'])
    cadence = [load('validation/' + name) for name in ['timing_report.json', 'timing-pal_report.json']]
    for report in cadence:
        assert report['md_sha256'] == digest
        assert all(case['differing_state_frames'] == 0 for case in report['natural_input_sequences'])
        assert report['enemy']['differing_motion_counter_frames'] == 0
    menu = load('validation/menu_transition_report.json')
    boss = load('validation/first_boss_gameplay_report.json')
    assert menu['md_sha256'] == boss['md_sha256'] == digest and len(menu['cases']) == 6
    stages = []
    for name in ['md-auto-v0286-axe02', 'md-auto-v0286-d1-boss01', 'md-auto-v0286-d1-exit01']:
        folder = 'validation/natural-dungeon-combat/' + name
        report = load(folder + '/report.json')
        capture = load(folder + '/capture.json')
        assert report['rom_sha256'] == capture['rom_sha256'] == digest
        assert report['room_cleared'] and report['failure'] is None and not report['deaths']
        assert not capture['test_ram_writes'] and capture['sram_input'] is None
        stages.append(dict(trace=name, frames=capture['frames'], state=report['last_state']))
    folder = 'validation/natural-dungeon-combat/md-auto-v0286-d1-exit01'
    replay = load(folder + '-fixed-replay/replay_report.json')
    assert replay['passed'] and replay['whole_ram_bytes'] == 65536 and replay['final_png_exact']
    frame = stages[-1]['frames']
    ram = raw(folder + f'/ram_{frame:05d}.bin')
    stack = load('validation/stack-v0286-d1-all/stack_report.json')
    assert stack['read_only'] and stack['all_instructions'] and not stack['invalid_heap_examples']
    minimum = min(row['sp'] for row in stack['instruction_minima'])
    boundary = max(row['end'] for row in stack['heap_changes']) + 2
    assert minimum > boundary and all(row['valid'] for row in stack['heap_changes'])
    for stem, ext in [('ram', 'bin'), ('frame', 'png')]:
        assert raw(folder + f'/{stem}_{frame:05d}.{ext}') == raw(f'validation/stack-v0286-d1-all/{stem}_{frame:05d}.{ext}')
    sy = symbols(ROOT / 'megadrive/out/release/symbol.txt')
    data = lambda name, size: bytes(ram[(sy[name] + i) ^ 1] for i in range(size))
    source = ROOT / 'validation/natural-dungeon-combat/sms-auto-v0274-axe-exit01'
    sc = json.loads(historical(source / 'capture.json'))
    sr = historical(source / f"ram_{sc['frames']:05d}.bin")
    assert data('game_save_state', 592)[0x50:0x150] == sr[0x100:0x200]
    assert data('sms_vram', 16384)[0x3800:0x3d00] == sr[0x1600:0x1b00]
    assert md_checksum(rom) == int.from_bytes(rom[0x18e:0x190], 'big')
    result = dict(passed=True, md_sha256=digest, version=286, bytes=len(rom),
                  checksum=f'{md_checksum(rom):04X}', hero_conversion=hero['cases'],
                  source_timing_sequences=6, controlled_boss_frames=sum(c['frames'] for c in boss['cases']),
                  menu_cases=6, natural_first_dungeon=stages, deaths=0,
                  cold_fixed_ram_bytes=65536, cold_fixed_png_exact=True,
                  source_exit_flags_exact_bytes=256, source_exit_map_exact_bytes=1280,
                  minimum_sp=minimum, stack_boundary=boundary, stack_margin=minimum-boundary,
                  heap_valid=True, stack_observer_ram_and_png_exact=True,
                  second_crystal_verified=False, full_game_validated=False, evidence=refs,
                  limits=['16.95 percent is the measured hero preparation function CPU reduction, not global FPS. No claim that all seven v285 boss cadence gaps are removed.',
                          'Old v285 long controls diverge on v286. The current first dungeon was regenerated from live ordinary input; no invulnerability or state injection.',
                          'The assisted v285 boss search remains separate historical evidence; no second boss victory, full campaign, global source RNG/IRQ, waveform or hardware completion claim.'])
    (ROOT / 'analysis/hero_pattern_v0286_report.json').write_text(json.dumps(result, indent=2) + '\n')
    print({key: value for key, value in result.items() if key not in ['evidence', 'natural_first_dungeon']})


if __name__ == '__main__':
    main()
