"""Compare live SMS and native audio after a natural doorway music request."""

import argparse
from collections import Counter
import json
from pathlib import Path

from archive_lossless_evidence import sha
from run_core import ROOT, run
from validate_playable_sprite_limit import symbols


def audible_registers(registers):
    # The diagnostic core stores volume amplitudes. Zero means muted.
    result = list(registers)
    tone_two_clocks_noise = registers[6] & 3 == 3 and registers[7] != 0
    for channel in range(4):
        control = channel * 2
        if registers[control + 1] == 0 and not (channel == 2 and tone_two_clocks_noise):
            result[control] = None
    return result


def capture_audio(trace, rom, out, first_offset, last_offset, *, core, sy=None, wait=None):
    capture = json.loads((trace / 'capture.json').read_bytes())
    route = json.loads((trace / 'route_report.json').read_bytes())
    assert capture['rom_sha256'] == route['rom_sha256'] == sha(rom.read_bytes())
    assert capture['sram_input'] is None and not capture['test_ram_writes']
    assert route['reached_entrance'] and route['directional_probe_succeeded'] and not route['failure']
    end = capture['frames']
    controls = json.loads((trace / 'controls.json').read_bytes())
    presses = list(map(tuple, capture['presses']))
    for i, row in enumerate(controls):
        stop = min(end, controls[i + 1]['frame'] - 1) if i + 1 < len(controls) else end
        presses.extend((row['frame'], stop, b) for b in row['buttons'] if row['frame'] <= end)
    delay = 0
    if wait is not None:
        gate, delay = wait
        assert 0 < gate <= route['first_published_target_room_frame'] and delay > 0
        shifted = []
        for begin, stop, button in presses:
            if begin < gate:
                shifted.append((begin, min(stop, gate - 1), button))
            if stop >= gate:
                shifted.append((max(begin, gate) + delay, stop + delay, button))
        presses = shifted

    entry = route['first_published_target_room_frame'] + delay
    target = route['last_state']['room']
    observed_entry = None
    states, psg = {}, {}

    def observe(frame, ram):
        nonlocal observed_entry
        if not entry - 1 <= frame <= entry + last_offset:
            return
        if sy is None:
            room = int.from_bytes(ram[0xB9:0xBB], 'little')
            logical = ram[0x1E00:0x1F90]
        else:
            def data(name, size):
                return bytes(ram[(sy[name] + i) ^ 1] for i in range(size))

            def word(name):
                return int.from_bytes(data(name, 2), 'big')

            room = word('room_id')
            logical = bytearray(data('sound_ram', 400))
            track = word('sound_request')
            effect = word('sound_effect_request')
            assert word('sound_unhandled_command') == 0
            if track and not word('sound_request_delay'):
                logical[6] = track
            if effect:
                logical[8] = effect
        if room == target and observed_entry is None:
            observed_entry = frame
        if frame >= entry + first_offset:
            states[frame - entry] = bytes(logical)

    def observe_psg(frame, regs):
        if entry + first_offset <= frame <= entry + last_offset:
            psg[frame - entry] = regs

    run(rom, end + delay, out, {end + delay}, presses, skip_intro=False, core=core,
        ram_observer=observe, psg_observer=observe_psg, core_options=capture['core_options'])
    assert observed_entry == entry
    assert states.keys() == psg.keys() == set(range(first_offset, last_offset + 1))
    if not delay:
        name = f'frame_{end:05d}.png'
        assert (out / name).read_bytes() == (trace / name).read_bytes()
    return dict(sha256=capture['rom_sha256'], room=target, entry_frame=entry,
                options=capture['core_options'], states=states, psg=psg)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sms-trace', type=Path, required=True)
    parser.add_argument('--md-trace', type=Path, required=True)
    parser.add_argument('--md-rom', type=Path, required=True)
    parser.add_argument('--md-symbols', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--first-offset', type=int, required=True)
    parser.add_argument('--last-offset', type=int, required=True)
    parser.add_argument('--sms-wait', type=int, nargs=2, metavar=('FRAME', 'COUNT'))
    args = parser.parse_args()
    out = args.out.resolve()
    assert out.is_relative_to(ROOT / 'validation') and not out.exists()
    assert 0 <= args.first_offset <= args.last_offset
    core = ROOT.parents[1] / 'work/genesis-plus-gx/genesis_plus_gx_libretro.dll'
    sm = capture_audio(args.sms_trace, ROOT / 'input/original.sms', out / 'sms',
                       args.first_offset, args.last_offset, core=core, wait=args.sms_wait)
    md = capture_audio(args.md_trace, args.md_rom, out / 'md', args.first_offset,
                       args.last_offset, core=core, sy=symbols(args.md_symbols))
    assert sm['options'] == md['options'] and sm['room'] == md['room']
    audio_differences, psg_differences, audible_differences, tempo_differences = [], [], [], []
    register_differences = Counter()
    for offset in sm['states']:
        a, b = sm['states'][offset], md['states'][offset]
        if a != b:
            audio_differences.append(offset)
        if a[4] != b[4]:
            tempo_differences.append(offset)
        x, y = sm['psg'][offset], md['psg'][offset]
        if x != y:
            psg_differences.append(offset)
        x, y = audible_registers(x), audible_registers(y)
        if x != y:
            audible_differences.append(offset)
            register_differences.update(i for i, (a, b) in enumerate(zip(x, y)) if a != b)
    report = dict(source_sha256=sm['sha256'], md_sha256=md['sha256'], core_sha256=sha(core.read_bytes()),
                  core_options=sm['options'], room=sm['room'], source_entry_frame=sm['entry_frame'], md_entry_frame=md['entry_frame'],
                  sms_input_wait=args.sms_wait, offsets=[args.first_offset, args.last_offset],
                  compared_frames=len(sm['states']), logical_audio_difference_frames=audio_differences,
                  raw_psg_difference_frames=psg_differences, audible_psg_difference_frames=audible_differences,
                  audible_psg_difference_counts=register_differences, tempo_difference_frames=tempo_differences,
                  driver_sha256=sha(Path(__file__).read_bytes()), ram_writes=0, sram_imports=0)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('Doorway audio', len(sm['states']), 'frames,', len(audio_differences),
          'reader differences,', len(audible_differences), 'audible register differences')


if __name__ == '__main__':
    main()
