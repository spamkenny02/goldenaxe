"""Verify D8 west combat and both ordinary remote passage mechanisms."""
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
    prior = load('analysis/d8_entry_v0304_report.json')
    assert prior['passed'] and prior['ready_room'] == 0x1ea
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
    assert original[0x3234e+0x1c9*8:0x32356+0x1c9*8] == bytes([0x7a]+[0]*7)
    puzzle = load('analysis/room_puzzles_reference.json')
    contact = load('analysis/contact_script_reference.json')
    assert puzzle['source_sha256'] == contact['source_sha256'] == sha(original)
    source = next(r for r in puzzle['records'] if r['room'] == 0x1eb)
    assert source['kind'] == 'redraw_remote_flag' and source['explicit_registers']['e'] == 0xc8
    source = next(r for r in contact['records'] if r['room'] == 0x1ec)
    assert source['kind'] == 'stationary_up_passages' and source['explicit_registers']['e'] == 0xeb
    previous, previous_name = 191720, 'md-v0304-d8-entry03'
    stages = []
    for suffix, room in [('west01', 0x1c8), ('switch1eb-01', 0x1eb), ('switch1ec-02', 0x1eb)]:
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
        assert word('hero_health') == 40 and word('hero_max_health') == 88 and word('hero_keys') == 2
        assert word('hero_magic') == 48 and word('world_dungeon_number') == 8 and not word('sound_unhandled_command')
        assert word('hero_selected_item') == word('hero_weapon_level') == 1
        assert data('game_save_state', 592)[0x1f:0x28] == bytes([128]*7+[0]*2)
        items = data('hero_items', 17)
        assert items[10] == items[16] == 1 and items[12:15] == bytes([1]*3) and not items[15]
        if suffix == 'west01':
            assert r['room_cleared'] and not r['full_ram_prediction_matches'] and not flags[0xc8]&4
            events = load(root+'/events.json')
            assert any(e['room'] == 0x1c9 and any(x['type'] == 0x7a and x['hp'] for x in e['actors']) for e in events)
        else:
            assert r['passed'] and r['contact_route_passed'] and not r['contact_state_writes']
            load(root+'/contact_events.json')
            assert flags[0xc8]&4
            if suffix == 'switch1eb-01':
                assert r['contact_remote_room'] == 0x1c8 and r['contact_coordinate'] == 332
                assert r['contact_before']['remote_flags'] == 144 and r['contact_opened']['remote_flags'] == 148
            else:
                assert r['contact_room'] == 0x1ec and r['contact_coordinate'] == 360
                assert flags[0xeb]&0x40 and flags[0xea]&0x80
        stages.append(dict(trace=root, frames=frame, room=room, health=40, max_health=88, keys=2,
                           magic=48, c8_flags=flags[0xc8], eb_flags=flags[0xeb], whole_ram_png_exact=True))
        previous, previous_name = frame, root.rsplit('/', 1)[-1]
    for suffix in ['key01', 'switch1ec-01']:
        r = load('validation/natural-dungeon-combat/md-auto-v0304-d8-'+suffix+'/report.json')
        assert r['failure'] == 'controller_stalled' and not r['deaths']
    read('tools/summarize_d8_passages_v0304.py')
    result = dict(passed=True, version=304, md_sha256=digest, production_rom_unchanged=True, stages=stages,
                  ready_room=0x1eb, ready_frames=previous, ready_health=40, ready_max_health=88, ready_keys=2,
                  ready_magic=48, c8_remote_transformation_enabled=True, eb_west_passage_opened=True,
                  eighth_boss_entered=False, thief_key_owned=False, approach_assisted=True,
                  intermediate_7a_assisted=True, full_game_validated=False, evidence=refs, limits=[
                      'The intermediate type7A in1C9 was fought with the logged approach guard and is not an unassisted combat proof. The designated main boss196/type6B has not been entered.',
                      'Three fixed-input cold replays match all65536 RAM bytes and final PNG. No state from a secondary core is imported,no item/HP/gold/progression fixture is used,and only hero_hurt approach writes are inherited/extended.',
                      'The1EB UP mechanism sets remoteC8 bit4 after its redraw. The1EC mechanism opens1EB west and1EA east;the hero physically returns to1EB. The C8 transformed floor has not yet been traversed at this checkpoint.',
                      'key01 requested a key from a room whose clear reward is a map transformation;switch1ec-01 prematurely stopped its fallback controller on its already-cleared target. Both remain excluded controller diagnostics.',
                      'Thief key,D8 main boss/crystal/return,later dungeons,ending,saves,global RNG/phase and full SMS video/audio/hardware fidelity remain unproved.'])
    (ROOT/'analysis/d8_passages_v0304_report.json').write_bytes((json.dumps(result, indent=2)+'\n').encode())
    print(f'v304:D8 west and both remote switches;ready1EB at{previous},HP40/88;three cold RAM/PNG replays exact')


if __name__ == '__main__':
    main()
