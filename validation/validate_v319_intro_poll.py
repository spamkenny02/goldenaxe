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
p.add_argument('--sequence',action='store_true')
p.add_argument('--skip',action='store_true')
p.add_argument('--capture-work')
p.add_argument('--transfer',action='store_true')
p.add_argument('--prepare',action='store_true')
p.add_argument('--map',choices=['decode','place'])
p.add_argument('--clear',action='store_true')
p.add_argument('--scene',action='store_true')
a = p.parse_args()
if a.scene:a.map='decode'
if a.clear:a.transfer=True
if a.map:a.transfer=True
if a.prepare:a.transfer=True
if a.transfer:
 assert not a.skip
 a.sequence=True
if a.skip:a.sequence=True
if a.sequence:a.reveal=True
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
if a.sequence:
    palette=(root/'input/original.sms').read_bytes()[0x17e13:0x17e25]
    declarations='#include "source_intro_actors.h"\n#include "source_intro_fire.h"\n'+        'static const u8 sequence_bank5[16384]={[0x3e13]='+','.join(map(str,palette))+',[0x3e57]='+','.join(map(str,colors))+'};\n'
    dispatch='''static u8 sequence_callback(SourceClock *clock,SourceIrqContext *context,void *user)
{
 const SourceIntroActorData *data=user;
 u16 target=context->full_ram[0x1cec]|((u16)context->full_ram[0x1ced]<<8);
 if(target==0xf37) return source_intro_fire_callback(clock,context,(void *)(data->bank5+0x3e13));
 if(target==0x1055) return source_intro_actors_second(clock,context,user);
 if(target==0x104a) return source_intro_actors_third(clock,context,user);
 if(target==0xf36) return source_clock_plain(clock,10,1,source_irq_interrupt,context) && source_clock_checkpoint(clock,source_irq_interrupt,context);
 return 0;
}
'''
    wrapper=wrapper.replace('#include "source_intro_reveal.h"','#include "source_intro_reveal.h"\n'+declarations+dispatch)
    begin=wrapper.index('SourceIntroRevealPass reveal=');end=wrapper.index(';',begin)
    wrapper=wrapper[:begin]+'SourceIntroRevealSequenceOutput sequence;SourceIntroActorData sequence_data={low,sequence_bank5}'+wrapper[end:]
    wrapper=wrapper.replace('source_intro_reveal_pass(&clock,&context,&reveal,reveal_sink,0)',
        'source_intro_reveal_sequence(&clock,&context,ram[1184],sequence_callback,&sequence_data,reveal_sink,0,&sequence)')
    wrapper=wrapper.replace('reveal.address','sequence.last.address').replace('reveal.step','sequence.last.step').replace('reveal.value','sequence.last.value')
    wrapper=wrapper.replace('result.polls=reveal_event_position;',
        'ram[1184]=sequence.mask;result.below=sequence.passes;result.above=sequence.writes;result.counter=sequence.mask;result.skip=sequence.skip;\n result.polls=reveal_event_position;')
    wrapper=wrapper.replace('irq_status_values[8]','irq_status_values[64]')
    (out/'wrapper.c').write_text(wrapper)
if a.irq_status:
    assert wrapper.count('context.full_ram=actor_full_ram;')==1
    wrapper=wrapper.replace('context.full_ram=actor_full_ram;',
        'irq_status_count=ram[1184];irq_status_position=0;\n'
        ' for(u16 n=0;n<8;n++) irq_status_values[n]=ram[1185+n];\n context.full_ram=actor_full_ram;')
    (out/'wrapper.c').write_text(wrapper)
if a.sequence:
    wrapper=wrapper.replace('irq_status_count=ram[1184]','irq_status_count=ram[1192]')
    wrapper=wrapper.replace('n<8;n++) irq_status_values[n]=ram[1185+n]', 'n<64;n++) irq_status_values[n]=ram[1193+n]')
    (out/'wrapper.c').write_text(wrapper)
if a.skip:
    wrapper=wrapper.replace('irq_status_values[64];','irq_status_values[64],irq_joy_values[64];')
    wrapper=wrapper.replace('irq->ram[0x1b]=irq_status_values[irq_status_position++];',
        'irq->input.joy=irq_joy_values[irq_status_position];\n irq->ram[0x1b]=irq_status_values[irq_status_position++];')
    wrapper=wrapper.replace('context.full_ram=actor_full_ram;',
        'for(u16 n=0;n<64;n++) irq_joy_values[n]=ram[1257+n];\n context.full_ram=actor_full_ram;')
    wrapper=wrapper.replace('result.skip=sequence.skip;', 'result.skip=sequence.skip;result.error=sequence.skip;')
    (out/'wrapper.c').write_text(wrapper)
