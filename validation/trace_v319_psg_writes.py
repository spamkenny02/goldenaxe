"""Compare original port bytes/order and supplied PSG timestamps, with observer noninterference checks."""
import contextlib
import ctypes as c
import gzip
import io
import json
import statistics
import struct
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'tools'))
from run_core import run
from archive_lossless_evidence import sha

build = root / 'validation/v319-psg-write-observer01'
br = json.loads((build / 'build-report.json').read_bytes())
assert br['passed'] and br['original_source_restored']
core = Path(br['diagnostic_core'])
assert sha(core.read_bytes()) == br['core_sha256']
dll = c.CDLL(str(core))
dll.gaw_psg_writes_reset.restype = None
dll.gaw_psg_writes_size.restype = dll.gaw_psg_writes_errors.restype = c.c_uint
dll.gaw_psg_writes_data.restype = c.POINTER(c.c_uint)
out = root / 'validation/v319-psg-writes01'
assert not out.exists(), out
out.mkdir()
archive = root / 'analysis/v319-sms-psg'
manifest = json.loads((archive / 'manifest.json').read_bytes())
def old_states(region, tag):
    name = f'validation/v319-sms-psg02/{region}-{tag}/psg-registers.bin'
    item = manifest['compressed'][name]
    encoded = (archive / item['stored']).read_bytes()
    assert sha(encoded) == item['stored_sha256']
    raw = gzip.decompress(encoded)
    assert sha(raw) == item['raw_sha256'] and len(raw) == 14000 * 16
    return raw

rom = root / 'versions/v0319-d3ea2a83/gaw-megadrive-v0319.bin'
original = root / 'input/original.sms'
cases = []
for region in ('ntsc', 'pal'):
    records = {}
    for tag, cartridge in [('md', rom), ('sms', original)]:
        folder = out / (region + '-' + tag)
        events = []
        encoded = bytearray()
        states = bytearray()
        dll.gaw_psg_writes_reset()
        def observe_psg(frame, values):
            states.extend(struct.pack('<8H', *values))
        def observe_writes(frame):
            assert frame == len(events) + 1 and dll.gaw_psg_writes_errors() == 0
            count = dll.gaw_psg_writes_size()
            pointer = dll.gaw_psg_writes_data()
            row = tuple((int(pointer[n * 2]), int(pointer[n * 2 + 1])) for n in range(count))
            assert all(0 <= value <= 255 for _, value in row)
            assert all(a[0] <= b[0] for a, b in zip(row, row[1:])), ('Nonmonotonic supplied clocks', frame)
            for clocks, value in row:
                encoded.extend(struct.pack('<IIB', frame, clocks, value))
            events.append(row)
            dll.gaw_psg_writes_reset()
        with contextlib.redirect_stdout(io.StringIO()):
            run(cartridge, 14000, folder, set(), [], skip_intro=False, core=core,
                psg_observer=observe_psg, post_frame_observer=observe_writes,
                core_options={'genesis_plus_gx_region_detect': 'pal' if region == 'pal' else 'auto'})
        assert len(events) == 14000 and bytes(states) == old_states(region, tag)
        (folder / 'psg-port-writes.bin').write_bytes(encoded)
        (folder / 'exposed-psg-states.bin').write_bytes(states)
        records[tag] = events
        print(region, tag, 'writes:', sum(map(len, events)), '; original exposed states preserved', flush=True)
    byte_diff = []
    time_diff = []
    deltas = []
    examples = []
    nonempty = 0
    for frame, (m, s) in enumerate(zip(records['md'], records['sms']), 1):
        if m or s:
            nonempty += 1
        mv = tuple(v for _, v in m)
        sv = tuple(v for _, v in s)
        if mv != sv:
            byte_diff.append(frame)
            if len(examples) < 10:
                examples.append(dict(frame=frame, md=list(m), sms=list(s)))
        elif m:
            deltas.extend(a[0] - b[0] for a, b in zip(m, s))
        if m != s:
            time_diff.append(frame)
    case = dict(region=region, frames=14000, observer_exposed_states_exact_to_previous_core=True,
                frames_with_writes=nonempty, byte_order_difference_frames=len(byte_diff),
                timestamped_event_difference_frames=len(time_diff), first_byte_order_difference_frames=byte_diff[:20],
                first_byte_order_examples=examples,
                write_count={tag: sum(map(len, rows)) for tag, rows in records.items()},
                raw_supplied_clock_deltas_for_equal_byte_frames=dict(count=len(deltas), minimum=min(deltas),
                    maximum=max(deltas), median=statistics.median(deltas)) if deltas else None)
    cases.append(case)
    print(region, 'raw-byte/order difference frames:', len(byte_diff),
          '; timestamped differences:', len(time_diff), flush=True)
result = dict(passed=all(c['timestamped_event_difference_frames'] == 0 for c in cases),
              diagnostic_only=True, observer_noninterference_validated=True, cases=cases,
              rom_sha256=sha(rom.read_bytes()), source_sha256=sha(original.read_bytes()), core_sha256=sha(core.read_bytes()),
              driver_sha256=sha(Path(__file__).read_bytes()), ram_writes=0, sram_imports=0,
              cross_platform_clock_origin_alignment_applied=False, pcm_equivalence_validated=False,
              scope='Every PSG write logged before decoding, preserving original data byte/order and supplied '
                    'core clock. Observer reproduces the previous every-frame exposed states exactly. '
                    'Clock origins are not aligned across the two systems; timestamp differences alone '
                    'are not a certified physical lateness measurement. Includes platform startup writes.')
(out / 'report.json').write_text(json.dumps(result, indent=2) + '\n')
print('Raw PSG write comparison completed; ROM unchanged.', flush=True)
