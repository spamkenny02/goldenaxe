"""Audit direct original empty-callback IRQ continuations and their compiled68000 vectors."""
import json
import sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'tools'))
from archive_lossless_evidence import freeze,sha
callback=root/'validation/v319-native-intro-poll-callback01'
window=root/'validation/v319-native-intro-poll-window01'
host_callback=json.loads((callback/'report.json').read_bytes())
host_window=json.loads((window/'report.json').read_bytes())
assert host_callback['passed'] and host_window['passed']
assert [case['source_cases'] for case in host_callback['cases']]==[986,994]
assert [case['source_cases'] for case in host_window['cases']]==[36,36]
assert all(case['cases_crossing_irq']==case['source_cases'] for report in (host_callback,host_window) for case in report['cases'])
compiled=[json.loads((callback/'compiled-ntsc-report.json').read_bytes()),
          json.loads((callback/'compiled-pal-report.json').read_bytes()),
          json.loads((window/'compiled-report.json').read_bytes())]
assert [report['source_vector_cases'] for report in compiled]==[986,994,72]
for report in compiled:
 assert report['passed'] and len(report['results'])==2
 assert all(row['intro_poll_done']==1 and row['intro_poll_errors']==0 and
            row['intro_poll_cases']==report['source_vector_cases'] for row in report['results'])
for report in (host_callback,host_window):
 for name,digest in report['native_sources'].items():
  assert sha((root/'megadrive/src'/(name+'.c')).read_bytes())==digest
source=root.parents[1]/'work/genesis-plus-gx/core/z80/z80.c'
observers=[root/'validation'/('v319-intro-empty-'+profile+'-observer01') for profile in ('callback','window')]
for folder in observers:
 report=json.loads((folder/'report.json').read_bytes())
 assert report['passed'] and report['original_source_restored']
 assert report['original_source_sha256']==sha(source.read_bytes())
result=dict(passed=True,diagnostic_only=True,production_rom_changed=False,
 production_rom_sha256=sha((root/'gaw-megadrive.bin').read_bytes()),callback_target=0xf36,
 source_callback_checks=host_callback,source_window_checks=host_window,compiled68000_checks=compiled,
 distinct_source_vectors=2052,compiled_executions=4104,
 coverage='Natural original F09/caller-return and F1E/caller-return snapshots, with F36 empty callback. '
  'All2052 source cases cross IRQs. Exact wall/raster/IRQ work,R,IFF/EI/pending,336 IRQ RAM and400 reader '
  'bytes and complete polling counts. Original live source audio retained, no injected RAM or source ROM edits.',
 next_action='Translate and source-check F37 fire callback, then1055/104A actor callbacks with continuous '
  'source instruction scheduling and live palette/SAT memory; use those in the verified F09/F1E continuation. '
  'Check skip-D0B input branch separately. Then bind native video deadlines; no recorded frame overrides.',
 build_note='PAL-vector kernel2 first link failed due GCC/MSYS temporary path conversion. Saved failure log, '
  'relinked the same completed object tree with per-command TMPDIR/TMP/TEMP set to the existing current '
  'project directory. Reused that built kernel in a separate runtime verifier. No game code or oracle changed.',
 limits=['Empty callback only: original DCEC points to F36. Fire/actors, skip inputs and natural full-game contexts remain open.',
         'Compiled kernels validate native semantic state/work, not physical MD video/audio deadline publication or waveform.',
         'Published ROM unchanged; source_intro_wait was already present and remains unselected by the game.'],
 ram_writes=0,sram_imports=0,archive_manifest='analysis/v319-intro-empty/manifest.json')
target=root/'analysis/v319_intro_empty_report.json';assert not target.exists()
target.write_text(json.dumps(result,indent=2)+'\n')
paths={Path(__file__).resolve(),target,root/'validation/build_v319_intro_empty_observer.py',
 root/'validation/validate_v319_intro_poll.py',root/'validation/compile_v319_intro_poll_68k.py',
 root/'validation/run_v319_intro_empty_pal68k.py',root/'validation/build_v319_intro_poll_observer.py',
 root/'tools/run_core.py',root/'tools/build_timing_core.py',root/'tools/build_private_candidate.ps1'}
for name in ('source_intro_wait.c','source_intro_wait.h','source_wait.c','source_wait_restore.c',
             'source_clock.c','source_irq_context.c','source_irq.c'):
 paths.add(root/'megadrive/src'/name)
for folder in (callback,window,*observers):
 paths.update(p for p in folder.rglob('*') if p.is_file())
freeze(root,root/'analysis/v319-intro-empty',paths,result,[callback,window],cleanup=True)
print('2052 direct empty-callback source vectors;4104 compiled68000 executions audited. Published V319 unchanged.')
