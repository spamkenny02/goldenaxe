"""Version-bound D4 approach/first key/Earth proof; retain the later failed trial."""
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
    digest = sha(read('versions/v0304-b7b4e150/gaw-megadrive-v0304.bin'))
    prior = load('analysis/d3_campaign_v0304_report.json')
    assert prior['passed'] and prior['md_sha256'] == digest and prior['three_crystals_and_exterior_exit']
    symbol_path = 'validation/stack-v0304-d3-all/symbol.txt'
    read(symbol_path)
    sy = symbols(ROOT/symbol_path)
    specifications = [
        ('natural-dungeon-route/md-v0304-gold-entry01', 0x3f, 46, 8, 24, 0),
        ('natural-service-route/md-v0304-gold50-01', 0xf4, 46, 58, 24, 0),
        ('natural-dungeon-route/md-v0304-earth-entry01', 0xbf, 46, 58, 24, 0),
        ('natural-service-route/md-v0304-earth-learn01', 0xa3, 46, 8, 48, 1),
        ('natural-dungeon-route/md-v0304-d4-entry01', 0x1f0, 46, 8, 48, 1),
        ('natural-dungeon-combat/md-auto-v0304-d4-key01', 0x1f1, 46, None, 48, 1),
        ('natural-dungeon-combat/md-auto-v0304-d4-earth01', 0x1d1, 54, None, 40, 1),
    ]
    stages = []
    for trace, room, hp, gold, magic, level in specifications:
        root = 'validation/'+trace
        c = load(root+'/capture.json')
        frame = c['frames']
        report = load(root+('/route_report.json' if trace.startswith('natural-dungeon-route/') else '/report.json'))
        proof_root = root+f'-assisted-fixed-replay-{frame}'
        proof = load(proof_root+'/replay_report.json')
        assert c['rom_sha256'] == proof['rom_sha256'] == digest and c['sram_input'] is None
        assert report['failure'] is None and proof['passed'] and proof['whole_ram_bytes'] == 65536
        assert proof['final_png_exact'] and not proof['feedback_reads'] and not proof['boss_assistance']
        for name, expected in proof['evidence'].items():
            assert sha(read(root+'/'+name)) == expected
        assist, writes = recording(ROOT/root, c)
        assert assist['boss_room'] == 0x180 and assist['activation_after_frame'] == 53755
        assert assist['first_boss_entry'] is None and assist['first_boss_combat'] is None
        assert not assist['health_refills'] and not assist['primary_state_imports'] and not assist['rom_modifications']
        assert all(address == sy['hero_hurt'] for _, address, _ in writes)
        for stem, ext in [('ram', 'bin'), ('frame', 'png')]:
            name = f'/{stem}_{frame:05d}.{ext}'
            assert read(root+name) == read(proof_root+name)
        raw = read(root+f'/ram_{frame:05d}.bin')
        data = lambda name, count: bytes(raw[(sy[name]+i)^1] for i in range(count))
        word = lambda name: int.from_bytes(data(name, 2), 'big')
        assert word('room_id') == room and word('hero_health') == hp and word('hero_max_health') == 56
        assert word('hero_magic') == magic and data('hero_items', 17)[5] == level
        if gold is not None:
            assert word('hero_gold') == gold
        assert data('hero_items', 17)[13] == 1 and data('hero_items', 17)[12] == 0
        assert data('game_save_state', 592)[0x1f:0x28] == bytes([128]*3+[0]*6)
        if 'service-route/' in trace:
            assert report['passed'] and report['new_assistance_writes'] == 0
        if 'earth-entry' in trace:
            assert report['required_chop_verified'] and report['rope_terrain_requested']
        if trace.endswith('d4-key01'):
            assert report['new_key_verified'] and word('hero_keys') == 1
        if trace.endswith('d4-earth01'):
            assert report['earth_route_passed'] and report['earth_passage_traversed'] and report['earth_state_writes'] == 0
            assert report['earth_before']['magic']-report['earth_opened']['magic'] == 8
            assert not report['destination_combat_cleared'] and not report['room_cleared']
        stages.append(dict(trace=trace,frames=frame,room=room,health=hp,magic=magic,earth_level=level,whole_ram_png_exact=True))
    failed = 'validation/natural-dungeon-combat/md-auto-v0304-d4-a1-key01'
    diagnostic = load(failed+'-thief-diagnostic/diagnostic_report.json')
    failed_report = load(failed+'/report.json')
    assert failed_report['failure'] == 'frame_limit' and not failed_report['new_key_verified']
    assert diagnostic['rom_sha256'] == digest and diagnostic['final_sample']['hero'] == 12
    assert not diagnostic['new_state_writes'] and not diagnostic['feedback_reads']
    for name, expected in diagnostic['source_hashes'].items():
        assert sha(read(failed+'/'+name)) == expected
    source_case = load('validation/thief-lethal-capture-source-v0304/source_report.json')
    assert source_case['source_retains_grab_after_lethal_capture'] and not source_case['natural_source_reproduction']
    assert source_case['original_sha256'] == sha(read('input/original.sms'))
    assert source_case['fixture_sha256'] == sha(read('validation/thief-lethal-capture-source-v0304/source.sms'))
    read('validation/thief-lethal-capture-source-v0304/run/ram_00010.bin')
    for path in ['tools/natural_house_service.py','tools/natural_earth_passage.py',
                 'tools/diagnose_thief_capture_v0304.py','tools/validate_thief_lethal_capture_source.py',
                 'tools/summarize_d4_earth_v0304.py']:
        read(path)
    result = dict(passed=True,version=304,md_sha256=digest,production_rom_unchanged=True,
                  stages=stages,three_crystals=True,fourth_crystal_validated=False,
                  gold_gift=50,earth_payment=50,earth_level=1,earth_cast_cost=8,
                  first_d4_key_verified=True,earth_passage_traversed=True,destination_room_cleared=False,
                  approach_assisted=True,boss_entered=False,full_game_validated=False,
                  next_issue=dict(trace=failed,room=0x1a1,hero_state=12,
                                  original_routines_reproduce_in_isolation=True,natural_source_reproduction=False,
                                  diagnosis='Capture coincides with lethal damage to the grabbing thief; hero remains grabbed after that actor becomes a death particle. Original SMS5043 then2768 reproduce this state in an isolated fixture. A natural SMS reproduction is not claimed.'),
                  evidence=refs,
                  limits=['Seven completed stages have independent cold fixed-input RAM/PNG replays. Logged approach protection is restricted to hero_hurt; this is an assisted campaign.',
                          'Life rises46-to54 through ordinary play during the Earth route; no health/currency/equipment/progression injection is used.',
                          'The later A1 trial reaches its frame budget, retains one key and is not a successful room/key proof. Its fixed diagnostic records observations but is not a full final-state equivalence proof.',
                          'No fourth crystal, canoe, full source campaign, ending, saves or global video/audio fidelity is established here.'])
    (ROOT/'analysis/d4_earth_v0304_report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('v304:D4 first key and acquired Earth passage independently replayed; later thief-capture issue retained;ROM unchanged')


if __name__ == '__main__':
    main()
