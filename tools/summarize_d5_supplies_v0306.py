"""Audit current-ROM D5 boots, actual supplies and the pre-boss contact route."""
import json
from run_core import ROOT
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from validate_playable_sprite_limit import symbols
from validate_reward_hud_restore import translated
from assisted_prefix import recording

STAGES = [
    ('natural-dungeon-combat', 'md-auto-v0306-d5-key02', 'key'),
    ('natural-dungeon-combat', 'md-auto-v0306-d5-earth01', 'earth'),
    ('natural-dungeon-combat', 'md-auto-v0306-d5-boots01', 'boots'),
    ('natural-dungeon-combat', 'md-auto-v0306-d5-supply-exit01', 'exit'),
    ('natural-dungeon-route', 'md-v0306-d5-golda1-entry01', 'route'),
    ('natural-service-route', 'md-v0306-d5-golda1-gift01', 'gold'),
    ('natural-dungeon-route', 'md-v0306-d5-goldb4-entry01', 'route'),
    ('natural-service-route', 'md-v0306-d5-goldb4-gift01', 'gold'),
    ('natural-dungeon-route', 'md-v0306-d5-merchant94-entry01', 'route'),
    ('natural-service-route', 'md-v0306-d5-key94-buy01', 'purchase'),
    ('natural-dungeon-route', 'md-v0306-d5-return-entry01', 'route'),
    ('natural-dungeon-combat', 'md-auto-v0306-d5-warp01', 'earth'),
    ('natural-dungeon-combat', 'md-auto-v0306-d5-contact01', 'contact'),
]


