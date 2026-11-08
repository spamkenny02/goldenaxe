"""Audit full source IRQ handshakes/callbacks and retain read-only observers and captures."""
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'tools'))
from archive_lossless_evidence import freeze, sha

full = root / 'validation/v319-intro-irq-trace02'
raw = json.loads((full / 'report.json').read_bytes())
assert len(raw['cases']) == 2
for case in raw['cases']:
    assert case['frames'] == 14000 and case['observer_exposed_psg_noninterference']
    assert case['source_return_clock_delta_counts'] == {'1': case['source_full_irq_returns']}
    baseline = case['native_callback_frame_comparisons']['baseline']
    assert baseline['total_native_callbacks'] == case['source_callbacks']
    assert baseline['versus_baseline_callback_changes'] == []
    if case['region'] == 'pal':
        assert all(not item['versus_baseline_callback_changes'] for item in case['native_callback_frame_comparisons'].values())
    else:
        values = [case['native_callback_frame_comparisons'][f'prefetch{n:02}']['total_native_callbacks']
                  for n in range(1, 4)]
        assert values == [11851, 11855, 11858]
build = root / 'validation/v319-intro-irq-observer01'
br = json.loads((build / 'report.json').read_bytes())
assert br['passed'] and br['original_source_restored'] and br['core_sha256'] == raw['core_sha256']
source = root.parents[1] / 'work/genesis-plus-gx/core/z80/z80.c'
assert sha(source.read_bytes()) == br['original_source_sha256']
result = dict(diagnostic_only=True, observer_noninterference_audited=True,
    production_rom_sha256=sha((root / 'gaw-megadrive.bin').read_bytes()),
    source_sha256=sha((root / 'input/original.sms').read_bytes()),
    core_sha256=raw['core_sha256'], cases=raw['cases'],
    intro_state_noninterference_checked=dict(ntsc=['sms', 'baseline', 'prefetch01'], pal=[]),
    findings=['Every recorded completed source B95/full-IRQ handshake increments C02F exactly once: '
              '13397 NTSC and13466 PAL over14000 frames each.',
              'Source F32 entry counts11857 NTSC and11926 PAL equal native V319 intro_tick counts, '
              'but observed callback frame differs on94 NTSC and84 PAL frames. Matching total counts '
              'is not per-frame scheduling parity.',
              'All three foreground-preparation prototypes preserve native PAL callback frame placement '
              'relative to V319. NTSC total callback deltas are-6,-2,+1. Source comparison is retained '
              'separately, never replaced by baseline-only checks.',
              'At the second NTSC reveal, source and V319 call F32/intro_tick on1784,1789,1794,1799. '
              'Prefetch01 delays callbacks to1785,1790,1795,1800. Prefetch02 removes bootstrap extra waits '
              'but retains this reveal crossing. Immediate control prefetch03 first differs from baseline '
              'later, at3624, and increases the accumulated callback count by one at10425.'],
    next_action='Model the source full-IRQ request/acknowledgement and F09/F32 scheduling at loader/reveal '
        'boundaries independently of native audio computation cost. This evidence does not justify global '
        'callback frame overrides, animation phase patches, a global music delay or restoring rejected prototypes.',
    limits=['Original source and production ROM unmodified; prototypes remain rejected.',
            'Read-only observer parity: exposed PSG all five streams in both regions, previous intro states '
            'SMS/baseline/prefetch01 in NTSC only.',
            'No absolute cross-platform clock alignment, PCM, real hardware or full-game scheduler proof.'],
    ram_writes=0, sram_imports=0, archive_manifest='analysis/v319-intro-irq-trace/manifest.json')
report = root / 'analysis/v319_intro_irq_trace_report.json'
assert not report.exists()
report.write_text(json.dumps(result, indent=2) + '\n')
paths = {Path(__file__).resolve(), report, root / 'validation/trace_v319_intro_irq.py',
         root / 'validation/build_v319_intro_irq_observer.py', root / 'tools/build_timing_core.py', root / 'tools/run_core.py'}
short = root / 'validation/v319-intro-irq-trace01'
for folder in (full, short, build):
    paths.update(p for p in folder.rglob('*') if p.is_file())
freeze(root, root / 'analysis/v319-intro-irq-trace', paths, result, [full, short], cleanup=True)
print('Source full-IRQ/callback proof audited; all captures frozen, generated binaries cleaned.')
