"""Compare actual SMS/MD plane3 writes for the first reveal, including hidden-color bits."""
import contextlib
import io
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'tools'))
from run_core import run
from archive_lossless_evidence import sha
from validate_playable_sprite_limit import symbols

work = root / 'validation/v319-reveal-row-tail01'
out = work / 'first-plane3'
assert not (out / 'report.json').exists(), 'Probe already finalised'
out.mkdir(exist_ok=True)
baseline = root / 'versions/v0319-d3ea2a83/gaw-megadrive-v0319.bin'
candidate = work / 'project/out/release/rom.bin'
cases = []
for region, first in [('ntsc', 69), ('pal', 62)]:
    frames = [first, first + 1, first + 4]
    rows = {}
    phases = {}
    for tag, rom, syfile in [('baseline', baseline, root / 'megadrive/out/release/symbol.txt'),
                             ('candidate', candidate, work / 'project/out/release/symbol.txt'),
                             ('sms', root / 'input/original.sms', None)]:
        folder = out / (region + '-' + tag)
        options = {'genesis_plus_gx_region_detect': 'pal' if region == 'pal' else 'auto'}
        if not folder.exists():
            with contextlib.redirect_stdout(io.StringIO()):
                run(rom, max(frames), folder, set(frames), [], skip_intro=False, core_options=options)
        capture = json.loads((folder / 'capture.json').read_bytes())
        assert capture['rom_sha256'] == sha(rom.read_bytes()) and capture['frames'] == max(frames)
        assert capture['core_options'] == options and not capture['test_ram_writes'] and not capture['sram_input']
        sy = symbols(syfile) if syfile else None
        values = []
        for frame in frames:
            v = (folder / f'vram_{frame:05d}.bin').read_bytes()
            if tag == 'sms':
                plane = v[3:0x2400:4]
            else:
                plane = bytearray()
                for row in range(2304):
                    at = 512 + row * 4
                    packed = int.from_bytes(bytes(v[(at + n) ^ 1] for n in range(4)), 'big')
                    plane.append(sum(((packed >> (28 - 4 * pixel)) & 8) >> 3 << (7 - pixel)
                                     for pixel in range(8)))
                raw = (folder / f'ram_{frame:05d}.bin').read_bytes()
                word = lambda name: int.from_bytes(bytes(raw[(sy[name] + n) ^ 1] for n in range(2)), 'big')
                assert not word('sound_unhandled_command')
                phases[tag, frame] = {name: word(name) for name in
                                      ('intro_scene', 'intro_counter', 'intro_line', 'intro_logic_clock')}
            values.append(bytes(plane))
        rows[tag] = values
    initial = {tag: sum(b != 255 for b in rows[tag][0]) for tag in rows}
    assert initial == dict(baseline=180, candidate=182, sms=182), (region, initial)
    assert rows['candidate'][0] == rows['sms'][0]
    assert rows['candidate'][-1] == rows['baseline'][-1] == rows['sms'][-1]
    assert all(phases['candidate', f] == phases['baseline', f] for f in frames)
    cases.append(dict(region=region, frames=frames, first_slice_non_ff_rows=initial,
                      first_slice_all_2304_source_bytes_exact=True,
                      completed_pass_all_2304_source_bytes_exact=True,
                      native_logic_phase_unchanged=True,
                      per_frame_plane3_byte_differences={tag: [sum(a != b for a, b in zip(p, s))
                                                              for p, s in zip(rows[tag], rows['sms'])]
                                                        for tag in ('baseline', 'candidate')}))
result = dict(passed=True, candidate_sha256=sha(candidate.read_bytes()), baseline_sha256=sha(baseline.read_bytes()), cases=cases,
              ram_writes=0, sram_imports=0,
              scope='Cold no-input first reveal: physical pattern plane3, including bits hidden by equal palette colors. '
                    'First 182 rows and complete pass match SMS; selected native phase fields match V319. '
                    'Full boot visual comparisons remain a separate gate.')
(out / 'report.json').write_text(json.dumps(result, indent=2) + '\n')
print('PAL and NTSC first 182 rows and complete plane3 pass match SMS exactly; native phase unchanged.')
