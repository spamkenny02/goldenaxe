"""Audit every source reveal OUT and freeze the complete bounded native kernels."""
import json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'))
from archive_lossless_evidence import freeze,sha
work=root/'validation/v319-native-intro-poll-reveal05'
r=json.loads((work/'report.json').read_bytes());assert r['passed'] and r['reveal']
assert [row['source_cases'] for row in r['cases']]==[56,56]
for name,digest in r['native_sources'].items():assert sha((root/'megadrive/src'/(name+'.c')).read_bytes())==digest
for region in ('ntsc','pal'):
 cases=json.loads((work/region/'native-cases.json').read_bytes());assert len(cases)==56
 for case in cases:
  assert len(case['input_ram'])==1193 and case['expected'][6]>0
  assert len(case['events'])==13824 and case['expected'][12]==6912
  assert case['input_ram'][411:415]==[3,64,4,0]
  assert case['expected_ram'][411:415]==[3,100,4,0]
  assert case['expected_ram'][415]==case['input_ram'][415]
  assert case['expected'][2]==230400 and case['expected'][3]==41472
  events=case['events'];assert all(events[i]<events[i+2] for i in range(0,len(events)-2,2))
  assert all(events[i+1]>>8==(0xbe if i//2%3==2 else 0xbf) for i in range(0,len(events),2))
cr=json.loads((work/'compiled-all-report.json').read_bytes())
assert cr['passed'] and cr['source_entry_vectors']==112 and cr['compiled_executions']==224
covered=[]
for partition in cr['partitions']:
 p=partition['report'];assert p['passed'] and p['reveal']
 assert all(row['intro_poll_errors']==0 and row['intro_poll_cases']==p['source_vector_cases'] for row in p['results'])
 covered.extend(range(p['case_start'],p['case_start']+p['source_vector_cases']))
assert covered==list(range(112))
rebuild=root/'validation/v319-intro-reveal-rebuild01'
assert (rebuild/'project/out/release/rom.bin').read_bytes()==(root/'gaw-megadrive.bin').read_bytes()
for path in (root/'megadrive/src').rglob('*'):
 if path.is_file():assert path.read_bytes()==(rebuild/'project/src'/path.relative_to(root/'megadrive/src')).read_bytes()
observer=root/'validation/v319-intro-reveal-callback-observer01'
metadata=json.loads((observer/'report.json').read_bytes())
assert metadata['reveal'] and metadata['original_source_restored']
assert sha((root.parents[1]/'work/genesis-plus-gx/core/z80/z80.c').read_bytes())==metadata['original_source_sha256']
result=dict(passed=True,diagnostic_only=True,production_rom_changed=False,public_version=319,
 production_rom_sha256=sha((root/'gaw-megadrive.bin').read_bytes()),production_rebuild_byte_identical=True,
 source_profile=r,compiled68000_checks=cr,source_entry_vectors=112,compiled_executions=224,
 source_io_events=774144,compiled_io_events=1548288,
 implementation='New source_intro_reveal.c/.h: E8B..E9D plane reveal pass, alternate-HL address/DE step and foreground E rotations, paired DI/EI and precise SourceClock IRQ boundaries. Semantic OUT sink only; no hardware publication.',
 verification='Every BF low/high address byte and BE data byte, original instruction-completion elapsed time and derived raster compared. All1193 tracked bytes,400 reader bytes, total wall/IRQ work, R and IFF/EI/pending match original. Source event timestamps are instruction-entry observation plus12T for OUT, not an external bus trace.',
 optimization='Stable100T/18M1 loops batch only before VINT and with no first-fetch/EI/pending boundary. Other loops retain individual instructions. Every emitted time/value and final clock/RAM is checked against original, not an average frame budget.',
 status_binding='Original independently observed VDP status at each0137 IRQ entry is an explicit diagnostic input; must be computed from the live sprite model before production integration.',
 recovery='First host build rejected a signedness warning. Next checker rejected a4-byte packed-record offset error; events begin immediately after IRQ status, before record tail padding. Corrected byte layout passes. Slow and intermediate native binaries retained as provisional evidence.',
 limits=['Natural no-input112 pass entries over14000 source frames per region; all cross IRQ. No intro skip/composed F1E entry tested here.',
         'No production memory binding, live VDP status producer, physical raster/PSG deadlines, PCM or hardware certification.',
         'Diagnostic kernel frame counts include checking overhead and are not game frame rate. Public V319 does not select this routine.'],
 next_action='Compose F1E plus reveal and seven-pass D shift/branch loop; translate setup/publication as needed, bind compact memory and live source VDP status before native intro integration.',
 ram_writes=0,sram_imports=0,archive_manifest='analysis/v319-intro-reveal/manifest.json')
target=root/'analysis/v319_intro_reveal_report.json';assert not target.exists();target.write_text(json.dumps(result,indent=2)+'\n')
paths={target,Path(__file__).resolve()}
for name in ('build_v319_intro_empty_observer.py','build_v319_intro_poll_observer.py','validate_v319_intro_poll.py','compile_v319_intro_poll_68k.py','compile_v319_intro_reveal_all.py'):paths.add(root/'validation'/name)
for name in ('source_intro_reveal.c','source_intro_reveal.h','source_clock.c','source_clock.h','source_irq_context.c','source_irq_context.h'):paths.add(root/'megadrive/src'/name)
prior=[p for p in (root/'validation').glob('v319-native-intro-poll-reveal*') if p!=work]
for folder in [work,*prior,rebuild,observer]:paths.update(p for p in folder.rglob('*') if p.is_file())
freeze(root,root/'analysis/v319-intro-reveal',paths,result,[work,*prior,rebuild/'project/out'],cleanup=True)
print('All112 source reveal vectors,774144 exact OUT events and224 native executions frozen.')
