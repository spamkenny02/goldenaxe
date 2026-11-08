"""Isolated reveal experiment: source IRQ work replaces the fixed 3600T reserve."""
import hashlib
import json
import shutil
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(root / 'gaw-megadrive.bin') == 'd3ea2a83ea24ed8a0d3c9857f9fbe70d000a4f73358452c1887f40e78966c56e'
work = root / 'validation/v319-reveal-irq-budget01'
assert not work.exists(), work
project = work / 'project'
shutil.copytree(root / 'megadrive', project, ignore=shutil.ignore_patterns('out', '__pycache__'))
path = project / 'src/intro.inc'
s = path.read_text()
marker = 'static void intro_reveal(void)'
assert s.count(marker) == 1
helper = '''/* First interrupted slice follows the requested full IRQ. Later slices
 * follow audio-only IRQs. This private experiment uses the existing source
 * IRQ model and current reader work, rather than a recorded-frame override.
 * Global source/native entry phase remains a separate validation gate. */
static u32 intro_reveal_irq_cost(u16 full)
{
    u8 state[336]={0};SourceIrqInput entry;SourceIrqOutput output;
    SourceClockWork reader;
    state[0x2e]=full;state[0x35]=0xdd;state[0x30]=full?1:0;
    entry.raster=193UL*3420+72UL*15;entry.lines=SYS_isPAL()?313:262;
    entry.tile_count=0;entry.joy=0;entry.reset_mask=16;
    entry.compensation=SYS_isPAL()?0:128;
    reader.tstates=sound_source_work.tstates;reader.fetches=sound_source_work.fetches;
    if(!source_irq(state,&entry,&reader,&output))
    { sound_unhandled_command=0x503;intro_abort=1;return 0; }
    return output.whole.tstates;
}

'''
s = s.replace(marker, helper + marker, 1)
old = '''            u16 count=chunk?((SYS_isPAL()?71364UL:59736UL)-3600)/100:
                ((192-112)*228)/100;
            count&=0xfffc;'''
new = '''            u32 period=SYS_isPAL()?71364UL:59736UL;
            u32 irq=chunk?intro_reveal_irq_cost(chunk==1):0;
            u16 count;
            if(intro_abort || irq>=period)
            { sound_unhandled_command=0x503;intro_abort=1;return; }
            count=chunk?(period-irq)/100:((192-112)*228)/100;
            count&=0xfffc;
            if(!count) { sound_unhandled_command=0x503;intro_abort=1;return; }'''
assert s.count(old) == 1
path.write_text(s.replace(old, new, 1))
index = {p.relative_to(project).as_posix(): sha(p) for p in project.rglob('*') if p.is_file()}
(work / 'source-index.json').write_text(json.dumps(index, indent=2) + '\n')
(work / 'hypothesis.json').write_text(json.dumps(dict(
    diagnostic_only=True, promoted=False, public_rom_unchanged=True,
    changed_file='src/intro.inc', baseline_sha256=sha(root / 'gaw-megadrive.bin'),
    hypothesis='A fixed per-slice IRQ reserve omits full/audio-only distinction and current reader work.',
    limitations='Initial source/native phase is unchanged; no claim of improvement before SMS comparison.',
    ram_writes=0, sram_imports=0), indent=2) + '\n')
print('Private reveal IRQ-budget candidate prepared; public sources and ROM unchanged.')
