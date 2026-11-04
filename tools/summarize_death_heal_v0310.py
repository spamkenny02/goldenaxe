"""Audit ordinary death/Continue and free healing, with no added test writes."""
import json
from pathlib import Path
from run_core import ROOT
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols
from validate_reward_hud_restore import translated

CASES = [
    ('natural-service-route/md-v0310-d7-death-continue02', 'continue'),
    ('natural-dungeon-route/md-v0310-d7-healer94-route02', 'route'),
    ('natural-service-route/md-v0310-d7-healer94-service01', 'heal'),
]


def main():
    refs = {}
    def read(path):
        raw = evidence(path); refs[path.relative_to(ROOT).as_posix()] = sha(raw)
        return raw
    def load(path): return json.loads(read(path))
    digest = sha((ROOT/'gaw-megadrive.bin').read_bytes())
    assert digest == '32fe75a653d7152f7cbf873a32f2ffef14234ea190885ae8a8235f2ccd10e071'
    prior = load(ROOT/'analysis/d6_campaign_v0310_report.json')
    assert prior['passed'] and prior['md_sha256'] == digest and prior['sixth_crystal_and_exterior_return']
    source = ROOT/'validation/v0310-d7-sources'
    index = load(source/'healer_source_index.json')
    for name, h in index.items():
        assert sha(read(source/name)) == sha((ROOT/'tools'/name).read_bytes()) == h
    revision = load(source/'continue_exposure_revision.json')
    assert sha(read(source/revision['original_source'])) == revision['original_sha256']
    assert sha(read(source/revision['current_source'])) == revision['current_sha256']
    assert sha((ROOT/'tools/natural_death_continue.py').read_bytes()) == revision['current_sha256']
    assert sha(read(source/'summarize_death_heal_v0310.py')) == sha(Path(__file__).read_bytes())
    native = load(source/'native_source_index.json')
    for name, h in native.items():
        assert sha(read(source/name)) == sha((ROOT/'megadrive/src'/name).read_bytes()) == h
    sy = symbols(ROOT/'megadrive/out/release/symbol.txt')
    previous = ROOT/prior['stages'][-1]['trace']; prev_cap = load(previous/'capture.json')
    _, original_writes = recording(previous, prev_cap)
    base_raw = read(previous/f'ram_{prev_cap["frames"]:05d}.bin')
    base_data = lambda name, count: bytes(base_raw[(sy[name]+i)^1] for i in range(count))
    base_items = base_data('hero_items', 17); base_gems = base_data('game_save_state', 592)[0x1f:0x28]
    assert base_gems == bytes([128]*6+[0]*3)
    stages = []; reports = {}
    for relative, kind in CASES:
        folder = ROOT/'validation'/relative; cap = load(folder/'capture.json')
        r = load(folder/('route_report.json' if kind == 'route' else 'report.json'))
        a, writes = recording(folder, cap)
        assert cap['rom_sha256'] == r['rom_sha256'] == digest and cap['sram_input'] is None
        assert r['failure'] is None and cap['frames'] > prev_cap['frames']
        assert writes == original_writes and not a['boss_assistance'] and not a['primary_state_imports'] and not a['health_refills']
        assert len(a['episodes']) == 6 and a['boss_room'] == 0x115
        if kind == 'continue':
            assert r['passed'] and r['source_trace'] == previous.relative_to(ROOT/'validation').as_posix()
            assert r['normal_deaths'] == r['normal_continues'] == 1
            assert r['death']['frame'] < r['death_menu']['frame'] < r['resumed']['frame']
            assert r['death']['health'] == 0 and r['death']['hurt'] <= 128
            assert r['resumed']['room'] == 0x95 and r['resumed']['health'] == r['resumed']['magic'] == 24
            assert r['first_state']['health'] == 2 and r['first_state']['gold'] == 30 and r['resumed']['gold'] == 21
            assert not r['new_assistance_writes'] and not r['primary_state_imports'] and not r['currency_or_inventory_fixtures']
            assert r['driver_sha256'] == revision['current_sha256']
        elif kind == 'route':
            assert r['prefix_end'] == prev_cap['frames'] and r['recorded_service_prefix'] == previous.name
            assert r['reached_entrance'] and r['directional_probe_succeeded'] and not r['normal_continues']
            assert r['route_driver_sha256'] == index['natural_dungeon_route.py']
        else:
            assert r['passed'] and r['source_prefix'] == previous.name
            assert not r['new_assistance_writes'] and not r['primary_state_imports'] and not r['currency_or_inventory_fixtures']
            assert r['driver_sha256'] == index['natural_free_healer.py'] and r['normal_health_refill']
            assert r['first_state']['health'] == 24 and r['healed']['health'] == r['healed']['max_health'] == 80
            assert r['first_state']['gold'] == r['last_state']['gold'] == 21
            assert r['first_state']['magic'] == r['last_state']['magic'] == 24
            assert {1, 2, 3}.issubset(r['observed_healer_phases'])
        proof_folder = folder.with_name(folder.name+'-assisted-fixed-replay-'+str(cap['frames']))
        proof = load(proof_folder/'replay_report.json')
        assert proof['passed'] and proof['rom_sha256'] == digest and proof['whole_ram_bytes'] == 65536
        assert proof['final_png_exact'] and not proof['feedback_reads']
        for name, h in proof['evidence'].items(): assert sha(read(folder/name)) == h
        for stem, ext in [('ram', 'bin'), ('frame', 'png')]:
            name = f'{stem}_{cap["frames"]:05d}.{ext}'
            assert read(folder/name) == read(proof_folder/name)
        raw = read(folder/f'ram_{cap["frames"]:05d}.bin')
        data = lambda name, count: bytes(raw[(sy[name]+i)^1] for i in range(count))
        word = lambda name: int.from_bytes(data(name, 2), 'big')
        assert data('hero_items', 17) == base_items and data('game_save_state', 592)[0x1f:0x28] == base_gems
        assert word('hero_keys') == 2 and word('hero_max_health') == 80 and word('hero_max_magic') == 72
        assert word('hero_gold') == 21 and word('hero_magic') == 24 and word('hero_selected_item') == 1
        assert word('hero_health') > 0 and not word('world_dungeon_number') and not word('sound_unhandled_command')
        if kind in ('continue', 'heal'):
            sms = data('sms_vram', 16384); vram = read(folder/f'vram_{cap["frames"]:05d}.bin')
            regs = read(folder/f'vdp_regs_{cap["frames"]:05d}.bin')
            base = (regs[2]&56)<<10; width = [32,64,32,128][regs[16]&3]
            for n in range(128):
                at = base+((n//32+22)*width+n%32)*2
                assert int.from_bytes(vram[at:at+2], 'little') == translated(int.from_bytes(sms[0x3d00+n*2:0x3d02+n*2], 'little'))
        if kind == 'heal': assert word('room_id') == 0x94 and word('hero_health') == 80
        stages.append(dict(trace=folder.relative_to(ROOT).as_posix(), frames=cap['frames'], room=word('room_id'),
                           health=word('hero_health'), max_health=80, gold=21, keys=2, magic=24, whole_ram_png_exact=True))
        read(folder/'controls.json'); read(folder/'assistance.json')
        reports[kind] = r; previous, prev_cap = folder, cap
    result = dict(passed=True, version=310, md_sha256=digest, production_rom_unchanged=True,
                  stages=stages, normal_death_continue=True, free_healing_verified=True,
                  primary_state_imports=0, new_assistance_writes=0, currency_or_inventory_fixtures=False,
                  death=reports['continue']['death'], resumed=reports['continue']['resumed'], healed=reports['heal']['healed'],
                  six_crystals_and_inventory_retained=True, physical_huds_checked=2,
                  ready_trace=previous.relative_to(ROOT).as_posix(), ready_frame=prev_cap['frames'], full_game_validated=False,
                  evidence=refs, limits=['Only inherited approach guards; no added RAM writes, forced death, resource fixture or SRAM import.',
                                       'One natural death, Continue and free night on current NTSC ROM. D7 and global fidelity remain open.'])
    (ROOT/'analysis/death_heal_v0310_report.json').write_bytes((json.dumps(result, indent=2)+'\n').encode())
    print('v310: normal death/Continue, retained inventory/crystals and free healing verified')


if __name__ == '__main__':
    main()
