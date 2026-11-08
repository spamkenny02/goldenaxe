"""Audit composed source intro reveal sequences, all original IO and native kernels."""
import json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'))
from archive_lossless_evidence import freeze,sha
work=root/'validation/v319-native-intro-poll-sequence01'
r=json.loads((work/'report.json').read_bytes());assert r['passed'] and r['sequence']
assert [row['source_cases'] for row in r['cases']]==[7,7]
for name,digest in r['native_sources'].items():assert sha((root/'megadrive/src'/(name+'.c')).read_bytes())==digest
callbacks=set()
for region in ('ntsc','pal'):
 cases=json.loads((work/region/'native-cases.json').read_bytes());assert len(cases)==7
 for case in cases:
  before=case['input_ram'];after=case['expected_ram'];events=case['events']
  assert len(before)==1257 and len(after)==1257
  assert before[1184]==127 and after[1184]==0 and before[1192]==40
  assert after[411:416]==[3,100,4,0,0]
  assert len(events)==110592 and case['expected'][6]==40
  assert case['expected'][12:16]==[55296,8,18432,0]
  assert all(events[i]<events[i+2] for i in range(0,len(events)-2,2))
  assert sum(events[i+1]>>8==0xbe for i in range(0,len(events),2))==18432
  callbacks.add(before[409]|before[410]<<8)
assert callbacks=={0xf36,0xf37,0x1055}
cr=json.loads((work/'compiled-all-report.json').read_bytes())
assert cr['passed'] and cr['source_entry_vectors']==14 and cr['compiled_executions']==28
covered=[]
for partition in cr['partitions']:
 p=partition['report'];assert p['passed'] and p['sequence']
 assert all(row['intro_poll_errors']==0 and row['intro_poll_cases']==p['source_vector_cases'] for row in p['results'])
 covered.extend(range(p['case_start'],p['case_start']+p['source_vector_cases']))
assert covered==list(range(14))
rebuild=root/'validation/v319-intro-sequence-rebuild01'
assert (rebuild/'project/out/release/rom.bin').read_bytes()==(root/'gaw-megadrive.bin').read_bytes()
for path in (root/'megadrive/src').rglob('*'):
 if path.is_file():assert path.read_bytes()==(rebuild/'project/src'/path.relative_to(root/'megadrive/src')).read_bytes()
observer=root/'validation/v319-intro-reveal_sequence-callback-observer01'
metadata=json.loads((observer/'report.json').read_bytes())
assert metadata['sequence'] and metadata['original_source_restored'] and metadata['entry_pc']==0xe79
assert sha((root.parents[1]/'work/genesis-plus-gx/core/z80/z80.c').read_bytes())==metadata['original_source_sha256']
result=dict(passed=True,diagnostic_only=True,production_rom_changed=False,public_version=319,
 production_rom_sha256=sha((root/'gaw-megadrive.bin').read_bytes()),production_rebuild_byte_identical=True,
 source_profile=r,compiled68000_checks=cr,source_entry_vectors=14,compiled_executions=28,
 source_io_events=774144,compiled_io_events=1548288,
 implementation='New source_intro_reveal_sequence: E79..EA2, prefetched EA4 exit. One continuous SourceClock composes alternate-register setup, mask rotations, F1E window and current DCEC callback, full E8B reveal pass and SRL D/JR carry loop. No pre-recorded frame timings.',
 verification='Fourteen original natural complete sequences on both source regions. Every OUT port/value/relative instruction-completion time and derived raster compared. All1257 tracked bytes and400 audio-reader bytes, wall/IRQ work, R and latches match. Each sequence crosses40 IRQs and emits55296 OUT events across8 passes. Native diagnostic dispatch selects F36/F37/1055 from live semantic DCEC; 104A supported but not observed here.',
 correction='Earlier next-step notes called this a seven-pass loop. Original D=7F shifts through seven carry-set masks, then executes an eighth pass at D=0 before carry clears. Eight passes and final mask zero are directly observed and required by this checker.',
 status_binding='Independent original VDP status at each0137 entry remains explicit diagnostic IRQ input; not permitted as a recorded-frame substitute in production.',
 limits=['Natural no-input sequence entry E79 with D=7F, not setup E50..E75 or skip input/EA4 RET.',
         'No production memory binding, live VDP status producer, raster/PSG publication deadlines, PCM or hardware certification.',
         'Diagnostic kernel frame counts include checking overhead and are not game frame rate. Public V319 does not select these new routines.'],
 next_action='Cover intro skip composition and translate setup E50..E75 as necessary, reuse existing native decompression where sound, bind compact semantic memory and live sprite VDP status, then integrate with physical publication deadlines.',
 oracle_ram_writes=0,sram_imports=0,archive_manifest='analysis/v319-intro-sequence/manifest.json')
target=root/'analysis/v319_intro_sequence_report.json';assert not target.exists();target.write_text(json.dumps(result,indent=2)+'\n')
paths={target,Path(__file__).resolve()}
for name in ('build_v319_intro_empty_observer.py','build_v319_intro_poll_observer.py','validate_v319_intro_poll.py','compile_v319_intro_poll_68k.py','compile_v319_intro_sequence_all.py'):paths.add(root/'validation'/name)
for name in ('source_intro_reveal.c','source_intro_reveal.h','source_intro_wait.c','source_intro_wait.h','source_intro_actors.c','source_intro_actors.h','source_intro_fire.c','source_intro_fire.h','source_clock.c','source_clock.h','source_irq_context.c','source_irq_context.h'):paths.add(root/'megadrive/src'/name)
for folder in [work,rebuild,observer]:paths.update(p for p in folder.rglob('*') if p.is_file())
freeze(root,root/'analysis/v319-intro-sequence',paths,result,[work,rebuild/'project/out'],cleanup=True)
print('All14 complete sequences and28 native executions frozen; V319 unchanged.')
