"""Audit nontrivial direct SMS PSG streams, then archive the bounded boot-audio proof."""
import json
import struct
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'tools'))
from archive_lossless_evidence import freeze, sha

producer = Path(__file__).with_name('compare_v319_psg_to_sms.py')
short = root / 'validation/v319-sms-psg01'
long = root / 'validation/v319-sms-psg02'
first = json.loads((short / 'report.json').read_bytes())
full = json.loads((long / 'report.json').read_bytes())
rom = root / 'versions/v0319-d3ea2a83/gaw-megadrive-v0319.bin'
original = root / 'input/original.sms'
assert first['passed'] and full['passed'] and full['direct_sms_reference']
assert sha(rom.read_bytes()) == full['rom_sha256'] == first['rom_sha256'] == sha((root / 'gaw-megadrive.bin').read_bytes())
assert sha(original.read_bytes()) == full['source_sha256'] == first['source_sha256']
assert full['driver_sha256'] == first['driver_sha256'] == sha(producer.read_bytes())
assert full['core_sha256'] == first['core_sha256']
cases = []
for region in ('ntsc', 'pal'):
    streams = {}
    for tag, cartridge in [('md', rom), ('sms', original)]:
        folder = long / (region + '-' + tag)
        raw = (folder / 'psg-registers.bin').read_bytes()
        capture = json.loads((folder / 'capture.json').read_bytes())
        assert len(raw) == 14000 * 16
        assert capture['rom_sha256'] == sha(cartridge.read_bytes()) and capture['frames'] == 14000
        assert capture['core_options']['genesis_plus_gx_region_detect'] == ('pal' if region == 'pal' else 'auto')
        assert not capture['sram_input'] and not capture['test_ram_writes'] and not capture['presses']
        assert raw[:6500 * 16] == (short / (region + '-' + tag) / 'psg-registers.bin').read_bytes()
        streams[tag] = raw
    assert streams['md'] == streams['sms'], 'Raw all-register streams must match without shift/normalisation'
    rows = list(struct.iter_unpack('<8H', streams['sms']))
    unique = len(set(rows))
    per_register = [len({row[i] for row in rows}) for i in range(8)]
    assert unique > 1 and all(n > 1 for n in per_register), 'Reject trivial/stub register streams'
    cases.append(dict(region=region, frames=14000, exact_register_frames=14000,
                      different_register_frames=0, unique_states=unique,
                      different_value_counts_by_register=per_register,
                      non_fully_muted_state_frames=sum(any(row[n] < 15 for n in (1, 3, 5, 7)) for row in rows),
                      raw_register_sha256=sha(streams['sms']), short_run_prefix_exact=True))
archive = root / 'analysis/v319-sms-psg'
result = dict(passed=True, version=319, md_sha256=full['rom_sha256'], source_sha256=full['source_sha256'],
              core_sha256=full['core_sha256'], direct_sms_reference=True,
              frames_per_region=14000, total_compared_frames=28000, cases=cases,
              temporal_shift_frames=0, register_normalisation=False, ram_writes=0, sram_imports=0,
              intra_frame_write_timing_validated=False, pcm_equivalence_validated=False,
              whole_game_audio_validated=False,
              archive_manifest=(archive / 'manifest.json').relative_to(root).as_posix(),
              scope='All8 raw PSG registers match SMS at every sampled frame over two cold no-input '
                    'opening loops per region. Independently captured6500-frame prefixes also match. '
                    'Nontrivial tone/noise/volume states; no temporal shift. This is not an intra-frame '
                    'write trace, PCM or interactive/whole-game audio certification.')
report = root / 'analysis/sms_psg_v0319_report.json'
assert not report.exists(), report
report.write_text(json.dumps(result, indent=2) + '\n')
paths = {Path(__file__).resolve(), producer, report}
for work in (short, long):
    paths.update(p for p in work.rglob('*') if p.is_file())
freeze(root, archive, paths, result, [short, long], cleanup=True)
print('Direct SMS PSG proof audited and archived:28000 frames, all8 raw registers exact, nontrivial streams.')
