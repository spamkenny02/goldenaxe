"""Audit natural fire palette/counter callbacks, source timing and all compiled68000 vectors."""
import json
import sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'tools'))
from archive_lossless_evidence import freeze,sha
callback=root/'validation/v319-native-intro-poll-fire-callback02'
window=root/'validation/v319-native-intro-poll-fire-window03'
profiles=[]
for work,expected_counts in ((callback,[3533,3566]),(window,[30,30])):
 target=work/'report.json';report=json.loads(target.read_bytes())
 assert report['passed'] and report['fire']
 assert [row['source_cases'] for row in report['cases']]==expected_counts
 for row in report['cases']:
  cases=json.loads((work/row['region']/'native-cases.json').read_bytes())
  assert len(cases)==row['source_cases'] and row['cases_crossing_irq']==len(cases)
  assert all(len(c['input_ram'])==416 and c['input_ram'][409:411]==[0x37,0x0f] for c in cases)
  row['counter_value_changes']=sum(c['input_ram'][402]!=c['expected_ram'][402] for c in cases)
  row['palette_changes']=sum(c['input_ram'][337:340]!=c['expected_ram'][337:340] for c in cases)
  row['initial_counter_values']=sorted({c['input_ram'][402] for c in cases})
 # Correct the inherited empty-profile prose before freezing this new report;
 # numeric results/raw data are unchanged and audited above.
 report['metadata_clarification']='F37 fire profile, not inherited F36 empty-profile wording. Raw data/results unchanged.'
 report['verified'][0]+=' Fire palette/counter/mapper/callback snapshots also compared.'
 report['limits'][1]='Selected profile with original F37 fire callback; no actors or skip inputs.'
 target.write_text(json.dumps(report,indent=2)+'\n');profiles.append(report)
compiled=json.loads((callback/'compiled-all-report.json').read_bytes())
compiled_window=json.loads((window/'compiled-report.json').read_bytes())
assert compiled['passed'] and compiled['distinct_source_vectors']==7099 and compiled['compiled_executions']==14198
assert compiled_window['passed'] and compiled_window['source_vector_cases']==60
assert all(row['intro_poll_errors']==0 and row['intro_poll_cases']==60 for row in compiled_window['results'])
rebuild=root/'validation/v319-intro-fire-rebuild01'
assert (rebuild/'project/out/release/rom.bin').read_bytes()==(root/'gaw-megadrive.bin').read_bytes()
for name,digest in profiles[0]['native_sources'].items():
 assert sha((root/'megadrive/src'/(name+'.c')).read_bytes())==digest
for p in (root/'megadrive/src').rglob('*'):
 if p.is_file():assert p.read_bytes()==(rebuild/'project/src'/p.relative_to(root/'megadrive/src')).read_bytes()
observers=[root/'validation'/name for name in ('v319-intro-fire-callback-observer01',
 'v319-intro-fire-window-observer01','v319-intro-fire-window-observer02')]
original=root.parents[1]/'work/genesis-plus-gx/core/z80/z80.c'
for folder in observers:
 metadata=json.loads((folder/'report.json').read_bytes())
 assert metadata['original_source_restored'] and sha(original.read_bytes())==metadata['original_source_sha256']
assert ' -c core/z80/z80.c ' in (observers[-1]/'build.log').read_text()
result=dict(passed=True,diagnostic_only=True,production_rom_changed=False,public_version=319,
 production_rom_sha256=sha((root/'gaw-megadrive.bin').read_bytes()),production_rebuild_byte_identical=True,
 source_profiles=profiles,compiled_callback_checks=compiled,compiled_window_checks=compiled_window,
 distinct_source_vectors=7159,compiled_executions=14318,
 implementation='New native source_intro_fire_callback: F37 branching, byte counter INC/CP6/JR/XOR, '
 'mapper-byte update and BDFF palette address arithmetic/three LDI/RET, all with SourceClock boundaries.',
 scope='Natural F09 and F1E calls with original DCEC=0F37 fire callback,736 IRQ/audio bytes plus '
       'palette/counter/mapper/selected-callback snapshots; exact time,raster,IRQ work,R,latches and palette/counter state. '
       'All source calls cross an IRQ. Both source regions checked and every vector run on compiled68000 in both target regions.',
 observer_recovery='First window DLL linked a stale callback object because its build plan omitted recompiling z80.c. '
       'Runtime entry-PC assertion rejected its capture; no pass report was issued. New isolated window revision2 '
       'uses explicit make-W core/z80/z80.c. Source body, expected entry PC and original-state parity then checked. '
       'Initial host harness compile also rejected an SGDK string.h conflict; fixed using GCC builtin memset in the harness.',
 next_action='Translate and independently source-check intro actor/SAT callbacks1055/104A/1061/108B using '
       'SourceClock and full RAM overlays. Test skip-D0B separately, then compose source reveal row timing and bind native '
       'publication deadlines; no frame or counter overrides.',
 limits=['No published intro integration or audio emission change. This is native semantic source scheduling.',
         'No actor callback, skip input, physical MD raster publication, PCM or console hardware certification.'],
 ram_writes=0,sram_imports=0,archive_manifest='analysis/v319-intro-fire/manifest.json')
target=root/'analysis/v319_intro_fire_report.json';assert not target.exists()
target.write_text(json.dumps(result,indent=2)+'\n')
scripts=['archive_v319_intro_fire.py','compile_v319_intro_fire_all.py','build_v319_intro_empty_observer.py',
 'build_v319_intro_poll_observer.py','validate_v319_intro_poll.py','compile_v319_intro_poll_68k.py']
paths={root/'validation'/name for name in scripts};paths.add(target)
for name in ('source_intro_fire.c','source_intro_fire.h','source_intro_wait.c','source_intro_wait.h','source_room_memory.h'):
 paths.add(root/'megadrive/src'/name)
for name in ('build_timing_core.py','build_private_candidate.ps1','run_core.py'):paths.add(root/'tools'/name)
workdirs=[callback,window,rebuild,*observers]
workdirs += [root/'validation'/name for name in ('v319-native-intro-poll-fire-callback01',
 'v319-native-intro-poll-fire-window01','v319-native-intro-poll-fire-window02')]
for folder in workdirs:paths.update(p for p in folder.rglob('*') if p.is_file())
cleanup=[folder for folder in workdirs if folder not in observers and folder!=rebuild]
cleanup.append(rebuild/'project/out')
freeze(root,root/'analysis/v319-intro-fire',paths,result,cleanup,cleanup=True)
print('7159 source fire vectors and14318 compiled68000 executions frozen; public V319 unchanged.')
