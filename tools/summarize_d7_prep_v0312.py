"""Audit current D7 supplies, entry, key rewards and Earth mechanisms."""
import json
from archive_lossless_evidence import sha
from assisted_prefix import recording
from rebase_natural_campaign import evidence
from run_core import ROOT
from validate_playable_sprite_limit import symbols


def main():
    refs = {}

    def read(path):
        raw = evidence(ROOT/path)
        refs[path] = sha(raw)
        return raw

    def load(path):
        return json.loads(read(path))

    prior = load('analysis/d6_campaign_v0312_report.json')
    digest = sha(read('gaw-megadrive.bin'))
    assert prior['passed'] and prior['sixth_crystal_and_exterior_return'] and prior['md_sha256'] == digest
    manifest = 'validation/run-v0312-d7-03/'
    points = load(manifest+'verified_endpoints.json')
    expected = [('natural-dungeon-route/md-v0312-d7-03-key-shop-route','route',None),
                ('natural-service-route/md-v0312-d7-03-buy-key','purchase',None),
                ('natural-dungeon-route/md-v0312-d7-03-entry','entry',None),
                ('natural-dungeon-combat/md-auto-v0312-d7-03-key01','key',0x1cb),
                ('natural-dungeon-combat/md-auto-v0312-d7-03-key03','key',0x1b9),
                ('natural-dungeon-combat/md-auto-v0312-d7-03-earth01','earth',0x36),
                ('natural-dungeon-combat/md-auto-v0312-d7-03-earth02','earth',0x2b)]
    assert len(points) == len(expected) == 7
    commands = [json.loads(row) for row in read(manifest+'commands.jsonl').splitlines()]
    for command in commands:
        assert command['sha256'] == sha(read('tools/'+command['tool']))
    proposal = load(manifest+'historical_proposal.json')
    assert proposal['sha256'] == sha(read(proposal['path']))
    previous = prior['stages'][-1]['trace']
    pc = load(previous+'/capture.json')
    _, previous_writes = recording(ROOT/previous,pc)
    activation = pc['frames']
    sy = symbols(ROOT/'megadrive/out/release/symbol.txt')
    stages = []
    for point, (suffix,kind,target) in zip(points,expected):
        trace = 'validation/'+suffix
        assert point['trace'] == trace
        cap = load(trace+'/capture.json')
        r = load(trace+('/route_report.json' if kind in ('route','entry') else '/report.json'))
        frame = cap['frames']
        assert frame == point['frames'] and frame > pc['frames']
        assert r['failure'] is None and not r.get('deaths',0) and r[point['gate']]
        assert cap['rom_sha256'] == r['rom_sha256'] == digest and cap['sram_input'] is None
        if kind == 'purchase':
            assert r['source_prefix'] == previous.split('/')[-1]
            assert r['passed'] and r['keys_bought'] == 1 and r['unit_price'] == 60
            assert r['first_state']['gold'] == 62 and r['last_state']['gold'] == 2
            assert r['first_state']['keys'] == 0 and r['last_state']['keys'] == 1
            assert not r['new_assistance_writes'] and not r['currency_or_inventory_fixtures']
        else:
            assert r['prefix_end'] == pc['frames']
        if kind in ('route','entry'):
            assert r['reached_entrance'] and r['directional_probe_succeeded'] and not r['normal_continues']
            assert r['route_driver_sha256'] == sha(read('tools/natural_dungeon_route.py'))
            assert (r['recorded_combat_prefix'] or r['recorded_service_prefix']) == previous.split('/')[-1]
            if kind == 'entry':
                assert r['door_index'] == 7 and r['house_outside'] is None
        if kind in ('key','earth'):
            assert r['recorded_new_game_prefix'] == previous.split('/')[-1]
            assert r['driver_sha256'] == sha(read('tools/natural_dungeon_combat.py'))
            if kind == 'key':
                assert r['new_key_verified'] and r['room_cleared'] and r['target_room'] == target
            else:
                assert r['earth_route_passed'] and r['earth_action_only_requested'] and not r['earth_state_writes']
                assert r['earth_passage_room'] == 0x1b9 and r['earth_cell'] == target
                assert r['earth_before']['cell'] == 11 and r['earth_opened']['cell'] != 11
                assert r['earth_before']['magic']-r['earth_opened']['magic'] == 8
                assert r['earth_controller_sha256'] == sha(read('tools/natural_earth_passage.py'))
                read(trace+'/earth_events.json')
        aid,writes = recording(ROOT/trace,cap)
        read(trace+'/assistance.json')
        assert len(aid['episodes']) == 7 and aid['boss_room'] == 0x1b8
        assert aid['activation_after_frame'] == activation and aid['first_boss_entry'] is None
        assert not aid['boss_assistance'] and not aid['primary_state_imports'] and not aid['health_refills']
        assert writes[:len(previous_writes)] == previous_writes
        assert all(address == sy['hero_hurt'] and data in (b'\0\0',b'\0\x81') for _,address,data in writes)
        if kind == 'purchase':
            assert writes == previous_writes
        proof_root = trace+f'-assisted-fixed-replay-{frame}'
        proof = load(proof_root+'/replay_report.json')
        assert proof['passed'] and proof['rom_sha256'] == digest
        assert proof['whole_ram_bytes'] == 65536 and proof['final_png_exact'] and not proof['feedback_reads']
        for name in ('capture.json','controls.json','assistance.json'):
            assert proof['evidence'][name] == sha(read(trace+'/'+name))
        raw = read(trace+f'/ram_{frame:05d}.bin')
        assert raw == read(proof_root+f'/ram_{frame:05d}.bin')
        assert read(trace+f'/frame_{frame:05d}.png') == read(proof_root+f'/frame_{frame:05d}.png')
        def data(name,count):
            return bytes(raw[(sy[name]+i)^1] for i in range(count))
        def word(name):
            return int.from_bytes(data(name,2),'big')
        assert data('game_save_state',592)[0x1f:0x28] == bytes([128]*6+[0]*3)
        items = data('hero_items',17)
        assert items[0] == 2 and all(items[i] == 1 for i in (1,4,5,10,12,13,14)) and not items[16]
        assert word('hero_health') > 0 and word('hero_max_health') == 80 and not word('sound_unhandled_command')
        if kind == 'entry':
            assert word('room_id') == 0x1db
        if kind in ('key','earth'):
            assert word('room_id') == (target if kind == 'key' else 0x1b9)
        stages.append(dict(trace=trace,kind=kind,frames=frame,room=word('room_id'),health=word('hero_health'),
                           max_health=word('hero_max_health'),magic=word('hero_magic'),keys=word('hero_keys'),
                           gold=word('hero_gold'),whole_ram_png_exact=True))
        previous,pc,previous_writes = trace,cap,writes
    result = dict(passed=True,version=312,md_sha256=digest,production_rom_unchanged=True,stages=stages,
                  original_crystals_retained=6,keys_bought=1,key_price=60,earth_casts=2,earth_magic_spent=16,
                  intermediate_boss_entered=False,seventh_crystal_validated=False,full_game_validated=False,evidence=refs,
                  limits=['Current cold campaign; only declared approach hero_hurt writes, with no resource/actor/progression/SRAM imports.',
                          'The historical itinerary proposes inputs only. Current resources and all seven cold RAM/PNG endpoints are independently verified.',
                          'This preparation does not claim the D7 intermediate or main boss victory.'])
    (ROOT/'analysis/d7_prep_v0312_report.json').write_text(json.dumps(result,indent=2)+'\n')
    print('v312 D7 supplies, entry, keys and two Earth passages verified:',len(stages),'stages')


if __name__ == '__main__':
    main()
