"""Audit the sixth crystal and ordinary return on the unchanged v304 ROM."""
import json
from run_core import ROOT
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols


def main():
    refs = {}
    def read(name):
        raw = evidence(ROOT / name)
        refs[name] = sha(raw)
        return raw
    def load(name):
        return json.loads(read(name))
    digest = sha(read('versions/v0304-b7b4e150/gaw-megadrive-v0304.bin'))
    prior = load('analysis/d6_progress_v0304_report.json')
    assert prior['passed'] and prior['md_sha256'] == digest
    seen = set()
    source_hashes = set()
    def sources(name):
        if name in seen:
            return
        seen.add(name)
        index = load(name)
        for key, value in index.items():
            if key.endswith('source_index') or key.endswith('controller_index'):
                sources(value)
        for item in index.get('sources', {}).values():
            assert sha(read(item['path'])) == item['sha256']
            source_hashes.add(item['sha256'])
    sources('analysis/d6_progress_v0304_source_index.json')
    symbol_file = 'validation/stack-v0304-d6-all/symbol.txt'
    read(symbol_file)
    sy = symbols(ROOT / symbol_file)
    original = read('input/original.sms')
    assert original[0x3234e+0x115*8:0x32356+0x115*8] == bytes([0x64]+[0]*7)
    assert original[0x320ea+(0x64-0x20)*4:0x320ee+(0x64-0x20)*4] == bytes.fromhex('3c140440')
    stages = []
    previous = prior['stages'][-1]['frames']
    first_writes = None
    for suffix in ['boss01', 'boss03', 'exit01']:
        root = 'validation/natural-dungeon-combat/md-auto-v0304-d6-' + suffix
        c, r = load(root+'/capture.json'), load(root+'/report.json')
        frame = c['frames']
        proof_root = root+f'-assisted-fixed-replay-{frame}'
        p = load(proof_root+'/replay_report.json')
        assert r['prefix_end'] == previous and c['rom_sha256'] == p['rom_sha256'] == digest
        previous = frame
        assert c['sram_input'] is None and p['passed'] and not p['feedback_reads']
        assert p['whole_ram_bytes'] == 65536 and p['final_png_exact']
        for name, expected in p['evidence'].items():
            assert sha(read(root+'/'+name)) == expected
        a, writes = recording(ROOT/root, c)
        read(root+'/assistance.json')
        assert a['boss_room'] == 0x115 and len(a['episodes']) == 6 and not a['boss_assistance']
        assert a['release_write_frame'] == 146965
        assert a['first_boss_combat'] == dict(frame=146996, health=72, hurt=0)
        assert max(f for f, _, _ in writes) == 146965
        assert not a['primary_state_imports'] and not a['health_refills'] and not a['rom_modifications']
        assert all(address == sy['hero_hurt'] for _, address, _ in writes)
        if first_writes is None:
            first_writes = writes
        else:
            assert first_writes == writes
        assert not r['deaths'] and r['full_ram_prediction_matches'] == r['verified_persistent_prediction_windows']
        assert not r['stack_only_difference_windows'] and not r['primary_state_imports']
        for key, value in r.items():
            if key.endswith(('driver_sha256', 'wrapper_sha256', 'aim_sha256')):
                assert value in source_hashes, (key, value)
        for stem, ext in [('ram', 'bin'), ('frame', 'png')]:
            filename = f'/{stem}_{frame:05d}.{ext}'
            assert read(root+filename) == read(proof_root+filename)
        raw = read(root+f'/ram_{frame:05d}.bin')
        data = lambda n, k: bytes(raw[(sy[n]+i)^1] for i in range(k))
        word = lambda n: int.from_bytes(data(n, 2), 'big')
        capacity, crystals = (72, 5) if suffix == 'boss01' else (80, 6)
        assert word('hero_max_health') == capacity and word('hero_health') > 0
        assert word('hero_keys') == 0 and word('hero_selected_item') == word('hero_weapon_level') == 1
        items = data('hero_items', 17)
        assert items[10] == 1 and items[12:15] == bytes([1, 1, 1]) and word('hero_attack_speed') == 1
        assert data('game_save_state', 592)[0x1f:0x28] == bytes([128]*crystals+[0]*(9-crystals))
        if suffix == 'boss01':
            assert frame == 150596 and r['failure'] == 'frame_limit' and not r['room_cleared']
            assert a['test_stop_reason'] == 'boss_frame_budget' and word('hero_health') == 72
            actors = data('world_actor_state', 768)
            assert actors[0] == 0x64 and actors[24] == 40
            assert r['full_ram_prediction_matches'] == 450
        else:
            assert r['failure'] is None
            assert a['first_boss_damage'] == dict(frame=150687, before=72, after=58, hurt=47)
        if suffix == 'boss03':
            assert frame == 152143 and r['room_cleared'] and word('hero_health') == 80
            assert not word('item_reward_active') and word('hero_magic') == 48
            assert r['full_ram_prediction_matches'] == 104
            assert r['recorded_new_game_prefix'] == 'md-auto-v0304-d6-boss01'
        if suffix == 'exit01':
            assert r['full_dungeon_cleared'] and r['dungeon_exit_verified']
            assert a['new_assistance_writes'] == 0
            assert word('room_id') == 0x8b and word('world_dungeon_number') == 0
            assert r['recorded_new_game_prefix'] == 'md-auto-v0304-d6-boss03'
        stages.append(dict(trace=root, frames=frame, room=word('room_id'), health=word('hero_health'),
                           max_health=capacity, crystals=crystals, whole_ram_png_exact=True,
                           prediction_windows=r['full_ram_prediction_matches'], partial_combat_only=suffix=='boss01'))
    failed = load('validation/natural-dungeon-combat/md-auto-v0304-d6-boss02/report.json')
    assert failed['failure'] == 'continuation_route_died' and failed['last_state']['health'] == 0
    stack = load('validation/stack-v0304-d6-all/stack_report.json')
    assert stack['md_sha256'] == digest and stack['frames'] == previous and stack['all_instructions']
    assert not stack['invalid_heap_examples']
    margin = stack['minimum_sp'] - (stack['heap_changes'][-1]['end'] + 2)
    assert margin > 0
    for stem, ext in [('ram', 'bin'), ('frame', 'png')]:
        filename = f'/{stem}_{previous:05d}.{ext}'
        assert read('validation/stack-v0304-d6-all'+filename) == read(stages[-1]['trace']+filename)
    read('tools/summarize_d6_campaign_v0304.py')
    result = dict(passed=True, version=304, md_sha256=digest, production_rom_unchanged=True, stages=stages,
                  sixth_crystal_and_exterior_exit=True, exit_room=0x8b, exit_health=stages[-1]['health'],
                  max_health=80, keys_remaining=0, ice_bell_owned=True, boots_owned=True, canoe_owned=True,
                  rope_owned=True, axe_equipped=True, boss_assistance=False, primary_state_imports=0,
                  injected_health_refills=0, guard_release_lead_frames=31, source_boss_stats='3c140440',
                  failed_diagnostic_excluded_from_successful_chain=True, observed_stack_margin_bytes=margin,
                  stack_frames=previous, source_boss_fight_compared=False, full_game_validated=False,
                  evidence=refs, limits=[
                      'Assisted approaches only: all writes concern hero_hurt and end before the boss. Distributed ROM is unchanged.',
                      'Boss01 partial combat is cold-replayed before cautious boss03 resumes it. Defeated boss02 is a separate diagnostic, never an ancestor of victory or exit.',
                      'Three additional independent cold replays reproduce all65536 RAM bytes and final PNG. Prediction windows compare whole primary RAM. Stack margin is observed only on this route.',
                      'Six crystals and returns on v304 are established. D7 onward,ending,saves,global RNG and complete SMS video/audio/hardware fidelity remain unproved.'])
    (ROOT/'analysis/d6_campaign_v0304_report.json').write_bytes((json.dumps(result, indent=2)+'\n').encode())
    print(f'v304:sixth crystal and exterior8B return;HP{stages[-1]["health"]}/80;stack margin{margin};ROM unchanged')


if __name__ == '__main__':
    main()
