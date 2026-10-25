"""Read-only function-entry observation of a logged assisted boss fight."""
import argparse
import contextlib
import ctypes as c
import io
import json
import re
from run_core import ROOT, run
from rebase_natural_campaign import evidence
from archive_lossless_evidence import sha


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--trace', required=True)
    parser.add_argument('--end-frame', type=int, required=True)
    parser.add_argument('--tag', required=True)
    args = parser.parse_args()
    trace = (ROOT / 'validation' / args.trace).resolve()
    assert trace.is_relative_to(ROOT / 'validation')
    capture = json.loads(evidence(trace / 'capture.json'))
    assist = json.loads(evidence(trace / 'assistance.json'))
    controls = json.loads(evidence(trace / 'controls.json'))
    end = args.end_frame
    assert assist['release_write_frame'] < assist['first_boss_combat']['frame'] < end <= capture['frames']
    expected_ram = evidence(trace / f'ram_{end:05d}.bin')
    expected_png = evidence(trace / f'frame_{end:05d}.png')
    rom = ROOT / 'gaw-megadrive.bin'
    assert sha(rom.read_bytes()) == capture['rom_sha256']
    symbols = {m[2].split('.lto_priv.')[0].split('.constprop.')[0]: int(m[1], 16)
               for line in (ROOT / 'megadrive/out/release/symbol.txt').read_text().splitlines()
               if (m := re.match(r'([0-9a-fA-F]+)\s+\w\s+(\S+)', line))}
    watched = {symbols[name]: name for name in ['tick_world_simulation', 'tick_world_actors', 'wait_frame', 'world_vint']}
    core = ROOT.parents[1] / 'work/genesis-plus-gx/genesis_plus_gx_clock_libretro.dll'
    dll = c.CDLL(str(core))
    dll.gaw_md_config.argtypes = [c.c_uint, c.POINTER(c.c_uint)]
    dll.gaw_md_event_count.restype = c.c_uint
    dll.gaw_md_event_data.restype = c.POINTER(c.c_uint)
    pcs = (c.c_uint * len(watched))(*watched)
    dll.gaw_md_config(len(watched), pcs)
    rows = []
    samples = []
    first = assist['first_boss_combat']['frame']

    def observe(frame, ram):
        count = dll.gaw_md_event_count()
        assert count < 8192
        data = dll.gaw_md_event_data()
        if frame >= first:
            for n in range(count):
                pc, cycles, sp = (int(data[n * 3 + k]) for k in range(3))
                rows.append(dict(frame=frame, function=watched[pc], master_cycles=cycles, sp=sp & 65535))
            word = lambda name: int.from_bytes(bytes(ram[((symbols[name] + k) & 65535) ^ 1] for k in range(2)), 'big')
            samples.append(dict(frame=frame, game=word('game_state'), health=word('hero_health'), room=word('room_id')))
        dll.gaw_md_config(len(watched), pcs)

    presses = [(a, min(b, end), key) for a, b, key in capture['presses'] if a <= end]
    controls = [row for row in controls if row['frame'] <= end]
    for i, row in enumerate(controls):
        stop = controls[i + 1]['frame'] - 1 if i + 1 < len(controls) else end
        presses.extend((row['frame'], stop, key) for key in row['buttons'])
    writes = [(row['frame'], row['address'], bytes.fromhex(row['data_hex'])) for row in assist['writes']]
    assert all(f <= assist['release_write_frame'] for f, _, _ in writes)
    folder = ROOT / 'validation' / args.tag
    assert not folder.exists()
    with contextlib.redirect_stdout(io.StringIO()):
        run(rom, end, folder, {end}, presses, core=core, ram_writes=writes,
            skip_intro=False, ram_observer=observe, core_options=capture['core_options'])
    assert (folder / f'ram_{end:05d}.bin').read_bytes() == expected_ram
    assert (folder / f'frame_{end:05d}.png').read_bytes() == expected_png
    ticks = [row['frame'] for row in rows if row['function'] == 'tick_world_simulation']
    gaps = [dict(before=a, after=b, frames=b-a) for a, b in zip(ticks, ticks[1:]) if b-a != 1]
    report = dict(rom_sha256=capture['rom_sha256'], core_sha256=sha(core.read_bytes()),
                  trace=args.trace, first_frame=first, last_frame=end,
                  boss_room=assist['boss_room'], observed_ticks=len(ticks), gaps=gaps,
                  max_tick_gap=max((b-a for a, b in zip(ticks, ticks[1:])), default=0),
                  ram_and_png_match_recording=True, read_only_observer=True,
                  logged_approach_assistance=True, boss_assistance=False,
                  events=rows, samples=samples,
                  limits=['Function entries measure physical cadence on this recorded NTSC boss fight only. No source SMS, PAL, audio waveform or full-campaign timing equality claim.'])
    (folder / 'cadence_report.json').write_text(json.dumps(report, indent=2) + '\n')
    print({key: value for key, value in report.items() if key not in ['events', 'samples']})


if __name__ == '__main__':
    main()
