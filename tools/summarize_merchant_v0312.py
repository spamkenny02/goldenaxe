"""Bind merchant reveal and cross-scene evidence to the v312 cartridge hash."""
import json
from pathlib import Path

from archive_lossless_evidence import sha
from run_core import ROOT


def main():
    experiment = ROOT / 'validation/v0311-merchant'
    candidate = experiment / 'candidate02'
    references = {}

    def read(path):
        raw = path.read_bytes()
        references[str(path.relative_to(ROOT))] = sha(raw)
        return json.loads(raw)

    digest = sha((candidate / 'out/release/rom.bin').read_bytes())
    assert digest == '0b9aecb48fc9bb82cfcebc9547684742134d60e0f82e60b1a070ab3be50b4d64'
    for path in ['megadrive/out/release/rom.bin', 'gaw-megadrive.bin', 'gaw-title-megadrive.bin']:
        assert sha((ROOT / path).read_bytes()) == digest
    audit = read(experiment / 'candidate02-audit-report.json')
    assert audit['candidate_sha256'] == digest
    assert audit['merchant_mask_timing_source_exact'] and audit['black_window_source_exact']
    assert audit['release_cross_scene_gate_passed'] and not audit['scroll_regressions']
    assert len(audit['scenes']) == 2 and len(audit['transactions']) == 7
    all_merchants = read(candidate / 'all_merchants_report.json')
    assert all_merchants['md_sha256'] == digest
    assert all_merchants['all_23_towns_checked'] and len(all_merchants['cases']) == 43
    trace = read(experiment / 'candidate02-cold-d2-report.json')
    assert trace['semantic_trace_exact'] and not trace['first_differences']
    assert trace['frames'] == 38781 and trace['compared_frames'] == 35782
    assert not trace['initial_sram'] and trace['primary_state_imports'] == 0
    assert trace['roms'][0]['rom_sha256'] == audit['md_sha256']
    assert trace['roms'][1]['rom_sha256'] == digest
    for item in trace['roms']:
        path = experiment / f"cold-d2-{item['tag']}/capture.json"
        capture = read(path)
        assert references[str(path.relative_to(ROOT))] == item['capture_sha256']
        assert capture['rom_sha256'] == item['rom_sha256']
        assert capture['sram_input'] is None and not capture['save_states']
    end = trace['frames']
    first = experiment / f'cold-d2-v311/frame_{end:05d}.png'
    second = experiment / f'cold-d2-candidate02/frame_{end:05d}.png'
    assert first.read_bytes() == second.read_bytes()
    for path in [first, second, experiment / 'trace_candidate02.py']:
        references[str(path.relative_to(ROOT))] = sha(path.read_bytes())
    inventory = read(ROOT / 'validation/inventory_restore_v0312_report.json')
    assert inventory['md_sha256'] == digest and not inventory['diagnostic_only']
    assert len(inventory['cases']) == 6
    for case in inventory['cases']:
        assert case['inventory_open_and_closed']
        assert not any(case['static_background_pattern_difference_indices'].values())
        assert not case['early_native_static_pattern_changes_from_before_menu']
    result = dict(passed=True, version=312, md_sha256=digest,
                  baseline_sha256=audit['md_sha256'], adopted=True,
                  merchant_reveal=audit['scenes'], transactions=audit['transactions'],
                  all_merchants=all_merchants['cases'], scroll_comparisons=audit['scroll_comparisons'],
                  cold_ntsc_d2_comparison=trace, final_png_same_as_v311=True,
                  inventory_restore=inventory,
                  compared_semantic_state_exact=True, whole_ram_across_builds_compared=False,
                  full_game_validated=False, full_source_audio_video_validated=False,
                  source_global_r_irq_port_complete=False, hardware_validated=False,
                  evidence=references, driver_sha256=sha(Path(__file__).read_bytes()),
                  limits=[
                      'Merchant portrait plane-2 publication and black-window timing match live SMS captures in PAL/NTSC. First settled panel remains one frame late in PAL.',
                      '43 controlled cases cover 23 towns; one natural first-village walk/refusal/exit uses no RAM writes or initial SRAM.',
                      'Cold v311 controls replay through D2 exit on v312. Named state fields match on 35782 frames; stack/layout bytes are excluded. Recorded approach-only hurt writes are address-remapped, with no resource or actor writes and no primary state imports.',
                      'This extends targeted v312 evidence. Complete campaign-to-credits proof remains v310; source global timing, optional coverage and hardware remain open.'
                  ])
    output = ROOT / 'analysis/merchant_inventory_v0312_report.json'
    output.write_bytes((json.dumps(result, indent=2) + '\n').encode())
    print('v312 merchant reveal, 43 transactions and unchanged NTSC D2 trace audited.')


if __name__ == '__main__':
    main()
