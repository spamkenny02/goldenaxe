"""Replay audited native candidate palace milestones on the padded c0047 image."""
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

parser=argparse.ArgumentParser();parser.add_argument('part',choices=['entry','giant','inner','guardian','final'])
args=parser.parse_args();part=args.part;region='auto';suffix='palace-'+part
receipt=json.loads((ROOT/f'analysis/cold_palace_{part}_c0046_report.json').read_bytes())
assert receipt['passed'] and receipt['candidate']=='c0046' and receipt['md_sha256']=='9e747d38e0c6fb2d69b7c1aa8c2b296a61e8b6af41171d14e543ed9a6cb49cf5'
project=ROOT/'validation/c0046-campaign01/isolated/project'
ref=Path(receipt['current_campaign_trace'])
trace=project/'validation'/ref.parent.name/ref.name
cap=json.loads((trace/'capture.json').read_bytes());assist,writes=recording(trace,cap)
assert cap['rom_sha256']==receipt['md_sha256'] and cap['sram_input'] is None and cap['frames']==receipt['campaign_frames']
proof=trace.with_name(trace.name+'-assisted-fixed-replay-'+str(cap['frames']))
pr=json.loads((proof/'replay_report.json').read_bytes());assert pr['passed'] and pr['whole_ram_bytes']==65536 and pr['final_png_exact']
controls=json.loads((trace/'controls.json').read_bytes());end=cap['frames']
presses=list(map(tuple,cap['presses']))
for i,row in enumerate(controls):
    stop=controls[i+1]['frame']-1 if i+1<len(controls) else end
    presses += [(row['frame'],min(stop,end),b) for b in row['buttons'] if row['frame']<=end]
rom=ROOT/'versions/candidates/c0047-d3ea2a83/gaw-megadrive-c0047.bin'
work=ROOT/f'validation/c0047-{suffix}-{region}01';assert not work.exists()
with contextlib.redirect_stdout(io.StringIO()):
    run(rom,end,work,{end},presses,skip_intro=False,ram_writes=FrameWrites(writes),core_options=cap['core_options'])
for stem,ext in [('ram','bin'),('frame','png')]:
    name=f'{stem}_{end:05d}.{ext}'
    assert (work/name).read_bytes()==(trace/name).read_bytes()==(proof/name).read_bytes(),(region,name)
result=dict(passed=True,candidate='c0047',region=region,rom_sha256=sha(rom.read_bytes()),
    reference_rom_sha256=cap['rom_sha256'],frames=end,whole_ram_bytes_exact=65536,final_png_exact=True,
    initial_sram=False,primary_state_imports=0,approach_writes=len(writes),
    palace_milestone=part,
    scope='Exact c0046 recorded controller inputs on correctly padded c0047, with the same approach-only guard writes. No complete-campaign or SMS fidelity claim.')
paths=[Path(__file__).resolve(),ROOT/f'analysis/cold_palace_{part}_c0046_report.json',trace/'capture.json',trace/'controls.json',trace/'assistance.json',proof/'replay_report.json']
paths += [p for p in work.iterdir() if p.is_file()]
paths += [trace/f'ram_{end:05d}.bin',trace/f'frame_{end:05d}.png']
archive=ROOT/f'analysis/c0047-{suffix}-{region}'
result['archive_manifest']=(archive/'manifest.json').relative_to(ROOT).as_posix()
freeze(ROOT,archive,paths,result,[work])
(ROOT/f'analysis/c0047_{suffix.replace("-","_")}_{region}_report.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2),flush=True)
