"""Direct cold-boot SMS/native PSG register comparison; no baseline-only equivalence claim."""
import argparse
import contextlib
import io
import json
import struct
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'tools'))
from run_core import run
from archive_lossless_evidence import sha

p = argparse.ArgumentParser()
p.add_argument('--out', type=Path, default=root / 'validation/v319-sms-psg01')
p.add_argument('--frames', type=int, default=6500)
a = p.parse_args()
out = a.out.resolve()
assert out.is_relative_to(root / 'validation') and not out.exists() and a.frames > 0
out.mkdir()
rom = root / 'versions/v0319-d3ea2a83/gaw-megadrive-v0319.bin'
original = root / 'input/original.sms'
core = root.parents[1] / 'work/genesis-plus-gx/genesis_plus_gx_libretro.dll'
assert sha(rom.read_bytes()) == 'd3ea2a83ea24ed8a0d3c9857f9fbe70d000a4f73358452c1887f40e78966c56e'
cases = []
for region in ('ntsc', 'pal'):
    records = {}
    for tag, cartridge in [('md', rom), ('sms', original)]:
        rows = []
        def observe(frame, regs):
            assert frame == len(rows) + 1
            rows.append(tuple(regs))
        folder = out / (region + '-' + tag)
        with contextlib.redirect_stdout(io.StringIO()):
            run(cartridge, a.frames, folder, set(), [], skip_intro=False, core=core,
                psg_observer=observe,
                core_options={'genesis_plus_gx_region_detect': 'pal' if region == 'pal' else 'auto'})
        assert len(rows) == a.frames
        encoded = b''.join(struct.pack('<8H', *row) for row in rows)
        (folder / 'psg-registers.bin').write_bytes(encoded)
        records[tag] = rows
        print(region, tag, 'PSG frames captured:', len(rows), flush=True)
    differences = [i + 1 for i, (m, s) in enumerate(zip(records['md'], records['sms'])) if m != s]
    counts = [sum(m[n] != s[n] for m, s in zip(records['md'], records['sms'])) for n in range(8)]
    examples = [dict(frame=f, md=list(records['md'][f - 1]), sms=list(records['sms'][f - 1]))
                for f in differences[:12]]
    case = dict(region=region, frames=a.frames, exact_register_frames=a.frames - len(differences),
                different_register_frames=len(differences), different_frames_by_register=counts,
                first_differences=examples,
                register_sha256={tag: sha((out / (region + '-' + tag) / 'psg-registers.bin').read_bytes())
                                 for tag in records})
    cases.append(case)
    print(region, 'direct SMS PSG:', case['exact_register_frames'], 'exact frames;',
          case['different_register_frames'], 'different;', 'first', differences[:1], flush=True)
result = dict(passed=all(c['different_register_frames'] == 0 for c in cases),
              diagnostic_only=True, direct_sms_reference=True, cases=cases,
              rom_sha256=sha(rom.read_bytes()), source_sha256=sha(original.read_bytes()),
              core_sha256=sha(core.read_bytes()), driver_sha256=sha(Path(__file__).read_bytes()),
              ram_writes=0, sram_imports=0,
              scope='Every-frame cold no-input comparison of all8 PSG registers between V319 and SMS '
                    'in PAL and NTSC. Raw register states, including muted-channel periods; '
                    'no waveform, intra-frame write-time or whole-game equivalence claim.')
(out / 'report.json').write_text(json.dumps(result, indent=2) + '\n')
print('Direct SMS PSG comparison completed; no cartridge changed.', flush=True)
