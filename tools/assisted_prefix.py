"""Explicit, verified approach-assistance prefixes; never a natural-route proof."""
import json
from pathlib import Path
from run_core import ROOT, FrameWrites
from archive_lossless_evidence import sha

EPISODE_KEYS = ['activation_after_frame', 'boss_room', 'first_boss_entry',
                'release_write_frame', 'first_boss_combat', 'first_boss_damage']


def episodes(assist, capture):
    if 'episodes' in assist:
        result = assist['episodes']
        assert result and all(result[-1][key] == assist[key] for key in EPISODE_KEYS)
        return result
    return [dict(**{key: assist[key] for key in EPISODE_KEYS}, end_frame=capture['frames'] + 1)]


def recording(folder, capture):
    folder = folder.resolve()
    assert folder.is_relative_to(ROOT / 'validation')
    assist = json.loads((folder / 'assistance.json').read_bytes())
    assert assist['assisted_route'] and assist['ram_injections']
    assert not assist['rom_modifications']
    assert assist['primary_state_imports']==int(bool(capture['sram_input']))
    if capture['sram_input']:
        assert assist.get('controlled_sram_fixture') and assist.get('sram_initialization_import')
        initial=Path(capture['sram_input']).resolve();assert initial.is_relative_to(ROOT/'validation')
        assert sha(initial.read_bytes())==assist['sram_sha256']
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
    previous_end = 0
    covered = 0
    for episode in episodes(assist, capture):
        begin, end = episode['activation_after_frame'], episode['end_frame']
        assert previous_end <= begin < end <= capture['frames'] + 1
        local = [(f, a, data) for f, a, data in writes if begin < f <= end]
        assert local
        release = episode['release_write_frame']
        if release is not None:
            assert local[-1][0] == release and local[-1][2] == zero
            assert all(frame <= release for frame, _, _ in local)
        if episode['first_boss_combat'] is not None:
            assert begin < release < episode['first_boss_combat']['frame'] <= end
            hurt=episode['first_boss_combat']['hurt']
            assert hurt==0 or episode.get('natural_cooldown_observed') and 0<hurt<=128
        covered += len(local)
        previous_end = end
    assert covered == len(writes), 'All writes must belong to a declared approach episode'
    return assist, [(f, a, data) for f, a, data in writes if f <= capture['frames']]


def controlled_sram_input(folder,capture,enabled=False):
    if capture['sram_input'] is None:return None
    assert enabled,'SRAM prefixes require explicit controlled fixture mode; they are not cold campaign proofs'
    initial=Path(capture['sram_input']).resolve();assert initial.is_relative_to(ROOT/'validation')
    report=json.loads((folder/'report.json').read_bytes())
    assert report.get('controlled_sram_fixture') and not report.get('natural_campaign_proof',True)
    assert report.get('game_written_save') is False
    assert report.get('md_sha256',report.get('rom_sha256'))==capture['rom_sha256']
    assert sha(initial.read_bytes())==report['sram_sha256']
    return initial


def prefix_writes(folder, capture, enabled=False,controlled=False):
    initial=controlled_sram_input(folder,capture,controlled)
    if not capture['test_ram_writes']:
        return []
    assert enabled, 'Assisted recordings require explicit --assisted-prefix; they are not natural prefixes'
    assist, writes = recording(folder, capture)
    path = folder.with_name(folder.name + f"-assisted-fixed-replay-{capture['frames']}") / 'replay_report.json'
    proof = json.loads(path.read_bytes())
    assert proof['passed'] and proof['assisted_route'] and not proof['natural_campaign_proof']
    assert bool(proof.get('controlled_sram_fixture'))==bool(initial)
    if initial:assert proof['sram_sha256']==sha(initial.read_bytes())
    assert proof['frames'] == capture['frames'] and proof['rom_sha256'] == capture['rom_sha256']
    expected = 8192 if Path(capture['rom']).suffix.lower() == '.sms' else 65536
    assert proof['whole_ram_bytes'] == expected and proof['final_png_exact'] and not proof['feedback_reads']
    for name in ['capture.json', 'controls.json', 'assistance.json']:
        assert proof['evidence'][name] == sha((folder / name).read_bytes())
    return FrameWrites(writes)
