"""Verify the sixth crystal and cold-replayed return to exterior8B."""
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
    digest = sha(read('gaw-megadrive.bin'))
    boss = load('analysis/d6_boss_v0293_report.json')
    assert boss['passed'] and boss['md_sha256'] == digest and boss['sixth_crystal_acquired']
    root = 'validation/natural-dungeon-combat/md-auto-v0293-d6-exit03'
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
    sy = symbols(ROOT / 'megadrive/out/release/symbol.txt')
    assert a['unassisted_extension'] and not a['new_assistance_writes']
    assert not a['health_refills'] and not a['primary_state_imports']
    assert all(address == sy['hero_hurt'] and frame <= 145093 for frame, address, _ in writes)
    assert a['first_boss_combat'] == dict(frame=145124, health=72, hurt=0)
    assert r['full_dungeon_cleared'] and r['dungeon_exit_verified'] and not r['deaths'] and r['failure'] is None
    assert r['planning_decisions'] == r['verified_persistent_prediction_windows'] == r['full_ram_prediction_matches'] == 92
    assert not r['stack_only_difference_windows'] and not r['primary_state_imports']
    raw = read(root + f'/ram_{c["frames"]:05d}.bin')
    read(root + f'/frame_{c["frames"]:05d}.png')
    data = lambda name, n: bytes(raw[(sy[name] + i) ^ 1] for i in range(n))
    word = lambda name: int.from_bytes(data(name, 2), 'big')
    assert word('room_id') == 0x8b and word('world_dungeon_number') == 0 and word('game_state') == 12
    assert word('hero_health') == 74 and word('hero_max_health') == 80
    assert data('game_save_state', 592)[0x1f:0x25] == bytes([128] * 6)
    assert data('hero_items', 17)[10] == 1
    events = load(root + '/events.json')
    visited = []
    for e in events:
        if not visited or visited[-1] != e['room']:
            visited.append(e['room'])
    assert visited == [0x115,0x125,0x124,0x123,0x113,0x114,0x138,0x169,0x168,0x178,0x177,0x187,0x8b]
    decisions = load(root + '/planning_live.json')['decisions']
    assert any(d['action'] == 'leave-portal-contact-down' and d['primary']['room'] == 0x138 for d in decisions)
    driver = read('tools/natural_exit_planner.py')
    assert sha(driver) == r['exit_driver_sha256']
    for name in ['summarize_d6_campaign_v0293.py', 'replay_assisted_prefix.py', 'assisted_prefix.py']:
        read('tools/' + name)
    result = dict(passed=True, version=293, md_sha256=digest, production_rom_unchanged=True,
                  sixth_crystal_acquired=True, dungeon6_completed=True, native_six_crystals=True,
                  cold_exit_replay=True, whole_ram_bytes=65536, final_png_exact=True,
                  frames=c['frames'], rooms=visited, last_state=r['last_state'],
                  approach_assistance=True, boss_assistance=False, new_exit_assistance_writes=0,
                  planning_decisions=92, primary_state_imports=0, health_refills=0,
                  source_campaign_compared=False, full_game_validated=False, evidence=refs,
                  limits=['The first dungeon is unassisted; later approaches retain logged hurt-counter assistance. Boss combat and the sixth exit add no aid. This is not a fully unassisted campaign.',
                          'Final whole RAM and PNG match a separate cold official-core replay; intermediate frames and original SMS full campaign are not compared.',
                          'Dungeons7-10, ending and whole-game audio/visual/hardware fidelity remain unfinished. Previously published stack margin applies only through the fifth crystal and bridge; a longer observation is separate.'])
    (ROOT / 'analysis/d6_campaign_v0293_report.json').write_text(json.dumps(result, indent=2) + '\n')
    print('D6 crystal and exterior8B verified: six crystals,74/80HP,92 matched predictions and exact cold replay')


if __name__ == '__main__':
    main()
