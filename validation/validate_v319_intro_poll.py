"""Native F21 polling versus original-ROM entry/return snapshots and live reader IRQs."""
import argparse
import contextlib
import ctypes as c
import gzip
import io
import json
import os
import struct
import subprocess
import sys
from pathlib import Path
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'tools'))
from run_core import run
from archive_lossless_evidence import sha
from validate_native_source_wait import MODULES

p = argparse.ArgumentParser()
p.add_argument('--out-name', default='v319-native-intro-poll01')
a = p.parse_args()
assert a.out_name.startswith('v319-native-intro-poll') and '/' not in a.out_name and '\\' not in a.out_name
out = root / 'validation' / a.out_name
assert not out.exists()
out.mkdir()
wrapper = '''#include "source_intro_wait.h"
u8 poll_case(const u32 *phase,u8 refresh,u8 *ram,u8 *audio,const u8 *low,const u8 *bank,u32 *out)
{
 SourceClock clock;SourceIrqContext context={0};SourceIntroWaitOutput result;
 s32 raster=(s32)(phase[1]*3420)+(s32)(phase[0]-phase[2]);u32 period=phase[3]*3420;
 if((phase[3]!=262 && phase[3]!=313) || phase[5] || (phase[6]&4) || (phase[11]&16)) return 0;
 while(raster<0) raster+=period;
 while((u32)raster>=period) raster-=period;
 if(!source_clock_init(&clock,phase[3],raster,refresh,phase[8],phase[9],phase[10])) return 0;
 context.ram=ram;context.audio=audio;context.low=low;context.low_bytes=32768;context.bank6=bank;
 context.input.lines=phase[3];context.input.reset_mask=16;
 if(!source_intro_vcounter_poll(&clock,&context,&result)) return 0;
 out[0]=clock.raster;out[1]=clock.elapsed;out[2]=clock.foreground_tstates;out[3]=clock.foreground_m1;
 out[4]=clock.irq_tstates;out[5]=clock.irq_m1;out[6]=clock.irq_count;out[7]=clock.refresh;
 out[8]=clock.iff;out[9]=clock.blocked;out[10]=clock.pending;out[11]=clock.first;
 out[12]=result.polls;out[13]=result.below;out[14]=result.above;out[15]=result.counter;
 out[16]=result.error;out[17]=context.error;return 1;
}
'''
(out / 'wrapper.c').write_text(wrapper)
sdk = root.parents[1] / 'work/sgdk'
env = dict(os.environ); env['PATH'] = 'C:/msys64/ucrt64/bin;' + env['PATH']
modules = ['source_intro_wait', 'source_wait_restore', *MODULES]
command = ['C:/msys64/ucrt64/bin/gcc.exe', '-O3', '-shared', '-Wall', '-Wextra', '-Werror',
    '-I', str(sdk / 'inc'), '-I', str(root / 'megadrive/src'), str(out / 'wrapper.c')]
