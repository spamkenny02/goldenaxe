"""Audit current-ROM sixth crystal, real exit and every-instruction stack."""
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

    prior = load('analysis/d6_progress_v0306_report.json')
    assert prior['passed'] and prior['ice_bell_acquired'] and not prior['sixth_boss_entered']
    digest = sha((ROOT / 'gaw-megadrive.bin').read_bytes())
    assert digest == prior['md_sha256']
    assert sha((ROOT / 'versions/v0306-3a12380b/gaw-megadrive-v0306.bin').read_bytes()) == digest
    sy = symbols(ROOT / 'megadrive/out/release/symbol.txt')
    family = 'validation/natural-dungeon-combat/'
    exit_name = 'md-auto-v0306-d6-exit01'
    r = load(family + exit_name + '/report.json')
    parent = r['recorded_new_game_prefix']
    ready_name = prior['ready_trace'].split('/')[-1]
    names = []
    while parent != ready_name:
        assert parent.startswith('md-auto-v0306-d6-boss') and parent not in names
        names.append(parent)
        parent = load(family + parent + '/report.json')['recorded_new_game_prefix']
    names.reverse()
    assert names
    names.append(exit_name)
    previous_root = prior['ready_trace']
    previous_c = load(previous_root + '/capture.json')
    _, previous_writes = recording(ROOT / previous_root, previous_c)
    index = load('validation/v0306-d6-sources/source_index.json')
    for name, h in index.items():
        assert sha(read('validation/v0306-d6-sources/' + name.split('/')[-1])) == h
        assert sha((ROOT / name).read_bytes()) == h
    stages = []
    release = combat = damage = None
    final_raw = final_png = None
    for number, name in enumerate(names):
        root = family + name
        c = load(root + '/capture.json')
        r = load(root + '/report.json')
        frame = c['frames']
        is_exit = name == exit_name
        victory = not is_exit and r['room_cleared']
        assert c['rom_sha256'] == r['rom_sha256'] == digest and c['sram_input'] is None
        assert not r['rom_modifications'] and not r['sram_checkpoint_injection'] and not r['deaths']
        assert r['failure'] is None if victory or is_exit else r['failure'] == 'frame_limit'
        assert r['recorded_new_game_prefix'] == previous_root.split('/')[-1]
        assert r['prefix_end'] == previous_c['frames'] and frame > previous_c['frames']
        assert r['driver_sha256'] == index['tools/natural_dungeon_combat.py']
        if 'coarse_driver_sha256' in r:
            assert r['coarse_driver_sha256'] == index['tools/assisted_boss_coarse_route.py']
        if 'cautious_driver_sha256' in r:
            assert r['cautious_driver_sha256'] == sha(read('validation/v0306-d6-sources/natural_boss_cautious_planner.py'))
        assist, writes = recording(ROOT / root, c)
        read(root + '/assistance.json')
        assert len(assist['episodes']) == 6 and assist['boss_room'] == 0x115
        assert not assist['boss_assistance'] and not assist['health_refills'] and not assist['primary_state_imports']
        assert all(address == sy['hero_hurt'] for _, address, _ in writes)
        assert writes[:len(previous_writes)] == previous_writes
        if number == 0:
            release, combat, damage = assist['release_write_frame'], assist['first_boss_combat'], assist['first_boss_damage']
            assert release < combat['frame'] and combat['hurt'] == 0
            assert writes[-1][0] == release and writes[-1][2] == b'\0\0'
            if damage is not None:
                assert damage['frame'] > combat['frame'] and damage['after'] < damage['before']
        else:
            assert writes == previous_writes and assist['release_write_frame'] == release
            assert assist['first_boss_combat'] == combat
            if damage is None and assist['first_boss_damage'] is not None:
                damage = assist['first_boss_damage']
                assert damage['frame'] > combat['frame'] and damage['after'] < damage['before']
            elif damage is not None:
                assert assist['first_boss_damage'] == damage
        assert r['full_ram_prediction_matches'] == r['verified_persistent_prediction_windows'] > 0
        proof_root = root + f'-assisted-fixed-replay-{frame}'
        proof = load(proof_root + '/replay_report.json')
        assert proof['passed'] and proof['frames'] == frame and proof['rom_sha256'] == digest
        assert proof['whole_ram_bytes'] == 65536 and proof['final_png_exact'] and not proof['feedback_reads']
        for n in ['capture.json', 'controls.json', 'assistance.json']:
            assert proof['evidence'][n] == sha(read(root + '/' + n))
        raw = read(root + f'/ram_{frame:05d}.bin')
        png = read(root + f'/frame_{frame:05d}.png')
        assert raw == read(proof_root + f'/ram_{frame:05d}.bin')
        assert png == read(proof_root + f'/frame_{frame:05d}.png')
        data = lambda n, k: bytes(raw[(sy[n] + i) ^ 1] for i in range(k))
        word = lambda n: int.from_bytes(data(n, 2), 'big')
        items = data('hero_items', 17)
        assert word('game_state') == 12 and word('hero_health') > 0 and not word('sound_unhandled_command')
        assert items[0] == 2 and items[1] == 1 and items[4] == items[5] == 1
        assert items[10] == items[12] == items[13] == items[14] == 1 and not items[8]
        assert word('hero_selected_item') == 1 and word('hero_attack') == 4 and word('hero_armor_level') == 1
        if is_exit or victory:
            assert word('hero_max_health') == 80
            assert data('game_save_state', 592)[0x1f:0x28] == bytes([128] * 6 + [0] * 3)
        else:
            assert word('hero_max_health') == 72
            assert data('game_save_state', 592)[0x1f:0x28] == bytes([128] * 5 + [0] * 4)
            decisions = load(root + '/planning.json')
            initial_hp = decisions[0]['primary']['boss_hp']
            actor = data('world_actor_state', 768)
            assert actor[0] == 0x64 and 0 < actor[24] < initial_hp, 'A partial stage needs actual boss damage'
        if victory:
            assert r['collect_gem_requested'] and r['failure'] is None
            assert word('hero_health') == 80 and word('hero_magic') == word('hero_max_magic')
        if is_exit:
            assert r['full_dungeon_cleared'] and r['dungeon_exit_verified'] and not r['exit_before_crystal_requested']
            assert word('room_id') == 0x8b and word('world_dungeon_number') == 0
        stages.append(dict(trace=root, frames=frame, room=word('room_id'), health=word('hero_health'),
                           max_health=word('hero_max_health'), keys=word('hero_keys'), gold=word('hero_gold'),
                           magic=word('hero_magic'), prediction_windows=r['full_ram_prediction_matches'],
                           partial_combat_only=not (victory or is_exit), whole_ram_png_exact=True))
        previous_c, previous_root, previous_writes = c, root, writes
        final_raw, final_png = raw, png
    assert not stages[-2]['partial_combat_only']
    sms = data('sms_vram', 16384)
    v = read(previous_root + f'/vram_{previous_c["frames"]:05d}.bin')
    regs = read(previous_root + f'/vdp_regs_{previous_c["frames"]:05d}.bin')
    base = (regs[2] & 56) << 10
    width = [32, 64, 32, 128][regs[16] & 3]
    for n in range(128):
        at = base + ((n//32+22)*width+n%32)*2
        assert int.from_bytes(v[at:at+2], 'little') == translated(int.from_bytes(sms[0x3d00+n*2:0x3d02+n*2], 'little'))
    source = read('input/original.sms')
    for n in range(6):
        tile, offset = source[0x1edc+n*2:0x1ede+n*2]
        assert sms[0x3d00+offset:0x3d02+offset] == bytes([tile, 0x59])
    stack_root = 'validation/stack-v0306-d6-all'
    stack = load(stack_root + '/stack_report.json')
    assert stack['md_sha256'] == digest and stack['frames'] == previous_c['frames']
    assert stack['all_instructions'] and stack['logged_assistance_replayed'] and not stack['invalid_heap_examples']
    margin = stack['minimum_instruction_sp'] - max(row['end'] + 2 for row in stack['heap_changes'])
    assert margin > 0
    assert read(stack_root + f'/ram_{previous_c["frames"]:05d}.bin') == final_raw
    assert read(stack_root + f'/frame_{previous_c["frames"]:05d}.png') == final_png
    result = dict(passed=True, version=306, md_sha256=digest, production_rom_unchanged=True,
                  progress_report='analysis/d6_progress_v0306_report.json', stages=stages,
                  sixth_crystal_and_exterior_exit=True, main_boss_assistance=False,
                  boss_guard_release=release, first_boss_combat=combat, first_boss_damage=damage,
                  observed_instruction_stack_margin_bytes=margin, current_campaign_trace=previous_root,
                  campaign_frames=previous_c['frames'], final_hud_words_exact=128, source_crystal_markers_exact=6,
                  full_game_validated=False, evidence=refs,
                  limits=['Cold approach-assisted campaign, with no boss guard or HP/MP/inventory/currency/actor/progression/SRAM fixture.',
                          'Positive partial fights require observed boss HP loss and exact independent cold replay before extension.',
                          'Six crystals and the return to8B are proven; later campaign, ending, complete saves and global SMS RNG/audiovisual phase remain unproved.'])
    (ROOT / 'analysis/d6_campaign_v0306_report.json').write_bytes((json.dumps(result, indent=2) + '\n').encode())
    print('v306 sixth crystal and exit verified;', previous_c['frames'], 'frames; instruction stack margin', margin)


if __name__ == '__main__':
    main()
