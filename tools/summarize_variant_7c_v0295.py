"""Version-bound 7C fix, measured cadence limitation and current campaign evidence."""
import json
from run_core import ROOT
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols


def main():
    refs = {}
    def read(name):
        raw = evidence(ROOT/name); refs[name] = sha(raw); return raw
    def load(name): return json.loads(read(name))
    digest = sha(read('versions/v0295-b71a6bc6/gaw-megadrive-v0295.bin'))
    source = read('input/original.sms')
    assert int.from_bytes(source[0x2b63+0x7c*2:0x2b65+0x7c*2], 'little') == 0x54d3
    assert source[0x54d3:0x54d9].hex() == '2140abc3604c'
    policy = load('analysis/burst_variant_7c_v0295_policy_report.json')
    assert policy['md_sha256'] == digest and policy['cases'] == 795 and policy['all_768_actor_bytes_exact']
    current = load('analysis/burst_variant_7c_v0295_diagnostic.json')
    baseline = load('analysis/burst_variant_7c_v0294_baseline_diagnostic.json')
    assert current['md_sha256'] == digest and len(current['cases']) == len(baseline['cases']) == 6
    for new, old in zip(current['cases'], baseline['cases']):
        assert (new['region'], new['type']) == (old['region'], old['type'])
        assert new['exact_frames'] == 109 and new['first_mismatch']['frame'] == 2909
        if new['type'] == 0x7c:
            assert old['exact_frames'] == 0 and old['first_mismatch']['frame'] == 2800
        else: assert old == new
    cadence = load('analysis/burst_cadence_v0295_report.json')
    assert cadence['md_sha256'] == digest and cadence['read_only_timing_observer']
    assert all(row['gaps'][0] == dict(before=2908, after=2910, frames=2) for row in cadence['results'])
    sy = symbols(ROOT/'validation/stack-v0295-d2-all/symbol.txt')
    read('validation/stack-v0295-d2-all/symbol.txt')
    stages = []
    for root, report_name in [
        ('validation/natural-dungeon-combat/md-auto-v0295-d2-rebase01', 'report.json'),
        ('validation/natural-dungeon-route/md-v0295-d3-entry02', 'route_report.json')]:
        capture = load(root+'/capture.json'); report = load(root+'/'+report_name)
        proof = load(root+f'-assisted-fixed-replay-{capture["frames"]}/replay_report.json')
        assist, writes = recording(ROOT/root, capture); read(root+'/assistance.json')
        assert capture['rom_sha256'] == proof['rom_sha256'] == digest and capture['sram_input'] is None
        assert proof['passed'] and proof['whole_ram_bytes'] == 65536 and proof['final_png_exact'] and not proof['feedback_reads']
        for name, expected in proof['evidence'].items(): assert sha(read(root+'/'+name)) == expected
        assert report['failure'] is None and all(address == sy['hero_hurt'] for _, address, _ in writes)
        raw = read(root+f'/ram_{capture["frames"]:05d}.bin'); read(root+f'/frame_{capture["frames"]:05d}.png')
        data = lambda n,k: bytes(raw[(sy[n]+i)^1] for i in range(k))
        word = lambda n: int.from_bytes(data(n,2), 'big')
        assert data('game_save_state',592)[0x1f:0x28] == bytes([128,128]+[0]*7)
        assert word('hero_health') == 31 and word('hero_max_health') == 48
        assert data('hero_items',17)[1] == word('hero_selected_item') == 1
        if report_name == 'report.json':
            assert report['passed'] and report['full_dungeon_cleared'] and word('room_id') == 0xd6
            assert [(ep['boss_dungeon'], ep['release_write_frame'], ep['first_boss_combat']['frame']) for ep in assist['episodes']] == [(1,12338,12409),(2,33281,33338)]
            assert max(f for f,_,_ in writes) == 33281
        else:
            assert report['reached_entrance'] and word('room_id') == 0x1f8 and assist['first_boss_combat'] is None
        stages.append(dict(trace=root,frames=capture['frames'],room=word('room_id'),health=31,max_health=48,whole_ram_png_exact=True))
    stack = load('validation/stack-v0295-d2-all/stack_report.json')
    assert stack['md_sha256'] == digest and stack['all_instructions'] and stack['frames'] == 37128 and not stack['invalid_heap_examples']
    boundary = stack['heap_changes'][-1]['end']+2
    assert stack['minimum_sp']-boundary == 408
    assert read('validation/stack-v0295-d2-all/ram_37128.bin') == read('validation/natural-dungeon-combat/md-auto-v0295-d2-rebase01/ram_37128.bin')
    assert read('validation/stack-v0295-d2-all/frame_37128.png') == read('validation/natural-dungeon-combat/md-auto-v0295-d2-rebase01/frame_37128.png')
    index = load('analysis/variant_7c_v0295_source_index.json')
    for item in index['sources'].values(): assert sha(read(item['path'])) == item['sha256']
    read('tools/summarize_variant_7c_v0295.py')
    result = dict(passed=True,version=295,md_sha256=digest,native_variant_7c_fixed=True,
                  policy_cases=795,production_exact_initial_frames_per_case=109,
                  production_diagnostic_cases=6,burst_cadence_complete=False,
                  first_projectile_cycle_mismatch=2909,baseline_v0294_also_slow=True,
                  native_two_crystals=True,dungeon3_entrance_reached=True,stages=stages,
                  boss_assistance=False,health_refills=0,primary_state_imports=0,
                  observed_stack_margin_bytes=408,full_game_validated=False,evidence=refs,
                  limits=['795 controlled original/native cases use explicit inputs at two original LD A,R sites. Initial production fixtures align the world clock; the first109 frames match all768 actor bytes.',
                          'All six production comparisons diverge at2909 after the first eight-projectile burst. Read-only native function entries show two-physical-frame simulation gaps. The unchanged6A/6B variants have the same divergence on294; no complete combat cadence pass is claimed.',
                          'Cold campaign replays confirm D1,D2 crystals and exits,then D3 entrance. Logged test-only hurt guards cover approaches; D1/D2 boss fights and returns have no assistance. The remaining campaign,complete video/audio and hardware fidelity are unproved.'])
    (ROOT/'analysis/variant_7c_v0295_report.json').write_text(json.dumps(result,indent=2)+'\n')
    print('v295:795 policy cases;7C dispatch fixed;D1/D2 and D3 entry replayed;burst slowdown remains')


if __name__ == '__main__': main()
