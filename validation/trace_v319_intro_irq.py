"""Direct original F09/B95/full-IRQ/F32 trace and native callback entries; observer parity checked."""
import argparse
import collections
import contextlib
import ctypes as c
import gzip
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
p = argparse.ArgumentParser()
p.add_argument('--full', action='store_true')
a = p.parse_args()
frames = 14000 if a.full else 1900
out = root / ('validation/v319-intro-irq-trace02' if a.full else 'validation/v319-intro-irq-trace01')
assert not out.exists()
out.mkdir()
build = root / 'validation/v319-intro-irq-observer01'
metadata = json.loads((build / 'report.json').read_bytes())
core = Path(metadata['core'])
assert metadata['passed'] and sha(core.read_bytes()) == metadata['core_sha256']
dll = c.CDLL(str(core))
dll.gaw_intro_reset.restype = None
dll.gaw_intro_size.restype = dll.gaw_intro_errors.restype = c.c_uint
dll.gaw_intro_data.restype = c.POINTER(c.c_uint)
dll.gaw_md_config.argtypes = [c.c_uint, c.POINTER(c.c_uint)]
dll.gaw_md_event_count.restype = c.c_uint
dll.gaw_md_event_data.restype = c.POINTER(c.c_uint)
def evidence(archive_name, name):
    archive = root / 'analysis' / archive_name
    m = json.loads((archive / 'manifest.json').read_bytes())
    item = m['compressed'][name]
    encoded = (archive / item['stored']).read_bytes()
    assert sha(encoded) == item['stored_sha256']
    raw = gzip.decompress(encoded)
    assert sha(raw) == item['raw_sha256']
    return raw
def symbols(raw):
    return {m[2].split('.lto_priv.')[0].split('.constprop.')[0]: int(m[1], 16)
        for line in raw.decode().splitlines() if (m := re.match(r'([0-9a-fA-F]+)\s+\w\s+(\S+)', line))}
candidates = []
for number in (range(1, 4) if a.full else [1]):
    prefix = f'validation/v319-audio-prefetch{number:02}/project/out/release/'
    candidate_rom = out / f'candidate{number:02}.bin'
    candidate_rom.write_bytes(evidence('v319-audio-prefetch', prefix + 'rom.bin'))
    candidates.append((f'prefetch{number:02}', candidate_rom,
                       symbols(evidence('v319-audio-prefetch', prefix + 'symbol.txt'))))
