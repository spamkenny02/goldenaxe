"""Bind natural start-menu music and cursor/confirm checks to v312."""
import json
from pathlib import Path

from archive_lossless_evidence import sha
from run_core import ROOT


def main():
    references = {}

    def load(path):
        raw = (ROOT / path).read_bytes()
        references[path] = sha(raw)
        return json.loads(raw)

    digest = sha((ROOT / 'gaw-megadrive.bin').read_bytes())
    assert digest == '0b9aecb48fc9bb82cfcebc9547684742134d60e0f82e60b1a070ab3be50b4d64'
    source_digest = sha((ROOT / 'input/original.sms').read_bytes())
    music = load('validation/start_menu_audio_v0312_report.json')
    effects = load('validation/natural_start_menu_sfx_v0312_report.json')
    for report in (music, effects):
        assert report['md_sha256'] == digest and report['source_sha256'] == source_digest
        assert report['natural_controller_input'] and not report['ram_injections']
    assert len(music['cases']) == 2 and len(effects['cases']) == 4
    for case in music['cases']:
        region = case['region']
        assert case['results']['sms']['track_89_source_call_frames']
        for tag in ('sms', 'md'):
            assert case['results'][tag]['active_music_frames'] == 501
            assert case['results'][tag]['audible_frames'] > 400
            capture = load(f'validation/start-menu-audio-v0312-{tag}-{region}/capture.json')
            assert capture['rom_sha256'] == (digest if tag == 'md' else source_digest)
            assert capture['sram_input'] is None and not capture['test_ram_writes']
    for case in effects['cases']:
        region, choice = case['region'], case['choice']
        expected = [[1101, 0x95], [1301, 0x95]]
        if choice == 'continue':
            expected.append([1501, 0x95])
        expected.append([1601, 0xab])
        for tag in ('sms', 'md'):
            assert case['results'][tag]['events'] == expected
            assert case['results'][tag]['audible_effects']
            capture = load(f'validation/start-menu-sfx-v0312/{choice}-{region}-{tag}/capture.json')
            assert capture['rom_sha256'] == (digest if tag == 'md' else source_digest)
            assert capture['sram_input'] is None and not capture['test_ram_writes']
    assert effects['same_choice_presses_silent']
    for name in ('validate_start_menu_audio.py', 'validate_start_menu_sfx.py'):
        path = 'validation/v0312-ui-audio/' + name
        references[path] = sha((ROOT / path).read_bytes())
    result = dict(passed=True, version=312, md_sha256=digest, source_sha256=source_digest,
                  music=music['cases'], effects=effects['cases'],
                  music_track=0x89, music_active_and_audible_both_regions=True,
                  cursor_and_confirm_event_frames_source_exact=True,
                  unchanged_choice_presses_silent=True, ram_writes=0, initial_sram_inputs=0,
                  full_game_audio_validated=False, evidence=references,
                  driver_sha256=sha(Path(__file__).read_bytes()),
                  limits=['Natural New Game/Continue input in PAL and NTSC. Music uses the locally instrumented GX menu core; effects use the local GX build.',
                          'Checks track selection, active channels, audible PSG and effect scheduling. It does not claim equal music onset, complete PSG sequences, waveforms or whole-game audio.'])
    (ROOT / 'analysis/start_menu_v0312_report.json').write_bytes((json.dumps(result, indent=2) + '\n').encode())
    print('v312 start-menu music and source-exact cursor/confirm event timing audited, PAL/NTSC.')


if __name__ == '__main__':
    main()