if a.transfer:
    wrapper=wrapper.replace('#include "source_intro_reveal.h"','#include "source_intro_video.h"')
    wrapper=wrapper.replace('SourceIntroRevealSequenceOutput sequence;', 'SourceIntroMapOutput sequence;')
    wrapper=wrapper.replace('source_intro_reveal_sequence(&clock,&context,ram[1184],sequence_callback,&sequence_data,reveal_sink,0,&sequence)',
        'source_intro_map_transfer(&clock,&context,sequence_callback,&sequence_data,reveal_sink,0,0,&sequence)')
    wrapper=wrapper.replace('ram[411]=sequence.last.address;ram[412]=sequence.last.address>>8;ram[413]=sequence.last.step;ram[414]=sequence.last.step>>8;ram[415]=sequence.last.value;', '')
    wrapper=wrapper.replace('ram[1184]=sequence.mask;result.below=sequence.passes;result.above=sequence.writes;result.counter=sequence.mask;result.skip=sequence.skip;',
        'result.below=sequence.writes;result.skip=sequence.skip;')
    wrapper=wrapper.replace('irq_status_count=ram[1192]', 'irq_status_count=ram[1960]')
    wrapper=wrapper.replace('irq_status_values[n]=ram[1193+n]', 'irq_status_values[n]=ram[1961+n]')
    wrapper=wrapper.replace('context.full_ram=actor_full_ram;',
        'for(u16 n=0;n<768;n++) actor_full_ram[0x1600+n]=ram[1192+n];\n context.full_ram=actor_full_ram;')
    wrapper=wrapper.replace('if(reveal_event_position!=reveal_event_count) return 0;',
        'for(u16 n=0;n<768;n++) ram[1192+n]=actor_full_ram[0x1600+n];\n if(reveal_event_position!=reveal_event_count) return 0;')
    (out/'wrapper.c').write_text(wrapper)
if a.prepare:
    wrapper=wrapper.replace('source_intro_map_transfer(&clock,&context,sequence_callback,&sequence_data,reveal_sink,0,0,&sequence)',
        'source_intro_map_prepare(&clock,&context,ram[1184]|((u16)ram[1185]<<8),sequence_callback,&sequence_data,reveal_sink,0,0,&sequence)')
    wrapper=wrapper.replace('out[0]=clock.raster;',
        'ram[1184]=sequence.palette_end;ram[1185]=sequence.palette_end>>8;\n out[0]=clock.raster;')
    (out/'wrapper.c').write_text(wrapper)
if a.map:
    wrapper=wrapper.replace('#include "source_intro_video.h"','#include "source_intro_map.h"')
    wrapper=wrapper.replace('SourceIntroMapOutput sequence;', 'SourceIntroMapDecode sequence;')
    bank7=(root/'input/original.sms').read_bytes()[0x1c000:0x20000]
    wrapper=wrapper.replace('static u8 actor_full_ram[8192];','static u8 actor_full_ram[8192];\nstatic const u8 map_bank7[16384]={'+','.join(map(str,bank7))+'};')
    call=('source_intro_map_decode(&clock,&context,ram[408]==6?bank:ram[408]==7?map_bank7:0,ram[1184]|((u16)ram[1185]<<8),ram[1186]|((u16)ram[1187]<<8),&sequence)' if a.map=='decode' else
          'source_intro_map_place(&clock,&context,ram[1184]|((u16)ram[1185]<<8),ram[1186]|((u16)ram[1187]<<8),ram[1189],ram[1188],&sequence)')
    wrapper=wrapper.replace('source_intro_map_transfer(&clock,&context,sequence_callback,&sequence_data,reveal_sink,0,0,&sequence)',call)
    wrapper=wrapper.replace('result.below=sequence.writes;result.skip=sequence.skip;',
        'result.below=sequence.decoded_bytes;result.above=sequence.scratch_bytes;')
    wrapper=wrapper.replace('irq_status_count=ram[1960]', 'irq_status_count=ram[5032]')
    wrapper=wrapper.replace('irq_status_values[n]=ram[1961+n]', 'irq_status_values[n]=ram[5033+n]')
    wrapper=wrapper.replace('context.full_ram=actor_full_ram;',
        'for(u16 n=0;n<1280;n++) actor_full_ram[0x1100+n]=ram[1960+n];\n'
        ' for(u16 n=0;n<1792;n++) actor_full_ram[0x900+n]=ram[3240+n];\n context.full_ram=actor_full_ram;')
    wrapper=wrapper.replace('out[0]=clock.raster;',
        'for(u16 n=0;n<1280;n++) ram[1960+n]=actor_full_ram[0x1100+n];\n'
        ' for(u16 n=0;n<1792;n++) ram[3240+n]=actor_full_ram[0x900+n];\n'
        ' ram[1184]=sequence.source_end;ram[1185]=sequence.source_end>>8;\n'
        ' ram[1186]=sequence.destination_end;ram[1187]=sequence.destination_end>>8;\n'
        +(' ram[1188]=2;ram[1189]=0;\n' if a.map=='decode' else ' ram[1188]=0;\n')+
        ' out[0]=clock.raster;')
    wrapper=wrapper.replace('context.input.lines=phase[3];',
        '(void)sequence_data;(void)sequence_callback;(void)reveal_sink;(void)map_bank7;\n context.input.lines=phase[3];')
    (out/'wrapper.c').write_text(wrapper)
