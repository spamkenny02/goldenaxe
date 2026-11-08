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
p.add_argument('--profile', choices=['poll','callback','window'], default='poll')
p.add_argument('--fire', action='store_true')
p.add_argument('--observer-revision',type=int,default=1)
p.add_argument('--actors',choices=['second','third'])
p.add_argument('--irq-status',action='store_true')
p.add_argument('--init',action='store_true')
p.add_argument('--reveal',action='store_true')
a = p.parse_args()
if a.reveal:
 assert not(a.actors or a.fire or a.init) and a.profile=='callback'
 a.actors='second';a.irq_status=True
assert not a.init or (a.actors and a.profile=='callback')
assert not(a.fire and a.actors)
assert not a.irq_status or a.actors
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
if a.profile != 'poll':
    wrapper = wrapper.replace('source_intro_vcounter_poll(&clock,&context,&result)',
        'source_intro_wait_' + ('callback' if a.profile == 'callback' else 'window') + '(&clock,&context,0,0,&result)')
    (out / 'wrapper.c').write_text(wrapper)
if a.fire:
    assert a.profile != 'poll'
    palette=(root/'input/original.sms').read_bytes()[0x17e13:0x17e25]
    wrapper=wrapper.replace('#include "source_intro_wait.h"', '#include "source_intro_fire.h"\n'
        'static u8 fire_full_ram[8192];\nstatic const u8 fire_colors[18]={'+','.join(map(str,palette))+'};')
    wrapper=wrapper.replace('context.ram=ram;', '''__builtin_memset(fire_full_ram,0,sizeof(fire_full_ram));
 for(u16 n=0;n<72;n++) fire_full_ram[0x1ca0+n]=ram[336+n];
 fire_full_ram[0x1fff]=ram[408];fire_full_ram[0x1cec]=ram[409];fire_full_ram[0x1ced]=ram[410];
 context.full_ram=fire_full_ram;context.ram=ram;''')
    wrapper=wrapper.replace('(&clock,&context,0,0,&result)', '(&clock,&context,source_intro_fire_callback,(void *)fire_colors,&result)')
    wrapper=wrapper.replace('out[0]=clock.raster;', '''for(u16 n=0;n<72;n++) ram[336+n]=fire_full_ram[0x1ca0+n];
 ram[408]=fire_full_ram[0x1fff];ram[409]=fire_full_ram[0x1cec];ram[410]=fire_full_ram[0x1ced];
 out[0]=clock.raster;''')
    (out/'wrapper.c').write_text(wrapper)
if a.irq_status:
    hook='''static u8 irq_status_count,irq_status_position,irq_status_values[8];
u8 source_irq_interrupt_impl(void *,const SourceClockIrq *,SourceClockWork *);
u8 source_irq_interrupt(void *opaque,const SourceClockIrq *entry,SourceClockWork *work)
{
 SourceIrqContext *irq=opaque;
 if(irq_status_position>=irq_status_count) return 0;
 irq->ram[0x1b]=irq_status_values[irq_status_position++];
 return source_irq_interrupt_impl(opaque,entry,work);
}
'''
    point=wrapper.index('u8 poll_case(')
    wrapper=wrapper[:point]+hook+wrapper[point:]
    wrapper=wrapper.replace('out[0]=clock.raster;',
        'if(irq_status_position!=irq_status_count) return 0;\n out[0]=clock.raster;')
    (out/'wrapper.c').write_text(wrapper)
if a.actors:
    assert a.profile!='poll'
    colors=(root/'input/original.sms').read_bytes()[0x17e57:0x17e78]
    wrapper=wrapper.replace('#include "source_intro_wait.h"','#include "source_intro_actors.h"\n'
        'static u8 actor_full_ram[8192];\nstatic const u8 actor_bank5[16384]={[0x3e57]='+','.join(map(str,colors))+'};')
    wrapper=wrapper.replace('SourceClock clock;SourceIrqContext context={0};',
        'SourceClock clock;SourceIrqContext context={0};SourceIntroActorData actor_data={low,actor_bank5};')
    wrapper=wrapper.replace('context.ram=ram;', '''__builtin_memset(actor_full_ram,0,sizeof(actor_full_ram));
 for(u16 n=0;n<72;n++) actor_full_ram[0x1ca0+n]=ram[336+n];
 actor_full_ram[0x1fff]=ram[408];actor_full_ram[0x1cec]=ram[409];actor_full_ram[0x1ced]=ram[410];
 for(u16 n=0;n<768;n++) actor_full_ram[0x300+n]=ram[416+n];
 context.full_ram=actor_full_ram;context.ram=ram;''')
    wrapper=wrapper.replace('(&clock,&context,0,0,&result)',
        '(&clock,&context,source_intro_actors_'+a.actors+',&actor_data,&result)')
    wrapper=wrapper.replace('out[0]=clock.raster;', '''for(u16 n=0;n<72;n++) ram[336+n]=actor_full_ram[0x1ca0+n];
 ram[408]=actor_full_ram[0x1fff];ram[409]=actor_full_ram[0x1cec];ram[410]=actor_full_ram[0x1ced];
 for(u16 n=0;n<768;n++) ram[416+n]=actor_full_ram[0x300+n];
 out[0]=clock.raster;''')
    (out/'wrapper.c').write_text(wrapper)
