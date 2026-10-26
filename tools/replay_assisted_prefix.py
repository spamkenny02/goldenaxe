"""Official cold replay of approach assistance, including prefixes before the boss."""
import argparse
import contextlib
import io
import time
import json
from run_core import ROOT, run, FrameWrites
from archive_lossless_evidence import sha
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--trace', required=True)
    parser.add_argument('--trial', help='Additional independent replay suffix; canonical proof remains unchanged')
    args = parser.parse_args()
    folder = (ROOT / 'validation' / args.trace).resolve()
    assert folder.is_relative_to(ROOT / 'validation')
    capture = json.loads((folder / 'capture.json').read_bytes())
    controls = json.loads((folder / 'controls.json').read_bytes())
    assist, writes = recording(folder, capture)
    sms = folder.name.startswith('sms')
    rom = ROOT / 'input/original.sms' if sms else ROOT / 'gaw-megadrive.bin'
    assert capture['rom_sha256'] == sha(rom.read_bytes()) and capture['sram_input'] is None
    allowed_address = 0x305 if sms else symbols(ROOT / 'megadrive/out/release/symbol.txt')['hero_hurt']
    assert all(address == allowed_address for _, address, _ in writes)
    end = capture['frames']
    for stem, ext in [('ram', 'bin'), ('frame', 'png')]:
        assert (folder / f'{stem}_{end:05d}.{ext}').exists()
    presses = [tuple(row) for row in capture['presses']]
    for i, row in enumerate(controls):
        stop = controls[i + 1]['frame'] - 1 if i + 1 < len(controls) else end
        presses.extend((row['frame'], min(stop, end), key) for key in row['buttons'] if row['frame'] <= end)
    out = folder.with_name(folder.name + f'-assisted-fixed-replay-{end}' + ('-'+args.trial if args.trial else ''))
    assert not out.exists()
    started=time.perf_counter()
    with contextlib.redirect_stdout(io.StringIO()):
        run(rom, end, out, {end}, presses, ram_writes=FrameWrites(writes), skip_intro=False, core_options=capture['core_options'])
    for stem, ext in [('ram', 'bin'), ('frame', 'png')]:
        filename = f'{stem}_{end:05d}.{ext}'
        assert (folder / filename).read_bytes() == (out / filename).read_bytes(), filename
    report = dict(elapsed_seconds=time.perf_counter()-started,indexed_writes=True,passed=True, assisted_route=True, natural_campaign_proof=False,
                  rom_sha256=capture['rom_sha256'], frames=end, feedback_reads=False,
                  ram_injections=True, injection_count=len(writes),
                  last_injection_frame=writes[-1][0], release_write_frame=assist['release_write_frame'],
                  first_boss_combat=assist['first_boss_combat'], boss_assistance=False,
                  approach_only=assist['first_boss_combat'] is None,
                  whole_ram_bytes=8192 if sms else 65536, final_png_exact=True,
                  evidence={name: sha((folder / name).read_bytes()) for name in
                            ['capture.json', 'controls.json', 'assistance.json']})
    (out / 'replay_report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
