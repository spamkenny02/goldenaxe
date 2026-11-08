"""Freeze IRQ-safe video runs, decoded ROM plans and observed native CPU headroom."""
import json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'))
from archive_lossless_evidence import freeze,sha
work=root/'validation/v319-native-intro-poll-scene-runs04';profile=root/'validation/v319-native-intro-poll-scene-throughput05'
r=json.loads((work/'report.json').read_bytes());assert r['passed'] and r['scene']
assert [row['source_cases'] for row in r['cases']]==[5,5]
for name,digest in r['native_sources'].items():assert sha((root/'megadrive/src'/(name+'.c')).read_bytes())==digest
for name,digest in r['native_assets'].items():assert sha((root/'megadrive/src'/name).read_bytes())==digest
assets=json.loads((root/'analysis/intro_pattern_plan_assets_report.json').read_bytes())
assert assets['passed'] and assets['source_sha256']==sha((root/'input/original.sms').read_bytes())
assert assets['header_sha256']==sha((root/'megadrive/src/source_intro_pattern_plans_generated.h').read_bytes())
cr=json.loads((work/'compiled-report.json').read_bytes());assert cr['passed'] and cr['source_vector_cases']==10
assert all(row['intro_poll_errors']==0 for row in cr['results'])
pr=json.loads((profile/'compiled-report.json').read_bytes());assert pr['passed'] and pr['measure_native_frames'] and pr['profile_stages']
assert all(row['intro_poll_errors']==0 for row in pr['results'])
headroom=[]
for index,region in enumerate(('ntsc','pal')):
 cases=json.loads((work/region/'native-cases.json').read_bytes());measured=json.loads((profile/region/'native-cases.json').read_bytes())
 assert len(cases)==len(measured)==5
 target=next(row for row in pr['results'] if row['region']==region)
 for n,(original,benchmark) in enumerate(zip(cases,measured)):
  assert len(original['input_ram'])==15081 and original['expected'][12]==8452
  assert len(original['events'])==16904
  expected=original['expected'].copy();expected[12]=0
  assert benchmark==dict(original,events=[],expected=expected)
  virtual=original['expected'][1]/(original['phase'][3]*3420)
  actual=target['native_call_frames'][index*5+n]
  assert actual+1<virtual
  headroom.append(dict(region=region,case=n,source_frames=virtual,native_frames=actual,
   conservative_frames_left=virtual-actual-1))
regressions=[]
for name,count in [('prepare-runs01',14),('clear-runs01',14),('transfer-runs01',28),('map-runs01',14)]:
 folder=root/'validation'/('v319-native-intro-poll-'+name)
 rr=json.loads((folder/'report.json').read_bytes());cc=json.loads((folder/'compiled-report.json').read_bytes())
 assert rr['passed'] and cc['passed'] and cc['source_vector_cases']==count
 assert all(row['intro_poll_errors']==0 for row in cc['results'])
 for module,digest in rr['native_sources'].items():assert sha((root/'megadrive/src'/(module+'.c')).read_bytes())==digest
 regressions.append(dict(work=folder.relative_to(root).as_posix(),source_profile=rr,compiled68000_checks=cc))
rebuild=root/'validation/v319-intro-runs-rebuild03'
assert (rebuild/'project/out/release/rom.bin').read_bytes()==(root/'gaw-megadrive.bin').read_bytes()
for path in (root/'megadrive/src').rglob('*'):
 if path.is_file():assert path.read_bytes()==(rebuild/'project/src'/path.relative_to(root/'megadrive/src')).read_bytes()
