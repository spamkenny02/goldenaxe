"""Replay each exact c0046 first-dungeon recording on the padded c0047 image."""
import argparse
import contextlib
import io
import json
from pathlib import Path
import sys
sys.path.insert(0,'tools')
from run_core import ROOT,FrameWrites,run
from assisted_prefix import recording
from archive_lossless_evidence import freeze,sha

parser=argparse.ArgumentParser();parser.add_argument('region',choices=['auto','pal'])
parser.add_argument('--dungeon',type=int,choices=[1,2],default=1)
args=parser.parse_args();region=args.region;dungeon=args.dungeon
assert dungeon==1 or region=='auto','The c0046 second-dungeon recording is NTSC only'
root=ROOT/'validation/c0046-campaign01/isolated/project'
name='md-'+region+'-c46-d1-exit02' if dungeon==1 else 'md-auto-c0046-d2-exit01'
trace=root/'validation/natural-dungeon-combat'/name
cap=json.loads((trace/'capture.json').read_bytes());assist,writes=recording(trace,cap)
controls=json.loads((trace/'controls.json').read_bytes());end=cap['frames']
presses=list(map(tuple,cap['presses']))
for i,row in enumerate(controls):
    stop=controls[i+1]['frame']-1 if i+1<len(controls) else end
    presses += [(row['frame'],min(stop,end),b) for b in row['buttons'] if row['frame']<=end]
rom=ROOT/'versions/candidates/c0047-d3ea2a83/gaw-megadrive-c0047.bin'
work=ROOT/f'validation/c0047-d{dungeon}-{region}01';assert not work.exists()
with contextlib.redirect_stdout(io.StringIO()):
    run(rom,end,work,{end},presses,skip_intro=False,ram_writes=FrameWrites(writes),core_options=cap['core_options'])
for stem,ext in [('ram','bin'),('frame','png')]:
    name=f'{stem}_{end:05d}.{ext}'
    assert (work/name).read_bytes()==(trace/name).read_bytes(),(region,name)
result=dict(passed=True,candidate='c0047',region=region,rom_sha256=sha(rom.read_bytes()),
    reference_rom_sha256=cap['rom_sha256'],frames=end,whole_ram_bytes_exact=65536,final_png_exact=True,
    initial_sram=False,primary_state_imports=0,approach_writes=len(writes),
    dungeon=dungeon,
    scope='Exact c0046 recorded crystal/exterior inputs on correctly padded c0047, with the same approach-only guard writes. No complete-campaign or SMS fidelity claim.')
paths=[Path(__file__).resolve(),trace/'capture.json',trace/'controls.json',trace/'assistance.json']
paths += [p for p in work.iterdir() if p.is_file()]
paths += [trace/f'ram_{end:05d}.bin',trace/f'frame_{end:05d}.png']
archive=ROOT/f'analysis/c0047-d{dungeon}-{region}'
result['archive_manifest']=(archive/'manifest.json').relative_to(ROOT).as_posix()
freeze(ROOT,archive,paths,result,[work])
(ROOT/f'analysis/c0047_d{dungeon}_{region}_report.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2),flush=True)