if a.clear:
    wrapper=wrapper.replace('SourceIntroMapOutput sequence;', 'SourceIntroMapOutput sequence={0};')
    wrapper=wrapper.replace('source_intro_map_transfer(&clock,&context,sequence_callback,&sequence_data,reveal_sink,0,0,&sequence)',
        'source_intro_plane_clear(&clock,&context,reveal_sink,0,0,&sequence.writes)')
    wrapper=wrapper.replace('context.input.lines=phase[3];','(void)sequence_data;(void)sequence_callback;\n context.input.lines=phase[3];')
    (out/'wrapper.c').write_text(wrapper)
if a.scene:
    wrapper=wrapper.replace('#include "source_intro_map.h"','#include "source_intro_scene.h"\nstatic u8 scene_vram[16384];')
    wrapper=wrapper.replace('SourceIntroMapDecode sequence;', 'SourceIntroSceneOutput sequence;')
    old='source_intro_map_decode(&clock,&context,ram[408]==6?bank:ram[408]==7?map_bank7:0,ram[1184]|((u16)ram[1185]<<8),ram[1186]|((u16)ram[1187]<<8),&sequence)'
    assert old in wrapper
    wrapper=wrapper.replace(old,'source_intro_scene_load(&clock,&context,ram[1184]|((u16)ram[1185]<<8),ram[1186]|((u16)ram[1187]<<8),scene_vram,sequence_callback,&sequence_data,reveal_sink,0,&sequence)')
    wrapper=wrapper.replace('irq_status_count=ram[5032]', 'irq_status_count=ram[15016]')
    wrapper=wrapper.replace('irq_status_values[n]=ram[5033+n]', 'irq_status_values[n]=ram[15017+n]')
    wrapper=wrapper.replace('context.full_ram=actor_full_ram;',
        '__builtin_memset(scene_vram,0,sizeof(scene_vram));\n'
        ' for(u16 n=0;n<9216;n++) scene_vram[n]=ram[5032+n];\n'
        ' for(u16 n=0;n<768;n++) scene_vram[0x3800+n]=ram[14248+n];\n context.full_ram=actor_full_ram;')
    wrapper=wrapper.replace('sequence.source_end','sequence.hl').replace('sequence.destination_end','sequence.de')
    wrapper=wrapper.replace('ram[1188]=2;ram[1189]=0;', 'ram[1188]=sequence.bc;ram[1189]=sequence.bc>>8;')
    wrapper=wrapper.replace('result.above=sequence.scratch_bytes;', 'result.above=sequence.pattern_end;')
    wrapper=wrapper.replace('out[0]=clock.raster;',
        'for(u16 n=0;n<9216;n++) ram[5032+n]=scene_vram[n];\n'
        ' for(u16 n=0;n<768;n++) ram[14248+n]=scene_vram[0x3800+n];\n out[0]=clock.raster;')
    (out/'wrapper.c').write_text(wrapper)
