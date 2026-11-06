"""Use the completed v317 D9 campaign for owned Balloon, palace or actual save."""
import argparse,json,shutil
import continue_d8_entry_v0317 as helper
from run_core import ROOT
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence

from continue_d8_entry_v0317 import COMBAT,ROUTE,SERVICE,budget,load,replay,assert_canonical,run
helper.EVIDENCE=ROOT/'validation/v0317-after-d9-sources'

EXIT = 'md-auto-v0317-d9-exit01'
ROM = '7694654ec85dd6626c0e17ff1834e5893d4eb35481400a4725eac6b6f3503294'


def require_campaign_exit(branch):
    receipt=json.loads(evidence(ROOT/'analysis/d9_campaign_v0317_report.json'))
    assert receipt['passed'] and receipt['ninth_crystal_and_exterior_return']
    assert receipt['md_sha256']==ROM==sha((ROOT/'gaw-megadrive.bin').read_bytes())
    helper.EVIDENCE.mkdir(exist_ok=True)
    snapshot=helper.EVIDENCE/branch
    snapshot.mkdir(exist_ok=False)
    names=('natural_owned_overview.py','natural_palace_world_route.py',
           'natural_dungeon_route.py','natural_save_service.py',
           'validate_game_written_save.py','assisted_prefix.py',
           'assisted_boss_route.py','replay_assisted_prefix.py',
           'continue_after_d9_v0317.py','continue_d8_entry_v0317.py')
    hashes={}
    for name in names:
        target=snapshot/name
        shutil.copyfile(ROOT/'tools'/name,target)
        hashes[name]=sha(target.read_bytes())
    (snapshot/'source_index.json').write_text(json.dumps(hashes,indent=2)+'\n',encoding='utf-8')
    assert_canonical(COMBAT, EXIT)
    result = load(COMBAT, EXIT)
    capture = load(COMBAT, EXIT, 'capture.json')
    assert result['rom_sha256'] == ROM and capture['sram_input'] is None
    assert result['full_dungeon_cleared'] and not result['new_assistance_writes']
    assert result['failure'] is None and not result['deaths']


def enter_palace():
    trial = 'v0317-owned-overview01'
    run('natural_owned_overview.py', ['--trace', f'{COMBAT}/{EXIT}',
        '--assisted-prefix', '--trial', trial])
    overview = 'md-auto-' + trial
    replay(COMBAT, overview, lambda r: r['passed'] and r['actual_owned_balloon']
           and r['modal_resources_unchanged'] and not r['new_assistance_writes'])

    trial = 'v0317-cold-palace-entry02'
    run('natural_palace_world_route.py', ['--boss-room', '0x14c',
        '--new-assistance-episode', '--completed-exit-proof', f'{COMBAT}/{EXIT}',
        '--world-route', '--preserve-floor-hurt', '--assisted-prefix',
        '--prefix-completed-action', '--prefix-combat', overview, '--door-index', '10',
        '--live-prefix-terrain', '--live-room-replan', '--axe-terrain', '--rope-terrain',
        '--frames', budget(COMBAT, overview, 20000), '--trial', trial])
    replay(ROUTE, 'md-' + trial, lambda r: r['reached_entrance']
           and r['palace_gate_verified'] and not r['palace_new_map_or_resource_writes'])
    print('V0317 PALACE ENTRY VERIFIED', flush=True)


def save_and_reload():
    route = 'v0317-real-save-route02'
    run('natural_dungeon_route.py', ['--prefix-combat', EXIT, '--assisted-prefix',
        '--house-outside', '0xfa', '--house-target', '0x6f', '--trial', route,
        '--frames', budget(COMBAT, EXIT, 6000), '--axe-terrain', '--required-chop',
        '0xfa:0x5d', '--live-prefix-terrain', '--live-room-replan'])
    replay(ROUTE, 'md-' + route, lambda r: r['reached_entrance'])

    trial = 'v0317-nine-crystals-save01'
    run('natural_save_service.py', ['--prefix', 'md-' + route, '--assisted-prefix',
        '--trial', trial])
    run('validate_game_written_save.py', ['--trace', f'{SERVICE}/md-{trial}',
        '--trial', 'v0317-nine-crystals-01',
        '--release-report-name', 'game_written_save_v0317_nine_crystals_report.json'])
    print('V0317 GAME-WRITTEN SAVE AND CONTINUE VERIFIED', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('branch', choices=['palace', 'save'])
    args = parser.parse_args()
    completed_save = ROOT/'analysis/game_written_save_v0317_nine_crystals_report.json'
    if args.branch == 'save' and completed_save.exists():
        receipt = json.loads(completed_save.read_bytes())
        assert receipt['md_sha256'] == ROM == sha((ROOT/'gaw-megadrive.bin').read_bytes())
        assert receipt['passed'] and receipt['source_crystal_markers_exact'] == 9
        assert receipt['source_trace'] == f'{SERVICE}/md-v0317-nine-crystals-save01'
        assert receipt['raw_sram_fixed_replay_exact'] and receipt['save_whole_ram_png_exact']
        fixed = ROOT/receipt['fixed_replay_trace']/'replayed.srm'
        assert sha(evidence(fixed)) == receipt['source_sram_sha256']
        reload = json.loads(evidence(ROOT/receipt['reload_trace']/'report.json'))
        assert all(receipt[key] == value for key, value in reload.items())
        print('V0317 NINE-CRYSTAL SAVE AND CONTINUE ALREADY VERIFIED', flush=True)
        raise SystemExit(0)
    from cold_replay_stream import ReplayStream
    helper.EVIDENCE.mkdir(exist_ok=True)
    helper.STREAM=ReplayStream(helper.EVIDENCE/(args.branch+'-cold-stream'))
    try:
        require_campaign_exit(args.branch)
        {'palace': enter_palace, 'save': save_and_reload}[args.branch]()
    finally:helper.STREAM.close()
