"""Private source-dated native PSG replay. Relative spacing experiment, no absolute-phase claim."""
import argparse
import json
import shutil
from pathlib import Path

root = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument('--stack-workspace', action='store_true')
p.add_argument('--compact-workspace', action='store_true')
p.add_argument('--planned', action='store_true')
p.add_argument('--long-bursts', action='store_true')
a = p.parse_args()
assert not (a.stack_workspace and a.compact_workspace)
assert not a.planned or a.compact_workspace
assert not a.long_bursts or (a.compact_workspace and not a.planned)
work = root / ('validation/v319-buffered-psg05' if a.long_bursts else 'validation/v319-buffered-psg04' if a.planned else 'validation/v319-buffered-psg03' if a.compact_workspace else 'validation/v319-buffered-psg02' if a.stack_workspace else 'validation/v319-buffered-psg01')
assert not work.exists()
project = work / 'project'
shutil.copytree(root / 'megadrive', project, ignore=shutil.ignore_patterns('out', '__pycache__'))
path = project / 'src/sound.inc'
text = path.read_text()
text = text.replace('#include "source_audio_fast.h"', '#include "source_audio_fast.h"\n#include "source_audio_timed.h"\n#include "source_md_psg_replay.h"')
old = '''static void sound_reader_emit(void *context,const u8 *writes,u16 count)
{
    u16 n;(void)context;for(n=0;n<count;n++) PSG_write(writes[n]);
}'''
new = '''/* Diagnostic whole-reader staging. No source data/frame overrides.
 * Reject overflow; never silently truncate or play a partially captured IRQ.
 * Relative source dates are retained; first emission is deliberately anchored
 * after preparation, so this does NOT establish absolute SMS IRQ phase. */
static SourceAudioTimedSequenceOutput sound_timed_workspace;
static SourcePsgEvent sound_timed_events[64];
static volatile u16 sound_timed_count,sound_timed_error,sound_timed_max_count;
static volatile u32 sound_timed_irqs;
static void sound_reader_emit(void *context,const u8 *writes,const u32 *times,u16 count)
{
    u16 n;(void)context;
    if(sound_timed_error) return;
    if(count>64-sound_timed_count) {sound_timed_error=1;return;}
    for(n=0;n<count;n++)
    {
        SourcePsgEvent *event=sound_timed_events+sound_timed_count++;
        event->due=times[n]*15;event->value=writes[n];
    }
}
static void sound_timed_replay(void)
{
    SourceMdPsgReplayClock clock;u16 n,hv;u32 base,first;
    if(sound_timed_error || !sound_timed_count) return;
    if(sound_timed_count>sound_timed_max_count) sound_timed_max_count=sound_timed_count;
    first=sound_timed_events[0].due;
    for(n=0;n<sound_timed_count;n++) sound_timed_events[n].due-=first;
    hv=*(volatile u16 *)0xc00008;
    if(source_md_psg_replay_seed(&clock,SYS_isPAL()?313:262,hv,0))
    {sound_timed_error=2;return;}
    /* Enough lead for this short rebasing pass and consumer entry. The
     * consumer polls continuously, handling raw-V discontinuities itself. */
    base=clock.master+12000;
    for(n=0;n<sound_timed_count;n++) sound_timed_events[n].due+=base;
    if(source_md_psg_replay(&clock,sound_timed_events,sound_timed_count)) sound_timed_error=3;
    sound_timed_irqs++;
}'''
assert text.count(old) == 1
text = text.replace(old, new)
old = '''    accepted=source_audio_reader_stream_fast_work(sound_ram,sound_low_rom,0x8000,intro_bank6,
                                        &sound_source_de,&work,&sound_reader_status,
                                        sound_reader_emit,0,(SourceAudioSequenceOutput *)(scratch+0xd00));'''
new = '''    sound_timed_count=0;
    accepted=source_audio_reader_stream_fast_timed_work(sound_ram,sound_low_rom,0x8000,intro_bank6,
                                        &sound_source_de,&work,&sound_reader_status,
                                        sound_reader_emit,0,&sound_timed_workspace);
    if(accepted) sound_timed_replay();'''
assert text.count(old) == 1
text = text.replace(old, new)
if a.stack_workspace:
    text = text.replace('static SourceAudioTimedSequenceOutput sound_timed_workspace;\n', '')
    text = text.replace('    u8 accepted;SourceClockWork work;',
                        '    u8 accepted;SourceClockWork work;SourceAudioTimedSequenceOutput sound_timed_workspace;')
