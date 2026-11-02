"""Audit real final victory and ending, retaining the explicit synthetic-SRAM scope."""
import json
from run_core import ROOT
from archive_lossless_evidence import sha
from assisted_prefix import recording, prefix_writes
from validate_playable_sprite_limit import symbols


def main():
    digest=sha((ROOT/'gaw-megadrive.bin').read_bytes())
    assert digest=='7270576d6eeb2aee641776a3e364f2f3f320711d70bb91a566d7578161261049'
    sy=symbols(ROOT/'megadrive/out/release/symbol.txt')
    files={};stages=[];reports={};assists={};captures={}
    for name in ['finalboss01','ending02']:
        folder=ROOT/'validation/natural-dungeon-combat'/('md-auto-controlled-v0309-palace-'+name)
        cap=json.loads((folder/'capture.json').read_bytes())
        r=json.loads((folder/'report.json').read_bytes())
        assist,writes=recording(folder,cap)
        assert cap['rom_sha256']==digest and r['rom_sha256']==digest
        assert r['controlled_sram_fixture'] and r['primary_state_imports']==1 and r['natural_campaign_proof'] is False
        assert r['unassisted_extension'] and r['new_assistance_writes']==0 and r['failure'] is None
        assert prefix_writes(folder,cap,True,controlled=True)==writes
        assert writes[-1][0]==assist['release_write_frame']==151245 and writes[-1][2]==b'\0\0'
        assert all(address==sy['hero_hurt'] and value in (b'\0\0',b'\0\x81') for _,address,value in writes)
        replay=folder.with_name(folder.name+'-assisted-fixed-replay-'+str(cap['frames']))
        proof=json.loads((replay/'replay_report.json').read_bytes())
        assert proof['passed'] and proof['whole_ram_bytes']==65536 and proof['final_png_exact']
        assert proof['controlled_sram_fixture'] and proof['primary_state_imports']==1
        for stem,ext in [('ram','bin'),('frame','png')]:
            file=f'{stem}_{cap["frames"]:05d}.{ext}'
            assert (folder/file).read_bytes()==(replay/file).read_bytes()
        raw=(folder/f'ram_{cap["frames"]:05d}.bin').read_bytes()
        data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k))
        assert data('game_save_state',592)[0x28]==1
        assert int.from_bytes(data('hero_health',2),'big')>0
        if name=='ending02':
            assert data('title_phase',1)!=b'\0' or int.from_bytes(data('intro_running',2),'big')!=0
        reports[name],assists[name],captures[name]=r,assist,cap
        stages.append(dict(trace=folder.relative_to(ROOT).as_posix(),frames=cap['frames'],
                           state=r['last_state'],whole_ram_png_exact=True,extra_state_writes=0))
        for path in [folder/'capture.json',folder/'controls.json',folder/'assistance.json',folder/'report.json',
                     folder/f'ram_{cap["frames"]:05d}.bin',folder/f'frame_{cap["frames"]:05d}.png',replay/'replay_report.json']:
            files[path.relative_to(ROOT).as_posix()]=sha(path.read_bytes())
    fight=reports['finalboss01'];ending=reports['ending02']
    assert fight['ending_handoff_passed'] and fight['ending_handoff']['game']==14
    assert fight['ending_handoff']['health']==48 and fight['ending_handoff']['final_dungeon_defeated']
    combat=fight['first_intermediate_combat']
    assert combat['frame']==151328 and combat['health']==100 and combat['hurt']==0
    assert any(e['kind']==0x6d and e['hp']==90 for e in combat['actors'])
    assert fight['verified_persistent_prediction_windows']==fight['full_ram_prediction_matches']==114
    assert fight['stack_only_difference_windows']==0
    assert fight['extension_guard_checks_through_frame']==captures['finalboss01']['frames']
    assert ending['ending_complete'] and ending['last_state']['game']==0
    assert ending['last_state']['descriptor']==0 and ending['last_state']['credits_done']
    assert ending['nine_gems_visible_frame']<ending['credits_started_frame']<ending['credits_finished_frame']<ending['acknowledgement_frame']<=ending['title_flow_return_frame']
    assert ending['credits_finished_frame']-ending['credits_started_frame']>=7000
    assert assists['finalboss01']['writes']==assists['ending02']['writes']
    for file in ['tools/summarize_controlled_palace_ending_v0309.py','tools/continue_recorded_ending.py',
                 'analysis/controlled_palace_phase3_v0309_report.json','megadrive/src/main.c',
                 'megadrive/src/ending.inc','megadrive/src/ending_credits.inc']:
        files[file]=sha((ROOT/file).read_bytes())
    report=dict(passed=True,version=309,md_sha256=digest,controlled_sram_fixture=True,
                game_written_save=False,natural_campaign_proof=False,full_game_validated=False,
                primary_state_imports=1,new_health_inventory_progression_writes=0,
                final_boss_assistance=False,guard_release_frame=151245,first_final_combat=combat,
                final_victory=fight['ending_handoff'],prediction_windows_exact=114,
                ending_complete=True,nine_gems_visible_frame=ending['nine_gems_visible_frame'],
                credits_started_frame=ending['credits_started_frame'],credits_finished_frame=ending['credits_finished_frame'],
                title_flow_return_frame=ending['title_flow_return_frame'],music_requests=ending['music_requests'],
                stages=stages,evidence=files,
                limits=['One synthetic Continue SRAM record derived from actual v306 nine-crystal RAM; not a current-ROM campaign from New Game.',
                        'All palace combat and mechanisms after that initialization execute in the game. Approach hurt guards are explicitly logged and removed before both intermediates and final boss.',
                        'No RAM/state writes after151245. The full recorded final fight and ending replay from boot with exact final65536RAM and PNG.',
                        'Ending completion and return to title flow are proven here, not global SMS framebuffer/audio/timing equivalence or hardware compatibility.',
                        'Current cold campaign beyond its two crystals,optional content and global source fidelity remain open.'])
    (ROOT/'analysis/controlled_palace_ending_v0309_report.json').write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'))
    print('Actual final victory and complete ending verified in controlled palace scope')


if __name__=='__main__':
    main()
