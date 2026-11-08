"""Freeze exact stable pattern runs,fullVDP equivalence and measured scene gain."""
import json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'))
from archive_lossless_evidence import sha,freeze
work=root/'validation/v319-live-scene-profile05';r=json.loads((work/'report.json').read_bytes());cr=json.loads((work/'compiled-report.json').read_bytes());assert r['passed'] and r['pattern_runs'] and cr['passed']
dates=root/'validation/v319-pattern-run-dates01';dr=json.loads((dates/'report.json').read_bytes());assert dr['passed'] and dr['cases']==24 and dr['outputs']==392832
vdptest=root/'validation/v319-pattern-run-vdp03';vr=json.loads((vdptest/'report.json').read_bytes());assert vr['passed'] and vr['host_cases']==1728
for row in vr['results']:assert row['run_done'] and row['run_cases_done']==1728 and not row['run_errors']
for name,digest in vr['native_sources'].items():assert sha((root/'megadrive/src'/(name+'.c')).read_bytes())==digest
for name,digest in r['native_sources'].items():assert sha((root/'megadrive/src'/(name+'.c')).read_bytes())==digest
assert sha((root/'megadrive/src/source_pattern_clock.c').read_bytes())==dr['native_source_sha256']
baseline=json.loads((root/'analysis/v319_video_math_report.json').read_bytes())['optimized_profile'];timing=[]
for old,new in zip(baseline['results'],cr['results']):
 assert old['region']==new['region'] and new['intro_poll_done'] and not new['intro_poll_errors'] and new['intro_poll_cases']==10
 a=old['native_call_frames'];b=new['native_call_frames'];assert all(x<y for x,y in zip(b,a))
 timing.append(dict(region=new['region'],before=a,after=b,mean_reduction_percent=100*(1-sum(b)/sum(a))))
rebuild=root/'validation/v319-pattern-runs-rebuild01';rr=json.loads((rebuild/'report.json').read_bytes());assert rr['passed'] and rr['byte_identical_v319']
assert (rebuild/'project/out/release/rom.bin').read_bytes()==(root/'gaw-megadrive.bin').read_bytes()
for name,digest in rr['source_sha256'].items():
 assert sha((root/'megadrive/src'/name).read_bytes())==digest
 assert (rebuild/'project/src'/name).read_bytes()==(root/'megadrive/src'/name).read_bytes()
for name in ('source_intro_vdp.c','source_intro_vdp.h','source_intro_scene.c','source_intro_scene.h','source_pattern_clock.c','source_pattern_clock.h'):
 (work/('before-'+name)).write_bytes(subprocess.check_output(['git','show','HEAD:megadrive/src/'+name],cwd=root))
attempt=root/'validation/v319-pattern-run-vdp01/attempt.json'
if not attempt.exists():attempt.write_text(json.dumps(dict(passed=False,reason='Original differential kernel did not finish within30000 observed MD frames. Scalar synthetic memory setup used division for every byte; setup simplified to multiply/add and completed test repeated in new directories with larger observation bound and progress visibility.',observed=dict(run_cases_done=0,run_errors=0,run_done=0,frame=30000),final_evidence='validation/v319-pattern-run-vdp03/report.json'),indent=2)+'\n')
result=dict(passed=True,public_version=319,production_rom_changed=False,production_rebuild_byte_identical=True,production_rom_sha256=rr['sha256'],
 implementation='SourcePatternVideoRun preserves BF30T/BF45T/BE77T and exact135/134T strides,carry andterminal adjustments for stable before-IRQ sequences. Native decoder and scene expose optional run sinks; boundary instructions retain ordinary port sinks. LogicalVDP evaluates each sprite-sensitive BE before its mutation; whole runs in opposite sprite pattern bank can advance once because those bytes cannot affect SAT or sprite pixels. Full original write dates remain in descriptor for later physical delivery.',
 original_dated_output_equivalence=dr,full_vdp_equivalence=vr,compiled_scene_profile=cr,helper_profile=timing,
 budget_gate_passed=False,
 limits=['Optimized helper316..335MDframes NTSC (265..281PAL across these executions) is still above original scene budget. This is a CPU gate failure; do not activate in published ROM.',
 'Profile excludes setup/final comparisons and per-OUT expected checks; small per-IRQ status checks remain. No physical MD background rendering or PSG delivery is included.',
 'Background-bank batching is valid for logical sprite/status semantics only. Physical background pixel visibility must consume the retained per-byte dates; never turn it into one instantaneous physical upload.',
 'Scene snapshots rather than uninterrupted coldboot. Native IRQ date proof,full image/PSG throughput and hardware remain open.'],
 next_action='Profile remaining clear/map/per-line and IRQ overhead; implement equivalent dated runs there while preserving live status observations. Then remeasure combined CPU gate before physical video/PSG and ROM activation. FullV319 gameplay video is ready locally; upload pending browser access/visibility.',
 oracle_ram_writes=0,sram_imports=0,archive_manifest='analysis/v319-pattern-runs/manifest.json')
target=root/'analysis/v319_pattern_runs_report.json';assert not target.exists();target.write_text(json.dumps(result,indent=2)+'\n')
paths={target,Path(__file__).resolve()}
for name in ('profile_v319_live_scene.py','validate_v319_pattern_run_vdp.py','validate_v319_pattern_run_dates.py'):paths.add(root/'validation'/name)
for name in ('source_pattern_video.h','source_pattern_clock.c','source_pattern_clock.h','source_intro_scene.c','source_intro_scene.h','source_intro_vdp.c','source_intro_vdp.h'):paths.add(root/'megadrive/src'/name)
folders=[root/'validation'/name for name in ('v319-live-scene-profile03','v319-live-scene-profile04','v319-live-scene-profile05','v319-pattern-run-vdp01','v319-pattern-run-vdp02','v319-pattern-run-vdp03','v319-pattern-run-dates01')]
for folder in [*folders,rebuild]:paths.update(p for p in folder.rglob('*') if p.is_file())
freeze(root,root/'analysis/v319-pattern-runs',paths,result,[*folders,rebuild/'project/out'],cleanup=True)