sdk = root.parents[1] / 'work/sgdk'
env = dict(os.environ); env['PATH'] = 'C:/msys64/ucrt64/bin;' + env['PATH']
modules = ['source_intro_wait', 'source_wait_restore', *MODULES]
if a.fire: modules.insert(0,'source_intro_fire')
if a.actors: modules.insert(0,'source_intro_reveal' if a.reveal else 'source_intro_actors')
if a.sequence:modules[:0]=['source_intro_actors','source_intro_fire']
if a.transfer:modules.insert(0,'source_intro_video')
if a.map:modules.insert(0,'source_intro_map')
if a.scene:modules[:0]=['source_intro_scene','source_pattern_clock']
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
if a.sequence:build_folder='v319-intro-reveal_sequence-callback-observer01'
if a.skip:build_folder='v319-intro-reveal_skip-callback-observer01'
if a.transfer:build_folder='v319-intro-intro_transfer-callback-observer01'
if a.prepare:build_folder='v319-intro-intro_prepare-callback-observer01'
if a.map:build_folder='v319-intro-map_'+a.map+'-callback-observer01'
if a.clear:build_folder='v319-intro-plane_clear-callback-observer01'
if a.scene:build_folder='v319-intro-scene_load-callback-observer01'
build_folder=build_folder[:-2]+f'{a.observer_revision:02}'
build = json.loads((root / 'validation' / build_folder / 'report.json').read_bytes())
core = Path(build['core']); assert sha(core.read_bytes()) == build['core_sha256']
dll = c.CDLL(str(core))
dll.gaw_poll_reset.restype = None
dll.gaw_poll_size.restype = dll.gaw_poll_errors.restype = dll.gaw_poll_stride.restype = c.c_uint
dll.gaw_poll_data.restype = c.POINTER(c.c_uint8)
snapshot=15488 if a.scene else 5504 if a.map else 2432 if a.transfer else 1664 if a.sequence else 1656 if a.actors else 888 if a.fire else 808
stride=snapshot*2+8
if a.irq_status:stride+=264 if a.sequence else 40
if a.skip:stride+=256
if a.reveal:stride+=(8452 if a.scene else 6912 if a.clear else 770 if a.transfer else 55296 if a.sequence else 6912)*8
assert dll.gaw_poll_stride() == stride
image = (root / 'input/original.sms').read_bytes()
low = (c.c_uint8 * 32768).from_buffer_copy(image[:32768]); bank = (c.c_uint8 * 16384).from_buffer_copy(image[0x18000:0x1c000])
archive = root / 'analysis/v319-psg-write-spacing'
manifest = json.loads((archive / 'manifest.json').read_bytes())
results = []
for region in ('ntsc', 'pal'):
    if a.skip:
        from capture_v319_intro_skip import capture,reuse
        if a.capture_work:
            prior_work=(root/'validation'/a.capture_work).resolve();assert prior_work.is_relative_to(root/'validation')
            raw,psg,capture_report=reuse(root,prior_work/region,out/region)
        else:raw,psg,capture_report=capture(root,dll,core,out/region,region)
        count=len(raw)//stride
        (out/region/'source-poll-records.bin').write_bytes(raw)
        (out/region/'psg-states.bin').write_bytes(psg)
    else:
        dll.gaw_poll_reset(); psg = bytearray()
        with contextlib.redirect_stdout(io.StringIO()):
            run(root / 'input/original.sms', 14000, out / region, set(), [], skip_intro=False, core=core,
                psg_observer=lambda frame, values: psg.extend(struct.pack('<8H', *values)),
                core_options={'genesis_plus_gx_region_detect': 'pal' if region == 'pal' else 'auto'})
        assert dll.gaw_poll_errors() == 0
        count = dll.gaw_poll_size(); assert 0 < count < (512 if a.transfer else 128 if a.reveal else 4096)
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
            assert pc == (0xe50 if a.scene else 0xe2b if a.clear else (0xbd3 if a.map=='decode' else 0x7357) if a.map else 0xea5 if a.prepare else 0xefa if a.transfer else 0xe79 if a.sequence else 0xe8b if a.reveal else (0xf51 if a.actors=='second' else 0xf54) if a.init else 0xf09 if a.profile == 'callback' else 0xf1e)
            if a.init:phase=tuple(phase[i] if i!=4 else struct.unpack_from('<I',record,snapshot*2)[0] for i in range(12))
            assert final_pc in ((0xe75,) if a.scene else (struct.unpack_from('<I',record,snapshot*2+4)[0],) if a.transfer else (0xea4,0xd0b) if a.skip else (0xea4,) if a.sequence else (0xea0,) if a.reveal else (struct.unpack_from('<I', record, snapshot*2+4)[0],))
        before=first[72:408]+(first[808:snapshot] if a.fire or a.actors else b'')
        expected_state=last[72:408]+(last[808:snapshot] if a.fire or a.actors else b'')
        if a.irq_status:
            statuses=struct.unpack_from('<65I' if a.sequence else '<9I',record,snapshot*2+8)
            assert (0 if a.init or a.map else 1)<=statuses[0]<=(64 if a.sequence else 8) and all(v<=255 for v in statuses[1:])
            before+=bytes(statuses);expected_state+=bytes(statuses)
            if a.skip:
                joys=struct.unpack_from('<64I',record,snapshot*2+268);assert all(v<=63 for v in joys)
                before+=bytes(joys);expected_state+=bytes(joys)
        state = (c.c_uint8 * len(before)).from_buffer_copy(before); audio = (c.c_uint8 * 400).from_buffer_copy(first[408:808])
        if a.reveal:
            event_count=struct.unpack_from('<I',record,snapshot*2)[0];assert (0<=event_count<=55296 and event_count%6912==0) if a.skip else event_count==(8452 if a.scene else 0 if a.map else 6912 if a.clear else 770 if a.transfer else 55296 if a.sequence else 6912)
            event_values=struct.unpack_from('<'+str(event_count*2)+'I',record,snapshot*2+(524 if a.skip else 268 if a.sequence else 44))
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
        if a.skip:
            assert result[16]==int(final_pc==0xd0b)
            cases[-1]['source_return_pc']=final_pc
    (out / region / 'native-cases.json').write_text(json.dumps(cases, separators=(',', ':')) + '\n')
    row = dict(region=region, source_cases=count, source_poll_reads=sum(case['expected'][12] for case in cases),
        cases_crossing_irq=sum(bool(case['expected'][6]) for case in cases),
        observer_exposed_psg_exact_frames=len(psg)//16, source_records_sha256=sha(raw),
        maximum_polls=max(case['expected'][12] for case in cases))
    if a.reveal:
        row['source_io_events']=row.pop('source_poll_reads');row['maximum_io_events']=row.pop('maximum_polls')
    if a.skip:
        row['skip_vectors']=sum(c['source_return_pc']==0xd0b for c in cases);row['input_scenarios']=len(capture_report['scenarios'])
    if a.init:row['source_template_addresses']=sorted({case['phase'][4] for case in cases})
    results.append(row); print(json.dumps(row), flush=True)
