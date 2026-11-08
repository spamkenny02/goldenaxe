"""Freeze original intro plane clear IO and fast native stable-loop batching."""
import json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'))
from archive_lossless_evidence import freeze,sha
work=root/'validation/v319-native-intro-poll-clear02';old=root/'validation/v319-native-intro-poll-clear01'
p=work/'report.json';r=json.loads(p.read_bytes());assert r['passed'] and r['clear']
assert [row['source_cases'] for row in r['cases']]==[7,7]
for name,digest in r['native_sources'].items():assert sha((root/'megadrive/src'/(name+'.c')).read_bytes())==digest
for region in ('ntsc','pal'):
 cases=json.loads((work/region/'native-cases.json').read_bytes());assert len(cases)==7
 for case in cases:
  events=case['events'];assert len(case['input_ram'])==2025 and case['expected'][6]>0
  assert case['expected'][2:4]==[285732,39172] and case['expected'][12:14]==[6912,2304]
  assert len(events)==13824
  assert all(events[i]<events[i+2] for i in range(0,len(events)-2,2))
  for n in range(2304):
   address=0x4003+n*4
   assert events[n*6+1]==0xbf00|(address&255)
   assert events[n*6+3]==0xbf00|(address>>8)
   assert events[n*6+5]==0xbeff
cr=json.loads((work/'compiled-report.json').read_bytes());assert cr['passed'] and cr['source_vector_cases']==14
assert all(row['intro_poll_errors']==0 and row['intro_poll_cases']==14 for row in cr['results'])
old_cr=json.loads((old/'compiled-report.json').read_bytes());assert old_cr['passed']
rebuild=root/'validation/v319-intro-clear-rebuild02'
assert (rebuild/'project/out/release/rom.bin').read_bytes()==(root/'gaw-megadrive.bin').read_bytes()
for path in (root/'megadrive/src').rglob('*'):
 if path.is_file():assert path.read_bytes()==(rebuild/'project/src'/path.relative_to(root/'megadrive/src')).read_bytes()
old_rebuild=root/'validation/v319-intro-clear-rebuild01';old_report=json.loads((old/'report.json').read_bytes())
assert sha((old_rebuild/'project/src/source_intro_video.c').read_bytes())==old_report['native_sources']['source_intro_video']
observer=root/'validation/v319-intro-plane_clear-callback-observer01'
metadata=json.loads((observer/'report.json').read_bytes());assert metadata['clear'] and metadata['original_source_restored']
assert sha((root.parents[1]/'work/genesis-plus-gx/core/z80/z80.c').read_bytes())==metadata['original_source_sha256']
r['metadata_clarification']='Original E2B plane clear; inherited transfer profile prose corrected. Numeric results and raw captures unchanged.'
r['limits'][1]='Natural E2B plane clear, not EFA transfer or scene composition. Every foreground OUT checked; source VDP status is diagnostic external input.'
p.write_text(json.dumps(r,indent=2)+'\n')
result=dict(passed=True,diagnostic_only=True,production_rom_changed=False,public_version=319,
 production_rom_sha256=sha((root/'gaw-megadrive.bin').read_bytes()),production_rebuild_byte_identical=True,
 source_profile=r,compiled68000_checks=cr,source_entry_vectors=14,compiled_executions=28,
 source_io_events=96768,compiled_io_events=193536,
 implementation='source_intro_plane_clear: E2B..E3E,2304 fourth-plane bytes FF at command4003..63FF, RST28 DI/EI and three OUTs per byte, all original IRQ boundaries and final RET/checkpoint.',
 optimization='Batch stable taken loops124T/17M1 only until the next VINT and with no pending/first/EI delay. Final loop119T. Emit original completion offsets30T/45T/101T within each batch; individual instructions retain boundaries when batching is unavailable. Every OUT and final clock/RAM checked directly against original.',
 diagnostic_throughput=dict(unbatched_frames={row['region']:row['frame'] for row in old_cr['results']},
  batched_frames={row['region']:row['frame'] for row in cr['results']},scope='Same14-vector diagnostic kernel checks, not production game frame rate or physical publication deadlines.'),
 limits=['Natural no-input E2B calls over14000 frames per source region only. Full E50 scene composition and skip entry not tested here.',
         'Source VDP status remains explicit diagnostic IRQ input. No production memory/live sprite status binding or physical video/PSG deadline,PCM or hardware certification.',
         'Public V319 unchanged; new helper remains unselected.'],
 next_action='Compose E50..E75 using EA5 preparation, existing032A pattern decode, newE2B clear, BD3/BFE map decode,7357 placement and EFA transfer. Validate final pattern/map mirror and source timing before integration.',
 oracle_ram_writes=0,sram_imports=0,archive_manifest='analysis/v319-intro-clear/manifest.json')
target=root/'analysis/v319_intro_clear_report.json';assert not target.exists();target.write_text(json.dumps(result,indent=2)+'\n')
paths={target,Path(__file__).resolve()}
for name in ('build_v319_intro_empty_observer.py','build_v319_intro_poll_observer.py','validate_v319_intro_poll.py','compile_v319_intro_poll_68k.py'):paths.add(root/'validation'/name)
for name in ('source_intro_video.c','source_intro_video.h','source_clock.c','source_clock.h','source_intro_wait.c','source_intro_wait.h'):paths.add(root/'megadrive/src'/name)
for folder in [work,old,rebuild,old_rebuild,observer]:paths.update(p for p in folder.rglob('*') if p.is_file())
freeze(root,root/'analysis/v319-intro-clear',paths,result,[work,old,rebuild/'project/out',old_rebuild/'project/out'],cleanup=True)
print('14 source plane clears and28 optimized compiled68000 executions frozen; V319 unchanged.')
