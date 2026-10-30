"""Ship-aware input navigation and verified pre-boss approach on unchanged v304."""
import json
from run_core import ROOT
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols


def main():
    refs = {}
    def read(name):
        raw = evidence(ROOT/name)
        refs[name] = sha(raw)
        return raw
    def load(name):
        return json.loads(read(name))
    prior = load('analysis/d7_progress_v0304_report.json')
    assert prior['passed'] and prior['ship_acquired']
    digest = sha(read('versions/v0304-b7b4e150/gaw-megadrive-v0304.bin'))
    assert digest == prior['md_sha256']
    hashes, visited = set(), set()
    def source_index(name):
        if name in visited:
            return
        visited.add(name)
        index = load(name)
        for key, value in index.items():
            if key.endswith(('source_index', 'controller_index')):
                source_index(value)
        for item in index.get('sources', {}).values():
            assert sha(read(item['path'])) == item['sha256']
            hashes.add(item['sha256'])
    source_index('analysis/d7_sentinel_v0304_source_index.json')
    fixture = load('validation/ship-controller-v0304-01/report.json')
    assert fixture['passed'] and fixture['md_sha256'] == digest and not fixture['campaign_proof']
    assert fixture['cases'] == 8192 and fixture['compared_cache_bytes'] == 196608
    assert fixture['reference_sha256'] in hashes and fixture['validator_sha256'] in hashes
    assert sha(read('validation/ship-controller-v0304-01/source_outputs.bin')) == fixture['source_outputs_sha256']
    original = read('input/original.sms')
    assert sha(original) == fixture['source_sha256'] and sha(original[0x2d41:0x2d7b]) == fixture['source_routine_sha256']
    erratum = load('analysis/stack_minimum_v0304_erratum_report.json')
    assert erratum['passed'] and erratum['corrected_margin_bytes'] == 478
    symbol_file = 'validation/stack-v0304-d6-all/symbol.txt'
    read(symbol_file)
    sy = symbols(ROOT/symbol_file)
    stages = []
    previous = prior['stages'][-1]['frames']
    previous_name = prior['stages'][-1]['trace'].rsplit('/', 1)[-1]
    for suffix, frame, room, keys, magic in [('north-return02', 176702, 0x1b8, 3, 48),
            ('warp1a8-01', 177706, 0x198, 3, 40), ('approach03', 181983, 0x189, 2, 48)]:
        root = 'validation/natural-dungeon-combat/md-auto-v0304-d7-'+suffix
        c, r = load(root+'/capture.json'), load(root+'/report.json')
        proof = root+f'-assisted-fixed-replay-{frame}'
        p = load(proof+'/replay_report.json')
        assert c['frames'] == frame and c['rom_sha256'] == p['rom_sha256'] == digest and c['sram_input'] is None
        assert r['prefix_end'] == previous and r['recorded_new_game_prefix'] == previous_name
        previous, previous_name = frame, root.rsplit('/', 1)[-1]
        assert p['passed'] and p['whole_ram_bytes'] == 65536 and p['final_png_exact'] and not p['feedback_reads']
        for name, expected in p['evidence'].items():
            assert sha(read(root+'/'+name)) == expected
        a, writes = recording(ROOT/root, c)
        read(root+'/assistance.json')
        assert a['driver_sha256'] in hashes and r['driver_sha256'] in hashes
        assert len(a['episodes']) == 7 and a['boss_room'] == 0x179 and not a['boss_assistance']
        assert all(a[k] is None for k in ['first_boss_entry', 'release_write_frame', 'first_boss_combat', 'first_boss_damage'])
        assert all(address == sy['hero_hurt'] for _, address, _ in writes)
        assert not a['primary_state_imports'] and not a['health_refills'] and not a['rom_modifications']
        assert r['failure'] is None and not r['deaths']
        for stem, ext in [('ram', 'bin'), ('frame', 'png')]:
            filename = f'/{stem}_{frame:05d}.{ext}'
            assert read(root+filename) == read(proof+filename)
        raw = read(root+f'/ram_{frame:05d}.bin')
        data = lambda n, k: bytes(raw[(sy[n]+i)^1] for i in range(k))
        word = lambda n: int.from_bytes(data(n, 2), 'big')
        assert word('room_id') == room and word('game_state') == 12 and word('hero_health') == word('hero_max_health') == 80
        assert word('hero_keys') == keys and word('hero_magic') == magic and word('sound_unhandled_command') == 0
        assert word('hero_selected_item') == word('hero_weapon_level') == 1
        assert data('hero_items', 17)[16] == 1 and data('game_save_state', 592)[0x1f:0x28] == bytes([128]*6+[0]*3)
        if suffix == 'north-return02':
            assert r['room_cleared'] and r['rush_rooms'] == [0x1d5] and r['last_state']['ship'] == 1
        if suffix == 'warp1a8-01':
            assert r['earth_route_passed'] and r['earth_cell'] == 0x34 and r['earth_state_writes'] == 0
            assert r['earth_before']['magic'] - r['earth_opened']['magic'] == 8
            assert r['earth_controller_sha256'] in hashes
        if suffix == 'approach03':
            assert r['wake_sentinels_requested'] and r['room_cleared']
            decisions = load(root+'/pilot_decisions.json')
            assert {x['reason'] for x in decisions} >= {'approach_dormant_sentinel', 'wait_sentinel_reveal'}
            samples = load(root+'/samples.json')
            assert any(row['room'] == 0x189 and any(e['type'] == 0x58 and e['state'] == 10 and not e['flags'] & 2
                       for e in row['actors']) for row in samples)
            assert data('game_save_state', 592)[0x50+0x89] & 0x20
        stages.append(dict(trace=root, frames=frame, room=room, health=80, keys=keys, magic=magic, whole_ram_png_exact=True))
    for suffix, failure, room in [('north-return01', 'frame_limit', 0x1d5),
                                  ('approach01', 'controller_stalled', 0x1a8),
                                  ('approach02', 'controller_stalled', 0x189)]:
        r = load('validation/natural-dungeon-combat/md-auto-v0304-d7-'+suffix+'/report.json')
        assert r['failure'] == failure and r['last_state']['room'] == room
    read('tools/summarize_d7_navigation_v0304.py')
    result = dict(passed=True, version=304, md_sha256=digest, production_rom_unchanged=True, stages=stages,
                  source_ship_cache_cases=8192, source_ship_cache_bytes=196608, dormant_sentinel_input_fixed=True,
                  source_ship_cache_compared=True, source_campaign_compared=False, seventh_boss_entered=False,
                  ready_room=0x189, ready_health=80, ready_keys=2, ready_magic=48, ship_owned=True,
                  six_crystals_preserved=True, full_game_validated=False, evidence=refs,
                  limits=['Only controller inputs/collision predictions change. Approach hero_hurt assistance remains explicit;main boss179 not entered.',
                          'The source cache fixture compares original2D41,not full movement cadence or source campaign.',
                          'Three cold fixed-input replays reproduce whole RAM/PNG. Failed optional-combat,unopened-portal and dormant-sentinel attempts are separate diagnostics.',
                          'Stack erratum478 bytes covers D1-D6 only;this approach does not extend that stack measurement. Ending,saves,global RNG and complete fidelity remain unproved.'])
    (ROOT/'analysis/d7_navigation_v0304_report.json').write_bytes((json.dumps(result, indent=2)+'\n').encode())
    print('v304:ship cache8192 original cases;three exact approach replays;ready189 HP80 keys2;boss not entered')


if __name__ == '__main__':
    main()
