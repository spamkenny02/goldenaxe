"""Bind the isolated merchant publication fix to its measured cartridge."""
import json
import re

from archive_lossless_evidence import sha
from run_core import ROOT


def main():
    base = ROOT/'validation/merchant-panel-v0314'
    candidate = base/'candidate03'
    references = {}
    def read(path):
        raw = path.read_bytes()
        references[path.relative_to(ROOT).as_posix()] = sha(raw)
        return raw
    def load(path):
        return json.loads(read(path))
    digest = sha(read(candidate/'out/release/rom.bin'))
    public = sha((ROOT/'gaw-megadrive.bin').read_bytes())
    assert public == 'c53381c459a1e6254a8c9f1cfad1b8cda482cc0614697ad566133b28335e07a7'
    proposal = load(candidate/'proposal.json')
    assert proposal['baseline_sha256'] == public
    changed = []
    for name, expected in proposal['sources'].items():
        raw = read(candidate/name)
        assert sha(raw) == expected
        relative = name.removeprefix('src/')
        if raw != (ROOT/'megadrive/src'/relative).read_bytes():
            changed.append(relative)
    assert changed == ['merchant.inc'], changed
    source = read(candidate/'src/merchant.inc').decode()
    table = source.split('merchant_text_tiles[256] = {',1)[1].split('};',1)[0]
    tiles = bytes(int(n,16) for n in re.findall(r'0x([0-9a-fA-F]+)',table))
    charset = bytes.fromhex(proposal['charset_hex'])
    assert len(tiles)==256 and len(charset)==80
    for value in range(256):
        index = next((i for i in range(80,0,-1) if charset[i-1]==value),0)
        assert tiles[value] == (0xb0+index-1)&255
    cases = []
    for region, old_delta in [('pal',1),('ntsc',-1)]:
        before = load(base/f'baseline-{region}/report.json')
        after = load(base/f'candidate03-{region}/report.json')
        assert before['observations']['md']['rom_sha256']==public
        assert before['settled_panel_delta_frames']==old_delta
        assert after['observations']['md']['rom_sha256']==digest
        assert after['settled_panel_delta_frames']==0 and after['black_window_exact']
        for system in ('sms','md'):
            assert not after['observations'][system]['hud_empty_frames']
            assert not after['observations'][system]['display_disabled_frames']
        cases.append(dict(region=region,baseline_delta=old_delta,corrected_delta=0,
                          observations=after['observations']))
    portrait = load(base/'candidate03-portrait-report.json')
    pixels = load(base/'candidate03-panel-pixels-report.json')
    assert portrait['passed'] and pixels['passed']
    for case in portrait['cases']:
        assert case['sms']==case['md'] and len(case['sms'])==8
    for case in pixels['cases']:
        assert case['dialogue_bitmap_bytes_exact']==4160
        assert case['normalized_playfield_pixels_exact']==40960
    services = load(base/'candidate03-services/validation/all_merchants_report.json')
    assert services['md_sha256']==digest and services['all_23_towns_checked']
    assert len(services['cases'])==43
    inventory = load(base/'candidate03-services/validation/inventory_restore_report.json')
    assert inventory['md_sha256']==digest and len(inventory['cases'])==6
    for case in inventory['cases']:
        assert case['inventory_open_and_closed']
        assert not any(case['static_background_pattern_difference_indices'].values())
        assert not case['early_native_static_pattern_changes_from_before_menu']
    intro = load(base/'candidate03-intro-report.json')
    assert intro['passed'] and intro['md_sha256']==digest and intro['baseline_sha256']==public
    for name, expected in intro['evidence'].items():
        assert sha(read(ROOT/name))==expected
    result = dict(passed=True,md_sha256=digest,public_md_sha256=public,
        candidate_promoted=False,changed_native_sources=changed,
        merchant_source_sha256=sha(read(candidate/'src/merchant.inc')),
        charset_input_values_exact=256,natural_first_village_cases=cases,
        source_exact_portrait_poses_per_region=8,controlled_transaction_cases=43,
        inventory_restore_cases=6,intro_audio_boot_frames_per_region=6500,
        selected_intro_title_pngs_exact=8,evidence=references,
        full_game_validated=False,
        limits=['Natural first-village completed panel and black-window frames match SMS PAL/NTSC. Portrait checks cover plane2 masks; final playfield pixels are palette-normalized.',
                '43 transactions use controlled service fixtures across23 towns. Natural world access and exact panel timing in every town are not claimed.',
                'Intro/audio comparison is against the validated v314 on the same observation core. Complete campaign,global R/IRQ and hardware fidelity are separate.'])
    out = ROOT/'analysis/merchant_panel_candidate03_v0314_report.json'
    assert not out.exists()
    out.write_text(json.dumps(result,indent=2)+'\n')
    print('Merchant candidate verified:',digest,flush=True)


if __name__=='__main__':
    main()
