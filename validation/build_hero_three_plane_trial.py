"""Remove tiny memcpy calls from the hero three-plane expansion."""
import difflib
import os
from pathlib import Path
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[1]
old=ROOT/'validation/v318-dungeon-pattern-ram01'
work=ROOT/'validation/v318-hero-three-plane02'
assert not work.exists()
shutil.copytree(old/'src',work/'src')
source=(work/'src/main.c').read_text()
changes=[
('            memcpy(sms_vram+0x3e00+n*4,source,3);source+=3;', '            sms_vram[0x3e00+n*4]=source[0];sms_vram[0x3e01+n*4]=source[1];sms_vram[0x3e02+n*4]=source[2];source+=3;')]
after=source
for before,replacement in changes:
    assert after.count(before)==1
    after=after.replace(before,replacement)
(work/'src/main.c').write_text(after)
(work/'source.patch').write_text(''.join(difflib.unified_diff(source.splitlines(True),after.splitlines(True),fromfile='c0044/main.c',tofile='hero-three-plane/main.c')))
for name in ['timing.py','physical_sprites.py','ntsc_prefix.py']:
    shutil.copyfile(old/name,work/name)
sdk=(ROOT.parents[1]/'work/sgdk').resolve()
env=dict(os.environ)
env['PATH']=str(sdk/'bin')+';D:/jdk-25.0.1/bin;'+env['PATH']
path=sdk.as_posix();unix='/'+path[0].lower()+path[2:]
result=subprocess.run([str(sdk/'bin/sh.exe'),'-c','export PATH="$2/bin:$PATH"; make -f "$1/makefile.gen" "GDK=$1" -j2','build',path,unix],cwd=work,env=env,capture_output=True,text=True)
(work/'build.log').write_text(result.stdout+result.stderr)
assert result.returncode==0,result.stderr[-3000:]
# The release header declares a 2 MiB cartridge; SGDK's default alignment
# alone can leave a shorter file. Pad before computing its final checksum.
cartridge=work/'out/release/rom.bin';image=bytearray(cartridge.read_bytes())
assert 512<=len(image)<=2097152
assert int.from_bytes(image[0x1a4:0x1a8],'big')==2097151
image.extend(bytes([255])*(2097152-len(image)));cartridge.write_bytes(image)
import sys
subprocess.run([sys.executable,str(ROOT/'tools/finalize_md_rom.py'),str(cartridge)],check=True)
print('Built',cartridge,flush=True)
