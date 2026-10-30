"""Audit actual Earth, thief-key reward, remote gate and pre-boss D8 route."""
import json
from run_core import ROOT
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols


def main():
    refs = {}
    def read(name):
        raw = evidence(ROOT/name); refs[name] = sha(raw); return raw
    def load(name):
        return json.loads(read(name))
    prior = load('analysis/d8_passages_v0304_report.json')
    assert prior['passed'] and prior['ready_room'] == 0x1eb
    digest = sha(read('versions/v0304-b7b4e150/gaw-megadrive-v0304.bin'))
    assert digest == prior['md_sha256']
    hashes, seen = set(), set()
    def index(name):
        if name in seen:
            return
        seen.add(name); obj = load(name)
        for key, value in obj.items():
            if key.endswith(('source_index', 'controller_index')):
                index(value)
        for item in obj.get('sources', {}).values():
            assert sha(read(item['path'])) == item['sha256']; hashes.add(item['sha256'])
    index('analysis/d8_contact_v0304_source_index.json')
    symbol_file = 'validation/v0304-d8-paid-sources/symbol.txt'
    read(symbol_file); sy = symbols(ROOT/symbol_file)
    original = read('input/original.sms')
    assert original[0x3234e+0x196*8:0x32356+0x196*8] == bytes([0x6b]+[0]*7)
    assert original[0x320ea+(0x6b-32)*4:0x320ee+(0x6b-32)*4] == bytes.fromhex('50100240')
    reward = load('analysis/item_rewards_reference.json')
    contact = load('analysis/contact_script_reference.json')
    assert reward['source_sha256'] == contact['source_sha256'] == sha(original)
    source = next(r for r in reward['records'] if r['room'] == 0x1a9)
    assert source['inventory_offset'] == 15 and source['value'] == 1 and source['coordinate'] == 856
    source = next(r for r in contact['records'] if r['room'] == 0x19a)
    assert source['kind'] == 'stationary_up_passages' and source['explicit_registers']['e'] == 0xd8
    previous, previous_name = 203862, 'md-auto-v0304-d8-switch1ec-02'
    stages = []
    for suffix, room in [('earth1e8-01', 0x1aa), ('thief-key01', 0x1a9),
                         ('switch19a-01', 0x1aa), ('approach01', 0x1a6)]:
        root = 'validation/natural-dungeon-combat/md-auto-v0304-d8-'+suffix
        c, r = load(root+'/capture.json'), load(root+'/report.json')
        frame = c['frames']; proof = root+f'-assisted-fixed-replay-{frame}'
        p = load(proof+'/replay_report.json')
        assert c['rom_sha256'] == p['rom_sha256'] == digest and c['sram_input'] is None
        assert r['failure'] is None and not r['deaths']
        assert r['prefix_end'] == previous and r['recorded_new_game_prefix'] == previous_name
        assert p['passed'] and p['whole_ram_bytes'] == 65536 and p['final_png_exact'] and not p['feedback_reads']
        for filename, expected in p['evidence'].items():
            assert sha(read(root+'/'+filename)) == expected
        a, writes = recording(ROOT/root, c); read(root+'/assistance.json')
        assert a['driver_sha256'] in hashes and len(a['episodes']) == 8 and a['boss_room'] == 0x196
        assert a['first_boss_entry'] is None and a['first_boss_combat'] is None and not a['boss_assistance']
        assert not a['primary_state_imports'] and not a['health_refills'] and not a['rom_modifications']
        assert all(address == sy['hero_hurt'] for _, address, _ in writes)
        for key, value in r.items():
            if key.endswith(('driver_sha256', 'controller_sha256', 'aim_sha256')) and value is not None:
                assert value in hashes, (key, value)
        for stem, ext in [('ram', 'bin'), ('frame', 'png')]:
            filename = f'/{stem}_{frame:05d}.{ext}'
            assert read(root+filename) == read(proof+filename)
        raw = read(root+f'/ram_{frame:05d}.bin')
        data = lambda n, k: bytes(raw[(sy[n]+i)^1] for i in range(k))
        word = lambda n: int.from_bytes(data(n, 2), 'big')
        flags = data('game_save_state', 592)[0x50:0x150]
        assert word('room_id') == room and word('game_state') == 12 and word('hero_state') == 1
        assert 0 < word('hero_health') <= 88 and word('hero_max_health') == 88 and word('hero_keys') >= 2
        assert word('world_dungeon_number') == 8 and not word('sound_unhandled_command')
        assert word('hero_selected_item') == word('hero_weapon_level') == 1 and flags[0xc8]&4
        assert data('game_save_state', 592)[0x1f:0x28] == bytes([128]*7+[0]*2)
        items = data('hero_items', 17)
        assert items[10] == items[16] == 1 and items[12:15] == bytes([1]*3)
        assert items[15] == (0 if suffix == 'earth1e8-01' else 1)
        if suffix == 'earth1e8-01':
            assert frame == 209630 and r['passed'] and r['earth_passage_traversed'] and not r['earth_state_writes']
            assert r['earth_passage_room'] == 0x1e8 and r['earth_cell'] == 0x58
            assert r['earth_before']['cell'] == 11 and r['earth_opened']['cell'] == 12
            assert r['earth_before']['magic'] == 48 and r['earth_opened']['magic'] == 40
            events = load(root+'/events.json'); rooms = [e['room'] for e in events]
            assert all(n in rooms for n in [0x1c8, 0x1d8, 0x1e8, 0x1aa])
        elif suffix == 'thief-key01':
            assert frame == 215959 and r['item_acquisition_passed'] and r['collect_item_requested'] == 15
            assert r['item_acquired_frame'] == 215559 and r['item_reward_finished_frame'] == 215859
            assert not r['item_acquisition_state_writes'] and not word('item_reward_active')
            assert r['item_acquisition_first']['owned'] == 0 and r['item_acquisition_last']['owned'] == 1
            assert word('hero_health') == 64 and not r['last_actors'] and flags[0xa9]&4
        elif suffix == 'switch19a-01':
            assert frame == 218065 and r['passed'] and r['contact_route_passed'] and not r['contact_state_writes']
            assert r['contact_room'] == 0x19a and r['contact_coordinate'] == 332
            assert flags[0xd8]&0x40 and flags[0xd7]&0x80
        else:
            assert r['room_cleared'] and not any(e['slot'] < 8 for e in r['last_actors'])
            assert flags[0xd8]&0x40 and flags[0xd7]&0x80
        stages.append(dict(trace=root, frames=frame, room=room, health=word('hero_health'), max_health=88,
                           keys=word('hero_keys'), magic=word('hero_magic'), thief_key=items[15], whole_ram_png_exact=True))
        previous, previous_name = frame, root.rsplit('/', 1)[-1]
    read('tools/summarize_d8_progress_v0304.py')
    last = stages[-1]
    result = dict(passed=True, version=304, md_sha256=digest, production_rom_unchanged=True, stages=stages,
                  ready_room=0x1a6, ready_frames=previous, ready_health=last['health'], ready_max_health=88,
                  ready_keys=last['keys'], ready_magic=last['magic'], thief_key_acquired=True,
                  actual_c8_floor_traversed=True, main_boss_room=0x196, main_boss_kind=0x6b,
                  source_boss_stats='50100240', eighth_boss_entered=False, approach_assisted=True,
                  intermediate_7a_assisted=True, full_game_validated=False, evidence=refs, limits=[
                      'Four fixed-input cold replays match all65536 RAM bytes and final PNG. Only the logged approach hero_hurt guard is written;there are no imported game states or ownership/HP/gold/progression fixtures.',
                      'The intermediate type7A remains an assisted approach fight. The designated main196/type6B boss has not been entered;its guard release,ordinary combat,crystal and return remain unproved.',
                      'Earth opens actualE8 cell58 from0B to0C for8MP,then the portal is physically used. Actual reward1A9 sets item15 after its original interaction;caption closes and axe is re-equipped.',
                      'The19A UP mechanism opensD8 west/D7 east. The subsequent recorded route returns throughE8,D8,D7 and its portal toA6. Later thief-key door usage is not established solely by owning it.',
                      'This checkpoint does not extend the D7 instruction-stack profile. Later dungeons,ending,saves,global RNG/phase and full SMS video/audio/hardware fidelity remain unproved.'])
    (ROOT/'analysis/d8_progress_v0304_report.json').write_bytes((json.dumps(result, indent=2)+'\n').encode())
    print(f'v304:thief key and ready1A6 at{previous},HP{last["health"]}/88;four cold RAM/PNG replays exact')


if __name__ == '__main__':
    main()