cases = []
for region in ('ntsc', 'pal'):
    by_tag = {}
    for tag, rom, sy in [('sms', root / 'input/original.sms', None),
            ('baseline', root / 'gaw-megadrive.bin', symbols((root / 'megadrive/out/release/symbol.txt').read_bytes())),
            *candidates]:
        events = []; psg = bytearray(); states = bytearray()
        watched = {sy[name]: name for name in ('intro_tick', 'world_vint')} if sy else {}
        pcs = (c.c_uint * len(watched))(*watched)
        dll.gaw_md_config(len(watched), pcs); dll.gaw_intro_reset()
        def ram(frame, raw):
            if sy:
                fields = ['intro_running', 'intro_logic_clock', 'intro_scene', 'intro_counter', 'intro_line', 'intro_timer']
                row = [int.from_bytes(bytes(raw[((sy[name] + i) & 65535) ^ 1] for i in range(2)), 'big') for name in fields]
            else:
                row = [raw[0x2f], raw[0x2e]]
            states.extend(struct.pack('<' + 'H' * len(row), *row))
        def observe(frame):
            if sy:
                count = dll.gaw_md_event_count(); assert count < 8192
                pointer = dll.gaw_md_event_data()
                for n in range(count):
                    pc, clock, sp = [int(pointer[n * 3 + k]) for k in range(3)]
                    events.append([frame, watched[pc], clock, sp])
                dll.gaw_md_config(len(watched), pcs)
            else:
                assert dll.gaw_intro_errors() == 0
                pointer = dll.gaw_intro_data()
                for n in range(dll.gaw_intro_size()):
                    events.append([frame] + [int(pointer[n * 6 + k]) for k in range(6)])
                dll.gaw_intro_reset()
        with contextlib.redirect_stdout(io.StringIO()):
            run(rom, frames, out / (region + '-' + tag), set(), [], skip_intro=False, core=core,
                ram_observer=ram, psg_observer=lambda frame, regs: psg.extend(struct.pack('<8H', *regs)),
                post_frame_observer=observe,
                core_options={'genesis_plus_gx_region_detect': 'pal' if region == 'pal' else 'auto'})
        if tag == 'sms':
            previous = evidence('v319-psg-write-spacing', f'validation/v319-psg-writes01/{region}-sms/exposed-psg-states.bin')
        else:
            old_tag = 'candidate' if tag.startswith('prefetch') else 'baseline'
            number = int(tag[-2:]) if tag.startswith('prefetch') else 1
            previous = evidence('v319-audio-prefetch', f'validation/v319-audio-prefetch{number:02}/audio/{region}-{old_tag}/psg-states.bin')
        assert psg == previous[:frames * 16], ('Observer changed exposed PSG', region, tag)
        if region == 'ntsc' and tag in ('sms', 'baseline', 'prefetch01'):
            old_tag = 'candidate' if tag == 'prefetch01' else tag
            previous = evidence('v319-audio-prefetch', f'validation/v319-audio-prefetch01/intro-clock/{old_tag}-clock.bin')
            assert states == previous[:frames * (12 if sy else 4)], ('Observer changed intro states', tag)
        folder = out / (region + '-' + tag)
        (folder / 'events.json').write_text(json.dumps(events, separators=(',', ':')) + '\n')
        (folder / 'intro-state.bin').write_bytes(states)
        (folder / 'psg-state.bin').write_bytes(psg)
        by_tag[tag] = events
        print(region, tag, len(events), 'read-only events; prior exposed PSG exact', flush=True)
    source = by_tag['sms']
    # F32 is the source foreground actor callback AFTER B95 returns. 01DD is
    # immediately after the full IRQ increments C02F, before request clear.
    source_callbacks = [row for row in source if row[1] == 0xf32]
    handshakes = []; pending = None
    for row in source:
        if row[1] == 0xb95:
            assert pending is None
            pending = row
        elif row[1] == 0xbb3:
            assert pending is not None
            handshakes.append(dict(request_frame=pending[0], return_frame=row[0],
                clock_before=pending[3], clock_after=row[3], clock_delta=(row[3] - pending[3]) & 255))
            pending = None
    native_counts = {tag: collections.Counter(row[0] for row in rows if row[1] == 'intro_tick')
                     for tag, rows in by_tag.items() if tag != 'sms'}
    source_counts = collections.Counter(row[0] for row in source_callbacks)
    native_differences = {}
    for tag, counter in native_counts.items():
        diffs = [dict(frame=frame, native_callbacks=counter[frame], source_callbacks=source_counts[frame])
                 for frame in range(1, frames + 1) if counter[frame] != source_counts[frame]]
        baseline_counter = native_counts['baseline']
        differential = [dict(frame=frame, callbacks=counter[frame], baseline_callbacks=baseline_counter[frame])
                       for frame in range(1, frames + 1) if counter[frame] != baseline_counter[frame]]
        cumulative = 0
        for row in differential:
            cumulative += row['callbacks'] - row['baseline_callbacks']
            row['cumulative_callback_count_delta'] = cumulative
        native_differences[tag] = dict(different_frames=len(diffs), first_differences=diffs[:16],
            transition_1750_1820=[row for row in diffs if 1750 <= row['frame'] <= 1820],
            total_native_callbacks=sum(counter.values()), versus_baseline_callback_changes=differential)
    cases.append(dict(region=region, frames=frames, source_full_irq_returns=len(handshakes),
        source_return_clock_delta_counts=dict(collections.Counter(row['clock_delta'] for row in handshakes)),
        source_callbacks=len(source_callbacks), first_source_callback_entries=source_callbacks[:12],
        source_transition_handshakes=[row for row in handshakes if 1750 <= row['request_frame'] <= 1820],
        native_callback_frame_comparisons=native_differences, observer_exposed_psg_noninterference=True,
        observer_intro_state_noninterference=(region == 'ntsc')))
result = dict(diagnostic_only=True, cases=cases, core_sha256=sha(core.read_bytes()), ram_writes=0, sram_imports=0,
    scope='Direct source request/full-IRQ-return/F32 entries, and native intro_tick entry timestamps. '
          'Clocks are supplied core frame-relative master clocks, not aligned absolute platform epochs. '
          'Callback frame comparisons describe observed publication only; bootstrap/layout work differs between systems. '
          'NTSC native/source intro-state parity to prior core independently checked; both regions PSG parity checked.')
(out / 'report.json').write_text(json.dumps(result, indent=2) + '\n')
print('Direct full-IRQ and callback trace completed; original state streams preserved.')
