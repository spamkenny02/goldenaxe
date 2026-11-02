"""Verify palace guardian and actual Golden Axe acquisition; controlled scope only."""
import json
from run_core import ROOT
from archive_lossless_evidence import sha
from assisted_prefix import recording, prefix_writes
from validate_playable_sprite_limit import symbols


NAMES = [
    ('pre-guardian01', 'live navigation checkpoint; frame limit'),
    ('switch12c01', 'east switch open; live navigation checkpoint'),
    ('pre-guardian02', 'live navigation checkpoint before compartment loop'),
    ('pre-guardian03', 'compartment loop completed; room12E cleared'),
    ('guardian-release01', 'guard removed before room11E'),
    ('guardian01', 'unassisted fight checkpoint; guardian still has8HP'),
    ('guardian02', 'unassisted guardian victory; room empty'),
    ('final-approach01', 'next approach starts only after verified guardian victory'),
    ('goldenaxe01', 'actual Golden Axe upgrade and reward completion'),
]


def main():
    digest = sha((ROOT/'gaw-megadrive.bin').read_bytes())
    assert digest == '7270576d6eeb2aee641776a3e364f2f3f320711d70bb91a566d7578161261049'
    sy = symbols(ROOT/'megadrive/out/release/symbol.txt')
    evidence, stages, reports, assists, raws = {}, [], {}, {}, {}
    for name, scope in NAMES:
        folder = ROOT/'validation/natural-dungeon-combat'/('md-auto-controlled-v0309-palace-'+name)
        cap = json.loads((folder/'capture.json').read_bytes())
        report = json.loads((folder/'report.json').read_bytes())
        assist, writes = recording(folder, cap)
        assert cap['rom_sha256'] == digest and report['controlled_sram_fixture']
        assert report['natural_campaign_proof'] is False and report['primary_state_imports'] == 1
        assert all(address == sy['hero_hurt'] and value in (b'\0\0', b'\0\x81') for _, address, value in writes)
        assert prefix_writes(folder, cap, True, controlled=True) == writes
        replay = folder.with_name(folder.name+'-assisted-fixed-replay-'+str(cap['frames']))
        proof = json.loads((replay/'replay_report.json').read_bytes())
        assert proof['passed'] and proof['controlled_sram_fixture'] and proof['primary_state_imports'] == 1
        assert proof['whole_ram_bytes'] == 65536 and proof['final_png_exact']
        for stem, ext in [('ram','bin'), ('frame','png')]:
            filename = f'{stem}_{cap["frames"]:05d}.{ext}'
            assert (folder/filename).read_bytes() == (replay/filename).read_bytes()
        raw = (folder/f'ram_{cap["frames"]:05d}.bin').read_bytes()
        reports[name], assists[name], raws[name] = report, assist, raw
        stages.append(dict(trace=folder.relative_to(ROOT).as_posix(), scope=scope,
                           frames=cap['frames'], state=report['last_state'], failure=report['failure'],
                           whole_ram_png_exact=True, initial_state_imports=1))
        for path in [folder/'capture.json', folder/'report.json', folder/'controls.json', folder/'assistance.json',
                     folder/f'ram_{cap["frames"]:05d}.bin', folder/f'frame_{cap["frames"]:05d}.png', replay/'replay_report.json']:
            evidence[path.relative_to(ROOT).as_posix()] = sha(path.read_bytes())
    partial, victory = reports['guardian01'], reports['guardian02']
    assert partial['failure'] == 'frame_limit' and partial['last_actors'][0]['type'] == 0x7c
    assert partial['last_actors'][0]['hp'] == 8 and not partial['room_cleared']
    assert victory['failure'] is None and victory['room_cleared'] and not victory['deaths']
    assert not victory['last_actors'] and victory['last_state']['room'] == 0x11e
    assert victory['last_state']['health'] == 56 and victory['last_state']['room_flags'] & 0x40
    assert partial['guard_release_frame'] == victory['guard_release_frame'] == 76953
    assert partial['new_assistance_writes'] == victory['new_assistance_writes'] == 0
    assert partial['full_ram_prediction_matches'] == partial['verified_persistent_prediction_windows'] == 404
    assert partial['stack_only_difference_windows'] == 0
    assert max(w['frame'] for w in assists['guardian02']['writes']) == 76953
    resumed = assists['final-approach01']
    episode = resumed['episodes'][-2]
    assert episode['boss_room'] == 0x11e and episode['release_write_frame'] < episode['first_boss_entry']['frame'] < episode['first_boss_combat']['frame']
    assert episode['first_boss_combat']['hurt'] == 0 and resumed['boss_room'] == 0x14c
    assert reports['final-approach01']['new_guard_frame'] == 90716
    axe = reports['goldenaxe01']
    assert axe['item_acquisition_passed'] and axe['failure'] is None
    assert axe['item_target_value'] == 2 and axe['item_acquisition_first']['owned'] == 1
    assert axe['item_acquisition_last']['owned'] == 2 and axe['item_acquisition_last']['selected'] == 1
    assert not axe['item_acquisition_last']['reward_active'] and axe['item_acquisition_state_writes'] == 0
    raw = raws['goldenaxe01']
    word = lambda name: int.from_bytes(bytes(raw[(sy[name]+i)^1] for i in range(2)), 'big')
    assert word('hero_weapon_level') == 2 and word('hero_selected_item') == 1
    for name in ['analysis/controlled_palace_phase1_v0309_report.json',
                 'tools/summarize_controlled_palace_phase2_v0309.py', 'megadrive/src/main.c',
                 'versions/v0309-7270576d/gaw-megadrive-v0309.bin']:
        evidence[name] = sha((ROOT/name).read_bytes())
    result = dict(passed=True, version=309, md_sha256=digest,
                  controlled_sram_fixture=True, game_written_save=False, natural_campaign_proof=False,
                  full_game_validated=False, initial_state_imports=1,
                  post_boot_health_inventory_progression_writes=0,
                  guardian_assistance=False, guardian_prediction_windows=404,
                  guardian_release_frame=76953, guardian_victory_frame=stages[6]['frames'],
                  golden_axe_actual_upgrade=True, stages=stages, evidence=evidence,
                  limits=['Synthetic Continue fixture derived from actual v306 nine-crystal RAM; not a current New Game campaign.',
                          'Live navigation and combat checkpoints are explicitly incomplete; only the subsequent clear is a victory.',
                          'Final boss, ending, full current cold campaign and global SMS fidelity remain unproven.'])
    (ROOT/'analysis/controlled_palace_phase2_v0309_report.json').write_bytes((json.dumps(result, indent=2)+'\n').encode('utf-8'))
    print('Controlled palace phase2 verified:', len(stages), 'full-RAM/PNG replays; guardian and Golden Axe')


if __name__ == '__main__':
    main()
