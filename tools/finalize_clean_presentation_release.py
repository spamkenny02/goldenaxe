"""Freeze V328: native SDK video handoff and non-destructive save-name guards."""
import hashlib
import json
import shutil
from run_core import ROOT
from finalize_md_rom import md_checksum


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    rom = ROOT / 'validation/hardware-clean04-nameguard/candidate.bin'
    digest = sha(rom)
    raw = rom.read_bytes()
    assert len(raw) == 2097152 and md_checksum(raw) == int.from_bytes(raw[0x18e:0x190], 'big')
    assert digest == sha(ROOT / 'validation/hardware-clean05-repro/candidate.bin')
    folder = ROOT / 'reports/clean-presentation-v0328-2026-11-13'
    folder.mkdir(exist_ok=True)
    files = {
        'build': 'validation/hardware-clean05-repro/build-report.json',
        'boot': 'validation/hardware-clean04-boot/report.json',
        'planes-and-empty-slots': 'validation/hardware-clean04-planes/report.json',
        'campaign-ntsc': 'validation/hardware-clean04-campaign-ntsc/report.json',
        'campaign-pal': 'validation/hardware-clean04-campaign-pal/report.json',
        'konami': 'validation/hardware-clean04-menu/report.json',
        'continue': 'analysis/hardware-clean04-continue-report.json',
    }
    proofs = {}
    for name, path in files.items():
        source = ROOT / path
        result = json.loads(source.read_bytes())
        assert result['passed'] and result['md_sha256'] == digest
        if name.startswith('campaign-'):
            assert result['ending_seen'] and result['final']['crystals'] == 9
            assert not result['normal_deaths'] and not result['live_boss_guard_overlap_frames']
        if name == 'konami':
            assert result['case_count'] == 12
        if name == 'continue':
            assert len(result['cases']) == 4
        if name == 'planes-and-empty-slots':
            assert len(result['cases']) == 10
        target = folder / (name+'.json')
        shutil.copyfile(source, target)
        proofs[name] = dict(file=target.relative_to(ROOT).as_posix(), sha256=sha(target))
    captures = {
        'avant-noms-invalides.png': 'validation/hardware-clean04-old-reproduction/capture/frame_02250.png',
        'apres-noms-invalides.png': 'validation/hardware-clean04-planes/pal-empty-254/frame_01431.png',
        'jeu-bordures-noires.png': 'validation/hardware-clean04-planes/pal-game/frame_04231.png',
    }
    for name, path in captures.items():
        shutil.copyfile(ROOT / path, folder / name)
    videos = []
    from pathlib import Path
    for prefix in ['ADGPM2ljZEa', 'ADGPM2nnYQ']:
        video = next(Path('C:/Users/UniKennY/Downloads/Video').glob(prefix+'*.mp4'))
        videos.append(dict(sha256=sha(video), private_original_published=False))
    result = dict(passed=True, version=328, md_sha256=digest, bytes=len(raw),
                  checksum=f'{md_checksum(raw):04X}', hardware_validation_pending=True,
                  prior_v327_boot_reported_working=True, diagnostic_markers_removed=True,
                  sdk_vdp_init_preserved=True, black_margins_checked_pal_ntsc=True,
                  invalid_sram_names_hidden_and_load_refused=True,
                  save_data_not_erased_or_reformatted=True,
                  legitimate_save_continue_preserved=True,
                  source_bug_reproduction='V327 with syntheticFE SRAM shows FFFFFFFF through the unsupported-character fallback. This is a reproduction, not a dump of the user flashkit.',
                  margin_bug='Diagnostic tile512 remained in the outer plane rows, then was reused by normal gameplay graphics.',
                  private_video_evidence=videos, proofs=proofs,
                  scope='Software checks for splash, save names/loading and black margins, plus recorded PAL/NTSC campaigns with declared approach protection removed before live bosses. Full SRAM payload integrity is not certified merely by a valid name. V328 physical console confirmation remains pending; not a new global100percent release certification.')
    report = ROOT / 'analysis/clean_presentation_v0328_report.json'
    report.write_text(json.dumps(result,indent=2)+'\n',newline='\n')
    shutil.copyfile(report, folder / 'VALIDATION.json')
    shutil.copyfile(rom, ROOT / 'gaw-megadrive.bin')
    shutil.copyfile(rom, ROOT / 'gaw-title-megadrive.bin')
    print(json.dumps(dict(passed=True, md_sha256=digest, hardware_validation_pending=True)))


if __name__ == '__main__':
    main()
