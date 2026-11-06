"""Build native word loads for the source little-endian actor coordinates."""
import difflib
import os
from pathlib import Path
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[1]
old=ROOT/'validation/v318-dungeon-pattern-ram01'
work=ROOT/'validation/v318-actor-coordinates01'
assert not work.exists()
shutil.copytree(old/'src',work/'src')
path=work/'src/actors.c';source=path.read_text()
before='''                u16 y=(entity[0x10]|((u16)entity[0x11]<<8))+
                      (entity[0x14]|((u16)entity[0x15]<<8));
                u16 x=(entity[0x12]|((u16)entity[0x13]<<8))+
                      (entity[0x16]|((u16)entity[0x17]<<8));
                if(!counter) { x&=0xff00;y&=0xff00; }
                entity[4]=counter;entity[0x10]=y;entity[0x11]=y>>8;
                entity[0x12]=x;entity[0x13]=x>>8;'''
after='''                /* These actor records are even-aligned. memcpy avoids
                 * aliasing a byte record as u16 while allowing native word
                 * loads; byte swaps retain the source Z80 layout. */
                u16 y,x,dy,dx;
                __builtin_memcpy(&y,entity+0x10,2);
                __builtin_memcpy(&x,entity+0x12,2);
                __builtin_memcpy(&dy,entity+0x14,2);
                __builtin_memcpy(&dx,entity+0x16,2);
                y=__builtin_bswap16(y)+__builtin_bswap16(dy);
                x=__builtin_bswap16(x)+__builtin_bswap16(dx);
                if(!counter) { x&=0xff00;y&=0xff00; }
                y=__builtin_bswap16(y);x=__builtin_bswap16(x);
                entity[4]=counter;
                __builtin_memcpy(entity+0x10,&y,2);
                __builtin_memcpy(entity+0x12,&x,2);'''
assert source.count(before)==1
path.write_text(source.replace(before,after))
(work/'source.patch').write_text(''.join(difflib.unified_diff(source.splitlines(True),source.replace(before,after).splitlines(True),fromfile='c0044/actors.c',tofile='actor-coordinates/actors.c')))
for name in ['timing.py','ntsc_prefix.py']:
    shutil.copyfile(old/name,work/name)
sdk=(ROOT.parents[1]/'work/sgdk').resolve();env=dict(os.environ)
env['PATH']=str(sdk/'bin')+';D:/jdk-25.0.1/bin;'+env['PATH']
path=sdk.as_posix();unix='/'+path[0].lower()+path[2:]
result=subprocess.run([str(sdk/'bin/sh.exe'),'-c','export PATH="$2/bin:$PATH"; make -f "$1/makefile.gen" "GDK=$1" -j2','build',path,unix],cwd=work,env=env,capture_output=True,text=True)
(work/'build.log').write_text(result.stdout+result.stderr)
assert result.returncode==0,result.stderr[-3000:]
print('Built',work/'out/release/rom.bin',flush=True)