if a.init:
    wrapper=wrapper.replace('SourceIntroWaitOutput result;', 'SourceIntroWaitOutput result={0};')
    wrapper=wrapper.replace('source_intro_wait_callback(&clock,&context,source_intro_actors_'+a.actors+',&actor_data,&result)',
        'source_intro_actors_initialize(&clock,&context,&actor_data,(u16)phase[4],'+('1' if a.actors=='second' else '0')+')')
    # phase[4] carries captured source HL; output poll count stays zero for initialization.
    (out/'wrapper.c').write_text(wrapper)
if a.reveal:
    wrapper=wrapper.replace('#include "source_intro_actors.h"','#include "source_intro_reveal.h"')
    wrapper=wrapper.replace('SourceIntroActorData actor_data={low,actor_bank5};','SourceIntroRevealPass reveal={ram[411]|((u16)ram[412]<<8),ram[413]|((u16)ram[414]<<8),0,ram[415]};')
    wrapper=wrapper.replace('SourceIntroWaitOutput result;', 'SourceIntroWaitOutput result={0};')
    wrapper=wrapper.replace('source_intro_wait_callback(&clock,&context,source_intro_actors_second,&actor_data,&result)',
        'source_intro_reveal_pass(&clock,&context,&reveal,reveal_sink,0)')
    wrapper=wrapper.replace('static const u8 actor_bank5[16384]={[0x3e57]='+','.join(map(str,colors))+'};','')
    point=wrapper.index('u8 poll_case(')
    wrapper=wrapper[:point]+'''static u32 reveal_origin,reveal_period;
static const u32 *reveal_events;static u16 reveal_event_count,reveal_event_position;
void configure_reveal_events(const u32 *events,u16 count)
{reveal_events=events;reveal_event_count=count;reveal_event_position=0;}
static u8 reveal_sink(void *user,u32 elapsed,u32 raster,u8 port,u8 value)
{
 (void)user;
 if(reveal_event_position>=reveal_event_count ||
    elapsed!=reveal_events[reveal_event_position*2] ||
    raster!=(reveal_origin+elapsed)%reveal_period ||
    (((u32)port<<8)|value)!=reveal_events[reveal_event_position*2+1]) return 0;
 reveal_event_position++;return 1;
}
'''+wrapper[point:]
    wrapper=wrapper.replace('__builtin_memset(actor_full_ram,0,sizeof(actor_full_ram));',
        'reveal_origin=clock.raster;reveal_period=clock.period;\n __builtin_memset(actor_full_ram,0,sizeof(actor_full_ram));')
    wrapper=wrapper.replace('out[0]=clock.raster;','''if(reveal_event_position!=reveal_event_count) return 0;
 ram[411]=reveal.address;ram[412]=reveal.address>>8;ram[413]=reveal.step;ram[414]=reveal.step>>8;ram[415]=reveal.value;
 result.polls=reveal_event_position;
 out[0]=clock.raster;''')
    (out/'wrapper.c').write_text(wrapper)
if a.irq_status:
    assert wrapper.count('context.full_ram=actor_full_ram;')==1
    wrapper=wrapper.replace('context.full_ram=actor_full_ram;',
        'irq_status_count=ram[1184];irq_status_position=0;\n'
        ' for(u16 n=0;n<8;n++) irq_status_values[n]=ram[1185+n];\n context.full_ram=actor_full_ram;')
    (out/'wrapper.c').write_text(wrapper)
