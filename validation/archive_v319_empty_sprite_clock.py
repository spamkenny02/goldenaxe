"""Freeze exact empty-sprite calendar skipping and original-port regressions."""
import json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'))
from archive_lossless_evidence import sha,freeze
test=root/'validation/v319-empty-sprite-clock02';tr=json.loads((test/'report.json').read_bytes());assert tr['passed'] and tr['host_cases']==172500
for row in tr['results']:assert row['empty_done'] and row['empty_cases']==172500 and not row['empty_errors']
assert tr['native_source_sha256']==sha((root/'megadrive/src/source_intro_sprite_clock.c').read_bytes())
work=root/'validation/v319-live-scene-stages05';r=json.loads((work/'report.json').read_bytes());cr=json.loads((work/'compiled-report.json').read_bytes());assert r['passed'] and cr['passed']
baseline=json.loads((root/'analysis/v319_map_runs_report.json').read_bytes())['compiled_scene'];timing=[]
for old,new in zip(baseline['results'],cr['results']):
 assert old['region']==new['region'] and not new['intro_poll_errors'] and new['intro_poll_cases']==10
 assert all(a<b for a,b in zip(new['native_call_frames'],old['native_call_frames']))
 timing.append(dict(region=new['region'],before=old['native_call_frames'],after=new['native_call_frames'],stage_frames=new['native_stage_frames'],mean_reduction_percent=100*(1-sum(new['native_call_frames'])/sum(old['native_call_frames']))))
ports=root/'validation/v319-port-mirror04';pr=json.loads((ports/'report.json').read_bytes());assert pr['passed'] and pr['frames']==14000
for row in pr['results']:assert not any(row[k] for k in ('read_errors','rejected','vram_errors','protocol_errors','register_errors','palette_errors','capture_overflow'))
compiled=[]
for region in ('ntsc','pal'):
 c=json.loads((ports/('compiled-'+region+'-report.json')).read_bytes());assert c['passed'] and all(row['port_done'] and not row['port_errors'] for row in c['results']);compiled.append(c)
rebuild=root/'validation/v319-empty-sprite-rebuild01';rr=json.loads((rebuild/'report.json').read_bytes());assert rr['passed'] and rr['byte_identical_v319']
assert (rebuild/'project/out/release/rom.bin').read_bytes()==(root/'gaw-megadrive.bin').read_bytes()
for name,digest in rr['source_sha256'].items():
 assert sha((root/'megadrive/src'/name).read_bytes())==digest
 assert (rebuild/'project/src'/name).read_bytes()==(root/'megadrive/src'/name).read_bytes()
(work/'before-source_intro_sprite_clock.c').write_bytes(subprocess.check_output(['git','show','HEAD:megadrive/src/source_intro_sprite_clock.c'],cwd=root))
# Delete only verified byte-identical cold-image reference DLL duplicates.
core=root.parents[1]/'work/genesis-plus-gx';br=json.loads((root/'validation/v319-port-mirror-observer01/report.json').read_bytes());base=Path(br['core']).resolve();assert base.parent==core.resolve() and sha(base.read_bytes())==br['core_sha256'];removed=[]
for name in ('v319-port-mirror03','v319-port-mirror04'):
 duplicate=base.with_name(base.stem+'_'+name.replace('-','_')+'_pal.dll').resolve();assert duplicate.parent==core.resolve() and duplicate!=base
 if duplicate.exists():
  assert sha(duplicate.read_bytes())==br['core_sha256'];removed.append(dict(path=str(duplicate),bytes=duplicate.stat().st_size,sha256=br['core_sha256']));duplicate.unlink()
result=dict(passed=True,public_version=319,production_rom_changed=False,production_rebuild_byte_identical=True,production_rom_sha256=rr['sha256'],
 implementation='When cached counts are both zero,pending overflow zero,and live SAT starts withD0,stable parse/render operations are all no-ops. Advance only raster,line phase and independently latchedVINT,retaining all flags/collision coordinates/unused entries. NonMode4 also preserves sprite state. Calls ending before the next line take a direct increment path. Every other condition retains original line-by-line evaluation.',
 full_state_equivalence=tr,source_port_regression=pr,compiled_port_regression=compiled,compiled_scene=cr,helper_profile=timing,compiled_differential_cases=345000,budget_gate_passed=False,
 limits=['88..96MDframes NTSC and74..80PAL across these helper executions remain above original scene budget. Do not activate in publicROM.',
 'Helper profile excludes fixture setup/final checks/per-OUT expected checks; small IRQ diagnostic checks remain. Physical MD video/PSG publication excluded.',
 'Complete uninterrupted coldboot and independently captured native IRQ port dates remain open. No PCM/hardware/global fidelity certificate.'],
 removed_verified_reference_duplicates=removed,
 next_action='Profile active sprite/calendar and real IRQ/wait paths now dominating preparation/map waits;batch only intervals with no observable change. Recheck CPU gate before physical video/audio activation. FullV319 video remains local;YouTube access/visibility awaiting user.',
 oracle_ram_writes=0,sram_imports=0,archive_manifest='analysis/v319-empty-sprite-clock/manifest.json')
target=root/'analysis/v319_empty_sprite_clock_report.json';assert not target.exists();target.write_text(json.dumps(result,indent=2)+'\n')
paths={target,Path(__file__).resolve(),root/'validation/validate_v319_empty_sprite_clock.py',root/'validation/profile_v319_live_scene.py',root/'megadrive/src/source_intro_sprite_clock.c'}
folders=[root/'validation'/name for name in ('v319-empty-sprite-clock01','v319-empty-sprite-clock02','v319-live-scene-stages04','v319-live-scene-stages05','v319-port-mirror04')]
for folder in [*folders,rebuild]:paths.update(p for p in folder.rglob('*') if p.is_file())
freeze(root,root/'analysis/v319-empty-sprite-clock',paths,result,[*folders,rebuild/'project/out'],cleanup=True)
