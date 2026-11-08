"""Audit unmodified PSG bytes and origin-independent spacing; correct state metadata."""
import collections
import gzip
import json
import statistics
import struct
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'tools'))
from archive_lossless_evidence import freeze, sha

work = root / 'validation/v319-psg-writes01'
build = root / 'validation/v319-psg-write-observer01'
trace = json.loads((work / 'report.json').read_bytes())
assert trace['observer_noninterference_validated'] and not trace['passed']
old_archive = root / 'analysis/v319-sms-psg'
old_manifest = json.loads((old_archive / 'manifest.json').read_bytes())
rom = root / 'versions/v0319-d3ea2a83/gaw-megadrive-v0319.bin'
assert sha(rom.read_bytes()) == trace['rom_sha256']
cases = []
for region in ('ntsc', 'pal'):
    rows = {}
    state_bytes = {}
    for tag in ('md', 'sms'):
        folder = work / (region + '-' + tag)
        raw = (folder / 'psg-port-writes.bin').read_bytes()
        events = [[] for _ in range(14000)]
        for frame, clocks, value in struct.iter_unpack('<IIB', raw):
            assert 1 <= frame <= 14000
            events[frame - 1].append((clocks, value))
        rows[tag] = events
        state_bytes[tag] = (folder / 'exposed-psg-states.bin').read_bytes()
        item = old_manifest['compressed'][f'validation/v319-sms-psg02/{region}-{tag}/psg-registers.bin']
        encoded = (old_archive / item['stored']).read_bytes()
        assert sha(encoded) == item['stored_sha256']
        original = gzip.decompress(encoded)
        assert sha(original) == item['raw_sha256']
        assert original == state_bytes[tag] and len(original) == 14000 * 16
    assert state_bytes['md'] == state_bytes['sms']
    states = list(struct.iter_unpack('<8H', state_bytes['sms']))
    active = [n for n, row in enumerate(states, 1) if any(row[i] != 0 for i in (1, 3, 5, 7))]
    start = active[0]  # independently measured from SMS decoded volume, never chosen from mismatch frames
    differences = []
    intervals = {'md': [], 'sms': []}
    equal_intervals = total_intervals = equal_packets = multi_packets = musical_writes = 0
    examples = []
    for frame, (md, sms) in enumerate(zip(rows['md'], rows['sms']), 1):
        same_bytes = [v for _, v in md] == [v for _, v in sms]
        if not same_bytes:
            differences.append(dict(frame=frame, md=md, sms=sms))
        if frame < start:
            continue
        assert same_bytes, (region, frame)
        musical_writes += len(sms)
        md_gaps = [b[0] - a[0] for a, b in zip(md, md[1:])]
        sms_gaps = [b[0] - a[0] for a, b in zip(sms, sms[1:])]
        assert all(v >= 0 for v in md_gaps + sms_gaps)
        intervals['md'].extend(md_gaps)
        intervals['sms'].extend(sms_gaps)
        total_intervals += len(sms_gaps)
        equal_intervals += sum(m == s for m, s in zip(md_gaps, sms_gaps))
        if sms_gaps:
            multi_packets += 1
            equal_packets += md_gaps == sms_gaps
            if len(examples) < 6 and md_gaps != sms_gaps:
                examples.append(dict(frame=frame, bytes=[v for _, v in sms], md_gaps=md_gaps, sms_gaps=sms_gaps))
    assert len(differences) == 4 and all(d['frame'] < start for d in differences)
    def summary(values):
        return dict(count=len(values), minimum=min(values), maximum=max(values),
                    median=statistics.median(values), most_common=collections.Counter(values).most_common(12))
    cases.append(dict(region=region, frames=14000, exact_exposed_state_frames=14000,
        exposed_state_sha256=sha(state_bytes['sms']), unique_states=len(set(states)),
        non_fully_muted_state_frames=len(active), first_nonmuted_source_frame=start,
        exposed_volume_values=sorted({row[i] for row in states for i in (1, 3, 5, 7)}),
        startup_byte_order_differences=differences,
        startup_additional_md_writes=sum(len(x['md']) - len(x['sms']) for x in differences),
        bytes_and_order_exact_from_first_nonmuted_source_frame=True, equal_musical_writes_per_system=musical_writes,
        within_frame_multiwrite_packets=multi_packets, equal_spacing_packets=equal_packets,
        consecutive_write_intervals=total_intervals, exact_intervals=equal_intervals,
        spacing_master_clock_ticks={tag: summary(values) for tag, values in intervals.items()},
        spacing_difference_examples=examples))
result = dict(audit_passed=True, audio_timing_equivalence_passed=False, version=319,
    rom_sha256=trace['rom_sha256'], source_sha256=trace['source_sha256'], observer_core_sha256=trace['core_sha256'],
    cases=cases, frames_compared=28000, ram_writes=0, sram_imports=0,
    metadata_erratum=dict(supersedes='analysis/sms_psg_v0319_report.json',
        unchanged='Exact equality of all eight exposed states at every sampled frame remains proved.',
        corrected='Odd slots are decoded volume amplitudes, not raw attenuation nibbles. Zero means mute; '
                  'the old <15 activity count and raw-register label were incorrect. Original frozen evidence retained.'),
    timing_scope='Consecutive clock differences within the same frame cancel cross-platform clock origins. '
                 'No inter-frame interval or absolute lateness claim. All startup discrepancies retained. '
                 'No PCM equality or whole-game audio certification.',
    next_action='Native streaming emits successful channel lists in bursts. Preserve per-write source timestamps '
                'and establish actual delivery deadlines before changing production audio scheduling.',
    archive_manifest='analysis/v319-psg-write-spacing/manifest.json')
report = root / 'analysis/sms_psg_writes_v0319_report.json'
assert not report.exists()
report.write_text(json.dumps(result, indent=2) + '\n')
paths = {Path(__file__).resolve(), report, root / 'validation/trace_v319_psg_writes.py',
         root / 'validation/build_v319_psg_write_observer.py'}
for folder in (work, build):
    paths.update(p for p in folder.rglob('*') if p.is_file())
freeze(root, root / 'analysis/v319-psg-write-spacing', paths, result, [work], cleanup=True)
for case in cases:
    print(case['region'], 'active', case['non_fully_muted_state_frames'], 'start', case['first_nonmuted_source_frame'],
          'musical bytes', case['equal_musical_writes_per_system'], 'equal gaps', case['exact_intervals'],
          '/', case['consecutive_write_intervals'], 'spacing', case['spacing_master_clock_ticks'])
