"""Extend the row-tail experiment with actual audio-only IRQ work between slices."""
import hashlib
import json
import shutil
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
work = root / 'validation/v319-reveal-audio-rows01'
assert not work.exists(), work
parent = root / 'validation/v319-reveal-row-tail01/project'
project = work / 'project'
shutil.copytree(parent, project, ignore=shutil.ignore_patterns('out', '__pycache__', 'build.log', 'packaging-build.json'))
path = project / 'src/intro.inc'
s = path.read_text()
old = '''            u16 count=chunk?((SYS_isPAL()?71364UL:59736UL)-3600)/100:
                ((192-112)*228)/100;
            /* 80 scanlines * 228T / 100T = 182 complete writes.
             * Keep the existing later IRQ budgets; do not drop the first
             * slice's two-row tail to fit the four-row fast path. */
            if(chunk) count&=0xfffc;'''
new = '''            u32 available=(192-112)*228UL;
            u16 count;
            if(chunk)
            {
                /* F1E calls F09/B95 before waiting for V112. Its full
                 * IRQ is already before the first bitmap slice. Later
                 * transfer slices cross audio-only IRQs: source0140 is
                 * 524T plus the8000 reader, or12T more with C030 active. */
                u32 period=SYS_isPAL()?71364UL:59736UL;
                u32 irq=524UL+sound_source_work.tstates+(intro_timer?12:0);
                if(irq>=period) { sound_unhandled_command=0x503;intro_abort=1;return; }
                available=period-irq;
            }
            count=available/100;
            if(!count) { sound_unhandled_command=0x503;intro_abort=1;return; }'''
assert s.count(old) == 1
path.write_text(s.replace(old, new, 1))
(work / 'source-index.json').write_text(json.dumps({p.relative_to(project).as_posix(): sha(p)
                                                  for p in project.rglob('*') if p.is_file()}, indent=2) + '\n')
(work / 'hypothesis.json').write_text(json.dumps(dict(
    diagnostic_only=True, promoted=False, public_rom_unchanged=True,
    source_first_slice_rows=182, later_irq='audio-only, current reader work, C030 branch',
    baseline_sha256=sha(root / 'gaw-megadrive.bin'), ram_writes=0, sram_imports=0,
    scope='Row tails and source audio-only transfer work. Initial loader phase and sub-row IRQ phase '
          'remain unmodified; no source-pixel improvement claim before complete boot comparisons.'), indent=2) + '\n')
print('Private audio-only reveal budget prepared; full IRQ is not charged twice.')