sdk = root.parents[1] / 'work/sgdk'
env = dict(os.environ); env['PATH'] = 'C:/msys64/ucrt64/bin;' + env['PATH']
modules = ['source_intro_wait', 'source_wait_restore', *MODULES]
if a.fire: modules.insert(0,'source_intro_fire')
if a.actors: modules.insert(0,'source_intro_reveal' if a.reveal else 'source_intro_actors')
command = ['C:/msys64/ucrt64/bin/gcc.exe', '-O3', '-shared', '-Wall', '-Wextra', '-Werror',
    '-I', str(sdk / 'inc'), '-I', str(root / 'megadrive/src'), str(out / 'wrapper.c')]
module_paths=[root/'megadrive/src'/(name+'.c') for name in modules]
if a.irq_status:
    override=out/'irq-status-adapter.c'
    override.write_text('#define source_irq_interrupt source_irq_interrupt_impl\n#include "../../megadrive/src/source_irq_context.c"\n')
    module_paths=[override if p.name=='source_irq_context.c' else p for p in module_paths]
command += [str(p) for p in module_paths]
command += ['-o', str(out / 'native.dll')]
built = subprocess.run(command, env=env, capture_output=True, text=True)
(out / 'compile.log').write_text(built.stdout + built.stderr)
assert built.returncode == 0, built.stderr
native = c.CDLL(str(out / 'native.dll')).poll_case
native.argtypes = [c.POINTER(c.c_uint32), c.c_uint8] + [c.POINTER(c.c_uint8)] * 4 + [c.POINTER(c.c_uint32)]
native.restype = c.c_uint8
build_folder = 'v319-intro-poll-observer01' if a.profile == 'poll' else 'v319-intro-empty-' + a.profile + '-observer01'
if a.fire: build_folder=build_folder.replace('empty','fire')
if a.actors:build_folder=build_folder.replace('empty','actors_'+a.actors)
if a.init:build_folder=build_folder.replace('intro-actors_','intro-init_actors_')
if a.reveal:build_folder='v319-intro-reveal-callback-observer01'
build_folder=build_folder[:-2]+f'{a.observer_revision:02}'
build = json.loads((root / 'validation' / build_folder / 'report.json').read_bytes())
core = Path(build['core']); assert sha(core.read_bytes()) == build['core_sha256']
dll = c.CDLL(str(core))
dll.gaw_poll_reset.restype = None
dll.gaw_poll_size.restype = dll.gaw_poll_errors.restype = dll.gaw_poll_stride.restype = c.c_uint
dll.gaw_poll_data.restype = c.POINTER(c.c_uint8)
snapshot=1656 if a.actors else 888 if a.fire else 808
stride=snapshot*2+8
if a.irq_status:stride+=40
if a.reveal:stride+=6912*8
assert dll.gaw_poll_stride() == stride
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
    count = dll.gaw_poll_size(); assert 0 < count < (128 if a.reveal else 4096)
    raw = c.string_at(dll.gaw_poll_data(), count * stride)
    (out / region / 'source-poll-records.bin').write_bytes(raw)
    item = manifest['compressed'][f'validation/v319-psg-writes01/{region}-sms/exposed-psg-states.bin']
    encoded = (archive / item['stored']).read_bytes(); assert sha(encoded) == item['stored_sha256']
    prior = gzip.decompress(encoded); assert sha(prior) == item['raw_sha256'] and prior == psg
    (out / region / 'psg-states.bin').write_bytes(psg)
    cases = []
    for n in range(count):
        record = raw[n*stride:(n+1)*stride]; first = record[:snapshot]; last = record[snapshot:snapshot*2]
        phase = struct.unpack_from('<12I', first, 16); end = struct.unpack_from('<12I', last, 16)
        refresh, pc = struct.unpack_from('<2I', first, 64); final_refresh, final_pc = struct.unpack_from('<2I', last, 64)
        if a.profile == 'poll': assert (pc, final_pc) == (0xf21, 0xf2b)
        else:
            assert pc == (0xe8b if a.reveal else (0xf51 if a.actors=='second' else 0xf54) if a.init else 0xf09 if a.profile == 'callback' else 0xf1e)
            if a.init:phase=tuple(phase[i] if i!=4 else struct.unpack_from('<I',record,snapshot*2)[0] for i in range(12))
            assert final_pc == (0xea0 if a.reveal else struct.unpack_from('<I', record, snapshot*2+4)[0])
        before=first[72:408]+(first[808:snapshot] if a.fire or a.actors else b'')
        expected_state=last[72:408]+(last[808:snapshot] if a.fire or a.actors else b'')
        if a.irq_status:
            statuses=struct.unpack_from('<9I',record,snapshot*2+8)
            assert (0 if a.init else 1)<=statuses[0]<=8 and all(v<=255 for v in statuses[1:])
            before+=bytes(statuses);expected_state+=bytes(statuses)
        state = (c.c_uint8 * len(before)).from_buffer_copy(before); audio = (c.c_uint8 * 400).from_buffer_copy(first[408:808])
        if a.reveal:
            event_count=struct.unpack_from('<I',record,snapshot*2)[0];assert event_count==6912
            event_values=struct.unpack_from('<13824I',record,snapshot*2+44)
            event_buffer=(c.c_uint32*len(event_values))(*event_values)
            configure=c.CDLL(str(out/'native.dll')).configure_reveal_events
            configure.argtypes=[c.POINTER(c.c_uint32),c.c_uint16];configure.restype=None
            configure(event_buffer,event_count)
        result = (c.c_uint32 * 18)()
        assert native((c.c_uint32 * 12)(*phase), refresh, state, audio, low, bank, result), (region, n, 'native rejection')
        wall = struct.unpack_from('<Q', last)[0] - struct.unpack_from('<Q', first)[0]
        irq = struct.unpack_from('<Q', last, 8)[0] - struct.unpack_from('<Q', first, 8)[0]
        delta = (end[0] - end[2] + 0x80000000) % 0x100000000 - 0x80000000
        raster = (end[1] * 3420 + delta) % (end[3] * 3420)
        assert (result[0], result[1], result[4]*15, result[7]) == (raster, wall, irq, final_refresh), (region, n, list(result), raster, wall, irq, final_refresh)
        assert result[12] == (0 if a.init else struct.unpack_from('<I', record, snapshot*2)[0])
        if a.profile == 'poll':
            assert result[2] == 30*result[13] + 44*result[14] + 39
            assert result[3] == 3*result[13] + 5*result[14] + 5
        assert result[2]*15 + irq == wall
        assert (result[8], result[9], result[10], result[11]) == (end[8], end[9], end[10], 1)
        assert bytes(state) == expected_state and bytes(audio) == last[408:808], (region, n, 'RAM/audio')
        cases.append(dict(phase=list(phase), refresh=refresh, expected=list(result),
            input_ram=list(before), input_audio=list(first[408:808]),
            expected_ram=list(state), expected_audio=list(audio)))
        if a.reveal:cases[-1]['events']=list(event_values)
    (out / region / 'native-cases.json').write_text(json.dumps(cases, separators=(',', ':')) + '\n')
    row = dict(region=region, source_cases=count, source_poll_reads=sum(case['expected'][12] for case in cases),
        cases_crossing_irq=sum(bool(case['expected'][6]) for case in cases),
        observer_exposed_psg_exact_frames=14000, source_records_sha256=sha(raw),
        maximum_polls=max(case['expected'][12] for case in cases))
    if a.reveal:
        row['source_io_events']=row.pop('source_poll_reads');row['maximum_io_events']=row.pop('maximum_polls')
    if a.init:row['source_template_addresses']=sorted({case['phase'][4] for case in cases})
    results.append(row); print(json.dumps(row), flush=True)
