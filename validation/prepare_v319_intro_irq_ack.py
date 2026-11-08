"""Private explicit full-IRQ request/acknowledgement for intro callbacks."""
import argparse
import json
import shutil
from pathlib import Path

root = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument('--prefetch', action='store_true')
p.add_argument('--foreground-callback', action='store_true')
p.add_argument('--lean', action='store_true')
a = p.parse_args()
assert not a.lean or a.foreground_callback
number = (6 if a.prefetch else 5) if a.lean else (4 if a.prefetch else 3) if a.foreground_callback else (2 if a.prefetch else 1)
work = root / f'validation/v319-intro-irq-ack{number:02}'
assert not work.exists()
project = work / 'project'
if a.prefetch:
    source = root / 'validation/v319-audio-prefetch02/project'
else:
    source = root / 'megadrive'
shutil.copytree(source, project, ignore=shutil.ignore_patterns('out', '__pycache__', 'build.log', 'packaging-build.json'))
intro = project / 'src/intro.inc'
text = intro.read_text()
assert text.count('static u16 intro_logic_clock;') == 1
text = text.replace('static u16 intro_logic_clock;', '''static volatile u16 intro_logic_clock;
/* One source B95 request: clock-only for title waits, F32 for intro waits.
 * Video upload precedes the callback, which prepares the next IRQ's SAT. */
static volatile u16 intro_full_irq_request,intro_full_irq_error;
static volatile u32 intro_full_irq_requests,intro_full_irq_acks;
static void intro_request_full_irq(u16 kind)
{
    if(intro_full_irq_request) {intro_full_irq_error=1;return;}
    intro_full_irq_requests++;
    __asm__ volatile ("":::"memory");intro_full_irq_request=kind;
}
static void intro_wait_full_irq(void)
{
    if(intro_full_irq_request)
        do {wait_frame();} while(intro_full_irq_request);
    else {SYS_doVBlankProcessEx(IMMEDIATELY);input=JOY_readJoypad(JOY_1);}
}''')
old = '''    u32 before=vtimer;
    /* With display disabled, SGDK may process the current blank again.
     * Source B95 always waits for a new IRQ before returning. */
    do { wait_frame(); } while(vtimer==before);
    intro_logic_clock=(intro_logic_clock+1)&255;'''
new = '''    intro_request_full_irq(1);
    intro_wait_full_irq();'''
assert text.count(old) == 1
text = text.replace(old, new)
old = '''        if(intro_scene) intro_palette_pending=1;
        wait_frame();
        if(input&(BUTTON_A|BUTTON_B|BUTTON_C|BUTTON_START)) intro_abort=1;
        intro_logic_clock=(intro_logic_clock+1)&255;
        intro_tick();'''
new = '''        if(intro_scene) intro_palette_pending=1;
        intro_request_full_irq(2);intro_wait_full_irq();
        if(input&(BUTTON_A|BUTTON_B|BUTTON_C|BUTTON_START)) intro_abort=1;'''
assert text.count(old) == 1
text = text.replace(old, new)
old = '''    if(vtimer==requested_frame) wait_frame();
    else { SYS_doVBlankProcessEx(IMMEDIATELY);input=JOY_readJoypad(JOY_1); }
    if(input&(BUTTON_A|BUTTON_B|BUTTON_C|BUTTON_START)) intro_abort=1;
    intro_logic_clock=(intro_logic_clock+1)&255;intro_tick();'''
new = '''    (void)requested_frame;
    intro_wait_full_irq();
    if(input&(BUTTON_A|BUTTON_B|BUTTON_C|BUTTON_START)) intro_abort=1;'''
assert text.count(old) == 1
text = text.replace(old, new)
old = '''        u8 rotated=(u8)((mask<<2)|(mask>>6));
        if(intro_scene) intro_palette_pending=1;'''
new = '''        u8 rotated=(u8)((mask<<2)|(mask>>6));
        if(intro_scene) intro_palette_pending=1;
        intro_request_full_irq(2);'''
