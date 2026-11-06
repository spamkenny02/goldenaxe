"""Bind the native menu correction to measured SMS scenes and receiving-build checks."""
import json
from pathlib import Path

from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from run_core import ROOT


def main():
    base=ROOT/'validation/menu-audio-v0316';project=base/'candidate08';workspace=base/'candidate08-tests'
    digest=sha((project/'out/release/rom.bin').read_bytes());refs={}
    def load(path):
        refs[path.relative_to(ROOT).as_posix()]=sha(path.read_bytes())
        return json.loads(path.read_bytes())
    matrix=load(base/'candidate08-name-matrix/report.json')
    model=load(base/'name-map-model02/report.json')
    assert matrix['passed'] and matrix['md_sha256']==digest and len(matrix['cases'])==210
    assert matrix['source_report_sha256']==sha((base/'name-map-model02/report.json').read_bytes())
    assert model['correct_unambiguous_cases']==210 and not model['ram_writes']
    cases=[];tempo_frames=0;menu_music_frames=0
    for region in ('ntsc','pal'):
      for variant in ('default','early-menu','early-new','late-new'):
        folder=base/('candidate08-'+variant+'-'+region);probe=load(folder/'report.json');assert probe['rom_sha256']==digest
        rows={tag:json.loads((folder/tag/'observations.json').read_bytes())for tag in ('sms','md')}
        starts={tag:next(r['frame']for r in data if r['frame']>=int(probe['input_acks']['920']) and r['tempo'][1]==5)for tag,data in rows.items()}
        assert starts['sms']==starts['md']
        first=starts['sms'];pairs=[(a,b)for a,b in zip(rows['sms'],rows['md'])if a['frame']>=first]
        assert all(a['tempo']==b['tempo']for a,b in pairs),(region,variant,'tempo')
        before_story=[(a,b)for a,b in pairs if a['frame']<=1489]
        assert all(a['channels']==b['channels']for a,b in before_story),(region,variant,'menu music')
        world=[(a,b)for a,b in pairs if a['frame']>=(2449 if region=='pal'else 2455)]
        assert all(a['channels']==b['channels']for a,b in world),(region,variant,'world music')
        differences=[a['frame']for a,b in pairs if a['channels']!=b['channels']]
        tempo_frames+=len(pairs);menu_music_frames+=len(before_story)
        cases.append(dict(region=region,variant=variant,input_acks=probe['input_acks'],first_tempo5_frame=first,
                          tempo_frames_exact=len(pairs),menu_music_frames_exact=len(before_story),world_music_frames_exact=len(world),
                          remaining_music_channel_difference_frames=differences))
    visual=[];controller=[];regressions=[];world_cases=[]
    for region in ('ntsc','pal'):
        video=load(base/('candidate08-video-'+region)/'report.json');assert video['md_sha256']==digest
        checked=[row for row in video['pixel_differences']if row['frame']>=938]
        assert len(checked)==135 and all(not row['pixels']for row in checked)
        visual.append(dict(region=region,normalized_menu_frames_exact=58,normalized_name_frames_exact=77,
                           unclaimed_earlier_frames=[row for row in video['pixel_differences']if row['frame']<938 and row['pixels']]))
        # Controller observations are collected independently of rendering.
        # Reuse the source/native reader directly on this exact binary below.
        ctl=load(base/('candidate08-controller-'+region)/'report.json')
        assert ctl['md_sha256']==digest and not ctl['differences'];controller.append(dict(region=region,frames_exact=351))
        boot=workspace/'validation'/('boot-md-'+region)
        prior=ROOT/'validation/opening-return-v0315/candidate06-tests/validation'/('boot-md-'+region)
        boot_report=load(boot/'observations.json');assert boot_report['rom_sha256']==digest
        for name in ('audio_channels.bin','audio_tempo.bin','audio_psg.bin'):
            assert (boot/name).read_bytes()==evidence(prior/name),(region,name)
        old=json.loads(evidence(prior/'observations.json'));assert boot_report['maps']==old['maps']
        frames=[20,62,5952,6031]if region=='pal'else[23,69,5959,6045]
        for frame in frames:assert (boot/f'frame_{frame:05d}.png').read_bytes()==evidence(prior/f'frame_{frame:05d}.png')
        save=load(workspace/'validation/save-compatibility'/('menu08-'+region)/'report.json')
        assert save['passed'] and save['md_sha256']==digest and save['source_crystal_markers_exact']==9
        assert save['movement_frame']>save['ready_frame']
        prefix='md-pal'if region=='pal'else'md'
        route=load(workspace/'validation/natural-dungeon-route'/(prefix+'-menu08-fresh')/'route_report.json')
        assert route['rom_sha256']==digest and route['failure']is None and route['reached_entrance'] and route['directional_probe_succeeded']
        assert not route['ram_injections'] and not route['sram_checkpoint_injection'] and route['last_state']['room']==0x1e4
        regressions.append(dict(region=region,boot_audio_frames_unchanged=6500,boot_streams_exact=3,boot_pngs_exact=4,
                                real_nine_crystal_save_continued=True,save_ready=save['ready_frame'],save_movement=save['movement_frame'],
                                fresh_dungeon_entry_frame=route['first_controllable_frame'],route_final_health=route['last_state']['health']))
        for ack in (2400,2480):
            folder=base/('candidate08-world-'+region+'-'+str(ack));world_report=load(folder/'report.json')
            assert world_report['results']['md']['rom_sha256']==digest
            ready=world_report['results']['sms']['first_hero_ready'];assert ready==world_report['results']['md']['first_hero_ready']
            rows={tag:{row['frame']:row for row in json.loads((folder/tag/'observations.json').read_bytes())}for tag in ('sms','md')}
            assert all(rows['sms'][f]['occupancy_hex']==rows['md'][f]['occupancy_hex']for f in range(ready-31,ready+1))
            world_cases.append(dict(region=region,last_ack=ack,hero_ready_frame=ready,occupancy_frames_exact=32))
    inventory=load(workspace/'validation/inventory_restore_report.json');assert inventory['md_sha256']==digest and len(inventory['cases'])==6
    assert all(all(not values for values in row['static_background_pattern_difference_indices'].values())for row in inventory['cases'])
    sfx=load(workspace/'validation/natural_start_menu_sfx_report.json');assert sfx['md_sha256']==digest and len(sfx['cases'])==4
    for case in sfx['cases']:
        assert case['results']['sms']['events']==case['results']['md']['events']
        assert case['results']['sms']['audible_effects'] and case['results']['md']['audible_effects']
    proof=dict(passed=True,candidate_promoted=False,md_sha256=digest,
               public_md_sha256=sha((ROOT/'gaw-megadrive.bin').read_bytes()),changed_native_sources=['main.c'],
               main_source_sha256=sha((project/'src/main.c').read_bytes()),source_irq_loss_predictions_exact=210,
               natural_glyph_cases_exact=210,logical_audio_bytes_per_glyph_frame=400,glyph_frames_per_case=4,
               pending_effect_normalization=matrix['normalization'],menu_tempo_frames_exact=tempo_frames,
               menu_music_frames_exact=menu_music_frames,audio_cases=cases,visual_cases=visual,
               name_controller_cases=controller,start_menu_sfx_cases=4,receiving_build_regressions=regressions,
               first_world_cases=world_cases,inventory_cases=6,evidence=refs,
               core_sha256=sha((ROOT.parents[1]/'work/libretro/genesis_plus_gx_libretro.dll').read_bytes()),
               sfx_core_sha256=sha((ROOT/'validation/work/genesis-plus-gx/genesis_plus_gx_libretro.dll').read_bytes()),
               complete_campaign_on_this_binary=False,driver_sha256=sha(Path(__file__).read_bytes()),
               limits=['Restores14ED/110E/1178/1524 menu/name transitions, masked map IRQ handling, source24/8 autorepeat, delayed SAT and silent successful name acceptance.',
                       'The glyph matrix compares400 logical audio bytes with the actual native pending effect mapped to source DE08; raw byte differences and queue values are retained. No arbitrary byte masking.',
                       'The eight startup traces establish tempo phase and the stated menu/world music windows. Text-beep scheduling still produces the explicitly listed channel differences during the story.',
                       'Some NTSC frames before938 on the intro-skip/title-closing path differ. The full no-input6500-frame intro regression is a distinct check.',
                       'The first-glyph matrix does not prove simultaneous direction/typing, every button combination or all saved-name editing sequences.',
                       'A full v315 campaign exists; a full campaign on this new binary, global Z80 refresh/RNG equivalence and physical hardware remain unproven.'])
    target=ROOT/'analysis/menu_audio_candidate08_v0316_report.json';assert not target.exists();target.write_text(json.dumps(proof,indent=2)+'\n')
    print('Menu candidate08 verified:',digest,'tempo frames',tempo_frames,'menu music frames',menu_music_frames,'visual frames270; glyph cases210.',flush=True)


if __name__=='__main__':main()
