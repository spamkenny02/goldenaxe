"""Cold replay of logged approach assistance, followed by an unassisted boss.

This is explicitly NOT the no-injection natural campaign verifier.
"""
import argparse
import contextlib
import io
import json
from run_core import ROOT, run
from archive_lossless_evidence import sha


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--trace', required=True)
    parser.add_argument('--end-frame', type=int)
    parser.add_argument('--rom', help='Explicit numbered historical ROM; SHA must match the trace')
    args = parser.parse_args()
    folder = (ROOT / 'validation' / args.trace).resolve()
    assert folder.is_relative_to(ROOT / 'validation')
    capture = json.loads((folder / 'capture.json').read_bytes())
    assistance = json.loads((folder / 'assistance.json').read_bytes())
    controls = json.loads((folder / 'controls.json').read_bytes())
    end = args.end_frame or capture['frames']
    assert 0 < end <= capture['frames'] and capture['sram_input'] is None
    for stem, suffix in [('ram', 'bin'), ('frame', 'png')]:
        assert (folder / f'{stem}_{end:05d}.{suffix}').exists(), 'Choose an already captured comparison frame'
    assert assistance['first_boss_combat'] is not None
    release = assistance['release_write_frame']
    assert release < assistance['first_boss_combat']['frame'] <= end
    assert assistance['first_boss_combat']['hurt'] == 0
    assert assistance['writes'][-1]['frame'] == release
    assert assistance['writes'][-1]['data_hex'] == '0000'
    writes = [(row['frame'], row['address'], bytes.fromhex(row['data_hex']))
              for row in assistance['writes'] if row['frame'] <= end]
    assert all(frame <= release for frame, _, _ in writes)
    assert capture['test_ram_writes'] == [dict(frame=f, address=a, byte_count=len(data)) for f, a, data in writes]
    rom = ROOT / args.rom if args.rom else ROOT / 'gaw-megadrive.bin'
    assert sha(rom.read_bytes()) == capture['rom_sha256']
    controls = [row for row in controls if row['frame'] <= end]
    presses = [(a, min(b, end), key) for a, b, key in capture['presses'] if a <= end]
    for i, row in enumerate(controls):
        stop = controls[i + 1]['frame'] - 1 if i + 1 < len(controls) else end
        presses.extend((row['frame'], stop, key) for key in row['buttons'])
    out = folder.with_name(folder.name + f'-assisted-fixed-replay-{end}')
    assert not out.exists()
    with contextlib.redirect_stdout(io.StringIO()):
        run(rom, end, out, {end}, presses, skip_intro=False,
            ram_writes=writes, core_options=capture['core_options'])
    for stem, suffix in [('ram', 'bin'), ('frame', 'png')]:
        filename = f'{stem}_{end:05d}.{suffix}'
        assert (folder / filename).read_bytes() == (out / filename).read_bytes(), filename
    report = dict(passed=True, assisted_route=True, natural_campaign_proof=False,
                  rom_sha256=capture['rom_sha256'], trace=args.trace, frames=end,
                  ram_injections=True, injection_count=len(writes),
                  last_injection_frame=release, first_boss_combat=assistance['first_boss_combat'],
                  first_boss_damage=assistance['first_boss_damage'],
                  boss_assistance=False, feedback_reads=False, primary_state_imports=0,
                  whole_ram_bytes=(out / f'ram_{end:05d}.bin').stat().st_size,
                  final_png_exact=True,
                  evidence={name: sha((folder / name).read_bytes()) for name in
                            ['capture.json', 'controls.json', 'assistance.json']})
    (out / 'replay_report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
