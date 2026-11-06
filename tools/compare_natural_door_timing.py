"""Measure a recorded natural doorway on the original and native ROMs."""

import argparse
import ctypes as c
import json
from pathlib import Path

from archive_lossless_evidence import sha
from run_core import ROOT, run
from validate_playable_sprite_limit import symbols


SOURCE_PHASES = {0x0B12: 'fade_out', 0x0B24: 'load', 0x0ACE: 'fade_in',
                 0x1FB6: 'contours', 0x2002: 'end'}
NATIVE_PHASES = ('end', 'fade_out', 'load', 'fade_in', 'contours')


def measure(trace, rom, output, *, core=None, native_symbols=None):
    capture = json.loads((trace / 'capture.json').read_bytes())
    route = json.loads((trace / 'route_report.json').read_bytes())
    assert capture['rom_sha256'] == route['rom_sha256'] == sha(rom.read_bytes())
    assert capture['sram_input'] is None and not capture['test_ram_writes']
    assert route['directional_probe_succeeded'] and not route['failure']
    end = capture['frames']
    first, ready = route['first_published_target_room_frame'], route['first_controllable_frame']
    controls = json.loads((trace / 'controls.json').read_bytes())
    presses = list(map(tuple, capture['presses']))
    for i, row in enumerate(controls):
        stop = min(end, controls[i + 1]['frame'] - 1) if i + 1 < len(controls) else end
        presses.extend((row['frame'], stop, button) for button in row['buttons'] if row['frame'] <= end)

    phases = {}
    black_spans = []
    observed = set()
    previous = 0
    if core is not None:
        dll = c.CDLL(str(core))
        dll.gaw_timing_count.restype = c.c_uint
        dll.gaw_timing_events.restype = c.POINTER(c.c_uint64)

    def observe_ram(frame, ram):
        nonlocal previous
        if frame < first - 12 or frame > ready:
            return
        if core is not None:
            if frame == first - 12:
                dll.gaw_timing_reset()
                return
            count, events = dll.gaw_timing_count(), dll.gaw_timing_events()
            for i in range(previous, count):
                pc = events[i * 8]
                if pc in SOURCE_PHASES:
                    name = SOURCE_PHASES[pc]
                    assert name not in phases
                    phases[name] = frame
            previous = count
        else:
            address = native_symbols['resume_phase']
            phase = int.from_bytes(ram[address:address + 2], 'little')
            if phase or phases:
                phases.setdefault(NATIVE_PHASES[phase], frame)

    def observe_video(frame, raw, width, height, pitch, mode):
        if not first - 10 <= frame <= ready + 8:
            return
        assert raw and width == 256 and mode == 2 and height in (192, 224)
        assert frame not in observed
        observed.add(frame)
        top = (height - 192) // 2
        if any(raw[y * pitch:y * pitch + 512].strip(b'\0') for y in range(top, top + 160)):
            return
        if black_spans and frame == black_spans[-1][1] + 1:
            black_spans[-1][1] = frame
        else:
            black_spans.append([frame, frame])

    run(rom, end, output, {end}, presses, skip_intro=False, core=core,
        ram_observer=observe_ram, video_observer=observe_video, core_options=capture['core_options'])
    filename = f'frame_{end:05d}.png'
    assert (output / filename).read_bytes() == (trace / filename).read_bytes()
    assert list(phases) == list(SOURCE_PHASES.values())
    assert observed == set(range(first - 10, ready + 9))
    assert black_spans
    return dict(rom_sha256=capture['rom_sha256'], fps=capture['fps'], phases=phases,
                first_published_room=first, first_controllable=ready,
                hidden_load_frames=phases['fade_in'] - phases['load'],
                black_playfield_spans=black_spans,
                black_playfield_frames=sum(b - a + 1 for a, b in black_spans),
                endpoint_png_sha256=sha((output / filename).read_bytes()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sms-trace', type=Path, required=True)
    parser.add_argument('--md-trace', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    assert out.is_relative_to(ROOT / 'validation') and not out.exists()
    traces = (args.sms_trace.resolve(), args.md_trace.resolve())
    assert all(trace.is_relative_to(ROOT / 'validation') for trace in traces)
    regions = {json.loads((trace / 'route_report.json').read_bytes())['region'] for trace in traces}
    assert len(regions) == 1
    source_core = ROOT.parents[1] / 'work/genesis-plus-gx/genesis_plus_gx_hero_libretro.dll'
    source = measure(traces[0], ROOT / 'input/original.sms', out / 'sms', core=source_core)
    native = measure(traces[1], ROOT / 'gaw-megadrive.bin', out / 'md',
                     native_symbols=symbols(ROOT / 'megadrive/out/release/symbol.txt'))
    report = dict(region=regions.pop(), sms=source, md=native, driver_sha256=sha(Path(__file__).read_bytes()))
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
