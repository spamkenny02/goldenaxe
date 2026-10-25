"""Explicit, verified approach-assistance prefixes; never a natural-route proof."""
import json
from pathlib import Path
from run_core import ROOT
from archive_lossless_evidence import sha


def recording(folder, capture):
    folder = folder.resolve()
    assert folder.is_relative_to(ROOT / 'validation')
    assist = json.loads((folder / 'assistance.json').read_bytes())
    assert assist['assisted_route'] and assist['ram_injections']
    assert not assist['rom_modifications'] and not assist['primary_state_imports']
    assert assist['health_refills'] == 0 and assist['boss_assistance'] is False
    writes = [(row['frame'], row['address'], bytes.fromhex(row['data_hex'])) for row in assist['writes']]
    sms = Path(capture['rom']).suffix.lower() == '.sms'
    zero, guard = (b'\x00', b'\x81') if sms else (b'\x00\x00', b'\x00\x81')
    assert writes and all(data in (zero, guard) for _, _, data in writes)
    assert len({address for _, address, _ in writes}) == 1
    assert len({frame for frame, _, _ in writes}) == len(writes)
    assert all(0 < frame <= capture['frames'] + 1 for frame, _, _ in writes)
    assert writes == sorted(writes)
    assert capture['test_ram_writes'] == [dict(frame=f, address=a, byte_count=len(data)) for f, a, data in writes]
    release = assist['release_write_frame']
    if release is not None:
        assert writes[-1][0] == release and writes[-1][2] == zero
        assert all(frame <= release for frame, _, _ in writes)
    if assist['first_boss_combat'] is not None:
        assert release < assist['first_boss_combat']['frame']
        assert assist['first_boss_combat']['hurt'] == 0
    return assist, [(f, a, data) for f, a, data in writes if f <= capture['frames']]


def prefix_writes(folder, capture, enabled=False):
    assert capture['sram_input'] is None, 'Cold assisted-prefix proof does not import SRAM checkpoints'
    if not capture['test_ram_writes']:
        return []
    assert enabled, 'Assisted recordings require explicit --assisted-prefix; they are not natural prefixes'
    assist, writes = recording(folder, capture)
    path = folder.with_name(folder.name + f"-assisted-fixed-replay-{capture['frames']}") / 'replay_report.json'
    proof = json.loads(path.read_bytes())
    assert proof['passed'] and proof['assisted_route'] and not proof['natural_campaign_proof']
    assert proof['frames'] == capture['frames'] and proof['rom_sha256'] == capture['rom_sha256']
    expected = 8192 if Path(capture['rom']).suffix.lower() == '.sms' else 65536
    assert proof['whole_ram_bytes'] == expected and proof['final_png_exact'] and not proof['feedback_reads']
    for name in ['capture.json', 'controls.json', 'assistance.json']:
        assert proof['evidence'][name] == sha((folder / name).read_bytes())
    return writes
