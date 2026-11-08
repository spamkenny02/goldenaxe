"""Freeze explicit request/ack IRQ ordering controls with source video and reader proofs."""
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'tools'))
from archive_lossless_evidence import freeze, sha

rom = root / 'versions/v0319-d3ea2a83/gaw-megadrive-v0319.bin'
assert rom.read_bytes() == (root / 'gaw-megadrive.bin').read_bytes()
variants = []; paths = set(); cleanup = []
for number in range(1, 6):
    work = root / f'validation/v319-intro-irq-ack{number:02}'
    state = json.loads((work / 'state/report.json').read_bytes())
    assert state['md_sha256'] == sha((work / 'project/out/release/rom.bin').read_bytes())
    assert state['baseline_sha256'] == sha(rom.read_bytes())
    video = {}
    for case in state['cases']:
        assert case['frames'] == 14000 and case['runtime_errors'] == 0
        assert case['reader_state_difference_frames'] == case['source_psg_difference_frames'] == 0
        if number in (3, 5) or case['region'] == 'pal':
            assert case['intro_state_difference_frames'] == 0
        counter = case['counters']
        assert counter['pending'] in (1, 2)
        if number != 5:
            assert counter['intro_full_irq_requests'] == counter['intro_full_irq_acks'] + 1
        report = json.loads((work / ('video-' + case['region']) / 'report.json').read_bytes())
        assert report['md_sha256'] == state['md_sha256'] and report['baseline_sha256'] == sha(rom.read_bytes())
        assert report['frames'] == 14000
        video[case['region']] = dict(totals=report['totals'], improved_pixels=report['improved_pixels'],
            degraded_pixels=report['degraded_pixels'], no_source_pixel_regression=report['no_source_pixel_regression'])
    assert video['ntsc']['degraded_pixels'] > video['ntsc']['improved_pixels']
    variants.append(dict(number=number, hypothesis=json.loads((work / 'hypothesis.json').read_bytes()),
                         state=state, video=video, promoted=False))
    paths.update(p for p in work.rglob('*') if p.is_file())
    cleanup.append(work / 'project/out')
    cleanup.extend(p for p in work.iterdir() if p.is_dir() and p.name != 'project')
result = dict(diagnostic_only=True, promoted=False, public_version=319,
    production_rom_sha256=sha(rom.read_bytes()), variants=variants,
    disposition='Reject all five integrations. Moving native F32 work into IRQ tail is not equivalent to '
        'the source foreground callback after IRQ return. Foreground callbacks with explicit IRQ acknowledgement '
        'preserve all five sampled intro fields but still change raster pixels. Speculative preparation remains '
        'unsafe for NTSC video in this integration.',
    strongest_preserved_checks='Variants03/05: every frame of two14000-frame region runs has identical '
        'five intro fields and420 bytes of reader/work/DE/requests/track data to V319, and all eight exposed PSG '
        'values identical to SMS. These scoped equalities do not prove physical publication timing.',
    end_pending_request='All runs end while waiting for the following full IRQ; instrumented variants have '
        'requests=acks+1 and pending2. Lean variant has pending1. This is not an observed stuck wait.',
    next_action='Use continuous SourceClock instruction boundaries and dynamic SourceIrqContext audio work '
        'for reveal/loader scheduling. Existing source_wait/source_wait_complete already model B95 request '
        'and acknowledgement. Model F09/F32 continuation and F21 V-counter polling there, then connect native '
        'publication with measured preparation deadlines. Avoid frame-count/counter overrides or further '
        'arbitrary IRQ-tail relocation.',
    limits=['No production ROM/source modifications; private tests only.',
            'No interactive, SRAM, boss, PCM or real-hardware test of these rejected integrations.',
            'Five intro fields are logical clock, actor counter, text line, text timer, scene. '
            'All other RAM and every actual actor slot were not compared by this checker.',
            'Compact speculative channel capacity remains experimental; full-size native IRQ fallback retained.'],
    ram_writes=0, sram_imports=0, archive_manifest='analysis/v319-intro-irq-ack/manifest.json')
report = root / 'analysis/v319_intro_irq_ack_report.json'
assert not report.exists()
report.write_text(json.dumps(result, indent=2) + '\n')
paths.update([report, Path(__file__).resolve(), root / 'validation/prepare_v319_intro_irq_ack.py',
              root / 'validation/measure_v319_intro_irq_ack.py', root / 'validation/prepare_v319_audio_prefetch.py',
              root / 'tools/run_core.py', root / 'tools/compare_boot_to_sms.py', root / 'tools/build_private_candidate.ps1'])
freeze(root, root / 'analysis/v319-intro-irq-ack', paths, result, cleanup, cleanup=True)
print('Five request/ack controls audited and rejected; public V319 unchanged.')
