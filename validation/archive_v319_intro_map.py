"""Freeze original intro map decode/place states, timing and all compiled vectors."""
import json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'))
from archive_lossless_evidence import freeze,sha
works=[root/'validation'/name for name in ('v319-native-intro-poll-mapdecode03','v319-native-intro-poll-mapplace03')]
profiles=[];compiled=[];crossings=0;banks=set()
for work,mode in zip(works,['decode','place']):
 p=work/'report.json';r=json.loads(p.read_bytes());assert r['passed'] and r['map']==mode
 assert [row['source_cases'] for row in r['cases']]==[7,7]
 for name,digest in r['native_sources'].items():assert sha((root/'megadrive/src'/(name+'.c')).read_bytes())==digest
 for region in ('ntsc','pal'):
  cases=json.loads((work/region/'native-cases.json').read_bytes());assert len(cases)==7
  for case in cases:
   before=case['input_ram'];after=case['expected_ram'];assert len(before)==5097 and len(after)==5097
   assert case['events']==[] and case['expected'][12]==0
   crossings+=bool(case['expected'][6])
   if mode=='decode':
    banks.add(before[408]);assert before[1186:1188]==[0,201] and after[1186:1190]==[2,201,2,0]
    assert before[1192:1960]==after[1192:1960]
    assert case['expected'][13] in (576,1278) and case['expected'][14] in (242,281,728)
   else:
    assert before[1184:1190]==[0,201,8,214,12,48]
    assert after[1184:1190]==[64,203,8,217,0,48]
    assert case['expected'][13:15]==[576,0]
    expected=before[1192:1960].copy()
    for row in range(12):expected[8+row*64:8+row*64+48]=before[3240+row*48:3240+(row+1)*48]
    assert after[1192:1960]==expected and before[1960:5032]==after[1960:5032]
 cr=json.loads((work/'compiled-report.json').read_bytes());assert cr['passed'] and cr['map']==mode and cr['source_vector_cases']==14
 assert all(row['intro_poll_errors']==0 and row['intro_poll_cases']==14 for row in cr['results']);compiled.append(cr)
 r['metadata_clarification']='BD3/BFE map decode or7357 placement; inherited transfer-profile prose corrected, all numeric results/raw captures unchanged.'
 r['limits'][1]='Intro map decode/place only, selected original buffer contracts. ROM bank6/7 preserved as data source independently of the audio bank6 pointer.'
 r['verified'][0]+=' Scratch D100..D5FF, decoded C900..CFFF and placed D600..D8FF, plus HL/DE/BC snapshots, all compared.'
 p.write_text(json.dumps(r,indent=2)+'\n');profiles.append(r)
assert banks=={6,7} and crossings==13
rebuild=root/'validation/v319-intro-map-rebuild01'
assert (rebuild/'project/out/release/rom.bin').read_bytes()==(root/'gaw-megadrive.bin').read_bytes()
for path in (root/'megadrive/src').rglob('*'):
 if path.is_file():assert path.read_bytes()==(rebuild/'project/src'/path.relative_to(root/'megadrive/src')).read_bytes()
observers=[root/'validation'/name for name in ('v319-intro-map_decode-callback-observer01','v319-intro-map_place-callback-observer01','v319-intro-map_decode-callback-observer02','v319-intro-map_place-callback-observer02')]
for folder in observers:
 metadata=json.loads((folder/'report.json').read_bytes());assert metadata['original_source_restored']
 assert sha((root.parents[1]/'work/genesis-plus-gx/core/z80/z80.c').read_bytes())==metadata['original_source_sha256']
result=dict(passed=True,diagnostic_only=True,production_rom_changed=False,public_version=319,
 production_rom_sha256=sha((root/'gaw-megadrive.bin').read_bytes()),production_rebuild_byte_identical=True,
 source_profiles=profiles,compiled68000_checks=compiled,source_entry_vectors=28,compiled_executions=56,
 source_vectors_crossing_irq=crossings,
 implementation='New source_intro_map.c/.h: BD3 literal/increment stream to D100 scratch, BFE two interleaved literal/repeated planes to C900, and7357 strided row placement to D600. Includes native SourceClock instruction/IRQ timing and RET/checkpoint; live semantic memory aliases, no Z80 interpreter.',
 verification='Seven decode entries and seven48-byte/12-row placement entries per source region over14000 no-input frames. Every5097 tracked byte plus400 reader bytes, HL/DE/BC outputs, wall/IRQ time,R and latches match original.13 vectors cross IRQ,15 do not. Every vector executes compiled68000 on both target regions with zero errors.',
 recovery='Initial repeated-plane branch moved LD A,(HL) outside its loop; original repeats this read, so timing/R checker rejected it. Corrected per-byte read. Another original map uses ROM bank7, not bank6; rejected wrong data source replaced by explicit immutable mapped-bank pointer, leaving the audio reader bank6 pointer unchanged. Natural placement zero-IRQ vectors also exposed an overly strict diagnostic precondition, now corrected.',
 limits=['Original intro decode destination C900 and7357 source C900,destination D608,width48,height12 only. General malformed streams, zero dimensions and every capacity edge are not source-oracle tested.',
         'No skip inputs, full scene-loader composition, live production sprite status/memory binding or physical video/audio publication. VDP status remains diagnostic external input.',
         'No PCM or hardware certification. Public V319 remains unchanged.'],
 next_action='Translate0E2B plane clear and compose E50..E75 around existing032A pattern decode, EA5 preparation, BD3/BFE map decode,7357 placement and EFA publication. Then bind compact semantic memory/live sprite VDP status and MD publication deadlines.',
 oracle_ram_writes=0,sram_imports=0,archive_manifest='analysis/v319-intro-map/manifest.json')
target=root/'analysis/v319_intro_map_report.json';assert not target.exists();target.write_text(json.dumps(result,indent=2)+'\n')
paths={target,Path(__file__).resolve()}
for name in ('build_v319_intro_empty_observer.py','build_v319_intro_poll_observer.py','validate_v319_intro_poll.py','compile_v319_intro_poll_68k.py'):paths.add(root/'validation'/name)
for name in ('source_intro_map.c','source_intro_map.h','source_intro_video.c','source_intro_video.h','source_room_memory.h','source_clock.c','source_clock.h'):paths.add(root/'megadrive/src'/name)
prior=[root/'validation'/name for name in ('v319-native-intro-poll-mapdecode01','v319-native-intro-poll-mapdecode02','v319-native-intro-poll-mapplace01','v319-native-intro-poll-mapplace02')]
for folder in [*works,*prior,*observers,rebuild]:paths.update(p for p in folder.rglob('*') if p.is_file())
freeze(root,root/'analysis/v319-intro-map',paths,result,[*works,*prior,rebuild/'project/out'],cleanup=True)
print('28 source map entries and56 compiled68000 executions frozen; V319 unchanged.')
