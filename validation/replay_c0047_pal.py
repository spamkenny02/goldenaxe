"""Replay a passed PAL candidate milestone on the published padded c0047 ROM."""
import argparse,contextlib,io,json,sys
from pathlib import Path
sys.path.insert(0,'tools')
from run_core import ROOT,FrameWrites,run
from assisted_prefix import recording
from archive_lossless_evidence import freeze,sha
p=argparse.ArgumentParser();p.add_argument('--report',type=Path,required=True);p.add_argument('--milestone',choices=['after-d1','d2','d3','earth','d4','fire-sword','d5','d6','d7-preparation','d7-midboss','d7','d8-midboss','d8','d9-midboss','d9','ending'],required=True);a=p.parse_args()
report=a.report.resolve();assert report.is_relative_to(ROOT/'analysis')
r=json.loads(report.read_bytes());assert r['passed'] and r['candidate']=='c0046' and r['region']=='pal'
ref_digest=r.get('rom_sha256',r.get('md_sha256'));assert ref_digest=='9e747d38e0c6fb2d69b7c1aa8c2b296a61e8b6af41171d14e543ed9a6cb49cf5'
trace=(ROOT/r.get('current_campaign_trace',r['stages'][-1]['trace'])).resolve()
assert trace.is_relative_to(ROOT/'validation/c0046-campaign01/isolated/project/validation')
cap=json.loads((trace/'capture.json').read_bytes());assist,writes=recording(trace,cap)
assert cap['rom_sha256']==ref_digest and cap['sram_input'] is None and cap['core_options']['genesis_plus_gx_region_detect']=='pal'
end=cap['frames'];proof=trace.with_name(trace.name+f'-assisted-fixed-replay-{end}');pr=json.loads((proof/'replay_report.json').read_bytes())
assert pr['passed'] and pr['whole_ram_bytes']==65536 and pr['final_png_exact'] and not pr['feedback_reads'] and pr['rom_sha256']==ref_digest
controls=json.loads((trace/'controls.json').read_bytes());presses=[tuple(v) for v in cap['presses']]
for i,row in enumerate(controls):
    stop=controls[i+1]['frame']-1 if i+1<len(controls) else end
    presses.extend((row['frame'],min(stop,end),b) for b in row['buttons'] if row['frame']<=end)
rom=ROOT/'versions/candidates/c0047-d3ea2a83/gaw-megadrive-c0047.bin';work=ROOT/f'validation/c0047-pal-{a.milestone}01';assert not work.exists()
assert sha(rom.read_bytes())=='d3ea2a83ea24ed8a0d3c9857f9fbe70d000a4f73358452c1887f40e78966c56e'
with contextlib.redirect_stdout(io.StringIO()):run(rom,end,work,{end},presses,skip_intro=False,ram_writes=FrameWrites(writes),core_options=cap['core_options'])
for stem,ext in [('ram','bin'),('frame','png')]:
    name=f'{stem}_{end:05d}.{ext}';assert (work/name).read_bytes()==(trace/name).read_bytes()==(proof/name).read_bytes(),name
out=ROOT/f'analysis/c0047-pal-{a.milestone}'
result=dict(passed=True,candidate='c0047',region='pal',milestone=a.milestone,rom_sha256=sha(rom.read_bytes()),reference_rom_sha256=ref_digest,
            frames=end,whole_ram_bytes_exact=65536,final_png_exact=True,initial_sram=False,primary_state_imports=0,approach_writes=len(writes),
            source_report=report.relative_to(ROOT).as_posix(),source_report_sha256=sha(report.read_bytes()),archive_manifest=(out/'manifest.json').relative_to(ROOT).as_posix(),
            scope='Official-core cold replay of the audited PAL c0046 milestone on c0047, same controller recording and logged approach-only hurt writes; no global SMS or PCM fidelity claim.')
paths=[Path(__file__).resolve(),report,trace/'capture.json',trace/'controls.json',trace/'assistance.json',proof/'replay_report.json']
paths += [p for p in work.iterdir() if p.is_file()]+[trace/f'ram_{end:05d}.bin',trace/f'frame_{end:05d}.png']
freeze(ROOT,out,paths,result,[work],cleanup=True)
(ROOT/f'analysis/c0047_pal_{a.milestone.replace("-","_")}_report.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2),flush=True)
