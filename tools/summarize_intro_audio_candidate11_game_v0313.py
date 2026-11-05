"""Verify the atomic audio candidate against the recorded first-crystal campaign."""
import json
from run_core import ROOT
from archive_lossless_evidence import sha, freeze
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols


def main():
    project = ROOT/'validation/intro-audio-v0313/candidate11'
    refs = {}; paths = set()
    def read(path):
        raw = path.read_bytes(); refs[path.relative_to(ROOT).as_posix()] = sha(raw)
        paths.add(path); return raw
    def load(path): return json.loads(read(path))
    audio = load(ROOT/'analysis/intro_audio_candidate11_v0313_report.json')
    assert audio['passed'] and audio['targeted_intro_audio_title_checks_passed']
    name = 'md-auto-audio11-fresh-d1-rebase01'
    case = project/'validation/natural-dungeon-combat'/name
    c = load(case/'capture.json'); r = load(case/'report.json'); f = c['frames']
    digest = sha(read(project/'gaw-megadrive.bin'))
    assert digest == audio['md_sha256'] == c['rom_sha256'] == r['rom_sha256']
    assert r['passed'] and r['failure'] is None and not r['deaths']
    assert not r['terminal_field_mismatches'] and r['terminal_png_exact']
    assert r['dungeon_exit_verified'] and r['full_dungeon_cleared']
    assert r['last_state']['room'] == 0xb9 and r['last_state']['crystals'] == [128]+[0]*8
    assert not c['sram_input'] and not r['boss_assistance']
    a, writes = recording(case, c)
    sy = symbols(project/'megadrive/out/release/symbol.txt')
    assert not a['primary_state_imports'] and not a['health_refills'] and not a['boss_assistance']
    release = a['release_write_frame']; assert release == 14615
    assert all(addr == sy['hero_hurt'] and value in (b'\0\0', b'\0\x81') and t <= release
               for t, addr, value in writes)
    proofcase = case.with_name(name+'-assisted-fixed-replay-'+str(f))
    proof = load(proofcase/'replay_report.json')
    assert proof['passed'] and proof['whole_ram_bytes'] == 65536 and proof['final_png_exact']
    assert not proof['feedback_reads'] and proof['rom_sha256'] == digest
    assert proof['first_boss_combat'] == dict(frame=14826, health=18, hurt=0)
    assert proof['last_injection_frame'] == release and not proof['boss_assistance']
    for n, h in proof['evidence'].items(): assert sha(read(case/n)) == h
    for stem, ext in [('ram', 'bin'), ('frame', 'png')]:
        assert read(case/f'{stem}_{f:05d}.{ext}') == read(proofcase/f'{stem}_{f:05d}.{ext}')
    read(project/'megadrive/out/release/symbol.txt')
    read(ROOT/'validation/replay_intro_audio_candidate11_d1.py')
    read(ROOT/'tools/summarize_intro_audio_candidate11_game_v0313.py')
    archive = ROOT/'analysis/intro-audio-deadline-game-v0313'
    freeze(ROOT, archive, paths, dict(candidate_md_sha256=digest,
        scope='Atomic-queue, music-relative deadline candidate; first crystal and exterior return.'),
        [project], cleanup=False)
    result = dict(passed=True, md_sha256=digest, public_md_sha256=audio['public_md_sha256'],
        candidate_promoted=False, first_crystal_and_exterior_return_verified=True,
        campaign_frames=f, guard_release_frame=release, first_boss_combat=proof['first_boss_combat'],
        whole_ram_bytes=65536, final_png_exact=True, primary_state_imports=0,
        health_or_inventory_imports=0, full_game_validated=False,
        archive_manifest=archive.relative_to(ROOT).as_posix()+'/manifest.json', evidence=refs,
        limits=['Fresh candidate08 controls replayed from boot on candidate11; exact final fields and normalized PNG. Independent same-ROM cold replay compares all RAM and final PNG.',
                'Logged hurt guards only before the first boss; none during combat or return. Later campaign, save, whole-source RNG and hardware remain unverified on this candidate.'])
    (ROOT/'analysis/intro_audio_candidate11_game_v0313_report.json').write_text(
        json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print('Atomic audio candidate: first crystal, exterior return and whole-RAM cold replay verified')


if __name__ == '__main__': main()