assert text.count(old) == 1
text = text.replace(old, new)
intro.write_text(text)
main = project / 'src/main.c'
text = main.read_text()
old = '''    sound_tick();
    /* During overview construction'''
new = '''    sound_tick();
    if(intro_full_irq_request)
    {
        u16 kind=intro_full_irq_request;
        intro_logic_clock=(intro_logic_clock+1)&255;
        if(kind==2) intro_tick();
        intro_full_irq_acks++;
        __asm__ volatile ("":::"memory");intro_full_irq_request=0;
    }
    /* During overview construction'''
assert text.count(old) == 1
text = text.replace(old, new)
if a.foreground_callback:
    text = text.replace('        if(kind==2) intro_tick();', '        if(kind==2) intro_irq_callback_ready=1;')
    body = intro.read_text()
    body = body.replace('static volatile u16 intro_full_irq_request,intro_full_irq_error;',
        'static volatile u16 intro_full_irq_request,intro_full_irq_error,intro_irq_callback_ready;\n'
        'static void intro_tick(void);')
    old = '    else {SYS_doVBlankProcessEx(IMMEDIATELY);input=JOY_readJoypad(JOY_1);}\n}'
    new = '''    else {SYS_doVBlankProcessEx(IMMEDIATELY);input=JOY_readJoypad(JOY_1);}
    if(intro_irq_callback_ready)
    {intro_irq_callback_ready=0;intro_tick();}
}'''
    assert body.count(old) == 1
    intro.write_text(body.replace(old, new))
if a.lean:
    text = text.replace('''        u16 kind=intro_full_irq_request;
        intro_logic_clock=(intro_logic_clock+1)&255;
        if(kind==2) intro_irq_callback_ready=1;
        intro_full_irq_acks++;''', '''        intro_logic_clock=(intro_logic_clock+1)&255;''')
    body = intro.read_text()
    start = body.index('static volatile u16 intro_full_irq_request,')
    end = body.index('static volatile u16 intro_tick_work;', start)
    # This generated block ends immediately before the original next field.
    body = body[:start] + '''static volatile u16 intro_full_irq_request;
static void intro_tick(void);
static inline void intro_request_full_irq(u16 kind)
{
    (void)kind;
    __asm__ volatile ("":::"memory");intro_full_irq_request=1;
}
static void intro_wait_full_irq(u16 callback)
{
    if(intro_full_irq_request)
        do {wait_frame();} while(intro_full_irq_request);
    else {SYS_doVBlankProcessEx(IMMEDIATELY);input=JOY_readJoypad(JOY_1);}
    if(callback) intro_tick();
}
''' + body[end:]
    # Exactly three call sites: title clock-only, ordinary F09 and reveal F09.
    assert body.count('intro_wait_full_irq();') == 3
    body = body.replace('intro_wait_full_irq();', 'intro_wait_full_irq(0);', 1)
    body = body.replace('intro_wait_full_irq();', 'intro_wait_full_irq(1);')
    intro.write_text(body)
main.write_text(text)
(work / 'hypothesis.json').write_text(json.dumps(dict(diagnostic_only=True, promoted=False,
    prefetch=a.prefetch, native_68000=True, frame_overrides=False, ram_writes=0, sram_imports=0,
    foreground_callback=a.foreground_callback,
    lean=a.lean,
    request='Explicit clock-only or clock+F32 request before the wait/first reveal slice.',
    acknowledgement='Native IRQ after video and audio; prepares SAT/palette for following IRQ; foreground awaits acknowledgement.',
    limits='Source F32 executes in foreground after source IRQ return. IRQ-tail variants relocate its '
           'work; foreground variants acknowledge and publish readiness in IRQ, then execute in foreground. '
           'Not an instruction-phase equivalence claim.'), indent=2) + '\n')
print('Private explicit intro full-IRQ request/ack experiment prepared; prefetch', a.prefetch)
