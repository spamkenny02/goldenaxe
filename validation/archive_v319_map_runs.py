"""Freeze stable clear/map delivery and staged native CPU measurements."""
import json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'))
from archive_lossless_evidence import sha,freeze
baseline=root/'validation/v319-live-scene-stages01';work=root/'validation/v319-live-scene-stages03';test=root/'validation/v319-map-run-vdp02';rebuild=root/'validation/v319-map-runs-rebuild01'
b=json.loads((baseline/'compiled-report.json').read_bytes());r=json.loads((work/'report.json').read_bytes());cr=json.loads((work/'compiled-report.json').read_bytes());vr=json.loads((test/'report.json').read_bytes());rr=json.loads((rebuild/'report.json').read_bytes())
assert all(x['passed'] for x in (b,r,cr,vr,rr)) and r['scene_video_runs'] and r['pattern_runs'] and rr['byte_identical_v319']
assert vr['host_cases']==576
for row in vr['results']:assert row['run_done'] and row['run_cases_done']==576 and not row['run_errors']
for name,digest in vr['native_sources'].items():assert sha((root/'megadrive/src'/(name+'.c')).read_bytes())==digest
for name,digest in r['native_sources'].items():assert sha((root/'megadrive/src'/(name+'.c')).read_bytes())==digest
timing=[]
for old,new in zip(b['results'],cr['results']):
 assert old['region']==new['region'] and not new['intro_poll_errors'] and new['intro_poll_cases']==10
 assert all(a<b for a,b in zip(new['native_call_frames'],old['native_call_frames']))
 timing.append(dict(region=new['region'],before=old['native_call_frames'],after=new['native_call_frames'],stages_before=old['native_stage_frames'],stages_after=new['native_stage_frames'],mean_reduction_percent=100*(1-sum(new['native_call_frames'])/sum(old['native_call_frames']))))
assert (rebuild/'project/out/release/rom.bin').read_bytes()==(root/'gaw-megadrive.bin').read_bytes()
for name,digest in rr['source_sha256'].items():
 assert sha((root/'megadrive/src'/name).read_bytes())==digest
 assert (rebuild/'project/src'/name).read_bytes()==(root/'megadrive/src'/name).read_bytes()
names=('source_intro_scene.c','source_intro_scene.h','source_intro_scene_vdp.c','source_intro_scene_vdp.h','source_intro_vdp.c','source_intro_vdp.h')
for name in names:(work/('before-'+name)).write_bytes(subprocess.check_output(['git','show','HEAD:megadrive/src/'+name],cwd=root))
result=dict(passed=True,public_version=319,production_rom_changed=False,production_rebuild_byte_identical=True,production_rom_sha256=rr['sha256'],
 implementation='source_intro_scene_load_video_runs forwards existing exact clear/map descriptors instead of expanding per-OUT callbacks. SourceIntroVdp consumes clearBE101T/124Tstride/address+4 and transferBE16T/32Tstride/address+1. Sprite-sensitive bytes still evaluate before their mutation; opposite8KiB bank can advance once. Final port address,latch,buffer and instruction checkpoint remain individual-OUT exact.',
 stage_names=['prepare','patterns','plane_clear','map_decode','map_place','map_transfer'],profile=timing,compiled_scene=cr,full_vdp_equivalence=vr,
 compiled_scene_cases=20,compiled_vdp_differential_cases=1152,budget_gate_passed=False,
 limits=['Helper-only profile excludes fixture setup/final comparisons/per-OUT expected checks; small IRQ-status diagnostic checks remain. Physical MD background/video/PSG publication excluded.',
 '144..162MDframes NTSC,120..136PAL remain above source scene budget. This CPU gate is still failed; keep unselected in publicROM.',
 'Run descriptors preserve every original write date for physical renderer. Logical background-bank batching must not become one instantaneous physical upload.',
 'Initial scene snapshots,not uninterrupted coldboot; independent IRQ OUT-date audit and physical image/PCM/hardware remain open.'],
 next_action='Patterns and wait/IRQ preparation/transfer are now dominant; profile their hot paths and batch stable calendar spans or real IRQ packets without losing status observations. Recheck combined CPU gate before ROM activation. FullV319 video remains local pending browser access/visibility.',
 oracle_ram_writes=0,sram_imports=0,archive_manifest='analysis/v319-map-runs/manifest.json')
target=root/'analysis/v319_map_runs_report.json';assert not target.exists();target.write_text(json.dumps(result,indent=2)+'\n')
paths={target,Path(__file__).resolve()}
for name in ('profile_v319_live_scene.py','compile_v319_intro_poll_68k.py','validate_v319_map_run_vdp.py'):paths.add(root/'validation'/name)
for name in names:paths.add(root/'megadrive/src'/name)
folders=[baseline,root/'validation/v319-live-scene-stages02',work,root/'validation/v319-map-run-vdp01',test]
for folder in [*folders,rebuild]:paths.update(p for p in folder.rglob('*') if p.is_file())
freeze(root,root/'analysis/v319-map-runs',paths,result,[*folders,rebuild/'project/out'],cleanup=True)
