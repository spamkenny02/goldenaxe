"""Audit full EFA transfer and EA5 blank-map/palette setup against the original ROM."""
import json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'))
from archive_lossless_evidence import freeze,sha
works=[root/'validation'/name for name in ('v319-native-intro-poll-transfer03','v319-native-intro-poll-prepare02')]
profiles=[];compiled=[];image=(root/'input/original.sms').read_bytes();io_count=0
for work,count,prepare in zip(works,[14,7],[False,True]):
 r=json.loads((work/'report.json').read_bytes());assert r['passed'] and r['transfer'] and r['prepare']==prepare
 assert [row['source_cases'] for row in r['cases']]==[count,count]
 for name,digest in r['native_sources'].items():assert sha((root/'megadrive/src'/(name+'.c')).read_bytes())==digest
 for region in ('ntsc','pal'):
  cases=json.loads((work/region/'native-cases.json').read_bytes());assert len(cases)==count
  for case in cases:
   before=case['input_ram'];after=case['expected_ram'];events=case['events']
   assert len(before)==2025 and len(after)==2025 and len(events)==1540
   assert case['expected'][6]>0 and case['expected'][12:14]==[770,768]
   assert events[1]==0xbf00 and events[3]==0xbf78
   assert all(events[i]<events[i+2] for i in range(0,len(events)-2,2))
   assert all(events[i+1]>>8==0xbe for i in range(4,len(events),2))
   payload=bytes(events[i+1]&255 for i in range(4,len(events),2))
   if prepare:
    address=before[1184]|before[1185]<<8;assert address in (0x9d70,0xa655,0xaf1f)
    assert payload==b'\xfa\x09'*384 and bytes(after[1192:1960])==payload
    assert after[1184]|after[1185]<<8==address+4
    assert bytes(after[336:340])==image[0x18000+address-0x8000:0x18000+address-0x8000+4]
    assert not any(after[340:352]) and after[408]==6
   else:assert payload==bytes(before[1192:1960]) and after[1192:1960]==before[1192:1960]
   io_count+=770
 profiles.append(r)
 cr=json.loads((work/'compiled-report.json').read_bytes());assert cr['passed'] and cr['transfer'] and cr['source_vector_cases']==count*2
 assert all(row['intro_poll_errors']==0 and row['intro_poll_cases']==count*2 for row in cr['results'])
 compiled.append(cr)
assert io_count==32340
rebuild=root/'validation/v319-intro-transfer-rebuild02'
assert (rebuild/'project/out/release/rom.bin').read_bytes()==(root/'gaw-megadrive.bin').read_bytes()
for path in (root/'megadrive/src').rglob('*'):
 if path.is_file():assert path.read_bytes()==(rebuild/'project/src'/path.relative_to(root/'megadrive/src')).read_bytes()
observers=[root/'validation'/name for name in ('v319-intro-intro_transfer-callback-observer01','v319-intro-intro_prepare-callback-observer01')]
for folder in observers:
 metadata=json.loads((folder/'report.json').read_bytes());assert metadata['transfer'] and metadata['original_source_restored']
 assert sha((root.parents[1]/'work/genesis-plus-gx/core/z80/z80.c').read_bytes())==metadata['original_source_sha256']
result=dict(passed=True,diagnostic_only=True,production_rom_changed=False,public_version=319,
 production_rom_sha256=sha((root/'gaw-megadrive.bin').read_bytes()),production_rebuild_byte_identical=True,
 source_profiles=profiles,compiled68000_checks=compiled,source_entry_vectors=42,compiled_executions=84,
 source_io_events=32340,compiled_io_events=64680,
 implementation='New source_intro_video.c/.h. Full EFA transfer composes F1E window/callback, fixed D600..D8FF to logical7800 copy via384/RST28/OUTI, then falls through F09 wait/callback and returns. EA5 preparation fills768 bytes with FA09, calls EFA, clears16 palette bytes, maps bank6 and copies four colors from restored source HL. All instruction/IRQ boundaries retained.',
 verification='Natural original entry and actual caller-return snapshots, both regions14000 frames each. Every OUT instruction completion timestamp, derived raster, port/value and all2025 tracked bytes plus400 audio-reader bytes compared. All42 source entry vectors cross IRQs. Header addresses9D70/A655/AF1F and F36/F37/1055 callbacks observed. All vectors execute compiled68000 on both target regions.',
 status_binding='Captured original status at each0137 entry remains diagnostic external input. It must be computed from live source sprite/chip state before production use.',
 recovery='First transfer-only implementation already matched and compiled. Appending EA5 preparation first produced a host preprocessor error for hexadecimal token0x15fe+n; added whitespace, then both final profiles and kernels passed. Failed logs and earlier rebuild/source retained.',
 limits=['Natural no-input EFA and EA5 only; skip inside these new entry profiles is not checked here.',
         'Semantic IO sink, not physical MD video publication. E50 setup, pattern decode0E2B/032A and map decode0BD3/7357 composition remain open.',
         'No live production VDP status/memory binding, raster/PSG deadline, PCM or hardware certification. Public V319 unchanged.'],
 next_action='Compose E50..E75 scene setup around EA5/EFA, reuse source_pattern_decode for032A, translate map decode and strided placement as needed; bind compact memory/live source sprite status and physical publication deadlines before native intro integration.',
 oracle_ram_writes=0,sram_imports=0,archive_manifest='analysis/v319-intro-transfer/manifest.json')
target=root/'analysis/v319_intro_transfer_report.json';assert not target.exists();target.write_text(json.dumps(result,indent=2)+'\n')
paths={target,Path(__file__).resolve()}
for name in ('build_v319_intro_empty_observer.py','build_v319_intro_poll_observer.py','validate_v319_intro_poll.py','compile_v319_intro_poll_68k.py'):paths.add(root/'validation'/name)
for name in ('source_intro_video.c','source_intro_video.h','source_intro_reveal.c','source_intro_reveal.h','source_intro_wait.c','source_intro_wait.h','source_intro_actors.c','source_intro_actors.h','source_intro_fire.c','source_intro_fire.h','source_room_memory.h'):paths.add(root/'megadrive/src'/name)
prior=[root/'validation'/name for name in ('v319-native-intro-poll-transfer01','v319-native-intro-poll-transfer02','v319-native-intro-poll-prepare01')]
old_rebuild=root/'validation/v319-intro-transfer-rebuild01'
for folder in [*works,*prior,*observers,rebuild,old_rebuild]:paths.update(p for p in folder.rglob('*') if p.is_file())
freeze(root,root/'analysis/v319-intro-transfer',paths,result,[*works,*prior,rebuild/'project/out',old_rebuild/'project/out'],cleanup=True)
print('42 source transfer/setup entries and84 compiled68000 executions frozen; V319 unchanged.')
