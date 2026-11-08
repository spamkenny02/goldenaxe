"""Recover a terminal diagnostic LTO temporary-path failure by serial native linking of the same objects."""
import argparse
import json
import os
import subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--project',type=Path,required=True);a=p.parse_args()
project=a.project.resolve();assert project.is_relative_to(root/'validation')
log=project/'build.log';raw=log.read_bytes();text=raw.decode('utf-16' if raw.startswith(b'\xff\xfe') else 'utf-8')
assert 'Cannot create temporary file' in text and 'lto-wrapper failed' in text
assert not(project/'out/release/rom.bin').exists() and (project/'out/release/cmd_').is_file()
saved=project/'build-lto-path-failure.log';assert not saved.exists();saved.write_bytes(log.read_bytes())
sdk=root.parents[1]/'work/sgdk';env=dict(os.environ);env['PATH']=str(sdk/'bin')+';'+env['PATH']
command=[str(sdk/'bin/gcc.exe'),'-m68000','-B'+str(sdk/'bin'),'-n','-T',str(sdk/'md.ld'),
 '-nostdlib','out/release/sega.o','@out/release/cmd_',str(sdk/'lib/libmd.a'),str(sdk/'lib/libgcc.a'),
 '-o','out/release/rom.out','-Wl,--gc-sections','-flto=1','-ffat-lto-objects']
built=subprocess.run(command,cwd=project,env=env,capture_output=True,text=True)
(project/'serial-link.log').write_text(built.stdout+built.stderr)
assert built.returncode==0,built.stderr
(project/'serial-link-recipe.json').write_text(json.dumps(dict(command=command,scope='Diagnostic kernel only. '
 'Existing completed object files, unchanged source/oracle, serial LTO avoids recursive MSYS make temporary-path conversion.'),indent=2)+'\n')
subprocess.run(['powershell','-NoProfile','-ExecutionPolicy','Bypass','-File',str(root/'tools/build_private_candidate.ps1'),
 '-Project',str(project),'-PaddingByte','255'],cwd=root,env=env,check=True)
