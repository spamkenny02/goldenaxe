"""Audit normal-controller intro skip composition, independent source replay and68000."""
import json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'))
from archive_lossless_evidence import freeze,sha
work=root/'validation/v319-native-intro-poll-skip03';capture=root/'validation/v319-native-intro-poll-skip02'
r=json.loads((work/'report.json').read_bytes());assert r['passed'] and r['skip']
assert [row['source_cases'] for row in r['cases']]==[44,44]
assert [row['skip_vectors'] for row in r['cases']]==[42,42]
for name,digest in r['native_sources'].items():assert sha((root/'megadrive/src'/(name+'.c')).read_bytes())==digest
coverage=set();source_io=0;source_frames=0
for region in ('ntsc','pal'):
 cap=json.loads((work/region/'capture-report.json').read_bytes());assert cap['passed'] and len(cap['scenarios'])==42
 assert cap['unique_vectors']==44
 assert sha(Path(cap['reference_core']).read_bytes())==cap['reference_core_sha256']
 for row in cap['scenarios']:
  coverage.add((region,row['target'],row['stage'],row['button']));assert row['reference_psg_equal']
  folder=capture/region/f"{row['target']:04x}-stage{row['stage']}-button{row['button']}"
  assert sha((folder/'source-records.bin').read_bytes())==row['records_sha256']
  assert sha((folder/'observer-psg.bin').read_bytes())==row['psg_sha256']
  source_frames+=row['frames']
 cases=json.loads((work/region/'native-cases.json').read_bytes());assert len(cases)==44
 skipped=[c for c in cases if c['source_return_pc']==0xd0b];assert len(skipped)==42
 assert {c['expected'][13] for c in skipped}==set(range(7))
 for case in cases:
  before=case['input_ram'];after=case['expected_ram'];events=case['events'];is_skip=case['source_return_pc']==0xd0b
  assert len(before)==1321 and len(after)==1321
  assert case['expected'][16]==is_skip and len(events)==case['expected'][12]*2
  assert case['expected'][12]==case['expected'][13]*6912
  assert case['expected'][14]==case['expected'][13]*2304
  assert after[1184]==(127>>case['expected'][13])
  assert case['expected'][15]==after[1184]
  assert all(events[i]<events[i+2] for i in range(0,len(events)-2,2))
  assert all(v<=63 for v in before[1257:1321])
  if is_skip:assert after[0x21]&0x30 and any(before[1257:1321])
  source_io+=case['expected'][12]
assert len(coverage)==84 and source_io==1963008 and source_frames==154280
cr=json.loads((work/'compiled-all-report.json').read_bytes())
assert cr['passed'] and cr['source_entry_vectors']==88 and cr['compiled_executions']==176
covered=[]
for partition in cr['partitions']:
 p=partition['report'];assert p['passed'] and p['ram_bytes']==1321
 assert all(row['intro_poll_errors']==0 and row['intro_poll_cases']==p['source_vector_cases'] for row in p['results'])
 covered.extend(range(p['case_start'],p['case_start']+p['source_vector_cases']))
assert covered==list(range(88))
observer=root/'validation/v319-intro-reveal_skip-callback-observer01'
metadata=json.loads((observer/'report.json').read_bytes());assert metadata['skip'] and metadata['original_source_restored']
assert sha((root.parents[1]/'work/genesis-plus-gx/core/z80/z80.c').read_bytes())==metadata['original_source_sha256']
rom_sha=sha((root/'gaw-megadrive.bin').read_bytes());assert rom_sha=='d3ea2a83ea24ed8a0d3c9857f9fbe70d000a4f73358452c1887f40e78966c56e'
result=dict(passed=True,diagnostic_only=True,production_rom_changed=False,public_version=319,production_rom_sha256=rom_sha,
 source_profile=r,compiled68000_checks=cr,controller_scenarios=84,source_replay_frames=source_frames,
 source_entry_vectors=88,source_skip_vectors=84,compiled_executions=176,source_io_events=source_io,compiled_io_events=source_io*2,
 verification='Normal SMS controller buttons0/8, three live DCEC targets F36/F37/1055, seven reveal stages, both regions. Each observer run replayed in independent PSG observer core with identical frame inputs; every exposed PSG state matches. Native sequence exits at prefetched D0B with the same live RAM/audio, clock/R/latches, mask and every preceding OUT event. Full normal prefixes also retained.',
 input_binding='Per-IRQ status at0137 and actual joy bits observed after IN DC at01BC are diagnostic external inputs. Audio-only IRQs have no joy read. Production must bind live controller and chip state; no recorded-frame overrides.',
 deduplication='Only repeated complete prefixes deduplicated, excluding absolute diagnostic master/IRQ time origins from the key while retaining elapsed differences and original raw representative.42 skip vectors plus2 normal prefixes per region; no emulated data changed.',
 limits=['Controller input sampled at seven scenario thresholds; skip after0..6 complete passes covered. This is not every source cycle or every possible button hold/release pattern.',
         'Exit is D0B entry, not the title cleanup/display after D0B. Full E50 setup and physical publication integration remain open.',
         'No production memory binding, live VDP status producer, raster/PSG deadlines, PCM or hardware certification. Public V319 remains unchanged.'],
 next_action='Translate/setup E50..E75 and title cleanup D0B as needed, bind compact semantic memory and live sprite VDP status, then integrate the continuous native intro with physical publication deadlines.',
 oracle_ram_writes=0,sram_imports=0,archive_manifest='analysis/v319-intro-skip/manifest.json')
target=root/'analysis/v319_intro_skip_report.json';assert not target.exists();target.write_text(json.dumps(result,indent=2)+'\n')
# Clarify inherited prose in the earlier exhaustive raw capture run before freezing.
p=capture/'report.json';old=json.loads(p.read_bytes());old['metadata_clarification']='Normal controller skip capture, not inherited no-input profile wording. Numeric results and raw capture bytes unchanged.';old['verified'][1]=r['verified'][1];old['limits'][1]=r['limits'][1];p.write_text(json.dumps(old,indent=2)+'\n')
paths={target,Path(__file__).resolve()}
for name in ('build_v319_intro_empty_observer.py','build_v319_intro_poll_observer.py','capture_v319_intro_skip.py','validate_v319_intro_poll.py','compile_v319_intro_poll_68k.py','compile_v319_intro_skip_all.py'):paths.add(root/'validation'/name)
for name in ('source_intro_reveal.c','source_intro_reveal.h','source_intro_wait.c','source_intro_wait.h','source_intro_actors.c','source_intro_actors.h','source_intro_fire.c','source_intro_fire.h','source_irq_context.c','source_irq_context.h'):paths.add(root/'megadrive/src'/name)
failed=root/'validation/v319-native-intro-poll-skip01'
for folder in [work,capture,observer,failed]:paths.update(p for p in folder.rglob('*') if p.is_file())
freeze(root,root/'analysis/v319-intro-skip',paths,result,[work,capture,failed],cleanup=True)
print('84 normal controller scenarios and176 compiled68000 executions frozen; V319 unchanged.')
