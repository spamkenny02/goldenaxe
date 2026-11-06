"""Audit current-ROM D6 keys, contact mechanisms, Earth gates and Ice Bell."""
import json
from run_core import ROOT
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols
from validate_reward_hud_restore import translated


def main():
    refs = {}

    def read(name):
        raw = evidence(ROOT / name)
        refs[name] = sha(raw)
        return raw

    def load(name):
        return json.loads(read(name))

    prior = load('analysis/d5_campaign_v0317_report.json')
    assert prior['passed'] and prior['fifth_crystal_and_exterior_return']
    digest = sha((ROOT / 'gaw-megadrive.bin').read_bytes())
    assert digest == prior['md_sha256']
    sy = symbols(ROOT / 'megadrive/out/release/symbol.txt')
    source_names = load('validation/v0317-d6-sources02/source_index.json')
    index = {name:sha(read(name)) for name in source_names}
    assert index == source_names
    for name,h in index.items():assert sha(read('validation/v0317-d6-sources02/'+name.split('/')[-1]))==h
    native_names = load('validation/v0317-d6-sources02/native_source_index.json')
    native_index = {name:sha(read('megadrive/src/'+name)) for name in native_names}
    assert native_index == native_names
    old = load('analysis/d6_progress_v0304_report.json')
    entries = [('natural-service-route', 'md-v0317-d6-axe-equip01', 'weapon', None),
               ('natural-dungeon-route', 'md-v0317-d6-entry01', 'world', None)]
    executed = load('validation/v0317-d6-sources02/executed_recipes.json')
    recipes = [dict(row['source_recipe'], arguments=row['arguments']) for row in executed]
    assert len(recipes) == 15
    for entry, recipe in zip(old['stages'][1:], recipes):
        assert recipe['historical_report'] == entry['trace'] + '/report.json'
        assert recipe['kind'] == entry['kind']
        arguments = recipe['arguments']
        name = 'md-auto-' + arguments[arguments.index('--trial') + 1]
        entries.append(('natural-dungeon-combat', name, entry['kind'], entry['trace']))
    assert len(entries) == 17
    previous_root = prior['stages'][-1]['trace']
    previous_c = load(previous_root + '/capture.json')
    _, previous_writes = recording(ROOT / previous_root, previous_c)
    stages = []
    activation = None
    bells = False
    earth_costs = []
    keys = []
    bell_hud_words = 0
    ordinary_route_adaptations = []
    for position, (family, name, kind, historical) in enumerate(entries):
        root = f'validation/{family}/{name}'
        c = load(root + '/capture.json')
        r = load(root + ('/route_report.json' if kind == 'world' else '/report.json'))
        f = c['frames']
        assert c['rom_sha256'] == r['rom_sha256'] == digest and c['sram_input'] is None
        assert r['failure'] is None and not r.get('sram_checkpoint_injection', False)
        assert f > previous_c['frames']
        if kind == 'weapon':
            assert r['passed'] and r['seen_menu'] and r['selected_slot'] == 1
            assert r['source_trace'] == previous_root.removeprefix('validation/')
            assert r['first_state']['selected'] == 0 and r['last_state']['selected'] == 1
            assert not r['new_assistance_writes'] and not r['primary_state_imports']
            assert r['driver_sha256'] == index['tools/natural_weapon_selection.py']
            activation = f
        elif kind == 'world':
            assert r['prefix_end'] == previous_c['frames'] and r['recorded_service_prefix'] == previous_root.split('/')[-1]
            assert r['reached_entrance'] and r['directional_probe_succeeded'] and not r['normal_continues']
            assert r['live_prefix_terrain'] and r['live_initial_room'] == 0x49
            assert r['boots_acquired_in_prefix'] and r['probe_expected_y_displacement'] == 16
            assert r['route_driver_sha256'] == index['tools/natural_dungeon_route.py']
        else:
            assert r['recorded_new_game_prefix'] == previous_root.split('/')[-1]
            assert r['prefix_end'] == previous_c['frames'] and not r['deaths']
            assert r['driver_sha256'] == index['tools/natural_dungeon_combat.py']
            old_r = load(historical + '/report.json')
            recipe = recipes[position - 2]
            assert recipe['historical_report'] == historical + '/report.json'
            assert recipe['historical_report_sha256'] == refs[historical + '/report.json']
            assert r['itinerary'] == old_r['itinerary'] and r['target_room'] == old_r['target_room']
            if name.endswith('key03b'):
                assert 0x137 in r['rush_rooms']
                ordinary_route_adaptations.append(dict(trace=root, kind='use_open_south_exit137'))
            if name.endswith('torch117-01b'):
                assert r['retry_isolated_foes_requested'] and 0 <= r['isolated_foe_retries'] <= r['isolated_retry_limit']
                decisions = load(root + '/pilot_decisions.json')
                if r['isolated_foe_retries']: assert any(row.get('reason') == 'no_reachable_attack_reenter_room' and row['room'] == 0x137 for row in decisions)
                ordinary_route_adaptations.append(dict(trace=root, kind='ordinary_room_reentry', count=r['isolated_foe_retries']))
            if kind == 'earth':
                assert r['earth_route_passed'] and r['earth_cell_cleared'] and not r['earth_state_writes']
                assert r['earth_cell'] == old_r['earth_cell'] and r['earth_passage_room'] == old_r['earth_passage_room']
                assert r['earth_cast_position'] == old_r['earth_cast_position'] and r['earth_cast_direction'] == old_r['earth_cast_direction']
                assert r['earth_action_only_requested'] == old_r['earth_action_only_requested']
                assert r['earth_passage_traversed'] == (not r['earth_action_only_requested'])
                expected_earth = index['tools/natural_earth_passage.py']
                assert r['earth_controller_sha256'] == expected_earth
                events = load(root + '/earth_events.json')
                costs = [(a['frame'], b['frame']) for a, b in zip(events, events[1:])
                         if a['magic'] - b['magic'] == 8 and b['selected'] == 5 and b['spell'] == 4]
                assert costs, (name, 'no actual8MP cast decrement')
                earth_costs.append(dict(trace=root, cell=r['earth_cell'], direction=r['earth_cast_direction'], observed8MP_decrements=costs))
            elif kind == 'contact':
                assert r['contact_route_passed'] and not r['contact_state_writes']
                assert r['contact_room'] == old_r['contact_room'] and r['contact_destination'] == old_r['contact_destination']
                assert r['contact_controller_sha256'] == index['tools/natural_contact_passage.py']
            else:
                assert r['room_cleared']
                if kind == 'key':
                    assert r['new_key_verified']
                    keys.append(root)
                if kind == 'item':
                    assert r['collect_item_requested'] == 10 and r['last_state']['item_value'] == 1
                    bells = True
        assist, writes = recording(ROOT / root, c)
        read(root + '/assistance.json')
        assert len(assist['episodes']) == (5 if kind == 'weapon' else 6)
        assert not assist['boss_assistance'] and not assist['primary_state_imports'] and not assist['health_refills']
        assert all(address == sy['hero_hurt'] and value in (b'\0\0',b'\0\x81') for _, address, value in writes)
        assert writes[:len(previous_writes)] == previous_writes
        if kind == 'weapon':
            assert writes == previous_writes and assist['boss_room'] == 0x163
        else:
            assert assist['boss_room'] == 0x115 and assist['activation_after_frame'] == activation
            assert assist['first_boss_entry'] is None and assist['first_boss_combat'] is None
        proof_root = root + f'-assisted-fixed-replay-{f}'
        proof = load(proof_root + '/replay_report.json')
        assert proof['passed'] and proof['frames'] == f and proof['rom_sha256'] == digest
        assert proof['whole_ram_bytes'] == 65536 and proof['final_png_exact'] and not proof['feedback_reads']
        for n in ['capture.json', 'controls.json', 'assistance.json']:
            assert proof['evidence'][n] == sha(read(root + '/' + n))
        raw = read(root + f'/ram_{f:05d}.bin')
        assert raw == read(proof_root + f'/ram_{f:05d}.bin')
        assert read(root + f'/frame_{f:05d}.png') == read(proof_root + f'/frame_{f:05d}.png')
        data = lambda n, k: bytes(raw[(sy[n] + i) ^ 1] for i in range(k))
        word = lambda n: int.from_bytes(data(n, 2), 'big')
        items = data('hero_items', 17)
        assert data('game_save_state', 592)[0x1f:0x28] == bytes([128] * 5 + [0] * 4)
        assert word('hero_max_health') == 72 and word('hero_health') > 0
        assert word('game_state') == 12 and not word('sound_unhandled_command')
        assert items[0] == 2 and items[1] == 1 and items[4] == items[5] == 1
        assert items[12] == items[13] == items[14] == 1 and not items[8]
        assert word('hero_selected_item') == 1 and word('hero_armor_level') == 1
        assert bool(items[10]) == bells
        if kind == 'item':
            sms = data('sms_vram', 16384)
            v = read(root + f'/vram_{f:05d}.bin')
            regs = read(root + f'/vdp_regs_{f:05d}.bin')
            base = (regs[2] & 56) << 10
            width = [32, 64, 32, 128][regs[16] & 3]
            for n in range(128):
                at = base + ((n//32+22)*width+n%32)*2
                assert int.from_bytes(v[at:at+2], 'little') == translated(int.from_bytes(sms[0x3d00+n*2:0x3d02+n*2], 'little'))
            bell_hud_words = 128
        stages.append(dict(trace=root, frames=f, kind=kind, room=word('room_id'), health=word('hero_health'),
                           max_health=word('hero_max_health'), keys=word('hero_keys'), gold=word('hero_gold'),
                           magic=word('hero_magic'), bell=items[10], whole_ram_png_exact=True))
        previous_c, previous_root, previous_writes = c, root, writes
    cold = load('validation/v0317-d6-sources02/cold-stream/completed.json')
    assert cold['passed'] and cold['rom_sha256']==digest and cold['cold_boot_count']==1 and not cold['primary_state_imports']
    assert cold['emulated_frames']==previous_c['frames']
    assert [(x['trace'],x['frames']) for x in cold['checkpoints']]==[(x['trace'].removeprefix('validation/'),x['frames']) for x in stages]
    assert stages[-1]['room'] == 0x125 and bells and len(keys) == 5 and len(earth_costs) == 6
    assert r['earth_action_only_requested'] and r['earth_cell'] == 0x7b and r['earth_opened']['cell'] != 11
    result = dict(passed=True, version=317, md_sha256=digest, production_rom_unchanged=True, stages=stages,
                  acquired_key_stages=keys, earth_casts=earth_costs, ordinary_route_adaptations=ordinary_route_adaptations,
                  observed_earth_cast_count=sum(len(row['observed8MP_decrements']) for row in earth_costs),
                  ice_bell_acquired=True,
                  ice_bell_physical_hud_words_exact=bell_hud_words, five_crystals_retained=True,
                  sixth_boss_entered=False, sixth_crystal_validated=False, full_game_validated=False,
                  ready_trace=previous_root, ready_frame=previous_c['frames'], native_source_sha256=native_index, evidence=refs,
                  limits=['Cold campaign with only logged approach hero_hurt guards, never item/HP/MP/currency/actor/progression/SRAM imports.',
                          'Historical v304 itinerary and action recipes are proposals only. All current inputs execute from boot; all17 endpoints reproduce full65536RAM and PNG in one independent continuous cold fixed-input reader without state imports.',
                          'The preparatory cell7B in125 is cleared without claiming entry into115 or a sixth boss win.',
                          'An open south exit bypasses an unnecessary fight in137; any needed room reentry uses ordinary directional input, with no actor or map fixture.',
                          'Axe selection uses the ordinary menu; the live exterior map is required for the already unlocked fifth-crystal bridge.'])
    (ROOT / 'analysis/d6_progress_v0317_report.json').write_bytes((json.dumps(result, indent=2) + '\n').encode())
    print('v317 D6 progress verified:', len(stages), 'stages;', previous_c['frames'], 'frames')


if __name__ == '__main__':
    main()
