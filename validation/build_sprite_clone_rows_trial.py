"""Build an isolated row-copy optimization on top of c0044."""
import difflib
import os
from pathlib import Path
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[1]
old=ROOT/'validation/v318-dungeon-pattern-ram01'
work=ROOT/'validation/v318-clone-rows01'
assert not work.exists()
shutil.copytree(old/'src',work/'src')
source=(work/'src/main.c').read_text()
before='''            u16 bit=1;
            for(row=0;row<8;row++,bit+=bit)
            {
                /* A68000 long read consumes the two mirrored VDP data
                 * words in order. Build queued clones at their final RAM
                 * address instead of copying another32-byte buffer. */
                pixels[row]=queued?queued[row]:*data;
                if(!(mask&bit)) pixels[row]=0;
            }'''
after='''            /* Select RAM or VDP once for all eight rows. VDP reads must
             * still consume suppressed rows to preserve its address. */
            if(queued)
            {
'''+''.join(f'                pixels[{i}]=(mask&{1<<i})?queued[{i}]:0;\n' for i in range(8))+'''            }
            else
            {
'''+''.join(f'                pixels[{i}]=*data;if(!(mask&{1<<i})) pixels[{i}]=0;\n' for i in range(8))+'''            }'''
assert source.count(before)==1
(work/'src/main.c').write_text(source.replace(before,after))
(work/'source.patch').write_text(''.join(difflib.unified_diff(source.splitlines(True),source.replace(before,after).splitlines(True),fromfile='c0044/main.c',tofile='clone-rows/main.c')))
for name in ['timing.py','physical_sprites.py','ntsc_prefix.py']:
    shutil.copyfile(old/name,work/name)
sdk=(ROOT.parents[1]/'work/sgdk').resolve()
env=dict(os.environ)
env['PATH']=str(sdk/'bin')+';D:/jdk-25.0.1/bin;'+env['PATH']
path=sdk.as_posix();unix='/'+path[0].lower()+path[2:]
result=subprocess.run([str(sdk/'bin/sh.exe'),'-c','export PATH="$2/bin:$PATH"; make -f "$1/makefile.gen" "GDK=$1" -j2','build',path,unix],cwd=work,env=env,capture_output=True,text=True)
(work/'build.log').write_text(result.stdout+result.stderr)
assert result.returncode==0,result.stderr[-3000:]
print('Built',work/'out/release/rom.bin',flush=True)
