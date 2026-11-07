"""Create an isolated test root using read-only hard links to published inputs."""
import json
import os
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
lab=ROOT/'validation/c0046-campaign01'
project=lab/'isolated/project'
assert not lab.exists()
(project/'tools').mkdir(parents=True)
paths=subprocess.check_output(['rg','--files','tools'],cwd=ROOT,text=True).splitlines()
for name in paths:
    source=ROOT/name;dest=project/name
    dest.parent.mkdir(parents=True,exist_ok=True)
    os.link(source,dest)
release=project/'megadrive/out/release';release.mkdir(parents=True)
published=ROOT/'versions/candidates/c0046-9e747d38'
os.link(published/'gaw-megadrive-c0046.bin',project/'gaw-megadrive.bin')
os.link(published/'symbol.txt',release/'symbol.txt')
(project/'validation').mkdir()
(lab/'work').mkdir()
subprocess.run(['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(ROOT/'validation/setup_c0046_links.ps1'),
                '-Lab',str(lab),'-Root',str(ROOT)],check=True)
(lab/'setup.json').write_text(json.dumps(dict(project=str(project),
    rom='versions/candidates/c0046-9e747d38/gaw-megadrive-c0046.bin',
    tools_hard_linked_read_only=True,tool_count=len(paths),
    warning='Do not edit hard-linked tools, ROM or symbols in this lab. Reports and validation outputs are separate.'),indent=2)+'\n')
print(project,flush=True)
