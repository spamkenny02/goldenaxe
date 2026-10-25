"""Scope the v285 D2 key proof separately from assisted boss diagnostics."""
import argparse
import json
from run_core import ROOT
from rebase_natural_campaign import evidence
from archive_lossless_evidence import sha
from validate_playable_sprite_limit import symbols


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--assisted-trace')
    parser.add_argument('--assisted-end', type=int)
    args = parser.parse_args()
    refs = {}

    def read(name):
        raw = evidence(ROOT / name)
        refs[name] = sha(raw)
        return raw

    def record(name):
        return json.loads(read(name))

    digest = sha((ROOT / 'gaw-megadrive.bin').read_bytes())
    trace = 'validation/natural-dungeon-combat/md-auto-v0285-d2-plan05'
    report = record(trace + '/report.json')
    replay = record(trace + '-fixed-replay/replay_report.json')
    capture = record(trace + '/capture.json')
    assert report['rom_sha256'] == replay['rom_sha256'] == capture['rom_sha256'] == digest
    assert report['new_key_verified'] and report['deaths'] == 0 and report['failure'] is None
    assert replay['passed'] and replay['whole_ram_bytes'] == 65536 and replay['final_png_exact']
    assert not capture['test_ram_writes'] and not replay['ram_injections']
    end = capture['frames']
    ram = read(trace + f'/ram_{end:05d}.bin')
    stack = record('validation/stack-v0285-d2-keys-all/stack_report.json')
    assert stack['read_only'] and stack['all_instructions']
    assert read(f'validation/stack-v0285-d2-keys-all/ram_{end:05d}.bin') == ram
    assert read(f'validation/stack-v0285-d2-keys-all/frame_{end:05d}.png') == read(trace + f'/frame_{end:05d}.png')
    source = 'validation/natural-dungeon-combat/sms-auto-v0280-d2-bridge02'
    sc = record(source + '/capture.json')
    assert sc['rom_sha256'] == sha((ROOT / 'input/original.sms').read_bytes())
    sr = read(source + f"/ram_{sc['frames']:05d}.bin")
    sy = symbols(ROOT / 'megadrive/out/release/symbol.txt')
    data = lambda name, count: bytes(ram[(sy[name] + i) ^ 1] for i in range(count))
    assert data('game_save_state', 592)[0x50:0x150] == sr[0x100:0x200]
    assert data('sms_vram', 16384)[0x3800:0x3d00] == sr[0x1600:0x1b00]
    result = dict(passed=True, version=285, rom_sha256=digest, frames=end,
                  new_key_verified=True, keys_before=report['target_entry_keys'],
                  keys_after=report['last_state']['keys'], health=report['last_state']['health'],
                  deaths=0, natural_key_route=True, whole_ram_and_png_replayed=True,
                  source_flags_exact_bytes=256, source_map_exact_bytes=1280,
                  stack_frames=stack['frames'], minimum_sp=stack['minimum_sp'],
                  stack_replay_whole_ram_and_png_exact=True,
                  second_crystal_verified=False, full_game_validated=False)
    if args.assisted_trace:
        assert args.assisted_end
        at = 'validation/' + args.assisted_trace
        ar = record(at + '/assistance.json')
        ap = record(at + f'-assisted-fixed-replay-{args.assisted_end}/replay_report.json')
        assert ap['passed'] and ap['assisted_route'] and not ap['boss_assistance']
        assert ar['first_boss_combat']['hurt'] == 0
        assert ar['release_write_frame'] < ar['first_boss_combat']['frame']
        result['assisted_boss'] = dict(replay=ap, assistance={key: value for key, value in ar.items() if key != 'writes'})
    result['evidence'] = refs
    (ROOT / 'analysis/d2_progress_v0285_report.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: value for key, value in result.items() if key not in ['stack_report', 'evidence']}, indent=2))


if __name__ == '__main__':
    main()
