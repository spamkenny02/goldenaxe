"""Freeze composed scene state/VRAM/timing proof and measured native CPU budget gap."""
import json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'))
from archive_lossless_evidence import freeze,sha
work=root/'validation/v319-native-intro-poll-scene03';regression=root/'validation/v319-native-intro-poll-mapdecode05'
profile=root/'validation/v319-native-intro-poll-scene-throughput02';baseline=root/'validation/v319-native-intro-poll-scene-throughput01'
r=json.loads((work/'report.json').read_bytes());assert r['passed'] and r['scene']
assert [row['source_cases'] for row in r['cases']]==[5,5]
for name,digest in r['native_sources'].items():assert sha((root/'megadrive/src'/(name+'.c')).read_bytes())==digest
virtual=[]
for region in ('ntsc','pal'):
 cases=json.loads((work/region/'native-cases.json').read_bytes());assert len(cases)==5
 for case in cases:
  before=case['input_ram'];after=case['expected_ram'];events=case['events']
  assert len(before)==15081 and len(after)==15081 and len(events)==16904
  assert case['expected'][12:14]==[8452,576] and case['expected'][6]>0
  assert after[1184:1190]==[0,217,0,120,190,0]
  assert after[409:411]==before[1186:1188]
  assert all(events[i]<events[i+2] for i in range(0,len(events)-2,2))
  assert all(after[5032+n]==255 for n in range(3,9216,4))
  assert after[14248:15016]==after[1192:1960]
  virtual.append(dict(source_region=region,source_frames=case['expected'][1]/(case['phase'][3]*3420),source_irqs=case['expected'][6]))
cr=json.loads((work/'compiled-report.json').read_bytes());assert cr['passed'] and cr['scene'] and cr['source_vector_cases']==10
assert all(row['intro_poll_errors']==0 and row['intro_poll_cases']==10 for row in cr['results'])
reg=json.loads((regression/'report.json').read_bytes());reg_cr=json.loads((regression/'compiled-report.json').read_bytes())
assert reg['passed'] and reg_cr['passed'] and reg_cr['source_vector_cases']==14
for name,digest in reg['native_sources'].items():assert sha((root/'megadrive/src'/(name+'.c')).read_bytes())==digest
assert all(row['intro_poll_errors']==0 for row in reg_cr['results'])
for region in ('ntsc','pal'):
 original=json.loads((work/region/'native-cases.json').read_bytes())
 measured=json.loads((profile/region/'native-cases.json').read_bytes())
 assert len(original)==len(measured)
 for first,second in zip(original,measured):
  expected=first['expected'].copy();expected[12]=0
  assert second==dict(first,events=[],expected=expected)
pc=json.loads((profile/'compiled-report.json').read_bytes());assert pc['passed'] and pc['profile_stages'] and pc['measure_native_frames']
bc=json.loads((baseline/'compiled-both-kernel3-report.json').read_bytes());assert bc['passed']
assert all(row['intro_poll_errors']==0 for row in pc['results'])
assert min(min(row['native_call_frames']) for row in pc['results'])>max(row['source_frames'] for row in virtual)+1
rebuild=root/'validation/v319-intro-scene-rebuild02';old_rebuild=root/'validation/v319-intro-scene-rebuild01'
assert (rebuild/'project/out/release/rom.bin').read_bytes()==(root/'gaw-megadrive.bin').read_bytes()
for path in (root/'megadrive/src').rglob('*'):
 if path.is_file():assert path.read_bytes()==(rebuild/'project/src'/path.relative_to(root/'megadrive/src')).read_bytes()
