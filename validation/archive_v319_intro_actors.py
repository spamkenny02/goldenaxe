"""Audit native intro actor/pose/SAT/palette semantics and explicitly bound VDP IRQ status inputs."""
import json
import sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'tools'))
from archive_lossless_evidence import freeze,sha
second=root/'validation/v319-native-intro-poll-actors-second01'
third=root/'validation/v319-native-intro-poll-actors-third03'
rebuild=root/'validation/v319-intro-actors-rebuild01'
profiles=[];compiled=[]
for scene,work,counts in [('second',second,[3492,3500]),('third',third,[3846,3866])]:
 target=work/'report.json';report=json.loads(target.read_bytes())
 assert report['passed'] and report['actors']==scene and [r['source_cases'] for r in report['cases']]==counts
 assert report.get('irq_status',False)==(scene=='third')
 report['irq_status']=report.get('irq_status',False)
 for row in report['cases']:
  cases=json.loads((work/row['region']/'native-cases.json').read_bytes())
  assert len(cases)==row['cases_crossing_irq']==row['source_cases']
  poses=set();slots=set();statuses=set();actor_changes=0;visible=0
  for case in cases:
   before=case['input_ram'];after=case['expected_ram']
   assert len(before)==(1193 if scene=='third' else 1184)
   assert before[409:411]==([0x55,0x10] if scene=='second' else [0x4a,0x10])
   actor_changes+=before[416:1184]!=after[416:1184];visible+=after[144]!=208
   for n in range(16):
    actor=before[416+n*48:416+(n+1)*48]
    if actor[0]==2:slots.add(n);poses.add((n,actor[11]))
   if scene=='third':
    assert case['expected'][6]==before[1184]
    statuses.update(before[1185:1185+before[1184]])
  row.update(actor_record_change_cases=actor_changes,visible_sat_cases=visible,
             active_actor_slots=sorted(slots),observed_slot_poses=sorted(poses),supplied_irq_vdp_statuses=sorted(statuses))
  assert actor_changes and visible and poses
  if scene=='third':assert statuses=={159,191}
 if 'metadata_clarification' not in report:
  report['verified'][0]+=' Includes768 actor bytes and palette/counter/mapper/target snapshots.'
 report['metadata_clarification']='Actor profile, replacing inherited empty-callback prose; raw data and numeric oracle results unchanged.'
 report['limits'][1]='Selected original actor callback only; third scene receives each captured source VDP status as explicit native IRQ input. No physical MD status binding or skip inputs.'
 target.write_text(json.dumps(report,indent=2)+'\n');profiles.append(report)
 cr=json.loads((work/'compiled-all-report.json').read_bytes())
 assert cr['passed'] and cr['distinct_source_vectors']==sum(counts) and cr['compiled_executions']==sum(counts)*2
 for item in cr['kernels']:
  row=item['report'];assert row['actors']==scene and row['irq_status']==(scene=='third')
  assert all(r['intro_poll_done']==1 and r['intro_poll_errors']==0 and r['intro_poll_cases']==row['source_vector_cases'] for r in row['results'])
 compiled.append(cr)
assert sum(r['distinct_source_vectors'] for r in compiled)==14704
assert sum(r['compiled_executions'] for r in compiled)==29408
assert (rebuild/'project/out/release/rom.bin').read_bytes()==(root/'gaw-megadrive.bin').read_bytes()
for path in (root/'megadrive/src').rglob('*'):
 if path.is_file():assert path.read_bytes()==(rebuild/'project/src'/path.relative_to(root/'megadrive/src')).read_bytes()
observers=[root/'validation'/name for name in ['v319-intro-actors_second-callback-observer01',
 'v319-intro-actors_third-callback-observer01','v319-intro-actors_third-callback-observer02']]
for folder in observers:
 metadata=json.loads((folder/'report.json').read_bytes())
 assert metadata['original_source_restored'] and metadata['original_source_sha256']==sha((root.parents[1]/'work/genesis-plus-gx/core/z80/z80.c').read_bytes())
result=dict(passed=True,diagnostic_only=True,production_rom_changed=False,public_version=319,
 production_rom_sha256=sha((root/'gaw-megadrive.bin').read_bytes()),production_rebuild_byte_identical=True,
 source_profiles=profiles,compiled68000_checks=compiled,distinct_source_vectors=14704,compiled_executions=29408,
 implementation='New source_intro_actors.c/.h:1055/104A callbacks,1061 sixteen-slot actor scan,108B activation/pose '
  'updates,RST08 table lookup,A60 SAT reset,A78 relative sprite lists,0978 terminator andBE25 lightning palette. '
  'All original instruction/IRQ boundaries and native semantic RAM writes retained; no hardware output.',
 status_binding='Third-scene source sprite overflow changes C01B from9F toBF. The generic compact IRQ adapter '
  'does not manufacture VDP status. Diagnostic native IRQ binding receives exactly the status independently '
  'captured at each original0137 entry, with matching count/order, then delegates to unchanged source_irq_interrupt. '
  'This external chip-input fixture is not injected into the running SMS or the primary game campaign.',
 recovery='Initial third-scene checker rejected missing C01B hardware input, then rejected an uninitialized '
  'diagnostic status queue. The corrected harness compares every tracked byte, excluding none. One completed '
  'kernel build later failed terminal LTO temporary-path conversion; same objects were linked with-flto=1, '
  'normal packaging retained and vectors rerun. Failed logs and the exact serial link recipe retained.',
 next_action='Translate/source-check F51/F54 actor initialization, then E8B..E9D reveal row scheduling and '
  'F1E composition. Plan compact semantic memory/native publication deadlines before integration; explicit '
  'VDP status must be computed/bound from the live source sprite model, never replayed from recorded frames.',
 limits=['Natural no-input intro callbacks over14000 source frames per region; no synthetic actor corruption or skip inputs.',
         'No actor initialization oracle yet, no physical MD raster/PSG deadlines, PCM or hardware certification.',
         'Context full_ram is diagnostic semantic backing; these helpers remain unselected by the published game.'],
 ram_writes=0,sram_imports=0,archive_manifest='analysis/v319-intro-actors/manifest.json')
target=root/'analysis/v319_intro_actors_report.json';assert not target.exists()
target.write_text(json.dumps(result,indent=2)+'\n')
scripts=['archive_v319_intro_actors.py','compile_v319_intro_actors_all.py','run_v319_existing_actor_kernel.py',
 'relink_v319_kernel_serial.py','build_v319_intro_empty_observer.py','build_v319_intro_poll_observer.py',
 'validate_v319_intro_poll.py','compile_v319_intro_poll_68k.py']
paths={root/'validation'/name for name in scripts};paths.add(target)
for name in ('source_intro_actors.c','source_intro_actors.h','source_intro_wait.c','source_intro_wait.h',
 'source_irq_context.c','source_irq_context.h','source_room_memory.h'):paths.add(root/'megadrive/src'/name)
for name in ('build_timing_core.py','build_private_candidate.ps1','run_core.py'):paths.add(root/'tools'/name)
failures=[root/'validation'/name for name in ['v319-native-intro-poll-actors-third01','v319-native-intro-poll-actors-third02']]
for folder in [second,third,rebuild,*observers,*failures]:paths.update(p for p in folder.rglob('*') if p.is_file())
freeze(root,root/'analysis/v319-intro-actors',paths,result,[second,third,*failures,rebuild/'project/out'],cleanup=True)
print('14704 original actor callback vectors and29408 compiled68000 executions archived; V319 unchanged.')
