"""Combine the c0042 sentinel with the c0044 dungeon RAM atlas."""
import difflib
import os
from pathlib import Path
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[1]
old=ROOT/'validation/v318-dungeon-pattern-ram01'
work=ROOT/'validation/v318-dungeon-pattern-sentinel01'
assert not work.exists()
shutil.copytree(old/'src',work/'src')
source=(work/'src/main.c').read_text()
changes=[
('u32 clone[8],cached_key[8];u16 cached_tile[8];u8 cached_valid=0;', 'u32 clone[8],cached_key[8]={0};u16 cached_tile[8];'),
('if((cached_valid&(1<<cache_slot)) && cached_key[cache_slot]==key)', 'if(cached_key[cache_slot]==key)'),
('cached_valid|=1<<cache_slot;cached_key[cache_slot]=key;', 'cached_key[cache_slot]=key;')]
after=source
for before,replacement in changes:
    assert after.count(before)==1
    after=after.replace(before,replacement)
(work/'src/main.c').write_text(after)
(work/'source.patch').write_text(''.join(difflib.unified_diff(source.splitlines(True),after.splitlines(True),fromfile='c0044/main.c',tofile='atlas-sentinel/main.c')))
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
