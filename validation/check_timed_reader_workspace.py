"""Check caller-owned timed workspace against original-reader event/state fixtures."""
import ctypes as c
import json
import os
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'tools'))
from archive_lossless_evidence import sha
from validate_reader_timing import MODULES, Status, SINK
from validate_native_audio_prefix import Work

out = root / 'validation/v319-timed-workspace01'
assert not out.exists()
out.mkdir()
sdk = root.parents[1] / 'work/sgdk'
env = dict(os.environ)
env['PATH'] = 'C:/msys64/ucrt64/bin;' + env['PATH']
modules = MODULES + ['source_audio_fast_timed', 'source_audio_reader_master']
command = ['C:/msys64/ucrt64/bin/gcc.exe', '-O3', '-shared', '-Wall', '-Wextra', '-Werror',
           '-I', str(sdk / 'inc'), '-I', str(root / 'megadrive/src')]
command += [str(root / 'megadrive/src' / (name + '.c')) for name in modules]
command += ['-o', str(out / 'reader.dll')]
built = subprocess.run(command, env=env, capture_output=True, text=True)
(out / 'compile.log').write_text(built.stdout + built.stderr)
assert built.returncode == 0, built.stderr
dll = c.CDLL(str(out / 'reader.dll'))
class Channel(c.Structure):
    _fields_ = [('de', c.c_uint16), ('count', c.c_uint16), ('unwind', c.c_uint8), ('error', c.c_uint8),
                ('writes', c.c_uint8 * 512), ('times', c.c_uint32 * 512)]
common = [c.POINTER(c.c_uint8), c.POINTER(c.c_uint8), c.c_uint16, c.POINTER(c.c_uint8),
          c.POINTER(c.c_uint16), c.POINTER(Work), c.POINTER(Status), SINK, c.c_void_p, c.POINTER(Channel)]
functions = [dll.source_audio_reader_stream_timed_work, dll.source_audio_reader_stream_fast_timed_work]
for fn in functions:
    fn.argtypes = common
    fn.restype = c.c_uint8
paths = [root / 'validation/native-audio-reader' / name for name in ('cases.json', 'extension-cases.json')]
suites = [suite for path in paths for suite in json.loads(path.read_bytes())]
events_path = root / 'validation/reader-timing/events.json'
events = json.loads(events_path.read_bytes())
assert len(suites) == len(events)
image = (root / 'input/original.sms').read_bytes()
bank = (c.c_uint8 * 16384).from_buffer_copy(image[0x18000:0x1c000])
cases = writes = 0
for suite, observed in zip(suites, events):
    fixture = (root / suite['fixture']).read_bytes()
    assert sha(fixture) == suite['fixture_sha256']
    low = (c.c_uint8 * 32768).from_buffer_copy(fixture[:32768])
    assert suite['kind'] == observed['kind'] and len(suite['cases']) == len(observed['events'])
    for row, expected in zip(suite['cases'], observed['events']):
        for fn in functions:
            state = (c.c_uint8 * 400).from_buffer_copy(bytes(row['before']))
            de = c.c_uint16(row['de_in']); work = Work(); status = Status(); channel = Channel()
            emitted = []; times = []
            @SINK
            def sink(context, data, dates, count):
                emitted.extend(data[i] for i in range(count))
                times.extend(dates[i] for i in range(count))
            ok = fn(state, low, 32768, bank, c.byref(de), c.byref(work), c.byref(status), sink, None, c.byref(channel))
            assert ok and not status.error
            assert bytes(state) == bytes(row['after']) and de.value == row['de']
            assert (work.tstates, work.fetches) == (row['tstates'], row['fetches'])
            assert emitted == expected['writes'] and times == expected['times']
            assert status.count == len(emitted) and status.track == expected['track']
        cases += 1
        writes += len(expected['writes'])
    print(suite['kind'], len(suite['cases']), 'source fixtures passed for both workspace APIs', flush=True)
result = dict(passed=True, source_cases=cases, implementations=2, source_writes_per_implementation=writes,
    exact_fields=['400-byte state', 'DE', 'T/M1 work', 'track', 'all PSG bytes in order', 'all source OUT dates'],
    fixture_inputs={str(path.relative_to(root)): sha(path.read_bytes()) for path in paths + [events_path]},
    sources={name: sha((root / 'megadrive/src' / (name + '.c')).read_bytes()) for name in modules},
    diagnostic_only=True, physical_timing_validated=False)
(out / 'report.json').write_text(json.dumps(result, indent=2) + '\n')
print(cases, 'source cases passed twice;', writes, 'source-dated writes per implementation.')
