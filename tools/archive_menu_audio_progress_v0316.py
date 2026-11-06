"""Preserve the verified menu work and the measured intro release gate."""
import difflib
import json
from pathlib import Path

from archive_lossless_evidence import freeze,sha
from run_core import ROOT


def main():
    base=ROOT/'validation/menu-audio-v0316';latest=base/'candidate09'
    public=sha((ROOT/'gaw-megadrive.bin').read_bytes())
    assert public=='8b94f2e022d1027b5bc3cefd18ffd9f79a8895fba7622defc400c10d6fdfff7b'
    assert (ROOT/'gaw-megadrive.bin').read_bytes()==(ROOT/'versions/v0316-8b94f2e0/gaw-megadrive-v0316.bin').read_bytes()
    refs={}
    def load(path):
        refs[path.relative_to(ROOT).as_posix()]=sha(path.read_bytes());return json.loads(path.read_bytes())
    matrix=load(base/'candidate08-name-matrix/report.json');assert matrix['passed'] and len(matrix['cases'])==210
    proven=matrix['md_sha256'];visual=[];audio=[];regressions=[]
    for region in ('ntsc','pal'):
        video=load(base/('candidate08-video-'+region)/'report.json');assert video['md_sha256']==proven
        measured=[r for r in video['pixel_differences']if r['frame']>=938]
        assert len(measured)==135 and all(not r['pixels']for r in measured)
        control=load(base/('candidate08-controller-'+region)/'report.json');assert control['md_sha256']==proven and not control['differences']
        visual.append(dict(region=region,normalized_menu_frames_exact=58,normalized_name_frames_exact=77,name_controller_frames_exact=351))
        for variant in ('default','early-menu','early-new','late-new'):
            folder=base/('candidate08-'+variant+'-'+region);probe=load(folder/'report.json');assert probe['rom_sha256']==proven
            rows=[json.loads((folder/tag/'observations.json').read_bytes())for tag in ('sms','md')]
            first=next(r['frame']for r in rows[0]if r['frame']>=int(probe['input_acks']['920']) and r['tempo'][1]==5)
            pairs=[(s,m)for s,m in zip(*rows)if s['frame']>=first]
            assert all(s['tempo']==m['tempo']for s,m in pairs)
            before=[(s,m)for s,m in pairs if s['frame']<=1489];assert all(s['channels']==m['channels']for s,m in before)
            world=[(s,m)for s,m in pairs if s['frame']>=(2449 if region=='pal'else 2455)]
            assert all(s['channels']==m['channels']for s,m in world)
            audio.append(dict(region=region,variant=variant,tempo_frames_exact=len(pairs),menu_music_frames_exact=len(before),
                              first_world_music_frames_exact=len(world),remaining_story_channel_difference_frames=[s['frame']for s,m in pairs if s['channels']!=m['channels']]))
        workspace=base/'candidate08-tests/validation'
        save=load(workspace/'save-compatibility'/('menu08-'+region)/'report.json')
        assert save['passed'] and save['md_sha256']==proven and save['source_crystal_markers_exact']==9
        prefix='md-pal'if region=='pal'else'md'
        route=load(workspace/'natural-dungeon-route'/(prefix+'-menu08-fresh')/'route_report.json')
        assert route['rom_sha256']==proven and route['failure']is None and route['reached_entrance']
        assert not route['ram_injections'] and not route['sram_checkpoint_injection']
        regressions.append(dict(region=region,real_save_continued=True,fresh_dungeon_entry=True,final_health=route['last_state']['health']))
    inventory=load(base/'candidate08-tests/validation/inventory_restore_report.json')
    assert inventory['md_sha256']==proven and len(inventory['cases'])==6
    assert all(all(not a for a in r['static_background_pattern_difference_indices'].values())for r in inventory['cases'])
    sfx=load(base/'candidate08-tests/validation/natural_start_menu_sfx_report.json');assert sfx['md_sha256']==proven
    assert len(sfx['cases'])==4 and all(r['results']['sms']['events']==r['results']['md']['events']for r in sfx['cases'])
    boot=load(base/'candidate09-boot-framebuffers/report.json');assert not boot['passed'] and boot['baseline_sha256']==public
    source=load(base/'candidate09-boot-source-pixels/report.json');assert source['md_sha256']==boot['md_sha256']
    assert sha((latest/'out/release/rom.bin').read_bytes())==boot['md_sha256']
    changes=[]
    for case in source['cases']:
        changes.append(dict(region=case['region'],changed_frames=len(case['frames']),
            pixels_baseline_matches_source=sum(r['baseline_matches_source']for r in case['frames']),
            pixels_candidate_matches_source=sum(r['candidate_matches_source']for r in case['frames']),
            pixels_neither_matches_source=sum(r['neither_matches_source']for r in case['frames'])))
    before=(ROOT/'megadrive/src/main.c').read_bytes().decode();after=(latest/'src/main.c').read_bytes().decode()
    patch=ROOT/'analysis/menu_audio_candidate09_v0316.patch';assert not patch.exists()
    patch.write_bytes(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),
        fromfile='a/megadrive/src/main.c',tofile='b/megadrive/src/main.c')).encode())
    report=ROOT/'analysis/menu_audio_progress_v0316_report.json';assert not report.exists()
    report.write_text(json.dumps(dict(passed=False,promoted=False,release_gate='New source-visible intro raster differences remain to correct.',
        public_md_sha256=public,latest_candidate_md_sha256=boot['md_sha256'],validated_menu_candidate_md_sha256=proven,
        latest_main_source_sha256=sha((latest/'src/main.c').read_bytes()),patch_sha256=sha(patch.read_bytes()),
        native_menu_glyph_cases_passed=210,glyph_logical_audio_bytes_per_frame=400,glyph_frames_per_case=4,
        native_pending_effect_normalization=matrix['normalization'],menu_visual_cases=visual,audio_cases=audio,
        receiving_candidate08_regressions=regressions,inventory_cases=6,start_menu_sfx_cases=4,
        candidate09_intro_frame_comparisons=boot['cases'],changed_source_pixel_comparisons=changes,evidence=refs,
        source_rom_unmodified=True,primary_state_imports_for_new_game_cases=0,
        limits=['Menu proofs are bound to candidate08; they do not automatically certify candidate09.',
                'Candidate08 was rejected by full emitted-frame intro comparison. Candidate09 isolates the menu IRQ callback and reduces the differences to21 NTSC/9 PAL frames, but source comparison still finds degraded pixels.',
                'The raw intro software-map hashes exposed a real emitted-image difference; no gate was relabeled as passed.',
                'Text-beep scheduling, simultaneous input/editing cases, full new-binary campaign, global Z80 refresh/RNG fidelity and physical hardware remain open.'],
        driver_sha256=sha(Path(__file__).read_bytes())),indent=2)+'\n')
    paths=[p for p in base.rglob('*')if p.is_file()]
    tool_names=['analyze_name_map_irq_loss.py','probe_name_controller.py','probe_start_menu_reveal.py',
        'profile_menu_audio_handoffs.py','profile_native_menu_handoffs.py','validate_name_map_candidate.py',
        'summarize_menu_audio_candidate08.py','compare_boot_framebuffers.py','compare_boot_changed_pixels.py',
        'archive_menu_audio_progress_v0316.py','build_private_candidate.ps1','probe_opening_audio_clock.py',
        'validate_inventory_restore.py','run_core.py']
    paths += [ROOT/'tools'/name for name in tool_names]+[report,patch]
    # Keep the current candidate ROM/ELF/object cache live for the next step.
    roots=[p for p in base.iterdir()if p.is_dir()and p.name!='candidate09']
    archive=ROOT/'analysis/menu-audio-progress-v0316'
    manifest=freeze(ROOT,archive,paths,dict(public_md_sha256=public,latest_candidate_md_sha256=boot['md_sha256'],
        scope='Unreleased menu work, all rejected candidates and source comparisons. Candidate09 remains live; other generated files may be removed only after lossless readback.'),roots,cleanup=True)
    removed=manifest['removed_verified_generated'];size=sum(p.stat().st_size for p in archive.rglob('*')if p.is_file())
    assert len(list((ROOT/'versions').glob('v*/*.bin')))==316
    assert sha((ROOT/'gaw-megadrive.bin').read_bytes())==public
    cleanup=ROOT/'analysis/menu_audio_progress_cleanup_v0316_report.json'
    cleanup.write_text(json.dumps(dict(passed=True,public_md_sha256=public,removed_files=len(removed),removed_bytes=sum(r['bytes']for r in removed),
        archive_bytes=size,net_artifact_bytes_freed=sum(r['bytes']for r in removed)-size,
        archive_manifest_sha256=sha((archive/'manifest.json').read_bytes()),numbered_roms_preserved=316,
        current_candidate09_preserved=True,all_archived_objects_readback_verified=True),indent=2)+'\n')
    print('Unreleased menu progress archived; production remains v316.',flush=True)


if __name__=='__main__':main()