baseline=json.loads((root/'analysis/v319_intro_scene_report.json').read_bytes())
result=dict(passed=True,diagnostic_only=True,production_rom_changed=False,public_version=319,
 production_rom_sha256=sha((root/'gaw-megadrive.bin').read_bytes()),production_rebuild_byte_identical=True,
 source_profile=r,compiled68000_checks=cr,source_entry_vectors=10,compiled_executions=20,
 monitored_source_out_events=84520,monitored_compiled_out_events=169040,regressions=regressions,
 changes=['Timed SourceIntroVideoRun descriptors for stable CLEAR and TRANSFER spans, split before possible IRQs. Checked scene path expands each descriptor through ordinary scene_out so observers see sequential VRAM updates; no-OUT-observer path applies direct stride fills/memcpy before the next IRQ.',
  'Map OUTI/NOP/JR batches32T/4M1 except terminal bytes; preserve every16T output completion and source32T spacing. Forward LDIR batching retains overlapping-copy semantics, never memcpy on overlapping D600/D602.',
  '7357 nonterminal LDI/DJNZ runs29T/3M1 copy bounded disjoint buffers until IRQ or last byte.',
  'BD3 whole literal/increment commands52+39N or58+30N T, BFE whole literal/repeated commands52+57N-carries or51+51N-carries T; exact M1 counts, bound capacity and immutable/stable bytes, no IRQ inside accepted blocks. Detailed paths remain at boundaries.',
  'Generated plans for original intro032A streams9D74/A659: immutable decoded bytes and T/M1 command prefixes, every command checked against the instruction model. No captured phases/frame delays. Existing decoder gains optional plan API; ordinary decode remains available.'],
 generated_pattern_assets=assets,native_profile=pr,observed_cpu_budget=dict(helper_only_met_for_same_region_cases=True,
  physical_delivery_budget_proved=False,matched_cases=headroom,measurement='SDK vtimer deltas inside helper, excluding fixture copies and final comparisons, OUT oracle disabled. One-frame resolution; budget check adds one full frame. Actual MD video/PSG delivery and live chip-status computation not included.'),
 baseline_reference=dict(path='analysis/v319_intro_scene_report.json',sha256=sha((root/'analysis/v319_intro_scene_report.json').read_bytes()),
  profile=baseline['performance']['optimized']),
 limits=['Primary proof covers the same ten natural no-input E50 loads; IRQ-status bytes remain independently captured diagnostic inputs.',
         'Individual032A OUT timestamps, full physical VDP/PSG publication and live sprite-status producer remain open. VRAM compares only0000..23FF/3800..3AFF plus the semantic RAM tracked before.',
         'Native helper CPU headroom is observed in this diagnostic, not a hardware or whole-game real-time certificate. Public V319 unchanged.'],
 next_action='Bind live source sprite/VDP status and plan compact runtime memory, then deliver timed native intro video/PSG to physical MD frames. Preserve per-IRQ/per-line observations when consuming run descriptors; validate visible intro and actual publication deadlines before a numbered ROM release.',
 oracle_ram_writes=0,sram_imports=0,archive_manifest='analysis/v319-intro-runs/manifest.json')
target=root/'analysis/v319_intro_runs_report.json';assert not target.exists();target.write_text(json.dumps(result,indent=2)+'\n')
paths={target,Path(__file__).resolve(),root/'analysis/intro_pattern_plan_assets_report.json',root/'tools/generate_intro_pattern_plans.py'}
for name in ('validate_v319_intro_poll.py','compile_v319_intro_poll_68k.py','build_v319_intro_scene_profile.py','revalidate_v319_intro_runs_all.py','revalidate_v319_intro_runs_final.py','revalidate_v319_intro_runs_budget.py'):paths.add(root/'validation'/name)
for name in ('source_intro_scene.c','source_intro_scene.h','source_intro_video.c','source_intro_video.h','source_intro_map.c','source_intro_map.h','source_pattern_clock.c','source_pattern_clock.h','source_intro_pattern_plans_generated.h','source_clock.c','source_clock.h','source_room_memory.h'):paths.add(root/'megadrive/src'/name)
folders=[root/'validation'/('v319-native-intro-poll-'+name) for name in ('scene-runs01','scene-runs02','scene-runs03','scene-runs04','prepare-runs01','clear-runs01','transfer-runs01','place-runs01','map-runs01','scene-throughput03','scene-throughput04','scene-throughput05')]
rebuilds=[root/'validation'/('v319-intro-runs-rebuild'+str(n).zfill(2)) for n in (1,2,3)]
for folder in [*folders,*rebuilds]:paths.update(p for p in folder.rglob('*') if p.is_file())
freeze(root,root/'analysis/v319-intro-runs',paths,result,[*folders,*[p/'project/out' for p in rebuilds]],cleanup=True)
print('Native scene CPU headroom observed, original state/IO timing unchanged; physical delivery still open.')
