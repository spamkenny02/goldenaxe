"""Private foreground preparation, IRQ consumption and exact native fallback experiment."""
import argparse
import json
import shutil
from pathlib import Path

root = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument('--count-crossed-irq', action='store_true')
p.add_argument('--immediate', action='store_true')
a = p.parse_args()
assert not a.immediate or a.count_crossed_irq
work = root / ('validation/v319-audio-prefetch03' if a.immediate else 'validation/v319-audio-prefetch02' if a.count_crossed_irq else 'validation/v319-audio-prefetch01')
assert not work.exists()
project = work / 'project'
shutil.copytree(root / 'megadrive', project, ignore=shutil.ignore_patterns('out', '__pycache__'))
src = project / 'src'
header = src / 'source_audio_timed.h'
header.write_text(header.read_text().replace('writes[512];u32 write_tstates[512]', 'writes[32];u32 write_tstates[32]'))
fast = src / 'source_audio_fast_timed.c'
fast.write_text('#define GAW_AUDIO_WRITE_LIMIT 32\n' + fast.read_text())
for filename in ('source_audio_sequence.c', 'source_audio_tone.c'):
    path = src / filename
    text = path.read_text().replace('#define EMIT(v,t)',
        '#ifndef GAW_AUDIO_WRITE_LIMIT\n#define GAW_AUDIO_WRITE_LIMIT 512\n#endif\n#define EMIT(v,t)')
    path.write_text(text.replace('output->count>=512', 'output->count>=GAW_AUDIO_WRITE_LIMIT'))
system = src / 'gaw_sgdk_sys.c'
text = system.read_text()
assert text.count('    DMA_init();') == 1
system.write_text(text.replace('    DMA_init();', '    DMA_initEx(32,65535,0);'))
sound = src / 'sound.inc'
text = sound.read_text().replace('#include "source_audio_fast.h"',
    '#include "source_audio_fast.h"\n#include "source_audio_timed.h"\n#include "source_md_psg_replay.h"')
needle = 'static u8 sound_read(u16 address)'
declarations = '''/* Foreground owns speculative state until valid is atomically published.
 * IRQ fallback never touches this storage or the foreground stack workspace.
 * No live reader state, request, PSG or game state changes during preparation. */
static u8 sound_prepared_state[400] __attribute__((aligned(2)));
static SourcePsgEvent sound_prepared_events[32];
static SourceClockWork sound_prepared_work;
static SourceAudioReaderStatus sound_prepared_status;
static u32 sound_prepared_epoch;
static u16 sound_prepared_de,sound_prepared_request,sound_prepared_delay,sound_prepared_effect;
static u8 sound_prepared_params[5];
static volatile u16 sound_prepared_valid,sound_prepared_count,sound_prepared_overflow,sound_prepared_clock_error;
static volatile u32 sound_prepared_attempts,sound_prepared_hits,sound_prepared_misses,sound_prepared_races;
static void sound_prepare(void);
'''
assert text.count(needle) == 1
text = text.replace(needle, declarations + needle)
text = text.replace('    SourceClockWork work;source_audio_stop(sound_ram,&work);sound_mute();',
                    '    SourceClockWork work;sound_prepared_valid=0;source_audio_stop(sound_ram,&work);sound_mute();')
