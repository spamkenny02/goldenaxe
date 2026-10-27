"""Verify the sixth crystal from cold controls, without claiming the exit."""
import json
from run_core import ROOT
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from validate_playable_sprite_limit import symbols
from assisted_prefix import recording


def main():
    refs = {}
    def read(name):
        raw = evidence(ROOT / name)
        refs[name] = sha(raw)
        return raw
    def load(name):
        return json.loads(read(name))
    digest = sha(read('gaw-megadrive.bin'))
    assert digest == sha(read('versions/v0293-878a7f44/gaw-megadrive-v0293.bin'))
    prior = load('analysis/d6_progress_v0293_report.json')
    assert prior['passed'] and prior['md_sha256'] == digest and not prior['boss_entered']
    sy = symbols(ROOT / 'megadrive/out/release/symbol.txt')
    stages = []
    for suffix in ['boss02', 'boss05']:
        root = 'validation/natural-dungeon-combat/md-auto-v0293-d6-' + suffix
        c = load(root + '/capture.json')
        r = load(root + '/report.json')
        p = load(root + f'-assisted-fixed-replay-{c["frames"]}/replay_report.json')
        a, writes = recording(ROOT / root, c)
        read(root + '/assistance.json')
        assert c['rom_sha256'] == p['rom_sha256'] == digest and c['sram_input'] is None
        assert p['passed'] and p['whole_ram_bytes'] == 65536 and p['final_png_exact']
        assert not p['feedback_reads'] and not p['boss_assistance']
        for name, expected in p['evidence'].items():
            assert sha(read(root + '/' + name)) == expected
        assert a['boss_room'] == 0x115 and not a['primary_state_imports'] and not a['health_refills']
        assert not a['boss_assistance']
        if suffix == 'boss05':
            assert a['unassisted_extension'] and a['new_assistance_writes'] == 0
        assert a['release_write_frame'] == 145093 and a['first_boss_combat'] == dict(frame=145124, health=72, hurt=0)
        assert all(address == sy['hero_hurt'] and frame <= 145093 for frame, address, _ in writes)
        assert a['retarget_audit'] == prior['retarget_audit']
        assert not r['deaths'] and not r['primary_state_imports']
        assert r['planning_decisions'] == r['verified_persistent_prediction_windows'] == r['full_ram_prediction_matches']
        assert not r['stack_only_difference_windows']
        raw = read(root + f'/ram_{c["frames"]:05d}.bin')
        read(root + f'/frame_{c["frames"]:05d}.png')
        data = lambda name, n: bytes(raw[(sy[name] + i) ^ 1] for i in range(n))
        word = lambda name: int.from_bytes(data(name, 2), 'big')
        save = data('game_save_state', 592)
        assert save[0x1f:0x24] == bytes([128] * 5)
        if suffix == 'boss02':
            assert r['failure'] == 'frame_limit' and not r['room_cleared']
            assert word('hero_health') == 72 and save[0x24] == 0
        else:
            assert r['failure'] is None and r['room_cleared'] and not r['last_actors']
            assert word('hero_health') == word('hero_max_health') == 80
            assert save[0x24] == 128 and data('hero_items', 17)[10] == 1
            assert r['last_state']['reward_active'] == r['last_state']['audio_error'] == 0
            events = load(root + '/events.json')
            assert any(e['frame'] == 149386 and e['health'] == 58 for e in events)
            assert any(e['health'] == 80 and e['progress'] == 128 for e in events)
        stages.append(dict(trace=root, frames=c['frames'], failure=r['failure'],
                           last_state=r['last_state'], planning_decisions=r['planning_decisions'],
                           whole_ram_bytes=65536, final_png_exact=True))
    for name in ['summarize_d6_boss_v0293.py', 'assisted_boss_route.py',
                 'natural_combat_navigation.py', 'natural_combat_beam.py',
                 'natural_dungeon_combat.py', 'replay_assisted_prefix.py']:
        read('tools/' + name)
    result = dict(passed=True, version=293, md_sha256=digest, production_rom_unchanged=True,
                  stages=stages, sixth_boss_defeated=True, sixth_crystal_acquired=True,
                  max_health=80, boss_assistance=False, approach_assistance=True,
                  last_assistance_frame=145093, first_boss_combat_frame=145124,
                  primary_state_imports=0, health_refills=0, dungeon6_exit_verified=False,
                  full_game_validated=False, source_campaign_compared=False, evidence=refs,
                  limits=['Historical approach uses logged hurt-counter writes; combat has ordinary damage, including an observed 72 to 58 HP hit. This is not a fully unassisted campaign.',
                          'Cold official-core replays compare final whole RAM and PNG. Intermediate images, original SMS campaign, audio timing and hardware fidelity are not proven.',
                          'Sixth crystal is complete; dungeon exit, later dungeons and ending remain outside this report.'])
    (ROOT / 'analysis/d6_boss_v0293_report.json').write_text(json.dumps(result, indent=2) + '\n')
    print('D6 boss and sixth crystal: cold replay exact, 80HP, no boss assistance; exit pending')


if __name__ == '__main__':
    main()
