"""Audit the isolated startup-resource delay candidate without replacing v312."""
import difflib
import json
from archive_lossless_evidence import sha
from assisted_prefix import recording
from rebase_natural_campaign import evidence
from run_core import ROOT
from validate_playable_sprite_limit import symbols


def main():
    refs = {}
    project = 'validation/title-boot-phase-v0312/candidate02/'

    def read(path):
        raw = evidence(ROOT/path)
        refs[path] = sha(raw)
        return raw

    def load(path):
        return json.loads(read(path))

    build = load(project+'build_report.json')
    candidate = sha(read(project+'gaw-megadrive.bin'))
    production = sha(read('gaw-megadrive.bin'))
    assert candidate == build['candidate_rom_sha256'] and production == build['production_rom_sha256']
    assert candidate == '48fb6e924a520ff579d3fb4eabe4aac365e9a37eed3dc33ff0dabfdc232e1932'
    assert production == '0b9aecb48fc9bb82cfcebc9547684742134d60e0f82e60b1a070ab3be50b4d64'
    before,after = read('megadrive/src/intro.inc'),read(project+'megadrive/src/intro.inc')
    assert sha(before) == build['source_before_sha256'] and sha(after) == build['source_after_sha256']
    assert build['production_source_unchanged'] and before != after
    assert read('megadrive/src/main.c') == read(project+'megadrive/src/main.c')
    patch = ''.join(difflib.unified_diff(before.decode().splitlines(True),after.decode().splitlines(True),
                    fromfile='a/megadrive/src/intro.inc',tofile='b/megadrive/src/intro.inc'))
    folder=ROOT/'analysis/title-boot-candidate-v0312'
    folder.mkdir(exist_ok=True)
    (folder/'startup.patch').write_bytes(patch.encode())
    read('analysis/title-boot-candidate-v0312/startup.patch')
    regions=[]
    for pal,old_offset in [(False,-21),(True,-22)]:
        suffix='-pal' if pal else ''
        old = load(f'validation/title_cadence{suffix}-natural-v0312-baseline01_report.json')
        title = load(project+f'validation/title_cadence{suffix}-natural-candidate02_report.json')
        story = load(project+f'validation/intro{suffix}_report.json')
        assert old['md_sha256'] == production and title['md_sha256'] == story['md_sha256'] == candidate
        assert set(old['map_start_offsets']) == set(old['palette_start_offsets']) == {old_offset}
        assert title['natural_boot'] and title['no_ram_mutations'] and title['relative_timing_exact']
        assert title['absolute_title_timing_exact'] and set(title['map_start_offsets']+title['palette_start_offsets']) == {0}
        assert len(title['pixel_checks']) == 20 and all(row['normalized_pixel_mismatches'] == 0 for row in title['pixel_checks'])
        assert story['natural_boot'] and story['no_buttons'] and story['no_ram_mutations']
        assert [row['line'] for row in story['story_lines']] == list(range(1,66))
        assert all(row['scene_and_text_map_bytes_exact'] == 1536 for row in story['story_lines'])
        assert story['line_start_offset_frames_range'] == ([0,0] if pal else [-1,0])
        assert story['source_intro_completion_frame'] == story['native_intro_completion_frame']
        interval=title['sms_map_frames'][0]-story['source_intro_completion_frame']
        assert title['md_map_frames'][0]-story['native_intro_completion_frame'] == interval == (79 if pal else 86)
        regions.append(dict(region='pal' if pal else 'ntsc',previous_title_offset=old_offset,
                            candidate_title_offset=0,story_start_offsets=story['line_start_offset_frames_range'],
                            story_completion_frame=story['native_intro_completion_frame'],
                            story_to_title_interval_frames=interval,normalized_title_images_exact=20))
    trace=project+'validation/natural-dungeon-combat/md-auto-title-boot-candidate02-d7-replay01'
    report,cap=load(trace+'/report.json'),load(trace+'/capture.json')
    assert report['passed'] and report['failure'] is None and not report['deaths']
    assert report['md_sha256'] == cap['rom_sha256'] == candidate and cap['sram_input'] is None
    assert report['terminal_field_mismatches'] == [] and report['terminal_png_exact']
    assert len(report['checked_bosses']) == 8 and all(row['passed'] and row['hurt'] == 0 for row in report['checked_bosses'])
    assert report['last_state']['crystals'] == [128]*7+[0]*2 and report['last_state']['room'] == 0x1b
    assert report['full_dungeon_cleared'] and report['dungeon_exit_verified']
    aid,writes=recording(ROOT/trace,cap)
    read(trace+'/assistance.json')
    sy=symbols(ROOT/(project+'megadrive/out/release/symbol.txt'))
    assert not aid['primary_state_imports'] and not aid['boss_assistance'] and not aid['health_refills']
    assert all(addr == sy['hero_hurt'] and value in (b'\0\0',b'\0\x81') for _,addr,value in writes)
    frame=cap['frames'];proof_root=trace+f'-assisted-fixed-replay-{frame}'
    proof=load(proof_root+'/replay_report.json')
    assert proof['passed'] and proof['rom_sha256'] == candidate and proof['whole_ram_bytes'] == 65536
    assert proof['final_png_exact'] and not proof['feedback_reads']
    for name in ('capture.json','controls.json','assistance.json'):
        assert proof['evidence'][name] == sha(read(trace+'/'+name))
    for stem,ext in [('ram','bin'),('frame','png')]:
        filename=f'/{stem}_{frame:05d}.{ext}'
        assert read(trace+filename) == read(proof_root+filename)
    result=dict(passed=True,md_sha256=candidate,production_rom_sha256=production,
                candidate_private=True,production_rom_unchanged=True,production_source_unchanged=True,
                regions=regions,story_lines_checked=130,normalized_title_images_checked=40,
                current_seven_crystal_inputs_replayed=True,checked_boss_entries=8,frames=frame,
                terminal_gameplay_fields_match_v0312=True,terminal_png_matches_v0312=True,
                independent_candidate_replay_whole_ram_png_exact=True,primary_state_imports=0,
                full_game_validated=False,evidence=refs,
                limits=['Candidate only. The public ROM remains v312 while the current campaign continues.',
                        'The delay reserves initial resource work before scene loading; it preserves the measured86/79-frame story-to-title interval.',
                        'Story text and title timing are covered; complete scene-reveal/sprite/audio timing, global R/IRQ and hardware remain open.',
                        'Seven crystals are replayed from boot with declared approach guards; D8 onward and saving are outside this candidate proof.'])
    (ROOT/'analysis/title_boot_candidate_v0312_report.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Private title candidate verified: PAL/NTSC title epochs, 130 story lines and seven-crystal cold replay')


if __name__=='__main__':
    main()