old=json.loads((root/'validation/v319-native-intro-poll-scene01/report.json').read_bytes())
assert sha((old_rebuild/'project/src/source_intro_map.c').read_bytes())==old['native_sources']['source_intro_map']
observer=root/'validation/v319-intro-scene_load-callback-observer01';metadata=json.loads((observer/'report.json').read_bytes())
assert metadata['scene'] and metadata['original_source_restored']
assert sha((root.parents[1]/'work/genesis-plus-gx/core/z80/z80.c').read_bytes())==metadata['original_source_sha256']
r['metadata_clarification']='Composed E50 scene loader. Inherited map-only profile prose corrected, raw data and numeric results unchanged.'
r['limits'][1]='E50..E72 scene load, exit E75. Snapshot includes9216 pattern bytes and768 map VRAM bytes. OUT collector covers clear/map operations only; individual032A OUT timestamps are not exposed.'
(work/'report.json').write_text(json.dumps(r,indent=2)+'\n')
result=dict(passed=True,diagnostic_only=True,production_rom_changed=False,public_version=319,
 production_rom_sha256=sha((root/'gaw-megadrive.bin').read_bytes()),production_rebuild_byte_identical=True,
 source_profile=r,compiled68000_checks=cr,source_entry_vectors=10,compiled_executions=20,
 monitored_source_out_events=84520,monitored_compiled_out_events=169040,
 regression=dict(source_profile=reg,compiled68000_checks=reg_cr,source_vectors=14,compiled_executions=28,scope='Recheck optimized decoder including ROM bank7 and IRQ/no-IRQ cases.'),
 implementation='New source_intro_scene.c/.h composes E50..E72 on one SourceClock: set DCEC, EA5 prepare,032A pattern decode, E2B plane clear,BD3/BFE map decode,7357 placement,EFA map transfer. Semantic16KiB VRAM mirror; optional clear/map OUT sink. Exit prefetched E75, no scene-stage frame lookup.',
 verification='All15081 tracked bytes including scratch,map,actor/palette state,9216 pattern and768 name-table VRAM bytes, plus400 reader bytes match original, along with wall/IRQ/R/latches and monitored OUT values/completion times/raster. Ten complete natural fire/actor scene loads over14000 no-input frames per region. Full IRQ status remains external diagnostic input.',
 optimization='BD3 first-layer literal/increment loops batch nonterminal39T/5M1 or30T/4M1 runs only before VINT. BFE second-layer literal/repeated loops batch57T/8M1 or51T/7M1 nonterminal/noncarry runs, split at low-byte carry and IRQ boundaries. Commit writes before the next IRQ; ordinary path handles all other boundaries. Whole scene and bank7 regression prove final original state/time unchanged.',
 performance=dict(within_source_frame_budget=False,source_durations=virtual,baseline=bc,optimized=pc,
  stage_order=['prepare_including_first_transfer','patterns032A','clearE2B','decodeBD3_BFE','place7357','final_transferEFA'],
  measurement='SDK vtimer deltas inside the native helper and six call wrappers, excluding fixture copies and final comparisons, foreground per-OUT oracle disabled. Every final state/clock still checked. One-frame resolution, optimistic: no physical MD video/PSG delivery. Profiling adds small overhead; cannot explain the large remaining gap.',
  finding='Native helper drops from124..125 to97..99 target NTSC frames and103..105 to81..83 PAL. Source scenes take24.27..26.95 NTSC or21.48..22.96 PAL virtual frames. Still too costly for faithful physical integration. Clear32-ish, prepare24-ish and final transfer20-ish target NTSC frames are next bottlenecks.'),
 limits=['No input/skip or alternate E50 headers beyond captured fire/actor paths. E3F actor initialization and E75 reveal not included in this profile.',
         'Pattern individual OUT timestamps and VRAM outside0000..23FF/3800..3AFF are not compared here. Source VDP status still diagnostic input, not a live producer.',
         'No production memory/live sprite binding, physical publication deadlines, PCM or hardware certification. Public V319 unchanged.'],
 next_action='Optimize clear and transfer semantic memory/IO delivery in IRQ-safe batches, then prepare LDIR loops; retain per-write checked path and source clock behavior. Reprofile whole native helper against source duration before integration. Then bind compact memory/live VDP status and actual MD video/PSG delivery.',
 oracle_ram_writes=0,sram_imports=0,archive_manifest='analysis/v319-intro-scene/manifest.json')
target=root/'analysis/v319_intro_scene_report.json';assert not target.exists();target.write_text(json.dumps(result,indent=2)+'\n')
paths={target,Path(__file__).resolve()}
for name in ('build_v319_intro_empty_observer.py','build_v319_intro_poll_observer.py','validate_v319_intro_poll.py','compile_v319_intro_poll_68k.py','build_v319_intro_scene_profile.py','profile_v319_intro_scene.py','profile_v319_intro_scene_stages.py'):paths.add(root/'validation'/name)
for name in ('source_intro_scene.c','source_intro_scene.h','source_intro_map.c','source_intro_map.h','source_intro_video.c','source_intro_video.h','source_pattern_clock.c','source_pattern_clock.h','source_clock.c','source_clock.h','source_room_memory.h'):paths.add(root/'megadrive/src'/name)
prior=[root/'validation'/name for name in ('v319-native-intro-poll-scene01','v319-native-intro-poll-scene02','v319-native-intro-poll-mapdecode04')]
for folder in [work,regression,profile,baseline,rebuild,old_rebuild,observer,*prior]:paths.update(p for p in folder.rglob('*') if p.is_file())
freeze(root,root/'analysis/v319-intro-scene',paths,result,[work,regression,profile,baseline,*prior,rebuild/'project/out',old_rebuild/'project/out'],cleanup=True)
print('Whole scene source/VRAM/clock proofs frozen; CPU budget gap remains, public V319 unchanged.')