command += [str(root / 'megadrive/src' / (name + '.c')) for name in modules]
command += ['-o', str(out / 'native.dll')]
built = subprocess.run(command, env=env, capture_output=True, text=True)
(out / 'compile.log').write_text(built.stdout + built.stderr)
assert built.returncode == 0, built.stderr
native = c.CDLL(str(out / 'native.dll')).poll_case
native.argtypes = [c.POINTER(c.c_uint32), c.c_uint8] + [c.POINTER(c.c_uint8)] * 4 + [c.POINTER(c.c_uint32)]
native.restype = c.c_uint8
build = json.loads((root / 'validation/v319-intro-poll-observer01/report.json').read_bytes())
core = Path(build['core']); assert sha(core.read_bytes()) == build['core_sha256']
dll = c.CDLL(str(core))
dll.gaw_poll_reset.restype = None
dll.gaw_poll_size.restype = dll.gaw_poll_errors.restype = dll.gaw_poll_stride.restype = c.c_uint
dll.gaw_poll_data.restype = c.POINTER(c.c_uint8)
assert dll.gaw_poll_stride() == 1624
image = (root / 'input/original.sms').read_bytes()
low = (c.c_uint8 * 32768).from_buffer_copy(image[:32768]); bank = (c.c_uint8 * 16384).from_buffer_copy(image[0x18000:0x1c000])
archive = root / 'analysis/v319-psg-write-spacing'
manifest = json.loads((archive / 'manifest.json').read_bytes())
results = []
for region in ('ntsc', 'pal'):
    dll.gaw_poll_reset(); psg = bytearray()
    with contextlib.redirect_stdout(io.StringIO()):
        run(root / 'input/original.sms', 14000, out / region, set(), [], skip_intro=False, core=core,
            psg_observer=lambda frame, values: psg.extend(struct.pack('<8H', *values)),
            core_options={'genesis_plus_gx_region_detect': 'pal' if region == 'pal' else 'auto'})
    assert dll.gaw_poll_errors() == 0
    count = dll.gaw_poll_size(); assert 0 < count < 4096
    raw = c.string_at(dll.gaw_poll_data(), count * 1624)
    (out / region / 'source-poll-records.bin').write_bytes(raw)
    item = manifest['compressed'][f'validation/v319-psg-writes01/{region}-sms/exposed-psg-states.bin']
    encoded = (archive / item['stored']).read_bytes(); assert sha(encoded) == item['stored_sha256']
    prior = gzip.decompress(encoded); assert sha(prior) == item['raw_sha256'] and prior == psg
    (out / region / 'psg-states.bin').write_bytes(psg)
    cases = []
    for n in range(count):
        record = raw[n*1624:(n+1)*1624]; first = record[:808]; last = record[808:1616]
        phase = struct.unpack_from('<12I', first, 16); end = struct.unpack_from('<12I', last, 16)
        refresh, pc = struct.unpack_from('<2I', first, 64); final_refresh, final_pc = struct.unpack_from('<2I', last, 64)
        assert (pc, final_pc) == (0xf21, 0xf2b)
        state = (c.c_uint8 * 336).from_buffer_copy(first[72:408]); audio = (c.c_uint8 * 400).from_buffer_copy(first[408:808])
        result = (c.c_uint32 * 18)()
        assert native((c.c_uint32 * 12)(*phase), refresh, state, audio, low, bank, result), (region, n, 'native rejection')
        wall = struct.unpack_from('<Q', last)[0] - struct.unpack_from('<Q', first)[0]
        irq = struct.unpack_from('<Q', last, 8)[0] - struct.unpack_from('<Q', first, 8)[0]
        delta = (end[0] - end[2] + 0x80000000) % 0x100000000 - 0x80000000
        raster = (end[1] * 3420 + delta) % (end[3] * 3420)
        assert (result[0], result[1], result[4]*15, result[7]) == (raster, wall, irq, final_refresh), (region, n, list(result), raster, wall, irq, final_refresh)
        assert result[12] == struct.unpack_from('<I', record, 1616)[0]
        assert result[2] == 30*result[13] + 44*result[14] + 39
        assert result[3] == 3*result[13] + 5*result[14] + 5
        assert (result[8], result[9], result[10], result[11]) == (end[8], end[9], end[10], 1)
        assert bytes(state) == last[72:408] and bytes(audio) == last[408:808], (region, n, 'RAM/audio')
        cases.append(dict(phase=list(phase), refresh=refresh, expected=list(result),
            input_ram=list(first[72:408]), input_audio=list(first[408:808]),
            expected_ram=list(state), expected_audio=list(audio)))
    (out / region / 'native-cases.json').write_text(json.dumps(cases, separators=(',', ':')) + '\n')
    row = dict(region=region, source_cases=count, source_poll_reads=sum(case['expected'][12] for case in cases),
        cases_crossing_irq=sum(bool(case['expected'][6]) for case in cases),
        observer_exposed_psg_exact_frames=14000, source_records_sha256=sha(raw),
        maximum_polls=max(case['expected'][12] for case in cases))
    results.append(row); print(json.dumps(row), flush=True)
report = dict(passed=True, diagnostic_only=True, production_rom_changed=False, cases=results,
    core_sha256=sha(core.read_bytes()), source_sha256=sha(image),
    native_sources={name: sha((root / 'megadrive/src' / (name + '.c')).read_bytes()) for name in modules},
    verified=['Original F21/F2B natural entry/return wall time, raster, polls, R, IFF/EI/pending,336 IRQ RAM and400 reader bytes.',
              'Both regions,14000 no-input cold source frames per region; observer PSG state unchanged.'],
    limits=['Host native semantic helper; compiled68000 timing and physical MD publication not checked here.',
            'F09 callback continuation APIs compile but have no direct oracle check in this poll-only test.',
            'No production clock integration, full-game or PCM certification.'])
(out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