report = dict(passed=True, diagnostic_only=True, profile=a.profile, fire=a.fire, actors=a.actors,
    irq_status=a.irq_status,init=a.init,reveal=a.reveal,sequence=a.sequence,skip=a.skip,transfer=a.transfer,prepare=a.prepare,map=a.map,clear=a.clear,scene=a.scene,production_rom_changed=False, cases=results,
    core_sha256=sha(core.read_bytes()), source_sha256=sha(image),
    native_assets=({'source_intro_pattern_plans_generated.h':sha((root/'megadrive/src/source_intro_pattern_plans_generated.h').read_bytes())} if a.scene else {}),
    native_sources={name: sha((root / 'megadrive/src' / (name + '.c')).read_bytes()) for name in modules},
    verified=['Original natural entry/return wall time, raster, '+('initial HL, ' if a.init else 'polls, ')+
              'R, IFF/EI/pending,336 IRQ RAM and400 reader bytes.'+
              (' Fire palette/counter/mapper/callback snapshots also compared.' if a.fire else '')+
              (' Actor768-byte records and palette/counter/mapper/callback snapshots also compared.' if a.actors else ''),
              'Normal controller skip scenarios, independently replayed source PSG states identical; repeated prefix dedup omits only absolute diagnostic time origins.' if a.skip else 'Both regions,14000 no-input cold source frames per region; observer PSG state unchanged.'],
    limits=['Host native semantic helper; compiled68000 timing and physical MD publication not checked here.',
            ('Normal controller skip inputs and complete prefixes; per-IRQ VDP status and actual observed joy input are diagnostic external inputs.' if a.skip else
             'Original E2B plane clear entry/return and every semantic OUT completion; natural no-input only. VDP status external diagnostic input.' if a.clear else
             'Intro map BD3/BFE decode or7357 placement entry/return; natural no-input only, original buffer contract filtered at entry. VDP status external diagnostic input.' if a.map else
             'Complete EA5 setup and EFA transfer with both callbacks, palette clearing and four bank6 header colors. Natural no-input only; VDP status external diagnostic input.' if a.prepare else
             'Complete EFA map transfer, F1E then F09 callbacks. Natural no-input only; VDP status external diagnostic input.' if a.transfer else
             'Composed E79..EA2 sequence, live F1E callbacks plus eight reveal passes. Natural no-input cases only; VDP status is external diagnostic input.' if a.sequence else
             'Reveal pass E8B..E9D only; every OUT instruction completion compared. Live VDP status remains external diagnostic input.' if a.reveal else
             'Natural actor initialization only; these vectors do not exercise IRQ crossing.' if a.init else
             'Selected original actor callback profile; captured VDP status is explicit diagnostic IRQ input where enabled.' if a.actors else
             'Selected profile with original F37 fire callback; no actors or skip inputs.' if a.fire else
             'Selected entry profile only; callback/window profiles use original F36 empty callback, not fire/actors.'),
            'No production clock integration, full-game or PCM certification.'])
(out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
