"""Audit real D7 resupply and first key, without currency/inventory fixtures."""
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
    prior = load('analysis/d6_campaign_v0306_report.json')
    assert prior['passed'] and prior['sixth_crystal_and_exterior_exit']
    digest = sha(read('versions/v0306-3a12380b/gaw-megadrive-v0306.bin'))
    assert digest == prior['md_sha256']
    sy = symbols(ROOT/'validation/stack-v0306-d6-all/symbol.txt')
    read('validation/stack-v0306-d6-all/symbol.txt')
    index = load('validation/v0306-d7-sources/source_index.json')
    for name, entry in index['sources'].items():
        assert sha(read(entry['path'])) == entry['sha256']
        assert sha(read('tools/'+name)) == entry['sha256']
    recipes = load('validation/v0306-d7-sources/supplies_recipes.json')
    assert len(recipes) == 7
    for recipe in recipes:
        assert sha(read(recipe['historical_report'])) == recipe['historical_sha256']
    gifts = load('analysis/house_gold_reference.json')
    merchants = load('analysis/merchant_assets.json')
    assert [0x7d, 30] in gifts['records'] and [0xac, 30] in gifts['records']
    assert [0x2e, 0, 2] in merchants['towns'] and merchants['goods'][2][1] == [30, 60, 5]
    stages = []
    previous = prior['campaign_frames']
    previous_trace = prior['current_campaign_trace'].removeprefix('validation/')
    specs = [('natural-dungeon-route/md-v0306-d7-gold7d-route01', 'route', 0x3f),
             ('natural-service-route/md-v0306-d7-gold7d-service01', 'gift', 0x7d),
             ('natural-dungeon-route/md-v0306-d7-goldac-route01', 'route', 0x3f),
             ('natural-service-route/md-v0306-d7-goldac-service01', 'gift', 0xac),
             ('natural-dungeon-route/md-v0306-d7-merchant2e-route02', 'route', 0),
             ('natural-service-route/md-v0306-d7-key2e-service02', 'purchase', 0x2e),
             ('natural-dungeon-route/md-v0306-d7-return-route02', 'route', 0x1db),
             ('natural-dungeon-combat/md-auto-v0306-d7-key02', 'key', 0x1cb)]
    for trace, kind, room in specs:
        root = 'validation/'+trace
        c = load(root+'/capture.json')
        frame = c['frames']
        r = load(root+('/route_report.json' if kind == 'route' else '/report.json'))
        proof = root+f'-assisted-fixed-replay-{frame}'
        p = load(proof+'/replay_report.json')
        assert c['rom_sha256'] == p['rom_sha256'] == digest and c['sram_input'] is None
        assert p['passed'] and p['whole_ram_bytes'] == 65536 and p['final_png_exact'] and not p['feedback_reads']
        assert r['failure'] is None and frame > previous
        if kind in ['route', 'key']:
            assert r['prefix_end'] == previous
        if kind in ['gift', 'purchase']:
            assert r['source_prefix'] == previous_trace.rsplit('/', 1)[-1]
        elif kind == 'key':
            assert r['recorded_new_game_prefix'] == previous_trace.rsplit('/', 1)[-1]
        else:
            assert previous_trace.rsplit('/', 1)[-1] in [r['recorded_combat_prefix'], r['recorded_service_prefix']]
        previous = frame
        previous_trace = trace
        for name, expected in p['evidence'].items():
            assert sha(read(root+'/'+name)) == expected
        a, writes = recording(ROOT/root, c)
        read(root+'/assistance.json')
        assert len(a['episodes']) == 7 and a['boss_room'] == 0x179 and a['activation_after_frame'] == prior['campaign_frames']
        assert all(a[key] is None for key in ['first_boss_entry', 'release_write_frame', 'first_boss_combat', 'first_boss_damage'])
        assert not a['boss_assistance'] and not a['primary_state_imports'] and not a['health_refills']
        assert all(address == sy['hero_hurt'] for _, address, _ in writes)
        for stem, ext in [('ram', 'bin'), ('frame', 'png')]:
            filename = f'/{stem}_{frame:05d}.{ext}'
            assert read(root+filename) == read(proof+filename)
        raw = read(root+f'/ram_{frame:05d}.bin')
        data = lambda n, k: bytes(raw[(sy[n]+i)^1] for i in range(k))
        word = lambda n: int.from_bytes(data(n, 2), 'big')
        assert word('room_id') == room and word('game_state') == 12 and word('hero_health') > 0
        assert word('hero_max_health') == 80 and word('hero_selected_item') == word('hero_weapon_level') == 1
        assert data('game_save_state', 592)[0x1f:0x28] == bytes([128]*6+[0]*3)
        items = data('hero_items', 17)
        assert items[10] == 1 and items[12:15] == bytes([1, 1, 1]) and word('hero_attack_speed') == 1
        assert items[15] == 0
        if kind == 'gift':
            amount = 30
            assert r['passed'] and r['last_state']['gold'] - r['first_state']['gold'] == amount
            assert r['new_assistance_writes'] == 0 and data('game_save_state', 592)[0x50+room] & 2
        if trace.endswith('goldac-route01'):
            assert r['required_chop'] == [0xac, 0x1c] and r['required_chop_verified']
        if trace.endswith('return-route02'):
            assert word('hero_keys') == 1
        if kind == 'purchase':
            assert r['passed'] and r['keys_bought'] == 1 and r['unit_price'] == 60
            assert r['first_state']['gold'] - r['last_state']['gold'] == 60 and word('hero_keys') == 1
            assert r['new_assistance_writes'] == 0 and not r['currency_or_inventory_fixtures']
        if kind == 'key':
            assert r['new_key_verified'] and r['target_entry_keys'] == 0 and word('hero_keys') == 1
            assert not r['deaths']
            assert data('game_save_state', 592)[0x50+0xdb] & 0x20
            events = load(root+'/events.json')
            assert any(e.get('room') == 0x1db and e.get('keys') == 0 and e.get('room_flags', 0) & 0x20 for e in events)
        stages.append(dict(trace=trace, kind=kind, frames=frame, room=room, health=word('hero_health'),
                           keys=word('hero_keys'), gold=word('hero_gold'), whole_ram_png_exact=True))
    rejected = load('validation/natural-dungeon-route/md-v0306-d7-merchant2e-route01/route_report.json')
    fixed = load('validation/natural-dungeon-route/md-v0306-d7-merchant2e-route02/route_report.json')
    assert rejected['last_state']['health'] == 20 and not load('validation/natural-dungeon-route/md-v0306-d7-merchant2e-route01/assistance.json')['preserve_floor_hurt_requested']
    assert load('validation/natural-dungeon-route/md-v0306-d7-merchant2e-route02/assistance.json')['preserve_floor_hurt_requested']
    assert fixed['last_state']['health'] == 76
    events = load('validation/natural-dungeon-route/md-v0306-d7-merchant2e-route02/events.json')
    health_events = [(e['frame'], e['health']) for e in events if 'health' in e]
    drops = [(f, old_hp, hp) for (_, old_hp), (f, hp) in zip(health_events, health_events[1:]) if hp < old_hp]
    assert len(drops) == 1 and drops[0][1:] == (80, 76)
    assert load('validation/natural-dungeon-route/md-v0306-d7-return-route02/assistance.json')['preserve_floor_hurt_requested']
    assert load('validation/natural-dungeon-combat/md-auto-v0306-d7-key02/assistance.json')['preserve_floor_hurt_requested']
    read('tools/summarize_d7_supplies_v0306.py')
    result = dict(passed=True, version=306, md_sha256=digest, production_rom_unchanged=True,
                  stages=stages, gift_amount=60, keys_purchased=1, key_unit_price=60,
                  first_dungeon_key_acquired=True, bought_key_spent_on_entry_door=True,
                  current_campaign_trace='validation/'+stages[-1]['trace'], campaign_frames=stages[-1]['frames'],
                  six_crystals_preserved=True, seventh_boss_entered=False, seventh_crystal_obtained=False,
                  currency_or_inventory_fixtures=False, injected_health_refills=0,
                  floor_cooldown_preserved_on_selected_later_routes=True, rejected_floor_reset_branch_not_promoted=True,
                  full_game_validated=False, evidence=refs, limits=[
                      'Merchant-route01 and its purchase branch are rejected: the diagnostic guard repeatedly reset natural floor cooldown. Route02 and subsequent dungeon steps explicitly preserve it. The interrupted return01 was not promoted.',
                      'Gifts7D/AC add30/30 horns;merchant2E sells an actual key for60. Ordinary input opens the entry lock and obtains the room1CB key. No currency,ownership or progression is injected.',
                      'Approach-only hero_hurt assistance is explicitly recorded. Seven episodes include the six prior main bosses,whose guards ended before their fights. The seventh boss has not been entered.',
                      'Independent cold replays match full RAM and PNG for these eight checkpoints. No current D7 boss,ending,saves or complete source campaign/fidelity claim follows.'])
    (ROOT/'analysis/d7_supplies_v0306_report.json').write_bytes((json.dumps(result, indent=2)+'\n').encode())
    print('v306:D7 gift,purchased key,entry lock and first key independently replayed;ROM unchanged')


if __name__ == '__main__':
    main()
