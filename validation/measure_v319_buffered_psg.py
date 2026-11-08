"""Direct emitted spacing probe for the buffered native prototype; no phase equivalence claim."""
import argparse
import collections
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
p.add_argument('--work', default='v319-buffered-psg01')
p.add_argument('--trace-name', default='trace')
a = p.parse_args()
work = root / 'validation' / a.work
assert work.resolve().is_relative_to(root / 'validation')
project = work / 'project'
out = work / a.trace_name
assert not out.exists()
out.mkdir()
core = root.parents[1] / 'work/genesis-plus-gx/genesis_plus_gx_v319_psg_writes_libretro.dll'
dll = c.CDLL(str(core))
dll.gaw_psg_writes_reset.restype = None
dll.gaw_psg_writes_size.restype = dll.gaw_psg_writes_errors.restype = c.c_uint
dll.gaw_psg_writes_data.restype = c.POINTER(c.c_uint)
sy = {m[2].split('.lto_priv.')[0]: int(m[1], 16) & 65535
      for line in (project / 'out/release/symbol.txt').read_text().splitlines()
      if (m := re.match(r'([0-9a-fA-F]+)\s+\w\s+(\S+)', line))}
archive = root / 'analysis/v319-psg-write-spacing'
manifest = json.loads((archive / 'manifest.json').read_bytes())
baseline = json.loads((root / 'analysis/sms_psg_writes_v0319_report.json').read_bytes())
def evidence(name):
    item = manifest['compressed'][name]
    encoded = (archive / item['stored']).read_bytes()
    assert sha(encoded) == item['stored_sha256']
    raw = gzip.decompress(encoded)
    assert sha(raw) == item['raw_sha256']
    return raw

cases = []
for region in ('ntsc', 'pal'):
    ref = next(item for item in baseline['cases'] if item['region'] == region)
    source = [[] for _ in range(14000)]
    for frame, clock, value in struct.iter_unpack('<IIB', evidence(f'validation/v319-psg-writes01/{region}-sms/psg-port-writes.bin')):
        source[frame - 1].append((clock, value))
    states = evidence(f'validation/v319-psg-writes01/{region}-sms/exposed-psg-states.bin')
    rows = []; psg = bytearray(); encoded = bytearray(); runtime_errors = []; max_count = 0
    staged = []; dated = bytearray()
    dll.gaw_psg_writes_reset()
    def observe_ram(frame, raw):
        global max_count
        def word(name):
            address = sy[name]
            return int.from_bytes(bytes(raw[(address + i) ^ 1] for i in range(2)), 'big')
        for name in ('sound_unhandled_command', 'sound_timed_error'):
            value = word(name)
            if value:
                runtime_errors.append(dict(frame=frame, name=name, value=value))
        max_count = max(max_count, word('sound_timed_max_count'))
        count = word('sound_timed_count')
        assert count <= 64
        address = sy['sound_timed_events']
        data = bytes(raw[(address + i) ^ 1] for i in range(count * 6))
        packet = [(int.from_bytes(data[i:i+4], 'big'), data[i+4]) for i in range(0, len(data), 6)]
        staged.append(packet)
        for due, value in packet:
            dated.extend(struct.pack('<IIB', frame, due, value))
    def observe_writes(frame):
        assert dll.gaw_psg_writes_errors() == 0
        pointer = dll.gaw_psg_writes_data()
        row = [(int(pointer[i * 2]), int(pointer[i * 2 + 1])) for i in range(dll.gaw_psg_writes_size())]
        assert all(0 <= value <= 255 for _, value in row)
        rows.append(row)
        for clock, value in row:
            encoded.extend(struct.pack('<IIB', frame, clock, value))
        dll.gaw_psg_writes_reset()
    with contextlib.redirect_stdout(io.StringIO()):
        run(project / 'out/release/rom.bin', 14000, out / region, set(), [], skip_intro=False, core=core,
            ram_observer=observe_ram, psg_observer=lambda frame, values: psg.extend(struct.pack('<8H', *values)),
            post_frame_observer=observe_writes,
            core_options={'genesis_plus_gx_region_detect': 'pal' if region == 'pal' else 'auto'})
    (out / region / 'psg-port-writes.bin').write_bytes(encoded)
    (out / region / 'exposed-psg-states.bin').write_bytes(psg)
    (out / region / 'prepared-source-dates.bin').write_bytes(dated)
    different_states = [n + 1 for n in range(14000) if psg[n * 16:(n + 1) * 16] != states[n * 16:(n + 1) * 16]]
    different_bytes = []; error_ticks = []; exact = 0; examples = []
    model_errors = []; model_byte_differences = []
    for frame, (md, sms) in enumerate(zip(rows, source), 1):
        if frame < ref['first_nonmuted_source_frame']:
            continue
        model = staged[frame - 1]
        if [v for _, v in model] != [v for _, v in sms]:
            model_byte_differences.append(frame)
        else:
            gaps = [b[0] - a[0] for a, b in zip(model, model[1:])]
            source_gaps = [b[0] - a[0] for a, b in zip(sms, sms[1:])]
            model_errors.extend(abs(a - b) for a, b in zip(gaps, source_gaps))
        if [v for _, v in md] != [v for _, v in sms]:
            different_bytes.append(frame)
            continue
        mg = [b[0] - a[0] for a, b in zip(md, md[1:])]
        sg = [b[0] - a[0] for a, b in zip(sms, sms[1:])]
        error_ticks.extend(abs(a - b) for a, b in zip(mg, sg))
        exact += sum(a == b for a, b in zip(mg, sg))
        if len(examples) < 5 and mg != sg:
            examples.append(dict(frame=frame, md_gaps=mg, sms_gaps=sg))
    case = dict(region=region, frames=14000, runtime_error_count=len(runtime_errors),
        first_runtime_errors=runtime_errors[:8], max_staged_events=max_count,
        different_exposed_state_frames=len(different_states), first_state_differences=different_states[:12],
        musical_byte_order_difference_frames=len(different_bytes), first_byte_differences=different_bytes[:12],
        compared_intervals=len(error_ticks), exact_intervals=exact,
        absolute_spacing_error_ticks=dict(median=statistics.median(error_ticks), maximum=max(error_ticks),
            mean=statistics.mean(error_ticks), most_common=collections.Counter(error_ticks).most_common(8)),
        spacing_examples=examples) if error_ticks else dict(region=region, frames=14000,
            runtime_error_count=len(runtime_errors), first_runtime_errors=runtime_errors[:8], max_staged_events=max_count,
            different_exposed_state_frames=len(different_states), first_state_differences=different_states[:12],
            musical_byte_order_difference_frames=len(different_bytes), first_byte_differences=different_bytes[:12],
            compared_intervals=0, no_comparable_musical_packets=True)
    case['prepared_source_byte_difference_frames'] = len(model_byte_differences)
    case['prepared_source_interval_difference_count'] = sum(v != 0 for v in model_errors)
    case['prepared_source_max_interval_error_ticks'] = max(model_errors, default=None)
    cases.append(case)
    print(region, json.dumps(case), flush=True)
result = dict(diagnostic_only=True, promoted=False, cases=cases,
    md_sha256=sha((project / 'out/release/rom.bin').read_bytes()), core_sha256=sha(core.read_bytes()),
    ram_writes=0, sram_imports=0, absolute_source_phase_validated=False,
    scope='Native whole-reader preparation and relative dated replay. No certification of first-write '
          'phase, full-frame video, interactive audio, SRAM, PCM or console hardware.')
(out / 'report.json').write_text(json.dumps(result, indent=2) + '\n')
