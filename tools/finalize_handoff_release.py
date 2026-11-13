"""Freeze V325 software evidence; physical flashkit validation remains pending."""
import hashlib
import json
import shutil
from run_core import ROOT
from finalize_md_rom import md_checksum


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    rom = ROOT / 'validation/hardware-handoff04-minimal/candidate.bin'
    raw = rom.read_bytes()
    digest = sha(rom)
    assert len(raw) == 2097152
    assert raw[0x1a4:0x1a8] == bytes.fromhex('001fffff')
    assert md_checksum(raw) == int.from_bytes(raw[0x18e:0x190], 'big')
    assert digest == sha(ROOT / 'validation/hardware-handoff05-repro/candidate.bin')
    files = {
        'build': 'validation/hardware-handoff05-repro/build-report.json',
        'boot': 'validation/hardware-handoff04-boot/report.json',
        'campaign-ntsc': 'validation/hardware-handoff04-campaign-ntsc/report.json',
        'campaign-pal': 'validation/hardware-handoff04-campaign-pal/report.json',
        'konami': 'validation/hardware-handoff04-menu/report.json',
        'continue': 'analysis/hardware-handoff04-continue-report.json',
    }
    folder = ROOT / 'reports/handoff-v0325-2026-11-13'
    folder.mkdir(exist_ok=True)
    proofs = {}
    for name, path in files.items():
        source = ROOT / path
        result = json.loads(source.read_bytes())
        assert result['passed'] and result.get('md_sha256', result.get('rom_sha256')) == digest
        if name.startswith('campaign-'):
            assert result['ending_seen'] and result['final']['crystals'] == 9
            assert not result['normal_deaths'] and not result['live_boss_guard_overlap_frames']
            assert result['cheats_disabled_every_frame_checked']
        if name == 'konami':
            assert result['case_count'] == 12
        if name == 'continue':
            assert len(result['cases']) == 4
        target = folder / (name + '.json')
        shutil.copyfile(source, target)
        proofs[name] = dict(file=target.relative_to(ROOT).as_posix(), sha256=sha(target))
    result = dict(
        passed=True, version=325, md_sha256=digest, bytes=len(raw),
        checksum=f'{md_checksum(raw):04X}',
        reproducible_build=True, rom_size_limit_respected=2097152,
        source_fix='Only read the 19 cached SGDK VDP registers; drain FIFO and explicitly initialize DMA registers19..23 instead of reading beyond the cache.',
        reported_hardware=dict(console='Mega Drive1', flashkit='2MiB ROM +32KiB SRAM',
                               v322_rc1_working=True, v324_voice_then_black_screen=True),
        hardware_validation_pending=True,
        hardware_root_cause_confirmed=False,
        original_intro_after_presentation=True, image_voice_fades_preserved=True,
        pal_ntsc_campaigns_to_ending=True, konami_and_continue_preserved=True,
        proofs=proofs,
        scope='Software regression gates only. The out-of-bounds VDP cache read is confirmed in source; whether this fixes the reported real-console failure requires a new flashkit test. Campaign approach protection remains declared and is removed before live bosses. No new global100percent fidelity certification.',
    )
    target = ROOT / 'analysis/hardware_handoff_v0325_report.json'
    target.write_text(json.dumps(result, indent=2) + '\n', newline='\n')
    shutil.copyfile(target, folder / 'VALIDATION.json')
    shutil.copyfile(rom, ROOT / 'gaw-megadrive.bin')
    shutil.copyfile(rom, ROOT / 'gaw-title-megadrive.bin')
    print(json.dumps(dict(passed=True, md_sha256=digest, hardware_validation_pending=True)))


if __name__ == '__main__':
    main()
