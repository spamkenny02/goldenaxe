"""Observe native intro callback clock versus source C02F; no test state writes."""
import contextlib
import io
import json
import re
import struct
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'tools'))
from run_core import run
from archive_lossless_evidence import sha

work = root / 'validation/v319-audio-prefetch01/intro-clock'
assert not work.exists()
work.mkdir()
fields = ['intro_running', 'intro_logic_clock', 'intro_scene', 'intro_counter', 'intro_line', 'intro_timer']
records = {}
for tag, rom, sy_path in [('baseline', root / 'gaw-megadrive.bin', root / 'megadrive/out/release/symbol.txt'),
                         ('candidate', root / 'validation/v319-audio-prefetch01/project/out/release/rom.bin', root / 'validation/v319-audio-prefetch01/project/out/release/symbol.txt'),
                         ('sms', root / 'input/original.sms', None)]:
    sy = {m[2].split('.lto_priv.')[0]: int(m[1], 16) & 65535
          for line in sy_path.read_text().splitlines() if (m := re.match(r'([0-9a-fA-F]+)\s+\w\s+(\S+)', line))} if sy_path else None
    rows = []
    def observe(frame, raw):
        if tag == 'sms': rows.append([raw[0x2f], raw[0x2e]])
        else:
            rows.append([int.from_bytes(bytes(raw[(sy[name] + i) ^ 1] for i in range(2)), 'big') for name in fields])
    with contextlib.redirect_stdout(io.StringIO()):
        run(rom, 14000, work / tag, set(), [], skip_intro=False, ram_observer=observe)
    (work / (tag + '-clock.bin')).write_bytes(b''.join(struct.pack('<' + 'H' * len(row), *row) for row in rows))
    records[tag] = rows
first = {}; counts = {}
for column, name in enumerate(fields):
    diffs = [n + 1 for n, (a, b) in enumerate(zip(records['baseline'], records['candidate'])) if a[column] != b[column]]
    first[name] = diffs[:12]; counts[name] = len(diffs)
for tag in ('baseline', 'candidate'):
    unequal = [n + 1 for n, (md, sms) in enumerate(zip(records[tag], records['sms'])) if md[0] and md[1] != sms[0]]
    increments = [(n + 1, (b[1] - a[1]) & 255) for n, (a, b) in enumerate(zip(records[tag], records[tag][1:]), 1)
                  if a[0] and b[0] and ((b[1] - a[1]) & 255) > 1]
    print(tag, 'clock/source mismatch', len(unequal), unequal[:12], 'multiple callback increments', increments[:12])
result = dict(fields=fields, different_frame_counts=counts, first_difference_frames=first,
    first_rows=[dict(frame=n + 1, baseline=a, candidate=b, sms=records['sms'][n])
                for n, (a, b) in enumerate(zip(records['baseline'], records['candidate']))
                if a != b][:20], diagnostic_only=True, ram_writes=0, sram_imports=0)
(work / 'report.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
