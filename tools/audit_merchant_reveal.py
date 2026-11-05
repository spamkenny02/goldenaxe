"""Audit captured merchant masks and cross-check an isolated candidate's scrolls.

This reads official-core captures, without starting or changing the game.
The candidate remains unpublished when another scene's timing regresses.
"""
import argparse
import hashlib
import json
from pathlib import Path

from run_core import ROOT


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def pose_frames(folder, tag):
    expected = {}
    for mask in (127, 63, 31, 15, 7, 3, 1, 0):
        rotated = mask
        planar, packed = bytearray(), bytearray()
        for _ in range(512):
            planar.append(rotated)
            word = sum(((rotated >> bit) & 1) << (bit * 4 + 2) for bit in range(8))
            packed.extend(word.to_bytes(4, 'big'))
            rotated = ((rotated >> 2) | (rotated << 6)) & 255
        expected[mask] = bytes(planar if tag == 'sms' else packed)
    found = {}
    for frame in range(3750, 3801):
        raw = (folder / f'vram_{frame:05d}.bin').read_bytes()
        # Genesis Plus GX stores MD VRAM words in host byte order.
        published = raw[2:2048:4] if tag == 'sms' else bytes(
            raw[i ^ 1] & 0x44 for i in range(512, 2560))
        for mask, pattern in expected.items():
            if published == pattern:
                found.setdefault(mask, frame)
    assert len(found) == 8, (folder, 'incomplete published portrait masks', found)
    return found


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--experiment', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    experiment = args.experiment.resolve()
    build = experiment / 'candidate01'
    rom = build / 'out/release/rom.bin'
    candidate_hash = sha(rom)
    baseline_path = ROOT / 'analysis/upward_ntsc_candidate_report.json'
    baseline = read(baseline_path)
    # That report's candidate is the numbered v311; its baseline is v310.
    assert baseline['candidate_sha256'] == sha(ROOT / 'versions/v0311-0972465d/gaw-megadrive-v0311.bin')
    reveal_path = build / 'natural-reveal/reveal_report.json'
    reveals = read(reveal_path)
    scenes = []
    for case in reveals:
        region = case['region']
        paths = {tag: build / f'natural-reveal/{region}-{tag}' for tag in ('sms', 'md')}
        for tag, path in paths.items():
            capture = read(path / 'capture.json')
            assert not capture['test_ram_writes'] and not capture['sram_input']
            assert capture['rom_sha256'] == (candidate_hash if tag == 'md' else baseline['source_sha256'])
        poses = {tag: pose_frames(path, tag) for tag, path in paths.items()}
        assert poses['sms'] == poses['md'], (region, poses)
        observed = case['observations']
        assert observed['sms']['playfield_black_frames'] == observed['md']['playfield_black_frames']
        assert len(observed['md']['playfield_black_frames']) == 9
        assert not observed['md']['hud_empty_frames'] and not observed['md']['display_disabled_frames']
        scenes.append(dict(region=region, complete_portrait_pose_frames=poses,
                           compared_plane_two_rows_per_pose=512,
                           other_portrait_planes_checked=False,
                           observations=observed, no_ram_writes=True, no_sram_input=True))
    transactions_path = build / 'merchant_report.json'
    transactions = read(transactions_path)
    assert transactions['md_sha256'] == candidate_hash
    assert len(transactions['cases']) == 7 and transactions['natural_walk_refusal_exit_without_ram_injection']
    comparisons, raw_reports = [], {}
    for region, suffix in [('ntsc', ''), ('pal', '-pal')]:
        path = experiment / f'upward-up-matrix-candidate{suffix}_report.json'
        report = read(path)
        assert report['md_sha256'] == candidate_hash
        previous = {room['origin']: room for room in baseline['cases'][f'candidate_{region}']['rooms']}
        assert len(report['cases']) == 3
        for room in report['cases']:
            assert room['destination_state_source_exact']
            assert not room['timing']['md']['nonhero_sprite_errors']
            old = previous[room['origin']]['timing']
            current = room['timing']
            old_delta = old['md']['resumed'] - old['sms']['resumed']
            delta = current['md']['resumed'] - current['sms']['resumed']
            comparisons.append(dict(region=region, origin=room['origin'], target=room['target'],
                                    v311_resume_delta=old_delta, candidate_resume_delta=delta,
                                    regressed=abs(delta) > abs(old_delta), timing=current))
        raw_reports[str(path.relative_to(ROOT))] = sha(path)
    regressions = [case for case in comparisons if case['regressed']]
    result = dict(md_sha256=baseline['candidate_sha256'], candidate_sha256=candidate_hash,
                  source_sha256=baseline['source_sha256'], adopted=False,
                  merchant_mask_timing_source_exact=True, black_window_source_exact=True,
                  scenes=scenes, transactions=transactions['cases'],
                  natural_merchant_walk_refusal_exit_verified=True,
                  scroll_comparisons=comparisons, scroll_regressions=regressions,
                  release_cross_scene_gate_passed=not regressions,
                  campaign_verified=False, merchant_audio_verified=False,
                  decision='Keep v311; merchant candidate requires independent loading timing correction.' if regressions
                  else 'Targeted cross-scene gate passed; campaign and remaining fidelity work still required.',
                  evidence_sha256={**raw_reports, str(reveal_path.relative_to(ROOT)): sha(reveal_path),
                                   str(transactions_path.relative_to(ROOT)): sha(transactions_path),
                                   str(baseline_path.relative_to(ROOT)): sha(baseline_path)},
                  driver_sha256=sha(Path(__file__)))
    args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(f'Merchant masks/black window exact in both regions; {len(regressions)} scroll timing regression(s).')


if __name__ == '__main__':
    main()
