"""Retain rejected native replay prototypes, source-vector checks and unchanged production rebuild."""
import gzip
import json
import statistics
import struct
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'tools'))
from archive_lossless_evidence import freeze, sha

rom = root / 'versions/v0319-d3ea2a83/gaw-megadrive-v0319.bin'
rebuild = root / 'validation/v319-timed-workspace-rebuild01'
assert (rebuild / 'project/out/release/rom.bin').read_bytes() == rom.read_bytes() == (root / 'gaw-megadrive.bin').read_bytes()
host = json.loads((root / 'validation/v319-timed-workspace01/report.json').read_bytes())
assert host['passed'] and host['source_cases'] == 25644 and host['source_writes_per_implementation'] == 89200
variants = []
for n in range(1, 6):
    work = root / f'validation/v319-buffered-psg{n:02}'
    trace = work / ('trace02' if n in (1, 3) else 'trace')
    capture = json.loads((trace / 'report.json').read_bytes())
    assert sha((work / 'project/out/release/rom.bin').read_bytes()) == capture['md_sha256']
    variants.append(dict(number=n, hypothesis=json.loads((work / 'hypothesis.json').read_bytes()),
                         capture=capture, trace_report=trace.relative_to(root).as_posix() + '/report.json'))
best = variants[2]['capture']
assert all(case['runtime_error_count'] == case['different_exposed_state_frames'] ==
           case['musical_byte_order_difference_frames'] == case['prepared_source_byte_difference_frames'] ==
           case['prepared_source_interval_difference_count'] == 0 for case in best['cases'])
old_archive = root / 'analysis/v319-psg-write-spacing'
manifest = json.loads((old_archive / 'manifest.json').read_bytes())
def old_events(region, tag):
    item = manifest['compressed'][f'validation/v319-psg-writes01/{region}-{tag}/psg-port-writes.bin']
    encoded = (old_archive / item['stored']).read_bytes()
    assert sha(encoded) == item['stored_sha256']
    raw = gzip.decompress(encoded)
    assert sha(raw) == item['raw_sha256']
    frames = [[] for _ in range(14000)]
    for frame, time, value in struct.iter_unpack('<IIB', raw):
        frames[frame - 1].append((time, value))
    return frames
baseline = json.loads((root / 'analysis/sms_psg_writes_v0319_report.json').read_bytes())
comparisons = []
for region in ('ntsc', 'pal'):
    ref = next(case for case in baseline['cases'] if case['region'] == region)
    md = old_events(region, 'md'); sms = old_events(region, 'sms'); errors = []
    for frame in range(ref['first_nonmuted_source_frame'] - 1, 14000):
        assert [v for _, v in md[frame]] == [v for _, v in sms[frame]]
        m = [b[0] - a[0] for a, b in zip(md[frame], md[frame][1:])]
        s = [b[0] - a[0] for a, b in zip(sms[frame], sms[frame][1:])]
        errors.extend(abs(a - b) for a, b in zip(m, s))
    candidate = next(case for case in best['cases'] if case['region'] == region)
    assert len(errors) == candidate['compared_intervals']
    video = json.loads((root / f'validation/v319-buffered-psg03/video-{region}/report.json').read_bytes())
    assert video['md_sha256'] == best['md_sha256'] and video['baseline_sha256'] == sha(rom.read_bytes())
    comparisons.append(dict(region=region, compared_intervals=len(errors),
        baseline_spacing_error_ticks=dict(median=statistics.median(errors), mean=statistics.mean(errors), maximum=max(errors)),
        prototype_spacing_error_ticks=candidate['absolute_spacing_error_ticks'],
        source_video_comparison=video['totals']))
result = dict(diagnostic_only=True, promoted=False, production_rom_sha256=sha(rom.read_bytes()),
    production_rebuild_byte_identical=True, source_workspace_api_checks=host, variants=variants,
    comparisons=comparisons, public_version=319,
    disposition='Reject all five replay prototypes. Variant03 preserves end-of-frame sound state and '
        'source-dated lists, greatly reducing spacing error, but regresses opening video in both regions. '
        'Variant04 drifts in NTSC; variant05 faults in NTSC. Variants01/02 do not reach PSG startup.',
    source_api_change='Caller-owned timed workspace APIs reuse existing timed semantics; old APIs remain wrappers. '
        'Fast/master compositions are named separately. Production does not select these APIs and rebuilds byte-identically.',
    next_action='Deliver source-dated events without synchronously waiting in the video IRQ. Establish preparation '
        'deadlines and first-write physical phase. Existing raw replay seed-to-entry clock sampling bounds '
        'must include rebasing and burst classification overhead; do not merely increase waits to hide faults.',
    limits=['No production bug fix or new public ROM claimed.', 'No absolute phase or PCM equality.',
            'Compact32-channel/64-IRQ staging is a rejecting diagnostic bound, not proof of full-game capacity.',
            'Source full-vector checks run on host; physical replay probes run native68000 in emulator.'],
    archive_manifest='analysis/v319-buffered-psg/manifest.json')
report = root / 'analysis/v319_buffered_psg_report.json'
assert not report.exists()
report.write_text(json.dumps(result, indent=2) + '\n')
paths = {Path(__file__).resolve(), report, root / 'validation/prepare_v319_buffered_psg.py',
         root / 'validation/measure_v319_buffered_psg.py', root / 'validation/check_timed_reader_workspace.py',
         root / 'tools/compare_boot_to_sms.py', root / 'tools/run_core.py', root / 'tools/build_private_candidate.ps1'}
cleanup = []
for n in range(1, 6):
    work = root / f'validation/v319-buffered-psg{n:02}'
    paths.update(p for p in work.rglob('*') if p.is_file())
    cleanup.append(work / 'project/out')
    cleanup.extend(p for p in work.iterdir() if p.is_dir() and p.name != 'project')
for work in (rebuild, root / 'validation/v319-timed-workspace01'):
    paths.update(p for p in work.rglob('*') if p.is_file())
cleanup.extend([rebuild / 'project/out', root / 'validation/v319-timed-workspace01'])
for name in ('source_audio_fast_timed.c', 'source_audio_reader_master.c', 'source_audio_reader_timed.c', 'source_audio_timed.h'):
    paths.add(root / 'megadrive/src' / name)
freeze(root, root / 'analysis/v319-buffered-psg', paths, result, cleanup, cleanup=True)
for comparison in comparisons:
    print(comparison['region'], 'baseline median error', comparison['baseline_spacing_error_ticks']['median'],
          'prototype', comparison['prototype_spacing_error_ticks']['median'], 'ticks; rejected due video regression')
print('All prototypes archived; production rebuild is byte-identical to V319.')
