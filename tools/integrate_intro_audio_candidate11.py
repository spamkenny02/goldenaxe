"""Integrate the tested audio sources once the running v313 campaign is complete."""
import json, subprocess
from run_core import ROOT
from archive_lossless_evidence import sha

CANDIDATE = 'c53381c459a1e6254a8c9f1cfad1b8cda482cc0614697ad566133b28335e07a7'
PUBLIC = '48fb6e924a520ff579d3fb4eabe4aac365e9a37eed3dc33ff0dabfdc232e1932'


def main():
    def report(name): return json.loads((ROOT/'analysis'/name).read_bytes())
    # Root aliases/symbols are used by that campaign. Never replace them mid-run.
    final = report('cold_palace_final_v0313_report.json')
    assert final['passed'] and final['campaign_from_new_game_completed'] and final['ending_complete']
    assert final['md_sha256'] == PUBLIC
    audio = report('intro_audio_candidate11_v0313_report.json')
    game = report('intro_audio_candidate11_game_v0313_report.json')
    menu = report('start_menu_candidate11_v0313_report.json')
    for proof in (audio, game, menu): assert proof['passed'] and proof['md_sha256'] == CANDIDATE
    assert audio['targeted_intro_audio_title_checks_passed']
    assert game['first_crystal_and_exterior_return_verified']
    assert menu['cursor_and_confirm_event_frames_source_exact']
    assert sha((ROOT/'gaw-megadrive.bin').read_bytes()) == PUBLIC
    project = ROOT/'validation/intro-audio-v0313/candidate11'
    assert sha((project/'gaw-megadrive.bin').read_bytes()) == CANDIDATE
    source = ROOT/'megadrive/src'
    changed = []
    for path in source.rglob('*'):
        if not path.is_file(): continue
        relative = path.relative_to(source)
        other = project/'megadrive/src'/relative
        assert other.is_file(), relative
        if path.read_bytes() != other.read_bytes():
            assert sha(path.read_bytes()) == audio['evidence']['megadrive/src/'+relative.as_posix()]
            changed.append(relative.as_posix())
    assert sorted(changed) == ['intro.inc', 'main.c', 'sound.inc']
    assert not (source/'gaw_sgdk_sys.c').exists()
    for name in [*changed, 'gaw_sgdk_sys.c']:
        (source/name).write_bytes((project/'megadrive/src'/name).read_bytes())
    (ROOT/'megadrive/SGDK-license.txt').write_bytes((project/'SGDK-license.txt').read_bytes())
    with (ROOT/'validation/intro-audio-production-build.log').open('wb') as log:
        subprocess.run(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass',
                        '-File', str(ROOT/'build.ps1')], cwd=ROOT, stdout=log,
                       stderr=subprocess.STDOUT, check=True)
    assert sha((ROOT/'gaw-megadrive.bin').read_bytes()) == CANDIDATE, 'Production build differs from tested candidate'
    assert (ROOT/'gaw-title-megadrive.bin').read_bytes() == (project/'gaw-megadrive.bin').read_bytes()
    versions = json.loads((ROOT/'versions/index.json').read_bytes())
    version = next(row for row in versions if row['sha256'] == CANDIDATE)
    result = dict(passed=True, version=version['version'], md_sha256=CANDIDATE,
        previous_md_sha256=PUBLIC, production_build_matches_tested_candidate=True,
        actual_source_files_integrated=[*changed, 'gaw_sgdk_sys.c'],
        sgdk_license='megadrive/SGDK-license.txt', full_game_validated=False,
        limits=['The complete v313 campaign remains tied to its previous binary. This release has its own intro/title, start menu and first-crystal proof; its later campaign remains to verify.'])
    output = ROOT/'analysis'/f'intro_audio_integration_v{version["version"]:04d}_report.json'
    output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print('Integrated tested native audio candidate as version', version['version'])


if __name__ == '__main__': main()
