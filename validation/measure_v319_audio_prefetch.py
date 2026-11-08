"""Audit speculative preparation against live production state and original SMS PSG writes."""
import argparse
import contextlib
import ctypes as c
import gzip
import io
import json
import re
import statistics
import struct
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'tools'))
from run_core import run
from archive_lossless_evidence import sha

p = argparse.ArgumentParser()
p.add_argument('--work', default='v319-audio-prefetch01')
a = p.parse_args()
work = root / 'validation' / a.work
assert work.resolve().is_relative_to(root / 'validation')
project = work / 'project'
out = work / 'audio'
assert not out.exists()
out.mkdir()
core = root.parents[1] / 'work/genesis-plus-gx/genesis_plus_gx_v319_psg_writes_libretro.dll'
dll = c.CDLL(str(core))
dll.gaw_psg_writes_reset.restype = None
dll.gaw_psg_writes_size.restype = dll.gaw_psg_writes_errors.restype = c.c_uint
dll.gaw_psg_writes_data.restype = c.POINTER(c.c_uint)
archive = root / 'analysis/v319-psg-write-spacing'
manifest = json.loads((archive / 'manifest.json').read_bytes())
ref_report = json.loads((root / 'analysis/sms_psg_writes_v0319_report.json').read_bytes())
def evidence(name):
    item = manifest['compressed'][name]
    encoded = (archive / item['stored']).read_bytes()
    assert sha(encoded) == item['stored_sha256']
    raw = gzip.decompress(encoded)
    assert sha(raw) == item['raw_sha256']
    return raw
def symbols(path):
    return {m[2].split('.lto_priv.')[0]: int(m[1], 16) & 65535
            for line in path.read_text().splitlines() if (m := re.match(r'([0-9a-fA-F]+)\s+\w\s+(\S+)', line))}
cases = []
for region in ('ntsc', 'pal'):
    record = {}
    stats = {}; errors = []
    for tag, rom, sy_path in [('baseline', root / 'gaw-megadrive.bin', root / 'megadrive/out/release/symbol.txt'),
                             ('candidate', project / 'out/release/rom.bin', project / 'out/release/symbol.txt')]:
        sy = symbols(sy_path)
        audio_state = bytearray(); psg = bytearray(); ports = bytearray(); packets = []
        dll.gaw_psg_writes_reset()
        def ram(frame, raw):
            def data(name, size):
                return bytes(raw[(sy[name] + i) ^ 1] for i in range(size))
            audio_state.extend(data('sound_ram', 400) + data('sound_effect_request', 2))
            if int.from_bytes(data('sound_unhandled_command', 2), 'big'):
                errors.append(dict(frame=frame, tag=tag, error='reader'))
            if tag == 'candidate':
                if 'sound_prepared_clock_error' in sy and int.from_bytes(data('sound_prepared_clock_error', 2), 'big'):
                    errors.append(dict(frame=frame, tag=tag, error='clock'))
                for name in ('attempts', 'hits', 'misses', 'races'):
                    stats[name] = int.from_bytes(data('sound_prepared_' + name, 4), 'big')
        def port(frame):
            assert dll.gaw_psg_writes_errors() == 0
            pointer = dll.gaw_psg_writes_data()
            row = [(int(pointer[i * 2]), int(pointer[i * 2 + 1])) for i in range(dll.gaw_psg_writes_size())]
            packets.append(row)
            for clock, value in row:
                ports.extend(struct.pack('<IIB', frame, clock, value))
            dll.gaw_psg_writes_reset()
        with contextlib.redirect_stdout(io.StringIO()):
            run(rom, 14000, out / (region + '-' + tag), set(), [], skip_intro=False, core=core,
                ram_observer=ram, psg_observer=lambda frame, values: psg.extend(struct.pack('<8H', *values)),
                post_frame_observer=port,
                core_options={'genesis_plus_gx_region_detect': 'pal' if region == 'pal' else 'auto'})
        folder = out / (region + '-' + tag)
        (folder / 'reader-state.bin').write_bytes(audio_state)
        (folder / 'psg-states.bin').write_bytes(psg)
        (folder / 'port-writes.bin').write_bytes(ports)
        record[tag] = (audio_state, psg, packets)
        print(region, tag, 'captured', flush=True)
    assert len(record['baseline'][0]) == len(record['candidate'][0]) == 14000 * 402
    original = [[] for _ in range(14000)]
    for frame, clock, value in struct.iter_unpack('<IIB', evidence(f'validation/v319-psg-writes01/{region}-sms/psg-port-writes.bin')):
        original[frame - 1].append((clock, value))
    source_states = evidence(f'validation/v319-psg-writes01/{region}-sms/exposed-psg-states.bin')
    assert record['baseline'][1] == source_states
    start = next(case['first_nonmuted_source_frame'] for case in ref_report['cases'] if case['region'] == region)
    byte_diffs = []; intervals = []; state_diffs = []; reader_diffs = []
    for frame in range(1, 14001):
        a = (frame - 1) * 402; b = (frame - 1) * 16
        if record['baseline'][0][a:a+402] != record['candidate'][0][a:a+402]: reader_diffs.append(frame)
        if record['candidate'][1][b:b+16] != source_states[b:b+16]: state_diffs.append(frame)
        if frame < start: continue
        m = record['candidate'][2][frame - 1]; s = original[frame - 1]
        if [v for _, v in m] != [v for _, v in s]:
            byte_diffs.append(frame); continue
        mg = [b[0] - a[0] for a, b in zip(m, m[1:])]
        sg = [b[0] - a[0] for a, b in zip(s, s[1:])]
        intervals.extend(abs(a - b) for a, b in zip(mg, sg))
    case = dict(region=region, frames=14000, counters=stats,
        runtime_error_count=len(errors), first_runtime_errors=errors[:8],
        reader_state_difference_frames=len(reader_diffs), first_reader_differences=reader_diffs[:12],
        source_psg_state_difference_frames=len(state_diffs), first_psg_differences=state_diffs[:12],
        musical_byte_order_difference_frames=len(byte_diffs), first_byte_differences=byte_diffs[:12],
        compared_intervals=len(intervals), exact_intervals=sum(v == 0 for v in intervals),
        spacing_error_ticks=dict(median=statistics.median(intervals), mean=statistics.mean(intervals), maximum=max(intervals)) if intervals else None,
        reader_sha256={tag: sha(row[0]) for tag, row in record.items()})
    cases.append(case)
    print(json.dumps(case), flush=True)
result = dict(diagnostic_only=True, promoted=False, cases=cases, core_sha256=sha(core.read_bytes()),
    md_sha256=sha((project / 'out/release/rom.bin').read_bytes()), production_sha256=sha((root / 'gaw-megadrive.bin').read_bytes()),
    ram_writes=0, sram_imports=0, absolute_source_phase_validated=False,
    scope='Cold no-input opening only. Native speculative reader preparation plus native IRQ replay/fallback. '
          'No video, interactive, SRAM, PCM or hardware certification.')
(out / 'report.json').write_text(json.dumps(result, indent=2) + '\n')
