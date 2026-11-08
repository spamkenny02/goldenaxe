"""Freeze native source-poll implementation, direct oracle vectors,68000 results and batching stress."""
import json
import sys
from pathlib import Path
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'tools'))
from archive_lossless_evidence import freeze, sha

base = root / 'validation/v319-native-intro-poll01'
fast = root / 'validation/v319-native-intro-poll02'
observer = root / 'validation/v319-intro-poll-observer01'
rebuild = root / 'validation/v319-intro-wait-rebuild01'
baseline = json.loads((base / 'report.json').read_bytes())
optimized = json.loads((fast / 'report.json').read_bytes())
slow68 = json.loads((base / 'compiled-report.json').read_bytes())
fast68 = json.loads((fast / 'compiled-report.json').read_bytes())
stress = json.loads((fast / 'stress-report.json').read_bytes())
assert all(item['passed'] for item in (baseline, optimized, slow68, fast68, stress))
assert sha((base / 'unbatched-source.c').read_bytes()) == baseline['native_sources']['source_intro_wait']
assert sha((root / 'megadrive/src/source_intro_wait.c').read_bytes()) == optimized['native_sources']['source_intro_wait']
assert baseline['cases'] == optimized['cases']
assert [case['source_poll_reads'] for case in optimized['cases']] == [77629, 95141]
assert sum(case['cases'] for case in stress['cases']) == 5948
assert [case['frame'] for case in slow68['results']] == [2453, 2053]
assert [case['frame'] for case in fast68['results']] == [105, 89]
rom = root / 'gaw-megadrive.bin'
assert (rebuild / 'project/out/release/rom.bin').read_bytes() == rom.read_bytes()
for file in (root / 'megadrive/src').rglob('*'):
    if file.is_file():
        assert file.read_bytes() == (rebuild / 'project/src' / file.relative_to(root / 'megadrive/src')).read_bytes()
build = json.loads((observer / 'report.json').read_bytes())
assert build['original_source_restored']
assert sha((root.parents[1] / 'work/genesis-plus-gx/core/z80/z80.c').read_bytes()) == build['original_source_sha256']
result = dict(passed=True, diagnostic_only=True, production_rom_changed=False,
    production_rom_sha256=sha(rom.read_bytes()), production_rebuild_byte_identical=True,
    natural_source_poll_checks=optimized, compiled68000_unbatched=slow68,
    compiled68000_batched=fast68, batching_boundary_regression=stress,
    implementation='Native source_intro_wait.h/.c: F21 VCounter poll with exact IN/CP/JR boundaries, '
        'mode4/192 counter discontinuities and source IRQ adapter. Failed30T/3M1 and44T/5M1 loops '
        'batch only before the counter condition changes and before VINT. Generic F09/F32/F1E composition '
        'APIs also written, not selected by the published game.',
    coverage='172 natural original-ROM F21/F2B entry/return vectors,172770 actual source port reads, '
        'both regions. Wall time,raster,polls,R,IFF/EI/pending,336 IRQ RAM bytes and400 audio bytes '
        'checked. These natural vectors have no IRQ inside the poll.',
    next_action='Validate F09/F32/F1E continuation APIs against original source snapshots, including '
        'the empty F36 callback first, then actual fire/actor callbacks with source instruction scheduling. '
        'Do not select them in production before native publication deadlines and source raster are validated.',
    limits=['F09 callback/window APIs are compiled but have no direct source-oracle check yet.',
            'Synthetic5948-case IRQ/DI/EI/R/paused/live regression compares to the unbatched native '
            'implementation, not direct emulator execution of those artificial phases.',
            'Compiled kernel completion frames are aggregate diagnostic throughput, not gameplay FPS '
            'or individual routine cycle counts.',
            'First kernel attempt failed header packaging. A second kernel build used the project2MiB '
            'header; the initial2000-frame run stopped before completion with144 cases and no errors. '
            'The completed build was then reused in a new5000-frame run, finishing2453NTSC/2053PAL.',
            'No integration into published intro, asynchronous PSG scheduler, PCM or real hardware proof.'],
    archive_manifest='analysis/v319-native-intro-poll/manifest.json')
report = root / 'analysis/v319_native_intro_poll_report.json'
assert not report.exists()
report.write_text(json.dumps(result, indent=2) + '\n')
scripts = ['build_v319_intro_poll_observer.py','validate_v319_intro_poll.py','compile_v319_intro_poll_68k.py',
           'run_v319_intro_poll_68k.py','stress_v319_intro_poll.py','archive_v319_intro_poll.py']
paths = {root / 'validation' / name for name in scripts}
paths.update([report, root / 'megadrive/src/source_intro_wait.c',root / 'megadrive/src/source_intro_wait.h',
              root / 'tools/build_timing_core.py',root / 'tools/build_private_candidate.ps1',root / 'tools/run_core.py'])
for folder in (base,fast,observer,rebuild):
    paths.update(file for file in folder.rglob('*') if file.is_file())
cleanup = [base / 'kernel/out', base / 'kernel02/out', fast / 'kernel/out', rebuild / 'project/out']
for folder in (base, fast):
    cleanup.append(folder) if folder == base else None
    cleanup.extend(child for child in folder.iterdir() if child.is_dir() and child.name in
                   ('ntsc','pal','compiled-ntsc','compiled-pal','compiled02-ntsc','compiled02-pal'))
# The baseline root contains only diagnostic source/captures; its retained
# generated assembly can be restored from the archive. Production snapshots
# outside this root retain their assembly unchanged.
cleanup.append(fast)
freeze(root, root / 'analysis/v319-native-intro-poll', paths, result, cleanup, cleanup=True)
print('Native source-poll proof frozen; production source rebuild identical to V319.')