report = dict(passed=True, diagnostic_only=True, profile=a.profile, fire=a.fire, actors=a.actors,
    irq_status=a.irq_status,init=a.init,reveal=a.reveal,production_rom_changed=False, cases=results,
    core_sha256=sha(core.read_bytes()), source_sha256=sha(image),
    native_sources={name: sha((root / 'megadrive/src' / (name + '.c')).read_bytes()) for name in modules},
    verified=['Original natural entry/return wall time, raster, '+('initial HL, ' if a.init else 'polls, ')+
              'R, IFF/EI/pending,336 IRQ RAM and400 reader bytes.'+
              (' Fire palette/counter/mapper/callback snapshots also compared.' if a.fire else '')+
              (' Actor768-byte records and palette/counter/mapper/callback snapshots also compared.' if a.actors else ''),
              'Both regions,14000 no-input cold source frames per region; observer PSG state unchanged.'],
    limits=['Host native semantic helper; compiled68000 timing and physical MD publication not checked here.',
            ('Reveal pass E8B..E9D only; every OUT instruction completion compared. Live VDP status remains external diagnostic input.' if a.reveal else
             'Natural actor initialization only; these vectors do not exercise IRQ crossing.' if a.init else
             'Selected original actor callback profile; captured VDP status is explicit diagnostic IRQ input where enabled.' if a.actors else
             'Selected profile with original F37 fire callback; no actors or skip inputs.' if a.fire else
             'Selected entry profile only; callback/window profiles use original F36 empty callback, not fire/actors.'),
            'No production clock integration, full-game or PCM certification.'])
(out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
