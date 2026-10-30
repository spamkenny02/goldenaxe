"""Audit the paid coastal passage and ordinary ship approach to dungeon eight."""
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
    prior = load('analysis/d7_campaign_v0304_report.json')
    assert prior['passed'] and prior['seventh_crystal_and_exterior_exit']
    digest = sha(read('versions/v0304-b7b4e150/gaw-megadrive-v0304.bin'))
    assert digest == prior['md_sha256']
    hashes, seen = set(), set()
    def index(name):
        if name in seen:
            return
        seen.add(name)
        obj = load(name)
        for key, value in obj.items():
            if key.endswith(('source_index', 'controller_index')):
                index(value)
        for item in obj.get('sources', {}).values():
            assert sha(read(item['path'])) == item['sha256']; hashes.add(item['sha256'])
    index('analysis/d8_paid_passage_v0304_source_index.json')
    symbol_file = 'validation/v0304-d8-paid-sources/symbol.txt'
    read(symbol_file); sy = symbols(ROOT/symbol_file)
    proposal = load('analysis/d8_source_route_proposal.json')
    original = read('input/original.sms')
    assert proposal['source_sha256'] == sha(original) and proposal['entry'] == 0x1ea
    assert proposal['bosses'][0]['room'] == 0x196 and proposal['bosses'][0]['kinds'] == [0x6b]
    assert original[0x3234e+0x196*8:0x32356+0x196*8] == bytes([0x6b]+[0]*7)
    paid = load('analysis/paid_passage_reference.json')
    assert paid['source_sha256'] == sha(original) and [0x3c,0x1a,32,232] in paid['routes']
    stages = []
    previous = 189330
    for family, name, report_name, room in [
        ('natural-dungeon-route', 'md-v0304-d8-paid3c-route01', 'route_report.json', 0x9f),
        ('natural-service-route', 'md-v0304-d8-paid3c-service01', 'report.json', 0x1a),
        ('natural-dungeon-route', 'md-v0304-d8-entry03', 'route_report.json', 0x1ea)]:
        root = f'validation/{family}/{name}'
        c, r = load(root+'/capture.json'), load(root+'/'+report_name)
        frame = c['frames']
        proof = root+f'-assisted-fixed-replay-{frame}'
        p = load(proof+'/replay_report.json')
        assert c['rom_sha256'] == p['rom_sha256'] == digest and c['sram_input'] is None
        assert r['failure'] is None and p['passed'] and p['whole_ram_bytes'] == 65536
        assert p['final_png_exact'] and not p['feedback_reads']
        for filename, expected in p['evidence'].items():
            assert sha(read(root+'/'+filename)) == expected
        a, writes = recording(ROOT/root, c)
        read(root+'/assistance.json')
        assert a['driver_sha256'] in hashes
        assert len(a['episodes']) == 8 and a['boss_room'] == 0x196
        assert a['first_boss_entry'] is None and a['first_boss_combat'] is None
        assert a['release_write_frame'] is None and not a['boss_assistance']
        assert not a['primary_state_imports'] and not a['health_refills'] and not a['rom_modifications']
        assert all(address == sy['hero_hurt'] for _, address, _ in writes)
        for key, value in r.items():
            if key.endswith(('driver_sha256', 'controller_sha256')) and value is not None:
                assert value in hashes, (key, value)
        for stem, ext in [('ram', 'bin'), ('frame', 'png')]:
            filename = f'/{stem}_{frame:05d}.{ext}'
            assert read(root+filename) == read(proof+filename)
        raw = read(root+f'/ram_{frame:05d}.bin')
        data = lambda n, k: bytes(raw[(sy[n]+i)^1] for i in range(k))
        word = lambda n: int.from_bytes(data(n, 2), 'big')
        assert word('room_id') == room and word('game_state') == 12 and word('hero_state') == 1
        assert word('hero_health') > 0 and word('hero_max_health') == 88
        assert word('hero_keys') == 2 and word('hero_magic') == 40 and not word('sound_unhandled_command')
        assert word('hero_selected_item') == word('hero_weapon_level') == 1
        assert data('game_save_state', 592)[0x1f:0x28] == bytes([128]*7+[0]*2)
        items = data('hero_items', 17)
        assert items[10] == items[16] == 1 and items[12:15] == bytes([1]*3) and not items[15]
        if family == 'natural-service-route':
            assert r['passed'] and r['price'] == 10 and r['outside'] == 0x3c and r['target'] == 0x1a
            assert r['first_state']['gold'] == 41 and r['last_state']['gold'] == 31
            assert not r['new_assistance_writes'] and not r['currency_or_inventory_fixtures']
            assert r['source_prefix'] == stages[-1]['trace'].rsplit('/', 1)[-1]
        else:
            assert r['prefix_end'] == previous and r['reached_entrance'] and r['directional_probe_succeeded']
            assert r['rendered_final_frame_nonblack'] and r['ship_acquired_in_prefix']
            if room == 0x9f:
                assert r['door_entry_direction'] == 1 and r['axe_chop_decisions'] == 3
                assert data('game_save_state', 592)[0x50+0x3c]&1
            else:
                assert word('world_dungeon_number') == 8 and word('hero_gold') == 31
                assert r['recorded_service_prefix'] == stages[-1]['trace'].rsplit('/', 1)[-1]
        previous = frame
        stages.append(dict(trace=root, frames=frame, room=room, health=word('hero_health'),
                           gold=word('hero_gold'), keys=2, magic=40, whole_ram_png_exact=True))
    for suffix in ['entry01', 'entry02']:
        root = 'validation/natural-dungeon-route/md-v0304-d8-'+suffix
        r = load(root+'/route_report.json')
        assert not r['reached_entrance'] and r['last_state']['room'] == 0x49
    read('tools/summarize_d8_entry_v0304.py')
    result = dict(passed=True, version=304, md_sha256=digest, production_rom_unchanged=True,
                  coastal_passage_paid=True, passage_origin=0x3c, passage_destination=0x1a,
                  passage_price=10, stages=stages, ready_room=0x1ea,
                  ready_frames=previous, ready_health=stages[-1]['health'], ready_max_health=88,
                  ready_keys=2, ready_magic=40, seventh_crystal_preserved=True, eighth_boss_entered=False,
                  approach_assisted=True, full_game_validated=False, evidence=refs, limits=[
                      'Approach guard is an eighth logged test episode,hero_hurt writes only;no ownership,gold,health or progression fixture. It must end before the designated boss196/type6B.',
                      'Fixed-input cold replays compare all65536 RAM bytes and final PNG at each stage. They prove this native route,not a full SMS campaign or global RNG/phase equivalence.',
                      'The first two direct sea attempts stop at the transformed bridge49. They remain excluded diagnostics. The retained route cuts the real3C stair and enters from above,then pays ten horns and boards from the coastal dock.',
                      'D8 master key,boss,crystal and return are not yet proved;later dungeons,ending,saves and full video/audio/hardware fidelity remain unproved.'])
    out = ROOT/'analysis/d8_entry_v0304_report.json'
    out.write_bytes((json.dumps(result, indent=2)+'\n').encode())
    print(f'v304:D8 entry1EA at{previous},HP{stages[-1]["health"]}/88;paid3C->1A ten horns;three cold replays exact')


if __name__ == '__main__':
    main()
