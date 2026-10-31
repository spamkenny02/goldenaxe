"""Audit current-ROM Oil->Fire->Long Sword progression and a D5 entrance."""
import json
from run_core import ROOT
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from validate_playable_sprite_limit import symbols
from assisted_prefix import recording


STAGES = [
    ('natural-dungeon-route', 'md-v0306-fire-entry01', 'route'),
    ('natural-service-route', 'md-v0306-fire-intro01', 'intro'),
    ('natural-dungeon-route', 'md-v0306-fire-entry02', 'route'),
    ('natural-service-route', 'md-v0306-fire-learn01', 'learn'),
    ('natural-dungeon-route', 'md-v0306-sword2-entry01', 'route'),
    ('natural-service-route', 'md-v0306-sword2-gift01', 'sword'),
    ('natural-dungeon-route', 'md-v0306-d5-entry01', 'route'),
]


def main():
    refs = {}

    def read(name):
        raw = evidence(ROOT / name)
        refs[name] = sha(raw)
        return raw

    def load(name):
        return json.loads(read(name))

    digest = sha((ROOT / 'gaw-megadrive.bin').read_bytes())
    release = load('analysis/reward_hud_v0306_report.json')
    assert release['passed'] and release['version'] == 306 and release['md_sha256'] == digest
    assert release['four_crystals_current_rom_replayed'] and not release['full_game_validated']
    assert sha((ROOT / 'versions/v0306-3a12380b/gaw-megadrive-v0306.bin').read_bytes()) == digest
    assert sha((ROOT / 'gaw-title-megadrive.bin').read_bytes()) == digest
    sy = symbols(ROOT / 'megadrive/out/release/symbol.txt')
    base = 'validation/natural-dungeon-combat/md-auto-v0306-d4-rebase01'
    previous_capture = load(base + '/capture.json')
    previous_assist, previous_writes = recording(ROOT / base, previous_capture)
    previous_root = base
    stages = []
    final_raw = None
    for family, name, kind in STAGES:
        root = f'validation/{family}/{name}'
        c = load(root + '/capture.json')
        report = load(root + ('/route_report.json' if kind == 'route' else '/report.json'))
        frame = c['frames']
        assert c['rom_sha256'] == report['rom_sha256'] == digest
        assert c['sram_input'] is None and not report['sram_checkpoint_injection']
        assert frame > previous_capture['frames'] and report['failure'] is None
        if kind == 'route':
            assert report['prefix_end'] == previous_capture['frames']
            assert report['reached_entrance'] and report['directional_probe_succeeded']
            assert not report['normal_continues']
        else:
            assert report['passed'] and report['new_assistance_writes'] == 0
            assert report['source_prefix'] == previous_root.split('/')[-1]
        assist, writes = recording(ROOT / root, c)
        read(root + '/assistance.json')
        assert len(assist['episodes']) == 5
        assert assist['boss_room'] == 0x163 and assist['activation_after_frame'] == 86364
        assert assist['first_boss_entry'] is None and assist['first_boss_combat'] is None
        assert not assist['boss_assistance'] and not assist['health_refills'] and not assist['primary_state_imports']
        assert all(address == sy['hero_hurt'] for _, address, _ in writes)
        assert writes[:len(previous_writes)] == previous_writes
        if kind != 'route':
            assert writes == previous_writes
        proof = load(root + f'-assisted-fixed-replay-{frame}/replay_report.json')
        assert proof['passed'] and proof['frames'] == frame and proof['rom_sha256'] == digest
        assert proof['whole_ram_bytes'] == 65536 and proof['final_png_exact'] and not proof['feedback_reads']
        for n in ['capture.json', 'controls.json', 'assistance.json']:
            assert proof['evidence'][n] == sha(read(root + '/' + n))
        raw = read(root + f'/ram_{frame:05d}.bin')
        read(root + f'/frame_{frame:05d}.png')
        data = lambda n, k: bytes(raw[(sy[n] + i) ^ 1] for i in range(k))
        word = lambda n: int.from_bytes(data(n, 2), 'big')
        items = data('hero_items', 17)
        assert data('game_save_state', 592)[0x1f:0x28] == bytes([128] * 4 + [0] * 5)
        assert word('hero_health') > 0 and word('hero_max_health') == 64
        assert word('game_state') == 12 and not word('sound_unhandled_command')
        assert items[12] and items[13] and word('hero_weapon_level') == 1
        if kind == 'intro':
            assert items[4] == 0 and items[8] == 1
            assert data('game_save_state', 592)[0x43] == 1
            assert word('hero_magic') == word('hero_max_magic') == 48
        if kind == 'learn':
            assert items[4] == 1 and items[8] == 0
            assert word('hero_magic') == word('hero_max_magic') == 72
            assert report['first_state']['level'] == 0 and report['last_state']['level'] == 1
            assert report['first_state']['gold'] == report['last_state']['gold'] == 9
        if kind == 'sword':
            assert word('hero_basic_level') == items[0] == 2
            assert word('hero_armor_level') == 1
            assert report['reward_observed']
            assert report['first_state']['basic'] == 1 and report['last_state']['basic'] == 2
            assert report['last_state']['flags'] == report['first_state']['flags'] | 2
            assert report['first_state']['gold'] == report['last_state']['gold'] == 9
        stages.append(dict(trace=root, frames=frame, kind=kind, room=word('room_id'),
                           health=word('hero_health'), max_health=word('hero_max_health'),
                           magic=word('hero_magic'), max_magic=word('hero_max_magic'),
                           fire=items[4], oil=items[8], basic=word('hero_basic_level'),
                           armor=word('hero_armor_level'), selected=word('hero_selected_item'),
                           whole_ram_png_exact=True))
        previous_capture, previous_root, previous_writes = c, root, writes
        if kind == 'sword':
            final_raw = raw
    assert stages[-1]['room'] == 0x186 and stages[-1]['fire'] == 1 and stages[-1]['basic'] == 2
    source_index = load('validation/v0306-equipment-sources/source_index.json')
    for n, h in source_index.items():
        assert sha(read('validation/v0306-equipment-sources/' + n.split('/')[-1])) == h
        assert sha((ROOT / n).read_bytes()) == h
    comparison = load('analysis/spell_teacher_game_v0306-fire-learn_report.json')
    assert comparison['passed'] and comparison['md_sha256'] == digest and comparison['controlled_fixtures']
    assert len(comparison['cases']) == 2 and not comparison['missing_service_reproduced']
    for case in comparison['cases']:
        assert case['sms']['rows'][-1]['fields'] == case['md']['rows'][-1]['fields']
    door = load('analysis/canoe_house_v0306-entry01_report.json')
    assert door['md_sha256'] == digest and door['controlled_fixtures']
    assert all(not case[tag]['entered'] for case in door['cases'] for tag in ['sms', 'md'])
    clear = load('analysis/room_clear_reference.json')
    assert any(r['room'] == 0x27 and r['kind'] == 7 for r in clear['records'])
    rejected = load('validation/natural-dungeon-route/md-v0306-armor2-entry02/route_report.json')
    assert not rejected['reached_entrance'] and rejected['failure'] == 'no_waypoint_progress'
    stack_root = 'validation/stack-v0306-fire-sword-all'
    stack = load(stack_root + '/stack_report.json')
    assert stack['md_sha256'] == digest and stack['all_instructions'] and stack['logged_assistance_replayed']
    assert not stack['invalid_heap_examples'] and stack['frames'] == 96309
    margin = stack['minimum_instruction_sp'] - max(row['end'] + 2 for row in stack['heap_changes'])
    assert margin > 0
    assert read(stack_root + '/ram_96309.bin') == final_raw
    assert read(stack_root + '/frame_96309.png') == read('validation/natural-service-route/md-v0306-sword2-gift01/frame_96309.png')
    result = dict(passed=True, version=306, md_sha256=digest, production_rom_unchanged=True,
                  stages=stages, fire_oil_exchange_verified=True, long_sword_gift_verified=True,
                  d5_entrance_reached=True, d5_crystal_verified=False,
                  observed_instruction_stack_margin_bytes=margin, stack_scope_frames=96309,
                  armor_quest_not_obtained=True, four_crystals_current_rom=True,
                  full_game_validated=False, evidence=refs,
                  limits=['Approach-assisted cold campaign; no main boss assistance, ownership/currency/HP fixture or SRAM import.',
                          'The D5 approach guard remains pending. No D5 boss win is claimed.',
                          'Town27 remains closed before its original room-clear transformation. The comparison uses a closed-map fixture, not a natural clear or armor acquisition.',
                          'The all-instruction stack profile stops after the Long Sword gift; it does not cover the later D5 entrance.',
                          'Sword level2 is owned; the axe remains selected. No global audio/video timing or complete campaign claim.'])
    (ROOT / 'analysis/fire_sword_v0306_report.json').write_bytes((json.dumps(result, indent=2) + '\n').encode())
    print({k: v for k, v in result.items() if k not in ['evidence', 'limits']})


if __name__ == '__main__':
    main()
