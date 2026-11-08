"""Preserve the source reveal's 182-row first slice and its rotating-mask tail."""
import hashlib
import json
import shutil
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(root / 'gaw-megadrive.bin') == 'd3ea2a83ea24ed8a0d3c9857f9fbe70d000a4f73358452c1887f40e78966c56e'
work = root / 'validation/v319-reveal-row-tail01'
assert not work.exists(), work
project = work / 'project'
shutil.copytree(root / 'megadrive', project, ignore=shutil.ignore_patterns('out', '__pycache__'))
path = project / 'src/intro.inc'
s = path.read_text()
old = '            count&=0xfffc;'
assert s.count(old) == 1
s = s.replace(old, '''            /* 80 scanlines * 228T / 100T = 182 complete writes.
             * Keep the existing later IRQ budgets; do not drop the first
             * slice's two-row tail to fit the four-row fast path. */
            if(chunk) count&=0xfffc;''', 1)
old = '''                u16 groups=count>>2;
                while(groups--)
                {
                    sms[0]=masks[0];sms[4]=masks[1];sms[8]=masks[2];sms[12]=masks[3];
                    md[0]=(md[0]&0x77777777UL)|planes[0];
                    md[1]=(md[1]&0x77777777UL)|planes[1];
                    md[2]=(md[2]&0x77777777UL)|planes[2];
                    md[3]=(md[3]&0x77777777UL)|planes[3];
                    sms+=16;md+=4;
                }
                row+=count;'''
new = '''                u16 groups=count>>2,phase=row&3,tail=count&3;
                u8 m0=masks[phase],m1=masks[(phase+1)&3];
                u8 m2=masks[(phase+2)&3],m3=masks[(phase+3)&3];
                u32 p0=planes[phase],p1=planes[(phase+1)&3];
                u32 p2=planes[(phase+2)&3],p3=planes[(phase+3)&3];
                while(groups--)
                {
                    sms[0]=m0;sms[4]=m1;sms[8]=m2;sms[12]=m3;
                    md[0]=(md[0]&0x77777777UL)|p0;
                    md[1]=(md[1]&0x77777777UL)|p1;
                    md[2]=(md[2]&0x77777777UL)|p2;
                    md[3]=(md[3]&0x77777777UL)|p3;
                    sms+=16;md+=4;
                }
                row+=count-tail;
                while(tail--)
                {
                    sms[0]=masks[row&3];
                    md[0]=(md[0]&0x77777777UL)|planes[row&3];
                    sms+=4;md++;row++;
                }'''
assert s.count(old) == 1
path.write_text(s.replace(old, new, 1))
index = {p.relative_to(project).as_posix(): sha(p) for p in project.rglob('*') if p.is_file()}
(work / 'source-index.json').write_text(json.dumps(index, indent=2) + '\n')
(work / 'hypothesis.json').write_text(json.dumps(dict(
    diagnostic_only=True, promoted=False, public_rom_unchanged=True,
    changed_file='src/intro.inc', baseline_sha256=sha(root / 'gaw-megadrive.bin'),
    source_first_slice_rows=80 * 228 // 100, prior_rounded_rows=180,
    ram_writes=0, sram_imports=0,
    scope='First-slice remainder and mask-phase continuation only. Later slice budgets unchanged. '
          'No improvement claim before complete PAL/NTSC boot comparison.'), indent=2) + '\n')
print('Private first-slice row-tail fix prepared; later IRQ budgets and public ROM unchanged.')
