"""Bind secondary-rendering benchmark and an unchanged, cold-replayed D5 exit."""
import json
from archive_lossless_evidence import sha
from assisted_prefix import recording
from rebase_natural_campaign import evidence
from run_core import ROOT


def main():
    refs = {}

    def read(path):
        raw = evidence(ROOT/path)
        refs[path] = sha(raw)
        return raw

    def load(path):
        return json.loads(read(path))

    benchmark = load('validation/prediction-video-skip-v0312-05/report.json')
    assert benchmark['passed'] and benchmark['benchmark_only']
    assert benchmark['secondary_refresh_fixture_zero'] and benchmark['primary_imports'] == 0
    assert len(benchmark['cases']) == 60 and all(case['whole_ram_exact'] for case in benchmark['cases'])
    digest = sha(read('gaw-megadrive.bin'))
    assert benchmark['md_sha256'] == digest
    prior = load('analysis/d5_campaign_v0312_report.json')
    assert prior['passed'] and prior['md_sha256'] == digest
    normal = 'validation/natural-dungeon-combat/md-auto-v0312-d5-exit02'
    fast = 'validation/natural-dungeon-combat/md-auto-v0312-d5-fast-exit-check02'
    normal_cap = load(normal+'/capture.json')
    cap, r = load(fast+'/capture.json'), load(fast+'/report.json')
    frame = cap['frames']
    assert frame == normal_cap['frames'] == 131180
    assert cap['sram_input'] is None and cap['rom_sha256'] == r['rom_sha256'] == digest
    assert r['failure'] is None and not r['deaths'] and r['dungeon_exit_verified']
    assert r['unassisted_extension'] and not r['new_assistance_writes'] and not r['primary_state_imports']
    assert r['secondary_video_suppressed'] and not r['primary_video_suppressed']
    assert r['secondary_audio_enabled'] and not r['fast_savestate_format']
    assert r['full_ram_prediction_matches'] == r['verified_persistent_prediction_windows'] == 7
    assert not r['stack_only_difference_windows']
    for key, path in [('prediction_video_wrapper_sha256','tools/unassisted_fast_prediction.py'),
                      ('prediction_video_adapter_sha256','tools/prediction_video_skip.py')]:
        assert r[key] == sha(read(path))
    aid, writes = recording(ROOT/fast, cap)
    normal_aid, normal_writes = recording(ROOT/normal, normal_cap)
    assert writes == normal_writes and aid['release_write_frame'] == normal_aid['release_write_frame']
    proof_root = fast + f'-assisted-fixed-replay-{frame}'
    proof = load(proof_root+'/replay_report.json')
    assert proof['passed'] and proof['rom_sha256'] == digest
    assert proof['whole_ram_bytes'] == 65536 and proof['final_png_exact'] and not proof['feedback_reads']
    for name in ('capture.json','controls.json','assistance.json'):
        assert proof['evidence'][name] == sha(read(fast+'/'+name))
    for stem, ext in [('ram','bin'),('frame','png')]:
        name=f'/{stem}_{frame:05d}.{ext}'
        assert read(normal+name) == read(fast+name) == read(proof_root+name)
    result = dict(passed=True,version=312,md_sha256=digest,production_rom_unchanged=True,
                  benchmark_cases=60,benchmark_speedup=benchmark['speedup'],
                  benchmark_secondary_refresh_fixture_zero=True,
                  unassisted_exit_trace=fast,frames=frame,full_ram_prediction_windows=7,
                  normal_planner_endpoint_ram_png_exact=True,official_cold_replay_ram_png_exact=True,
                  primary_state_imports=0,new_assistance_writes=0,evidence=refs,
                  limits=['The measured speedup covers secondary prediction work, not all tests or game speed.',
                          'Sixty secondary-only antichamber/boss cases and a real D5 exit are covered; no global emulator-equivalence claim.',
                          'Future uses retain per-window full-RAM verification and an official cold replay. Audio and the snapshot format remain enabled.'])
    (ROOT/'analysis/prediction_video_skip_v0312_report.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Secondary video suppression verified: 60 cases, 7 live prediction windows and official cold replay')


if __name__ == '__main__':
    main()
