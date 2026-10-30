"""Audit D7 keys, Earth, remote passage and actual ship acquisition on v304."""
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
    prior = load('analysis/d7_supplies_v0304_report.json')
    assert prior['passed'] and prior['first_dungeon_key_acquired']
    digest = sha(read('versions/v0304-b7b4e150/gaw-megadrive-v0304.bin'))
    assert digest == prior['md_sha256']
    symbol_file = 'validation/stack-v0304-d6-all/symbol.txt'
    read(symbol_file)
    sy = symbols(ROOT/symbol_file)
    hashes, seen = set(), set()
    def source_index(name):
        if name in seen:
            return
        seen.add(name)
        index = load(name)
        for key, value in index.items():
            if key.endswith(('source_index', 'controller_index')):
                source_index(value)
        for item in index.get('sources', {}).values():
            assert sha(read(item['path'])) == item['sha256']
            hashes.add(item['sha256'])
    source_index('analysis/d7_progress_v0304_source_index.json')
    original = read('input/original.sms')
    assert original[0x3234e+0x1b8*8:0x32356+0x1b8*8] == bytes([0x78]+[0]*7)
    assert original[0x320ea+(0x78-0x20)*4:0x320ee+(0x78-0x20)*4] == bytes.fromhex('1e0c0420')
    exceptions = original[0x3226d:0x322ae]
    n = list(exceptions[1:1+exceptions[0]]).index(0x5a)
    assert exceptions[1+exceptions[0]+n] == 5
    assert original[0x322ae+0x5c:0x322ae+0x5e] == bytes([1, 14])
    contacts = load('analysis/contact_script_reference.json')
    remote = next(r for r in contacts['records'] if r['room'] == 0x1e6 and r['kind'] == 'stationary_up_passages')
    assert remote['coordinate'] == 332 and remote['explicit_registers']['d'] == 4 and remote['explicit_registers']['e'] == 0xd6
    rewards = load('analysis/item_rewards_reference.json')
    ship = next(r for r in rewards['records'] if r['room'] == 0x1d5)
    assert ship['inventory_offset'] == 16 and ship['value'] == 1 and ship['item'] == 20
    stages = []
    previous = prior['stages'][-1]['frames']
    previous_name = prior['stages'][-1]['trace'].rsplit('/', 1)[-1]
    for suffix, room in [('key03', 0x1b9), ('earth1b9-01', 0x1b9), ('earth1b9-02', 0x1b9),
                         ('contact1b9-01', 0x1b8), ('south01', 0x1d6),
                         ('remote1e6-01', 0x1d6), ('ship02', 0x1d5)]:
        root = 'validation/natural-dungeon-combat/md-auto-v0304-d7-'+suffix
        c, r = load(root+'/capture.json'), load(root+'/report.json')
        frame = c['frames']
        proof = root+f'-assisted-fixed-replay-{frame}'
        p = load(proof+'/replay_report.json')
        assert c['rom_sha256'] == p['rom_sha256'] == digest and c['sram_input'] is None
        assert r['prefix_end'] == previous and r['recorded_new_game_prefix'] == previous_name
        previous, previous_name = frame, root.rsplit('/', 1)[-1]
        assert p['passed'] and p['whole_ram_bytes'] == 65536 and p['final_png_exact'] and not p['feedback_reads']
        for name, expected in p['evidence'].items():
            assert sha(read(root+'/'+name)) == expected
        a, writes = recording(ROOT/root, c)
        read(root+'/assistance.json')
        assert a['driver_sha256'] in hashes and a['boss_room'] == 0x179 and len(a['episodes']) == 7
        assert a['activation_after_frame'] == 153868 and not a['boss_assistance']
        assert all(a[k] is None for k in ['first_boss_entry', 'release_write_frame', 'first_boss_combat', 'first_boss_damage'])
        assert not a['primary_state_imports'] and not a['health_refills'] and not a['rom_modifications']
        assert all(address == sy['hero_hurt'] for _, address, _ in writes)
        for key, value in r.items():
            if value is not None and key.endswith(('driver_sha256', 'wrapper_sha256', 'aim_sha256', 'controller_sha256')):
                assert value in hashes, (key, value)
        assert r['failure'] is None and not r['deaths']
        for stem, ext in [('ram', 'bin'), ('frame', 'png')]:
            filename = f'/{stem}_{frame:05d}.{ext}'
            assert read(root+filename) == read(proof+filename)
        raw = read(root+f'/ram_{frame:05d}.bin')
        data = lambda n, k: bytes(raw[(sy[n]+i)^1] for i in range(k))
        word = lambda n: int.from_bytes(data(n, 2), 'big')
        save, items = data('game_save_state', 592), data('hero_items', 17)
        assert word('room_id') == room and word('game_state') == 12 and word('hero_health') > 0
        assert word('sound_unhandled_command') == 0
        assert word('hero_max_health') == 80 and word('hero_selected_item') == word('hero_weapon_level') == 1
        assert save[0x1f:0x28] == bytes([128]*6+[0]*3) and word('world_dungeon_number') == 7
        assert items[10] == 1 and items[12:15] == bytes([1, 1, 1]) and not items[15]
        assert word('hero_attack_speed') == 1 and items[16] == (1 if suffix == 'ship02' else 0)
        if suffix == 'key03':
            assert r['new_key_verified'] and r['target_entry_keys'] == 1 and word('hero_keys') == 2
            events = load(root+'/events.json')
            assert any(sum(e['type'] == 14 for e in row.get('loot', [])) == 2 for row in events)
        if suffix.startswith('earth'):
            assert r['passed'] and r['earth_action_only_requested'] and r['earth_cell_cleared']
            assert r['earth_state_writes'] == 0 and r['earth_before']['cell'] == 11 and r['earth_opened']['cell'] == 0
            expected_magic = 40 if suffix.endswith('01') else 32
            assert word('hero_magic') == expected_magic and word('hero_keys') == 3
            assert r['earth_before']['magic'] - r['earth_opened']['magic'] == 8
        if suffix.startswith('contact') or suffix.startswith('remote'):
            assert r['contact_route_passed'] and r['contact_state_writes'] == 0
        if suffix == 'contact1b9-01':
            assert r['contact_opened']['flags'] & 4
            actors = data('world_actor_state', 768)
            assert actors[0] == 0x78 and actors[1] != 0 and actors[0x13] != 0
        if suffix == 'south01':
            assert r['room_cleared'] and save[0x50+0xb8] & 0x40 and not data('world_actor_state', 768)[0]
        if suffix in ['remote1e6-01', 'ship02']:
            assert save[0x50+0xe6] & 4 and save[0x50+0xd6] & 0x40 and save[0x50+0xd5] & 0x80
        if suffix == 'ship02':
            assert r['passed'] and r['item_acquisition_passed'] and r['item_acquisition_state_writes'] == 0
            assert not r['item_acquisition_first']['owned'] and r['item_acquisition_last']['owned'] == 1
            assert not word('item_reward_active') and word('hero_state') == 1
            actors = data('world_actor_state', 768)
            traps = [(i, actors[i*48], actors[i*48+24]) for i in range(8) if actors[i*48] == 0x5e]
            assert traps == [(i, 0x5e, 0) for i in range(4)] and not r['room_cleared']
            others = [(i, actors[i*48], actors[i*48+24]) for i in range(8) if actors[i*48] and actors[i*48] != 0x5e]
            assert others == [(4, 0x44, 10)]
        stages.append(dict(trace=root, frames=frame, room=room, health=word('hero_health'),
                           keys=word('hero_keys'), magic=word('hero_magic'), ship_owned=bool(items[16]), whole_ram_png_exact=True))
    diagnostic = load('validation/natural-dungeon-combat/md-auto-v0304-d7-ship01/report.json')
    assert diagnostic['failure'] == 'controller_stalled' and not diagnostic['item_acquisition_passed']
    assert diagnostic['last_state']['room'] == 0x1d6 and diagnostic['last_state']['keys'] == 3
    read('tools/summarize_d7_progress_v0304.py')
    result = dict(passed=True, version=304, md_sha256=digest, production_rom_unchanged=True, stages=stages,
                  ship_acquired=True, ship_inventory_offset=16, remote1e6_to1d6_passage_verified=True,
                  persistent_floor_traps_retained=4, remaining_live_actor=dict(slot=4, type=0x44, hp=10),
                  room1b8_midboss_defeated=True,
                  room1b8_midboss_assisted=True, room1b8_unassisted_fight_validated=False, earth_magic_spent=16,
                  additional_key_drop_observed=True, source_rng_reproduced=False, seventh_boss_entered=False,
                  seventh_crystal_obtained=False, primary_state_imports=0, injected_health_refills=0,
                  full_game_validated=False, evidence=refs, limits=[
                      'Approach-only hero_hurt guards remain explicitly logged. No HP,mana,ownership,currency,progression or actor deletion fixture. Seventh boss179 is not entered.',
                      'The intermediate type78 dragon in1B8 is defeated during the assisted approach. Its unassisted fight is not established by this report;boss_assistance in the route logs refers to the designated main boss179.',
                      'Room1B9 contains two real type14 loot records: room reward and an extra enemy drop. A second pickup raises keys2->3 during Earth approach. The original class5 drop table permits a key; global source RNG remains unproved.',
                      'The direct1D6->1D5 proposal is blocked. The ordinary UP mechanism in1E6 at coordinate332 opens remote1D6 west and neighbor1D5 east before returning to the ship room.',
                      'The item controller finishes on actual ownership plus closed reward and ordinary gameplay. It preserves four zero-HP type5E traps and a living type44 actor at10HP,without labelling the room cleared. Native reward logic permits this acquisition.',
                      'Seven independent cold-input replays match all65536 RAM bytes and final PNG. This is a current-ROM progression proof,not a full SMS campaign,ending,saves or complete fidelity proof.'])
    (ROOT/'analysis/d7_progress_v0304_report.json').write_bytes((json.dumps(result, indent=2)+'\n').encode())
    print('v304:D7 ship and remote passage independently replayed;four floor traps retained;ROM unchanged')


if __name__ == '__main__':
    main()
