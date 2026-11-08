"""Freeze rejected reveal experiments and the source row-boundary finding."""
import json
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'tools'))
from archive_lossless_evidence import freeze, sha
from validate_playable_sprite_limit import symbols

baseline = root / 'versions/v0319-d3ea2a83/gaw-megadrive-v0319.bin'
digest = sha(baseline.read_bytes())
assert sha((root / 'gaw-megadrive.bin').read_bytes()) == digest
assert (root / 'megadrive/src/intro.inc').read_bytes() == subprocess.check_output(
    ['git', 'show', 'HEAD:megadrive/src/intro.inc'], cwd=root)
names = ['v319-reveal-irq-budget01', 'v319-reveal-row-tail01', 'v319-reveal-audio-rows01']
paths = {Path(__file__).resolve()}
cleanup = []
cases = []
for name in names:
    work = root / 'validation' / name
    rom = work / 'project/out/release/rom.bin'
    sy = symbols(rom.with_name('symbol.txt'))
    comparisons = []
    for region in ('ntsc', 'pal'):
        folder = work / ('compare-' + region)
        r = json.loads((folder / 'report.json').read_bytes())
        assert r['frames'] == 14000 and r['md_sha256'] == sha(rom.read_bytes())
        assert r['baseline_sha256'] == digest and r['ram_writes'] == r['sram_imports'] == 0
        raw = (folder / 'candidate/ram_14000.bin').read_bytes()
        word = lambda n: int.from_bytes(bytes(raw[(sy[n] + i) ^ 1] for i in range(2)), 'big')
        assert not word('sound_unhandled_command') and not word('intro_abort')
        comparisons.append(dict(region=region, totals=r['totals'], improved_pixels=r['improved_pixels'],
                                degraded_pixels=r['degraded_pixels'],
                                no_source_pixel_regression=r['no_source_pixel_regression']))
        cleanup.append(folder)
    assert not all(c['no_source_pixel_regression'] for c in comparisons)
    cases.append(dict(name=name, rom_sha256=sha(rom.read_bytes()), promoted=False, comparisons=comparisons))
    paths.update(p for p in work.rglob('*') if p.is_file())
    cleanup.append(work / 'project/out')
    if (work / 'first-plane3').exists():
        cleanup.append(work / 'first-plane3')
probe_path = root / 'validation/v319-reveal-row-tail01/first-plane3/report.json'
probe = json.loads(probe_path.read_bytes())
assert probe['passed'] and all(c['first_slice_all_2304_source_bytes_exact'] for c in probe['cases'])
for name in ('prepare_v319_reveal_irq_budget.py', 'prepare_v319_reveal_row_tail.py',
             'prepare_v319_reveal_audio_rows.py', 'probe_v319_reveal_row_tail.py'):
    paths.add(Path(__file__).with_name(name))
for name in ('compare_boot_to_sms.py', 'run_core.py', 'build_private_candidate.ps1'):
    paths.add(root / 'tools' / name)
result = dict(passed=False, diagnostic_only=True, promoted=False, public_rom_unchanged=True,
              public_rom_sha256=digest, cases=cases, first_slice_probe=probe,
              observations=[
                  'Source first-slice plane3 contains182 changed rows; V319 rounds this to180.',
                  'The row-tail prototype reproduces all2304 physical plane3 bytes at the first slice '
                  'and completed pass in both regions, with selected native logic fields unchanged.',
                  'Physical VRAM-boundary equality alone does not prove source-visible raster equality: '
                  'the isolated row-tail fix increases total visible errors slightly in both regions.',
                  'F1E calls F09/B95 before waiting for V112; charging its full IRQ again between '
                  'copy slices is incorrect and seriously degrades NTSC.',
                  'Audio-only per-slice work without sub-instruction/row publication phase also fails '
                  'the source-pixel gate. Do not promote any of these three candidates.',
                  'Next timing work needs continuous source instruction phase and visible-pattern '
                  'publication timing, rather than another fixed frame or budget adjustment.'],
              ram_writes=0, sram_imports=0,
              scope='Three isolated native experiments, every boot frame compared over14000 frames '
                    'per region. Rejected development binaries, not numbered releases or gameplay changes.')
report = root / 'analysis/v319_reveal_experiments_report.json'
assert not report.exists(), report
report.write_text(json.dumps(result, indent=2) + '\n')
paths.add(report)
freeze(root, root / 'analysis/v319-reveal-experiments', paths, result, cleanup, cleanup=True)
assert sha((root / 'gaw-megadrive.bin').read_bytes()) == digest
print('Three rejected reveal candidates archived; source row-boundary finding retained, V319 unchanged.')
