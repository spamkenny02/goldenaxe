"""Compare optimized polling to the source-checked unbatched implementation at IRQ/EI/wrap edges."""
import ctypes as c
import json
import random
import sys
from pathlib import Path
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'tools'))
from archive_lossless_evidence import sha
base = root / 'validation/v319-native-intro-poll01'
fast = root / 'validation/v319-native-intro-poll02'
report = fast / 'stress-report.json'
assert not report.exists()
functions = []
for folder in (base, fast):
    fn = c.CDLL(str(folder / 'native.dll')).poll_case
    fn.argtypes = [c.POINTER(c.c_uint32), c.c_uint8] + [c.POINTER(c.c_uint8)] * 4 + [c.POINTER(c.c_uint32)]
    fn.restype = c.c_uint8
    functions.append(fn)
image = (root / 'input/original.sms').read_bytes()
low = (c.c_uint8 * 32768).from_buffer_copy(image[:32768]); bank = (c.c_uint8 * 16384).from_buffer_copy(image[0x18000:0x1c000])
rng = random.Random(0xf2100f2b)
results = []
for lines, region in ((262, 'ntsc'), (313, 'pal')):
    seed_cases = json.loads((base / region / 'native-cases.json').read_bytes())
    phases = {0, lines*3420-1}
    for line in (111,112,127,128,192,193,218,219,242,243,lines-1):
        if line>=lines: continue
        phases.update((line*3420 + offset) % (lines*3420) for offset in (-166,-165,-1,0,1,165,166))
    cases = [(phase, iff, blocked, pending, refresh, full, skip, comp)
             for phase in sorted(phases) for iff,blocked,pending,refresh,full,skip,comp in
             [(0,0,0,0,0,0,0),(1,0,0,127,0,0,128),(1,0,1,255,0,0,0),
              (1,1,1,128,1,0,128),(1,0,1,0,1,1,0),(0,1,1,255,1,0,128)]]
    cases += [(rng.randrange(lines*3420),rng.randrange(2),rng.randrange(2),rng.randrange(2),
               rng.randrange(256),rng.randrange(2),rng.randrange(2),rng.choice((0,128))) for _ in range(2500)]
    accepted = rejected = with_irq = with_full = 0
    digest = bytearray()
    for n, (raster,iff,blocked,pending,refresh,full,skip,comp) in enumerate(cases):
        state = bytearray(336); state[0x35]=0xdd; state[0x2e]=full; state[0x33]=skip
        state[0x30]=n%256
        sound = bytearray(seed_cases[n%len(seed_cases)]['input_audio'])
        sound[3]=comp
        if n%2: sound[10]=1  # Paused and genuine live-reader states both covered.
        phase = (c.c_uint32 * 12)(raster,raster//3420,(raster//3420)*3420,lines,
            242 if lines==313 else 218,0,32,32,iff,blocked,pending,0)
        observed = []
        for fn in functions:
            ram = (c.c_uint8 * 336).from_buffer_copy(state); audio = (c.c_uint8 * 400).from_buffer_copy(sound)
            output = (c.c_uint32 * 18)()
            ok = fn(phase,refresh,ram,audio,low,bank,output)
            observed.append((ok,tuple(output),bytes(ram),bytes(audio)))
        assert observed[0] == observed[1], (region,n,cases[n],observed[0][:2],observed[1][:2])
        row = observed[1]
        if row[0]:
            accepted+=1;with_irq+=bool(row[1][6]);with_full+=bool(full and row[1][6])
        else: rejected+=1
        digest.extend(bytes([row[0]]));digest.extend(row[2]);digest.extend(row[3])
    result = dict(region=region,cases=len(cases),accepted=accepted,rejected=rejected,
        accepted_with_irq=with_irq,accepted_with_full_irq=with_full,result_sha256=sha(digest))
    assert with_irq and with_full
    results.append(result);print(result,flush=True)
report.write_text(json.dumps(dict(passed=True,cases=results,scope='Optimized/native unbatched parity at '
    'synthetic raster,DI/EI/pending,R,full/audio IRQ,paused/live reader contexts. The unbatched '
    'implementation is directly source-checked for natural polls; these synthetic contexts are '
    'regression coverage, not a second direct source oracle.'),indent=2)+'\n')
