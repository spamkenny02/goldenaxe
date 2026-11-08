"""Freeze foreground-preparation controls and their source video regressions."""
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'tools'))
from archive_lossless_evidence import freeze, sha

rom = root / 'versions/v0319-d3ea2a83/gaw-megadrive-v0319.bin'
assert rom.read_bytes() == (root / 'gaw-megadrive.bin').read_bytes()
variants = []; paths = set(); cleanup = []
for n in range(1, 4):
    work = root / f'validation/v319-audio-prefetch{n:02}'
    audio = json.loads((work / 'audio/report.json').read_bytes())
    assert audio['md_sha256'] == sha((work / 'project/out/release/rom.bin').read_bytes())
    assert audio['production_sha256'] == sha(rom.read_bytes())
    for case in audio['cases']:
        assert case['runtime_error_count'] == case['reader_state_difference_frames'] == \
            case['source_psg_state_difference_frames'] == case['musical_byte_order_difference_frames'] == 0
        assert case['counters']['hits'] > 13000
    video = {}
    for region in ('ntsc', 'pal'):
        report = json.loads((work / ('video-' + region) / 'report.json').read_bytes())
        assert report['md_sha256'] == audio['md_sha256'] and report['baseline_sha256'] == sha(rom.read_bytes())
        assert report['frames'] == 14000 and report['degraded_pixels'] > 0
        video[region] = dict(totals=report['totals'], improved_pixels=report['improved_pixels'],
                             degraded_pixels=report['degraded_pixels'], no_source_pixel_regression=report['no_source_pixel_regression'])
    variants.append(dict(number=n, hypothesis=json.loads((work / 'hypothesis.json').read_bytes()),
                         audio=audio, source_video=video, promoted=False))
    paths.update(p for p in work.rglob('*') if p.is_file())
    cleanup.append(work / 'project/out')
    cleanup.extend(p for p in work.iterdir() if p.is_dir() and p.name != 'project')
clock = json.loads((root / 'validation/v319-audio-prefetch01/intro-clock/report.json').read_bytes())
assert clock['different_frame_counts']['intro_line'] == clock['different_frame_counts']['intro_timer'] == 0
assert clock['different_frame_counts']['intro_logic_clock'] > 10000
result = dict(diagnostic_only=True, promoted=False, public_version=319, production_rom_sha256=sha(rom.read_bytes()),
    variants=variants, ntsc_intro_clock_probe=clock,
    disposition='Reject all three foreground-preparation integrations. Reader state, source PSG states and musical '
        'byte/order remain exact across 14000 frames per region for all variants, but source video regresses. '
        'Avoiding a second wait after a preparation crossing reduces the regression, not eliminates it. '
        'Immediate-emission control also regresses NTSC and worsens spacing.',
    observations=['Speculative state is separate; actual IRQ reader is the fallback for stale frames, changed requests, '
        'foreground fade/compensation parameters, rejection and compact-capacity overflow.',
        'Variant01 baseline/candidate native intro line and timer remain equal at every sampled NTSC frame; '
        'intro callback clock differs on12209 and actor counter on3369. The clock/source mismatch is much larger '
        'than baseline. Foreground callback phase is therefore a separate integration issue, not a musical-state mismatch.',
        'Variant03 removes dated wait but retains speculative computation/cache use. It does not prove preparation '
        'alone causes all drift because emission work also changes relative to production.'],
    next_action='Trace full-IRQ requests/acknowledgement and F09/F32 callback publication against the source IRQ '
        'phase; integrate source callback scheduling independently of native reader cost. For asynchronous PSG '
        'delivery retain real preparation/publication deadlines and first-write phase. Do not tune animation counters '
        'to a recorded frame or assume matching end-of-frame PSG states imply correct video/audio timing.',
    limits=['No interactive input, boss, SRAM or full-game test of these rejected prototypes.',
            'The source C02F clock probe is NTSC only; PAL video/audio reports are separate.',
            'No PCM equality, absolute source audio phase, hardware or complete asynchronous scheduler claim.',
            'Production sources and V319 ROM unchanged by this experiment.'],
    archive_manifest='analysis/v319-audio-prefetch/manifest.json')
report = root / 'analysis/v319_audio_prefetch_report.json'
assert not report.exists()
report.write_text(json.dumps(result, indent=2) + '\n')
paths.update([report, Path(__file__).resolve(), root / 'validation/prepare_v319_audio_prefetch.py',
              root / 'validation/measure_v319_audio_prefetch.py', root / 'validation/probe_v319_intro_clock_prefetch.py',
              root / 'tools/run_core.py', root / 'tools/compare_boot_to_sms.py', root / 'tools/build_private_candidate.ps1'])
freeze(root, root / 'analysis/v319-audio-prefetch', paths, result, cleanup, cleanup=True)
for variant in variants:
    print('Rejected', variant['number'], {region: row['totals']['candidate_source_differences']
                                        for region, row in variant['source_video'].items()})
