"""Seventh crystal and unassisted exit, with corrected instruction-stack audit."""
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
    prior = load('analysis/d7_navigation_v0304_report.json')
    assert prior['passed'] and prior['ready_room'] == 0x189 and prior['ready_health'] == 80
    digest = sha(read('versions/v0304-b7b4e150/gaw-megadrive-v0304.bin'))
    assert digest == prior['md_sha256']
    seen, hashes = set(), set()
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
    source_index('analysis/d7_sentinel_v0304_source_index.json')
    original = read('input/original.sms')
    assert original[0x3234e+0x179*8:0x32356+0x179*8] == bytes([0x67]+[0]*7)
    assert original[0x320ea+(0x67-0x20)*4:0x320ee+(0x67-0x20)*4] == bytes.fromhex('3c120240')
    symbol_file = 'validation/stack-v0304-d7-all/symbol.txt'
    read(symbol_file)
    sy = symbols(ROOT/symbol_file)
    stages, shared_writes = [], None
    previous, previous_name = 181983, 'md-auto-v0304-d7-approach03'
    for suffix in ['boss01', 'boss03', 'return-earth01', 'exit02']:
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
        assert a['driver_sha256'] in hashes and r['driver_sha256'] in hashes
        assert a['boss_room'] == 0x179 and len(a['episodes']) == 7 and not a['boss_assistance']
        assert a['release_write_frame'] == 182050 and a['first_boss_combat'] == dict(frame=182077, health=80, hurt=0)
        assert a['first_boss_damage'] == dict(frame=182232, before=80, after=78, hurt=47)
        assert max(f for f, _, _ in writes) == 182050 and all(address == sy['hero_hurt'] for _, address, _ in writes)
        assert not a['primary_state_imports'] and not a['health_refills'] and not a['rom_modifications']
        if shared_writes is None:
            shared_writes = writes
        else:
            assert writes == shared_writes
        assert not r['deaths']
        if 'full_ram_prediction_matches' in r:
            assert r['full_ram_prediction_matches'] == r['verified_persistent_prediction_windows']
            assert not r['stack_only_difference_windows'] and not r['primary_state_imports']
        for key, value in r.items():
            if value is not None and key.endswith(('driver_sha256', 'wrapper_sha256', 'aim_sha256', 'controller_sha256')):
                assert value in hashes, (key, value)
        for stem, ext in [('ram', 'bin'), ('frame', 'png')]:
            filename = f'/{stem}_{frame:05d}.{ext}'
            assert read(root+filename) == read(proof+filename)
        raw = read(root+f'/ram_{frame:05d}.bin')
        data = lambda n, k: bytes(raw[(sy[n]+i)^1] for i in range(k))
        word = lambda n: int.from_bytes(data(n, 2), 'big')
        capacity, crystals = (80, 6) if suffix == 'boss01' else (88, 7)
        assert word('game_state') == 12 and word('hero_max_health') == capacity and word('hero_health') > 0
        assert word('hero_keys') == 2 and word('sound_unhandled_command') == 0
        assert word('hero_selected_item') == word('hero_weapon_level') == 1
        items = data('hero_items', 17)
        assert items[10] == items[16] == 1 and items[12:15] == bytes([1, 1, 1]) and not items[15]
        assert word('hero_attack_speed') == 1
        assert data('game_save_state', 592)[0x1f:0x28] == bytes([128]*crystals+[0]*(9-crystals))
        if suffix == 'boss01':
            assert frame == 185677 and r['failure'] == 'frame_limit' and not r['room_cleared']
            assert a['test_stop_reason'] == 'boss_frame_budget' and r['full_ram_prediction_matches'] == 225
            assert word('hero_health') == 78 and data('world_actor_state', 768)[24] == 26
        else:
            assert r['failure'] is None
        if suffix == 'boss03':
            assert frame == 187841 and r['room_cleared'] and word('hero_health') == 88
            assert word('hero_magic') == 48 and not word('item_reward_active')
            events = load(root+'/events.json')
            assert min(e['health'] for e in events if e['max_health'] == 80) == 42
        if suffix == 'return-earth01':
            assert r['passed'] and r['earth_action_only_requested'] and r['earth_cell_cleared']
            assert r['earth_passage_room'] == 0x1b7 and r['earth_cell'] == 0x57 and r['earth_state_writes'] == 0
            assert r['earth_before']['magic'] - r['earth_opened']['magic'] == 8
            assert a['new_assistance_writes'] == 0 and not r['full_dungeon_cleared']
            assert word('room_id') == 0x1b7 and data('scratch', 4096)[0x857] == 0
        if suffix == 'exit02':
            assert r['full_dungeon_cleared'] and r['dungeon_exit_verified'] and a['new_assistance_writes'] == 0
            assert word('room_id') == 0x1b and word('world_dungeon_number') == 0
        stages.append(dict(trace=root, frames=frame, room=word('room_id'), health=word('hero_health'),
                           max_health=capacity, crystals=crystals, prediction_windows=r.get('full_ram_prediction_matches'),
                           whole_ram_png_exact=True, partial_combat_only=suffix=='boss01'))
    alternative = 'validation/natural-dungeon-combat/md-auto-v0304-d7-boss02'
    ar, ac = load(alternative+'/report.json'), load(alternative+'/capture.json')
    ap = load(alternative+f'-assisted-fixed-replay-{ac["frames"]}/replay_report.json')
    assert ar['failure'] == 'frame_limit' and ar['recorded_new_game_prefix'] == 'md-auto-v0304-d7-boss01'
    assert ar['last_state']['health'] == 78 and ar['last_actors'][0]['hp'] == 18
    assert ap['passed'] and ap['whole_ram_bytes'] == 65536 and ap['final_png_exact']
    assert ar['full_ram_prediction_matches'] == ar['verified_persistent_prediction_windows'] == 112
    stack = load('validation/stack-v0304-d7-all/stack_report.json')
    assert stack['md_sha256'] == digest and stack['frames'] == previous and stack['all_instructions']
    assert not stack['invalid_heap_examples'] and stack['read_only']
    assert stack['minimum_instruction_sp'] == min(x['sp'] for x in stack['instruction_minima'])
    assert stack['minimum_sp'] == min(stack['minimum_instruction_sp'], stack['minimum_sampled_sp'])
    boundary = max(x['end']+2 for x in stack['heap_changes'])
    margin = stack['minimum_sp']-boundary
    assert margin > 0
    for stem, ext in [('ram', 'bin'), ('frame', 'png')]:
        filename = f'/{stem}_{previous:05d}.{ext}'
        assert read('validation/stack-v0304-d7-all'+filename) == read(stages[-1]['trace']+filename)
    read('tools/summarize_d7_campaign_v0304.py')
    result = dict(passed=True, version=304, md_sha256=digest, production_rom_unchanged=True, stages=stages,
                  seventh_crystal_and_exterior_exit=True, exit_room=0x1b, exit_health=stages[-1]['health'], max_health=88,
                  keys_remaining=2, ship_owned=True, main_boss_assistance=False, primary_state_imports=0,
                  injected_health_refills=0, minimum_health_before_reward=42, guard_release_lead_frames=27,
                  source_boss_stats='3c120240', alternative_partial_branch_excluded=True,
                  observed_stack_margin_bytes=margin, stack_frames=previous,
                  sampled_stack_margin_bytes=stack['minimum_sampled_sp']-boundary,
                  source_boss_fight_compared=False, full_game_validated=False, evidence=refs, limits=[
                      'Successful chain is partial boss01 -> ordinary-input boss03 victory -> return-earth01 -> exit02. Alternate step32 boss02 ends at18 bossHP and is a separate cold-replayed partial,never an imported shortcut to victory.',
                      'All approach writes end182050,27 frames before combat182077 at80HP andhurt0. Ordinary damage is observed182232. Hero reaches42HP before the native crystal reward heals to88;return adds no assistance.',
                      'The prior approach includes an assisted intermediate type78 fight. This report proves the designated main boss179 and its return without protection,not an entirely unassisted campaign.',
                      'The return uses real Earth in1B7 to clear block57 before its portal. Inventory,8MP cast,re-equipping axe and final exit add no assistance writes.',
                      'Whole-RAM/final-PNG replays and corrected all-instruction SP metric cover this recorded path. The sampled-entry SP minimum is retained separately.',
                      'D8 onward,ending,saves,global RNG/phase,complete SMS campaign and full video/audio/hardware fidelity remain unproved.'])
    (ROOT/'analysis/d7_campaign_v0304_report.json').write_bytes((json.dumps(result, indent=2)+'\n').encode())
    print(f'v304:seventh crystal and exterior1B return;HP{stages[-1]["health"]}/88;instruction-stack margin{margin};ROM unchanged')


if __name__ == '__main__':
    main()