needle = 'static void sound_tick(void)'
helpers = '''static u8 sound_prepared_inputs_match(void)
{
    return sound_request==sound_prepared_request && sound_request_delay==sound_prepared_delay &&
        sound_effect_request==sound_prepared_effect && sound_ram[3]==sound_prepared_params[0] &&
        sound_ram[4]==sound_prepared_params[1] && sound_ram[11]==sound_prepared_params[2] &&
        sound_ram[12]==sound_prepared_params[3] && sound_ram[13]==sound_prepared_params[4];
}
static void sound_prepare_sink(void *unused,const u8 *writes,const u32 *times,u16 count)
{
    u16 n;(void)unused;
    if(sound_prepared_overflow) return;
    if(count>32-sound_prepared_count) {sound_prepared_overflow=1;return;}
    for(n=0;n<count;n++)
    {
        SourcePsgEvent *event=sound_prepared_events+sound_prepared_count++;
        event->due=times[n]*15;event->value=writes[n];
    }
}
static void sound_prepare(void)
{
    SourceAudioTimedSequenceOutput channel;u16 n,attempt;u8 accepted;
    for(attempt=0;attempt<2;attempt++)
    {
        if(sound_prepared_valid && sound_prepared_epoch==vtimer && sound_prepared_inputs_match()) return;
        sound_prepared_valid=0;sound_prepared_epoch=vtimer;sound_prepared_attempts++;
        sound_prepared_request=sound_request;sound_prepared_delay=sound_request_delay;
        sound_prepared_effect=sound_effect_request;sound_prepared_de=sound_source_de;
        sound_prepared_params[0]=sound_ram[3];sound_prepared_params[1]=sound_ram[4];
        sound_prepared_params[2]=sound_ram[11];sound_prepared_params[3]=sound_ram[12];sound_prepared_params[4]=sound_ram[13];
        memcpy(sound_prepared_state,sound_ram,400);
        if(!sound_prepared_delay && sound_prepared_request) sound_prepared_state[6]=sound_prepared_request;
        if(sound_prepared_effect) sound_prepared_state[8]=sound_prepared_effect;
        sound_prepared_count=0;sound_prepared_overflow=0;
        accepted=source_audio_reader_stream_fast_timed_work(sound_prepared_state,sound_low_rom,0x8000,intro_bank6,
            &sound_prepared_de,&sound_prepared_work,&sound_prepared_status,sound_prepare_sink,0,&channel);
        if(!accepted || sound_prepared_overflow) return; /* Full-size IRQ reader remains authoritative. */
        for(n=0;n<sound_prepared_count;n++)
            if(n && sound_prepared_events[n].due<sound_prepared_events[n-1].due) return;
        SYS_disableInts();
        if(sound_prepared_epoch==vtimer && sound_prepared_inputs_match())
        { __asm__ volatile ("":::"memory");sound_prepared_valid=1;SYS_enableInts();return; }
        SYS_enableInts();sound_prepared_races++;
    }
}
static void sound_prepared_emit(void)
{
    SourceMdPsgReplayClock clock;u16 n,hv;u32 first,base;
    if(!sound_prepared_count) return;
    first=sound_prepared_events[0].due;
    for(n=0;n<sound_prepared_count;n++) sound_prepared_events[n].due-=first;
    hv=*(volatile u16 *)0xc00008;
    if(source_md_psg_replay_seed(&clock,SYS_isPAL()?313:262,hv,0))
    {sound_prepared_clock_error=1;return;}
    base=clock.master+12000;
    for(n=0;n<sound_prepared_count;n++) sound_prepared_events[n].due+=base;
    if(source_md_psg_replay(&clock,sound_prepared_events,sound_prepared_count)) sound_prepared_clock_error=2;
}
'''
assert text.count(needle) == 1
if a.immediate:
    first = helpers.index('static void sound_prepared_emit(void)')
    helpers = helpers[:first] + '''static void sound_prepared_emit(void)
{
    u16 n;
    for(n=0;n<sound_prepared_count;n++) PSG_write(sound_prepared_events[n].value);
}
'''
text = text.replace(needle, helpers + needle)
text = text.replace('    u8 accepted;SourceClockWork work;',
    '    u8 accepted,use_prepared;SourceClockWork work;\n'
    '    use_prepared=sound_prepared_valid && sound_prepared_epoch+1==vtimer && sound_prepared_inputs_match();\n'
    '    sound_prepared_valid=0;')
old = '''    accepted=source_audio_reader_stream_fast_work(sound_ram,sound_low_rom,0x8000,intro_bank6,
                                        &sound_source_de,&work,&sound_reader_status,
                                        sound_reader_emit,0,(SourceAudioSequenceOutput *)(scratch+0xd00));'''
new = '''    if(use_prepared)
    {
        memcpy(sound_ram,sound_prepared_state,400);sound_source_de=sound_prepared_de;
        work=sound_prepared_work;sound_reader_status=sound_prepared_status;accepted=1;
        sound_prepared_emit();sound_prepared_hits++;
    }
    else
    {
        sound_prepared_misses++;
        accepted=source_audio_reader_stream_fast_work(sound_ram,sound_low_rom,0x8000,intro_bank6,
                                        &sound_source_de,&work,&sound_reader_status,
                                        sound_reader_emit,0,(SourceAudioSequenceOutput *)(scratch+0xd00));
    }'''
assert text.count(old) == 1
sound.write_text(text.replace(old, new))
main = src / 'main.c'
text = main.read_text()
needle = 'static void wait_frame(void)\n{\n    SYS_doVBlankProcess();'
replacement = 'static void sound_prepare(void);\nstatic void wait_frame(void)\n{\n    sound_prepare();\n    SYS_doVBlankProcess();'
if a.count_crossed_irq:
    replacement = '''static void sound_prepare(void);
static void wait_frame(void)
{
    u32 requested_frame=vtimer;
    sound_prepare();
    /* B95 requested its IRQ before foreground audio preparation. A real
     * IRQ crossing satisfies that request; do not force a second one. */
    if(vtimer==requested_frame) SYS_doVBlankProcess();
    else SYS_doVBlankProcessEx(IMMEDIATELY);'''
assert text.count(needle) == 1
text = text.replace(needle, replacement)
needle = '    world_video_pending=1;\n    while(world_video_pending)'
assert text.count(needle) == 1
text = text.replace(needle, '    sound_prepare();\n' + needle)
main.write_text(text)
(work / 'hypothesis.json').write_text(json.dumps(dict(diagnostic_only=True, promoted=False,
    preparation='Foreground before frame waits; never writes live reader state or PSG.',
    publication='Atomic valid flag only if frame and all foreground reader parameters/requests unchanged.',
    fallback='Full-size existing IRQ reader on stale cache, late effect/music, speculative rejection or overflow.',
    producer_capacity=32, timed_channel_capacity=32, max_speculative_attempts=2,
    native_68000_only=True, absolute_phase_validated=False,
    count_crossed_irq=a.count_crossed_irq,
    immediate_emission_control=a.immediate,
    limits='Prepared IRQ replay still waits physically; aim is to replace IRQ calculation with earlier idle-time '
          'preparation, not certify complete asynchronous output.'), indent=2) + '\n')
print('Private speculative foreground audio preparation built from current source; fallback preserved.')
