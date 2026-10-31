"""Audit fifth crystal, ordinary return, bridge and full-route instruction stack."""
import json
from run_core import ROOT
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from validate_playable_sprite_limit import symbols
from validate_reward_hud_restore import translated
from assisted_prefix import recording

STAGES = ['md-auto-v0306-d5-boss03', 'md-auto-v0306-d5-return-contact01', 'md-auto-v0306-d5-exit01']


def main():
    refs = {}

    def read(name):
        raw = evidence(ROOT / name)
        refs[name] = sha(raw)
        return raw

    def load(name):
        return json.loads(read(name))

    prior = load('analysis/d5_supplies_v0306_report.json')
    assert prior['passed'] and prior['four_crystals_retained'] and not prior['fifth_boss_entered']
    digest = sha((ROOT / 'gaw-megadrive.bin').read_bytes())
    assert digest == prior['md_sha256']
    assert sha((ROOT / 'versions/v0306-3a12380b/gaw-megadrive-v0306.bin').read_bytes()) == digest
    sy = symbols(ROOT / 'megadrive/out/release/symbol.txt')
    index = load('validation/v0306-d5-sources/boss_source_index.json')
    for name, item in index.items():
        assert sha(read('validation/v0306-d5-sources/' + item['snapshot'])) == item['sha256']
        assert sha((ROOT / name).read_bytes()) == item['sha256']
    previous_root = prior['ready_trace']
    previous_c = load(previous_root + '/capture.json')
    _, previous_writes = recording(ROOT / previous_root, previous_c)
    stages = []
    release = combat = damage = None
    final = final_raw = final_png = None
    for number, name in enumerate(STAGES):
        root = 'validation/natural-dungeon-combat/' + name
        c = load(root + '/capture.json')
        r = load(root + '/report.json')
        f = c['frames']
        assert c['rom_sha256'] == r['rom_sha256'] == digest and c['sram_input'] is None
        assert not r['sram_checkpoint_injection'] and not r['rom_modifications']
        assert r['recorded_new_game_prefix'] == previous_root.split('/')[-1]
        assert r['prefix_end'] == previous_c['frames'] and f > previous_c['frames']
        assert r['failure'] is None and not r['deaths']
        assert r['driver_sha256'] == index['tools/natural_dungeon_combat.py']['sha256']
        assist, writes = recording(ROOT / root, c)
        read(root + '/assistance.json')
        assert len(assist['episodes']) == 5 and assist['boss_room'] == 0x163
        assert not assist['boss_assistance'] and not assist['primary_state_imports'] and not assist['health_refills']
        assert all(address == sy['hero_hurt'] for _, address, _ in writes)
        assert writes[:len(previous_writes)] == previous_writes
        if number == 0:
            assert r['room_cleared'] and r['collect_gem_requested']
            assert r['equip_basic_requested'] and not r['equip_axe_requested']
            assert r['ordinary_entry_up_requested'] and len(r['ordinary_entry_inputs']) == 8
            assert all(row['buttons'] == [4] and row['room'] == 0x163 for row in r['ordinary_entry_inputs'])
            assert [row['y'] for row in r['ordinary_entry_inputs']] == list(range(160, 144, -2))
            assert r['coarse_driver_sha256'] == index['tools/assisted_boss_coarse_route.py']['sha256']
            assert r['full_ram_prediction_matches'] == r['verified_persistent_prediction_windows'] > 0
            release, combat, damage = assist['release_write_frame'], assist['first_boss_combat'], assist['first_boss_damage']
            assert release < combat['frame'] < damage['frame'] < r['clear_frame']
            assert combat['hurt'] == 0 and damage['after'] < damage['before']
            assert writes[-1][0] == release and writes[-1][2] == b'\0\0'
        else:
            assert writes == previous_writes
            assert assist['release_write_frame'] == release and assist['first_boss_combat'] == combat
        if number == 1:
            assert r['contact_route_passed'] and not r['contact_state_writes']
            assert r['contact_room'] == 0x173 and r['contact_destination'] == 0x174
        if number == 2:
            assert r['full_dungeon_cleared'] and r['dungeon_exit_verified']
            assert not r['exit_before_crystal_requested']
            assert r['full_ram_prediction_matches'] == r['verified_persistent_prediction_windows'] > 0
        proof_root = root + f'-assisted-fixed-replay-{f}'
        proof = load(proof_root + '/replay_report.json')
        assert proof['passed'] and proof['frames'] == f and proof['rom_sha256'] == digest
        assert proof['whole_ram_bytes'] == 65536 and proof['final_png_exact'] and not proof['feedback_reads']
        for n in ['capture.json', 'controls.json', 'assistance.json']:
            assert proof['evidence'][n] == sha(read(root + '/' + n))
        raw = read(root + f'/ram_{f:05d}.bin')
        png = read(root + f'/frame_{f:05d}.png')
        assert raw == read(proof_root + f'/ram_{f:05d}.bin')
        assert png == read(proof_root + f'/frame_{f:05d}.png')
        data = lambda n, k: bytes(raw[(sy[n] + i) ^ 1] for i in range(k))
        word = lambda n: int.from_bytes(data(n, 2), 'big')
        items = data('hero_items', 17)
        assert data('game_save_state', 592)[0x1f:0x28] == bytes([128] * 5 + [0] * 4)
        assert word('hero_max_health') == 72 and word('hero_health') > 0
        assert word('game_state') == 12 and not word('sound_unhandled_command')
        assert items[4] == 1 and items[5] == 1 and not items[8]
        assert items[12] and items[13] and items[14]
        assert items[0] == word('hero_basic_level') == 2 and word('hero_selected_item') == 0
        assert word('hero_attack') == 6 and word('hero_armor_level') == 1
        if number == 0:
            assert word('hero_health') == 72 and word('hero_magic') == word('hero_max_magic') == 72
        stages.append(dict(trace=root, frames=f, room=word('room_id'), health=word('hero_health'),
                           max_health=word('hero_max_health'), keys=word('hero_keys'), gold=word('hero_gold'),
                           magic=word('hero_magic'), selected=word('hero_selected_item'),
                           whole_ram_png_exact=True, prediction_windows=r.get('full_ram_prediction_matches')))
        previous_c, previous_root, previous_writes = c, root, writes
        final, final_raw, final_png = r, raw, png
    assert stages[-1]['room'] == 0x49 and final['last_state']['dungeon'] == 0
    assert data('game_save_state', 592)[0x99] & 1
    sms = data('sms_vram', 16384)
    v = read(previous_root + f'/vram_{previous_c["frames"]:05d}.bin')
    regs = read(previous_root + f'/vdp_regs_{previous_c["frames"]:05d}.bin')
    base = (regs[2] & 56) << 10
    width = [32, 64, 32, 128][regs[16] & 3]
    for n in range(128):
        at = base + ((n//32+22)*width+n%32)*2
        assert int.from_bytes(v[at:at+2], 'little') == translated(int.from_bytes(sms[0x3d00+n*2:0x3d02+n*2], 'little'))
    source = read('input/original.sms')
    for n in range(5):
        tile, offset = source[0x1edc+n*2:0x1ede+n*2]
        assert sms[0x3d00+offset:0x3d02+offset] == bytes([tile, 0x59])
    stack_root = 'validation/stack-v0306-d5-all'
    stack = load(stack_root + '/stack_report.json')
    assert stack['md_sha256'] == digest and stack['frames'] == previous_c['frames']
    assert stack['all_instructions'] and stack['logged_assistance_replayed'] and not stack['invalid_heap_examples']
    margin = stack['minimum_instruction_sp'] - max(row['end'] + 2 for row in stack['heap_changes'])
    assert margin > 0
    assert read(stack_root + f'/ram_{previous_c["frames"]:05d}.bin') == final_raw
    assert read(stack_root + f'/frame_{previous_c["frames"]:05d}.png') == final_png
    diagnostic_root = 'validation/natural-dungeon-combat/md-auto-v0306-d5-boss01'
    diagnostic = load(diagnostic_root + '/report.json')
    assert not diagnostic['room_cleared'] and diagnostic['failure'] == 'frame_limit'
    dc = load(diagnostic_root + '/capture.json')
    dp = load(diagnostic_root + f'-assisted-fixed-replay-{dc["frames"]}/replay_report.json')
    assert dp['passed'] and dp['whole_ram_bytes'] == 65536 and dp['final_png_exact']
    result = dict(passed=True, version=306, md_sha256=digest, production_rom_unchanged=True,
                  supplies_report='analysis/d5_supplies_v0306_report.json', stages=stages,
                  fifth_crystal_and_exterior_exit=True, fifth_crystal_bridge_flag=True,
                  main_boss_assistance=False, boss_guard_release=release, first_boss_combat=combat,
                  first_boss_damage=damage, observed_instruction_stack_margin_bytes=margin,
                  current_campaign_trace=previous_root, campaign_frames=previous_c['frames'],
                  final_hud_words_exact=128, source_crystal_markers_exact=5,
                  rejected_threshold_stall_preserved=True, full_game_validated=False, evidence=refs,
                  limits=['Approach-assisted cold campaign. Guards end before each main boss; no HP/MP/items/currency/actors/progression/SRAM fixture.',
                          'Optional ordinary inventory selection equips owned Long Sword; eight ordinary UP inputs finish entering the boss room before search. These are test-controller changes, not ROM patches.',
                          'The first threshold-stall attempt is a reproduced negative diagnostic, not a boss victory.',
                          'Five crystals and an exterior return are proven on v0306. Later campaign, ending, complete saves and source RNG/global audiovisual phase remain unproved.'])
    (ROOT / 'analysis/d5_campaign_v0306_report.json').write_bytes((json.dumps(result, indent=2) + '\n').encode())
    print('v306 fifth crystal and exit verified;', previous_c['frames'], 'frames; instruction stack margin', margin)


if __name__ == '__main__':
    main()