if a.compact_workspace:
    text = text.replace('static SourceAudioTimedSequenceOutput sound_timed_workspace;\n', '')
    text = text.replace('sound_reader_emit,0,&sound_timed_workspace);',
                        'sound_reader_emit,0,(SourceAudioTimedSequenceOutput *)(scratch+0xd00));')
    header = project / 'src/source_audio_timed.h'
    body = header.read_text()
    body = body.replace('writes[512];u32 write_tstates[512]', 'writes[32];u32 write_tstates[32]')
    header.write_text(body)
    fast = project / 'src/source_audio_fast_timed.c'
    fast.write_text('#define GAW_AUDIO_WRITE_LIMIT 32\n' + fast.read_text())
    for filename in ('source_audio_sequence.c', 'source_audio_tone.c'):
        module = project / 'src' / filename
        body = module.read_text()
        body = body.replace('#define EMIT(v,t)', '#ifndef GAW_AUDIO_WRITE_LIMIT\n#define GAW_AUDIO_WRITE_LIMIT 512\n#endif\n#define EMIT(v,t)')
        body = body.replace('output->count>=512', 'output->count>=GAW_AUDIO_WRITE_LIMIT')
        module.write_text(body)
    # Preserve the existing default-buffer behaviour, but leave space for the
    # 3072-byte default-font transient before main shrinks the DMA buffer.
    system = project / 'src/gaw_sgdk_sys.c'
    body = system.read_text()
    assert body.count('    DMA_init();') == 1
    system.write_text(body.replace('    DMA_init();', '    DMA_initEx(32,65535,0);'))
if a.planned:
    text = text.replace('#include "source_md_psg_replay.h"', '#include "source_md_psg_replay.h"\n#include "source_md_psg_plan.h"')
    text = text.replace('    SourceMdPsgReplayClock clock;u16 n,hv;u32 base,first;',
        '    SourceMdPsgReplayClock clock;u16 n,hv,used;u32 base,first;\n'
        '    SourceMdPsgBlock *blocks=(SourceMdPsgBlock *)(scratch+0xd00);')
    text = text.replace('    hv=*(volatile u16 *)0xc00008;',
        '    if(source_md_psg_plan(sound_timed_events,sound_timed_count,blocks,24,&used))\n'
        '    {sound_timed_error=4;return;}\n'
        '    hv=*(volatile u16 *)0xc00008;')
    text = text.replace('    for(n=0;n<sound_timed_count;n++) sound_timed_events[n].due+=base;\n'
        '    if(source_md_psg_replay(&clock,sound_timed_events,sound_timed_count)) sound_timed_error=3;',
        '    for(n=0;n<used;n++) blocks[n].due+=base;\n'
        '    if(source_md_psg_replay_planned(&clock,blocks,used)) sound_timed_error=3;')
if a.long_bursts:
    assembly = project / 'src/source_md_psg_replay.s'
    body = assembly.read_text()
    old = '''.Lreplay_try_quad:
    cmpi.w #4,%d7'''
    new = '''.Lreplay_try_quad:
    cmpi.l #315,%d0
    bne .Lreplay_poll
    cmpi.w #10,%d7
    bcs .Lreplay_try_quad_only
    move.l %a0,%a4
    move.l %d5,%d0
    moveq #8,%d1
.Lreplay_check_ten:
    addq.l #6,%a4
    addi.l #315,%d0
    cmp.l (%a4),%d0
    dbne %d1,.Lreplay_check_ten
    bne .Lreplay_try_quad_reset
    lea .Lreplay_ten(%pc),%a4
    bra .Lreplay_poll
.Lreplay_try_quad_reset:
    lea .Lreplay_single(%pc),%a4
.Lreplay_try_quad_only:
    move.l 6(%a0),%d0
    sub.l %d5,%d0
    cmpi.w #4,%d7'''
    assert body.count(old) == 1
    body = body.replace(old, new)
    old = '.Lreplay_quad:\n'
    new = '''.Lreplay_ten:
    .set .Lraw_ten_i,0
    .rept 9
    move.b 4+.Lraw_ten_i*6(%a0),(%a1)
    .rept 7
    nop
    .endr
    .set .Lraw_ten_i,.Lraw_ten_i+1
    .endr
    move.b 58(%a0),(%a1)
    lea 60(%a0),%a0
    subi.w #10,%d7
    bne .Lreplay_next
    bra .Lreplay_done
.Lreplay_quad:
'''
    assert body.count(old) == 1
    assembly.write_text(body.replace(old, new))
path.write_text(text)
(work / 'hypothesis.json').write_text(json.dumps(dict(diagnostic_only=True, promoted=False,
    source_dates=True, native_68000_emission=True, staging_capacity=64, first_write_lead_ticks=12000,
    absolute_source_phase_validated=False, expected_failure_is_explicit=True, stack_workspace=a.stack_workspace,
    compact_workspace=a.compact_workspace, per_channel_capacity=32 if a.compact_workspace else 512,
    planned_bursts=a.planned,
    raw_long_bursts=a.long_bursts,
    scope='Measure source relative spacing after native whole-reader preparation. '
          'Neither a production scheduler nor a global audio phase correction.'), indent=2) + '\n')
print('Private buffered native PSG experiment prepared.')
