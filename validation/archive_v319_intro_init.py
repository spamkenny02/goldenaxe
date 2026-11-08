"""Freeze source initialization vectors, native results and an unchanged game rebuild."""
import json
import sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'tools'))
from archive_lossless_evidence import freeze,sha
works=[root/'validation'/name for name in ('v319-native-intro-poll-init-second05','v319-native-intro-poll-init-third04')]
profiles=[];compiled=[]
for work,count in zip(works,[2,4]):
 report=json.loads((work/'report.json').read_bytes());assert report['passed'] and report['init']
 assert [r['source_cases'] for r in report['cases']]==[count,count]
 assert all(r['cases_crossing_irq']==0 and r['source_poll_reads']==0 for r in report['cases'])
 for module,digest in report['native_sources'].items():assert sha((root/'megadrive/src'/(module+'.c')).read_bytes())==digest
 for region in ('ntsc','pal'):
  cases=json.loads((work/region/'native-cases.json').read_bytes());assert len(cases)==count
  for case in cases:
   assert len(case['input_ram'])==1193 and case['input_ram'][1184]==0
   assert case['expected'][6]==0 and case['expected'][12]==0
   state=case['expected_ram'];actors=state[416:1184]
   assert state[402]==0
   expected_count=9 if work==works[0] or case['phase'][4]==0xf95 else 6
   assert sum(actors[i*48]==1 for i in range(16))==expected_count
   assert all(actors[i*48]==0 for i in range(expected_count,16))
 profiles.append(report)
 cr=json.loads((work/'compiled-report.json').read_bytes())
 assert cr['passed'] and cr['source_vector_cases']==count*2
 assert all(r['intro_poll_errors']==0 and r['intro_poll_cases']==count*2 for r in cr['results'])
 compiled.append(cr)
rebuild=root/'validation/v319-intro-init-rebuild02'
assert (rebuild/'project/out/release/rom.bin').read_bytes()==(root/'gaw-megadrive.bin').read_bytes()
for path in (root/'megadrive/src').rglob('*'):
 if path.is_file():assert path.read_bytes()==(rebuild/'project/src'/path.relative_to(root/'megadrive/src')).read_bytes()
observers=[root/'validation'/name for name in ('v319-intro-init_actors_second-callback-observer01','v319-intro-init_actors_third-callback-observer01')]
for folder in observers:
 r=json.loads((folder/'report.json').read_bytes())
 assert r['init'] and r['original_source_restored']
 assert sha((root.parents[1]/'work/genesis-plus-gx/core/z80/z80.c').read_bytes())==r['original_source_sha256']
result=dict(passed=True,diagnostic_only=True,production_rom_changed=False,public_version=319,
 production_rebuild_byte_identical=True,production_rom_sha256=sha((root/'gaw-megadrive.bin').read_bytes()),
 source_profiles=profiles,compiled68000_checks=compiled,source_entry_vectors=12,compiled_executions=24,
 implementation='F51/F54 actor initialization: reset DCE2, clear C300..C5FF at individual LDIR boundaries, copy six-byte templates to48-byte records, final conditional RET/checkpoint. Native SourceClock semantic operations, no Z80 interpreter.',
 observation='Two natural F51 calls and four F54 calls per region over14000 no-input frames; F54 includes the common suffix of F51 and the third-scene FE4 template. Nine/six waiting actor records are reproduced exactly. All tracked1193 input/output bytes and400 audio-reader bytes compared.',
 recovery='Initial checker required at least one IRQ and rejected these natural zero-IRQ vectors. Native implementation then missed the final opcode-prefetch checkpoint: wall time matched but R differed by one, and the checker rejected it. Corrected checkpoint passes. Earlier provisional runs retained; final source hashes and compiled kernels use the normalized committed source bytes.',
 limits=['Natural initialization calls have no IRQ crossing; instruction-boundary implementation is not a source-oracle proof of interrupted initialization.',
         'No skipped intro, malformed templates, production memory binding, raster/PSG deadlines, PCM or hardware certification.',
         'Unselected helper: public game remains V319.'],
 next_action='Translate E8B..E9D reveal scheduling and compose with F1E; bind live VDP sprite status and compact memory before production integration.',
 ram_writes=0,sram_imports=0,archive_manifest='analysis/v319-intro-init/manifest.json')
target=root/'analysis/v319_intro_init_report.json';assert not target.exists();target.write_text(json.dumps(result,indent=2)+'\n')
paths={target,Path(__file__).resolve()}
for name in ('build_v319_intro_empty_observer.py','validate_v319_intro_poll.py','compile_v319_intro_poll_68k.py'):paths.add(root/'validation'/name)
for name in ('source_intro_actors.c','source_intro_actors.h','source_clock.c','source_clock.h','source_room_memory.h'):paths.add(root/'megadrive/src'/name)
prior=[p for p in (root/'validation').glob('v319-native-intro-poll-init-*') if p not in works]
prior.append(root/'validation/v319-intro-init-rebuild01')
for folder in [*works,*prior,*observers,rebuild]:paths.update(p for p in folder.rglob('*') if p.is_file())
manifest=freeze(root,root/'analysis/v319-intro-init',paths,result,[*works,*[p for p in prior if 'rebuild' not in p.name],root/'validation/v319-intro-init-rebuild01/project/out',rebuild/'project/out'],cleanup=True)
print('Initialization source/native vectors frozen; public V319 unchanged.')