def main():
    refs = {}

    def read(name):
        raw = evidence(ROOT / name)
        refs[name] = sha(raw)
        return raw

    def load(name):
        return json.loads(read(name))

    prior = load('analysis/fire_sword_v0306_report.json')
    assert prior['passed'] and prior['d5_entrance_reached'] and not prior['d5_crystal_verified']
    digest = sha((ROOT / 'gaw-megadrive.bin').read_bytes())
    assert digest == prior['md_sha256']
    sy = symbols(ROOT / 'megadrive/out/release/symbol.txt')
    old_index = load('validation/v0306-d5-sources/source_index.json')
    new_index = load('validation/v0306-d5-sources/service_and_basic_index.json')
    for name, h in old_index.items():
        assert sha(read('validation/v0306-d5-sources/' + name.split('/')[-1])) == h
        if name.startswith('megadrive/'):
            assert sha((ROOT / name).read_bytes()) == h
    for name, item in new_index.items():
        assert sha(read('validation/v0306-d5-sources/' + item['snapshot'])) == item['sha256']
        assert sha((ROOT / name).read_bytes()) == item['sha256']
    drivers = {old_index['tools/natural_dungeon_combat.py'], new_index['tools/natural_dungeon_combat.py']['sha256']}
    previous_root = 'validation/natural-dungeon-route/md-v0306-d5-entry01'
    previous_c = load(previous_root + '/capture.json')
    _, previous_writes = recording(ROOT / previous_root, previous_c)
    stages = []
    gold_visits = []
    boot_hud_words = 0
    for family, name, kind in STAGES:
        root = f'validation/{family}/{name}'
        c = load(root + '/capture.json')
        r = load(root + ('/route_report.json' if kind == 'route' else '/report.json'))
        f = c['frames']
        assert c['rom_sha256'] == r['rom_sha256'] == digest
        assert c['sram_input'] is None
        if 'sram_checkpoint_injection' in r:
            assert not r['sram_checkpoint_injection']
        assert f > previous_c['frames'] and r['failure'] is None
        if kind == 'route':
            assert r['prefix_end'] == previous_c['frames'] and r['reached_entrance'] and r['directional_probe_succeeded']
            assert not r['normal_continues']
        elif family == 'natural-service-route':
            assert r['passed'] and r['source_prefix'] == previous_root.split('/')[-1]
            assert r['new_assistance_writes'] == 0
        else:
            assert r['recorded_new_game_prefix'] == previous_root.split('/')[-1]
            assert r['prefix_end'] == previous_c['frames'] and not r['deaths']
            assert r['driver_sha256'] in drivers
            if kind not in ['earth', 'contact']:
                assert r['room_cleared']
        assist, writes = recording(ROOT / root, c)
        read(root + '/assistance.json')
        assert len(assist['episodes']) == 5 and assist['boss_room'] == 0x163
        assert assist['activation_after_frame'] == 86364
        assert assist['first_boss_entry'] is None and assist['first_boss_combat'] is None
        assert not assist['boss_assistance'] and not assist['primary_state_imports'] and not assist['health_refills']
        assert writes[:len(previous_writes)] == previous_writes
        assert all(address == sy['hero_hurt'] for _, address, _ in writes)
        if family == 'natural-service-route':
            assert writes == previous_writes
        proof_root = root + f'-assisted-fixed-replay-{f}'
        proof = load(proof_root + '/replay_report.json')
        assert proof['passed'] and proof['whole_ram_bytes'] == 65536 and proof['final_png_exact']
        assert not proof['feedback_reads'] and proof['rom_sha256'] == digest
        for n in ['capture.json', 'controls.json', 'assistance.json']:
            assert proof['evidence'][n] == sha(read(root + '/' + n))
        raw = read(root + f'/ram_{f:05d}.bin')
        assert raw == read(proof_root + f'/ram_{f:05d}.bin')
        assert read(root + f'/frame_{f:05d}.png') == read(proof_root + f'/frame_{f:05d}.png')
        data = lambda n, k: bytes(raw[(sy[n] + i) ^ 1] for i in range(k))
        word = lambda n: int.from_bytes(data(n, 2), 'big')
        items = data('hero_items', 17)
        assert data('game_save_state', 592)[0x1f:0x28] == bytes([128] * 4 + [0] * 5)
        assert word('hero_max_health') == 64 and word('hero_health') > 0
        assert word('game_state') == 12 and not word('sound_unhandled_command')
        assert items[4] == 1 and not items[8] and items[12] and items[13]
        assert items[0] == word('hero_basic_level') == 2 and word('hero_armor_level') == 1
        if kind == 'key':
            assert r['new_key_verified'] and word('hero_keys') == 1
        if kind == 'earth':
            assert r['earth_route_passed'] and r['earth_passage_traversed'] and not r['earth_state_writes']
            assert r['earth_before']['magic'] - r['earth_opened']['magic'] == 8
            assert r['earth_before']['cell'] == 11 and r['earth_opened']['cell'] != 11
        if kind == 'boots':
            assert items[14] == 1 and r['collect_item_requested'] == 14 and r['last_state']['item_value'] == 1
            vram = read(root + f'/vram_{f:05d}.bin')
            regs = read(root + f'/vdp_regs_{f:05d}.bin')
            sms = data('sms_vram', 16384)
            base = (regs[2] & 56) << 10
            width = [32, 64, 32, 128][regs[16] & 3]
            for n in range(128):
                w = int.from_bytes(sms[0x3d00+n*2:0x3d02+n*2], 'little')
                at = base + ((n//32+22)*width+n%32)*2
                assert int.from_bytes(vram[at:at+2], 'little') == translated(w)
            boot_hud_words = 128
        if kind == 'exit':
            assert r['exit_before_crystal_requested'] and r['dungeon_exit_verified'] and not r['full_dungeon_cleared']
            assert word('room_id') == 0x49 and word('world_dungeon_number') == 0
        if kind == 'gold':
            assert r['last_state']['gold'] - r['first_state']['gold'] == 30
            assert r['last_state']['outside_flags'] == r['first_state']['outside_flags'] | 2
            gold_visits.append(dict(outside=word('room_id'), before=r['first_state']['gold'], after=r['last_state']['gold']))
        if kind == 'purchase':
            assert r['keys_bought'] == 1 and r['unit_price'] == 60
            assert r['first_state']['gold'] == 70 and r['last_state']['gold'] == 10
            assert r['first_state']['keys'] == 0 and r['last_state']['keys'] == 1
            assert r['free_healing_completed'] and r['first_state']['health'] == 42 and word('hero_health') == 64
            assert not r['currency_or_inventory_fixtures']
        if kind == 'contact':
            assert r['contact_route_passed'] and not r['contact_state_writes']
            assert r['contact_room'] == 0x162 and r['contact_destination'] == 0x172
            assert r['contact_opened']['flags'] & 4
        stages.append(dict(trace=root, frames=f, kind=kind, room=word('room_id'),
                           health=word('hero_health'), max_health=word('hero_max_health'),
                           keys=word('hero_keys'), gold=word('hero_gold'), magic=word('hero_magic'),
                           boots=items[14], selected=word('hero_selected_item'), whole_ram_png_exact=True))
        previous_root, previous_c, previous_writes = root, c, writes
    assert len(gold_visits) == 2 and stages[-1]['room'] == 0x172 and stages[-1]['keys'] == 1
    result = dict(passed=True, version=306, md_sha256=digest, production_rom_unchanged=True,
                  stages=stages, gold_gifts=gold_visits, boots_acquired=True, boots_physical_hud_words_exact=boot_hud_words,
                  real_key_purchase_price=60, real_free_heal=True, four_crystals_retained=True,
                  fifth_boss_entered=False, fifth_crystal_validated=False, full_game_validated=False,
                  ready_trace=previous_root, ready_frame=previous_c['frames'], evidence=refs,
                  limits=['Approach-assisted cold campaign, with only logged hero_hurt writes; no boss guard, HP/currency/MP/items/actors/progression/SRAM fixture.',
                          'All13 stages independently replay full65536RAM/finalPNG. Fifth main boss and crystal are not yet validated.',
                          'Closed-map armor attempt belongs to the previous report; no armor acquisition is claimed.',
                          'The optional equipment selector changes the test controller only; the distributed ROM remains v0306.'])
    (ROOT / 'analysis/d5_supplies_v0306_report.json').write_bytes((json.dumps(result, indent=2) + '\n').encode())
    print('v306 D5 supplies verified:', len(stages), 'stages; ready', previous_c['frames'])


if __name__ == '__main__':
    main()
