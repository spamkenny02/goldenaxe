"""Verify actual last-palace mechanisms and the guard release before Death Adder."""
import json
from run_core import ROOT
from archive_lossless_evidence import sha
from assisted_prefix import recording, prefix_writes
from validate_playable_sprite_limit import symbols

CASES = [
    ('switch17c02','live12D navigation checkpoint; southern route unavailable'),
    ('switch17c03','live12C navigation checkpoint; northern compartment unavailable'),
    ('switch17c04','backtracking completed; portal13E still blocked'),
    ('earth13e01','actual Earth cast opens13E portal; arrival16A'),
    ('switch17c05','16A combat clears barrier; remote17C switch opens17B portal'),
    ('portal13c01','live17B checkpoint; portal inaccessible from eastern compartment'),
    ('portal13c02','southern loop and actual17B->13C portal'),
    ('switch14b01','right flame activates14B persistent transformation'),
    ('portal15a02','northern loop and actual14B->15A portal'),
    ('pre-final01','live15B checkpoint; southern passage still requires Earth'),
    ('earth15b01','actual Earth cast opens15B southern passage'),
    ('pre-final02','live16C western compartment; eastern portal inaccessible'),
    ('switch16c01','northern16C switch opens the final approach'),
    ('pre-final03','15C cleared; northern doorway leads to14C'),
    ('final-release01','neutral frame removes guard before14C entry'),
]


def main():
    digest=sha((ROOT/'gaw-megadrive.bin').read_bytes())
    assert digest=='7270576d6eeb2aee641776a3e364f2f3f320711d70bb91a566d7578161261049'
    sy=symbols(ROOT/'megadrive/out/release/symbol.txt')
    files={};stages=[];reports={};assists={};raws={}
    for name,scope in CASES:
        folder=ROOT/'validation/natural-dungeon-combat'/('md-auto-controlled-v0309-palace-'+name)
        cap=json.loads((folder/'capture.json').read_bytes())
        report=json.loads((folder/'report.json').read_bytes())
        assist,writes=recording(folder,cap)
        assert cap['rom_sha256']==digest and cap['sram_input']
        assert report['controlled_sram_fixture'] and report['natural_campaign_proof'] is False
        assert report['primary_state_imports']==1
        assert all(address==sy['hero_hurt'] and value in (b'\0\0',b'\0\x81') for _,address,value in writes)
        assert prefix_writes(folder,cap,True,controlled=True)==writes
        assert assist['boss_room']==0x14c and assist['first_boss_entry'] is None and assist['first_boss_combat'] is None
        replay=folder.with_name(folder.name+'-assisted-fixed-replay-'+str(cap['frames']))
        proof=json.loads((replay/'replay_report.json').read_bytes())
        assert proof['passed'] and proof['whole_ram_bytes']==65536 and proof['final_png_exact']
        assert proof['controlled_sram_fixture'] and proof['primary_state_imports']==1
        for stem,ext in [('ram','bin'),('frame','png')]:
            file=f'{stem}_{cap["frames"]:05d}.{ext}'
            assert (folder/file).read_bytes()==(replay/file).read_bytes()
        reports[name],assists[name]=report,assist
        raws[name]=(folder/f'ram_{cap["frames"]:05d}.bin').read_bytes()
        stages.append(dict(trace=folder.relative_to(ROOT).as_posix(),scope=scope,frames=cap['frames'],
                           state=report['last_state'],failure=report['failure'],whole_ram_png_exact=True))
        for path in [folder/'capture.json',folder/'controls.json',folder/'assistance.json',folder/'report.json',
                     folder/f'ram_{cap["frames"]:05d}.bin',folder/f'frame_{cap["frames"]:05d}.png',replay/'replay_report.json']:
            files[path.relative_to(ROOT).as_posix()]=sha(path.read_bytes())
    earth=reports['earth13e01']
    assert earth['earth_route_passed'] and earth['earth_passage_opened'] and earth['earth_cell']==0x3a
    assert earth['earth_before']['magic']==72 and earth['last_state']['magic']==64
    assert earth['last_state']['room']==0x16a
    switch=reports['switch17c05']
    assert switch['contact_route_passed'] and switch['contact_remote_room']==0x17b
    assert switch['contact_opened']['remote_flags']&4
    assert reports['switch14b01']['contact_route_passed'] and reports['switch14b01']['last_state']['room_flags']&4
    assert reports['earth15b01']['earth_route_passed'] and reports['earth15b01']['earth_passage_opened']
    assert reports['switch16c01']['contact_route_passed'] and reports['switch16c01']['last_state']['room_flags']&0x20
    for name,room in [('portal13c02',0x13c),('portal15a02',0x15a),('pre-final03',0x15c)]:
        r=reports[name]
        assert r['failure'] is None and r['room_cleared'] and not r['deaths'] and not r['last_actors']
        assert r['last_state']['room']==room
    ready=reports['pre-final03']['last_state'];released=reports['final-release01']['last_state']
    assert ready['health']==released['health']>0 and ready['magic']==released['magic']
    assert ready['weapon']==2 and ready['selected']==1 and released['hurt']==0
    assert assists['final-release01']['closed_before_room']==0x14c
    assert stages[-1]['frames']==stages[-2]['frames']+1
    assert max(w['frame'] for w in assists['final-release01']['writes'])==stages[-1]['frames']
    for file in ['tools/summarize_controlled_palace_phase3_v0309.py','tools/inspect_recorded_dungeon_room.py',
                 'analysis/controlled_palace_phase2_v0309_report.json','megadrive/src/main.c']:
        files[file]=sha((ROOT/file).read_bytes())
    result=dict(passed=True,version=309,md_sha256=digest,controlled_sram_fixture=True,
                game_written_save=False,natural_campaign_proof=False,full_game_validated=False,
                primary_state_imports=1,post_boot_health_inventory_progression_writes=0,
                final_boss_entered=False,final_guard_release_frame=stages[-1]['frames'],
                latest_trace=stages[-1]['trace'],stages=stages,evidence=files,
                limits=['Synthetic Continue fixture from actual v306 nine-crystal RAM; not a current New Game campaign.',
                        'Incomplete controller checkpoints are identified explicitly. Successful later stages execute real movement and mechanisms.',
                        'The rejected Earth16A attempt stopped on its initial-cell assertion before any new action: that barrier is removed by the source room-clear script, not Earth.',
                        'Final fight, ending, current full cold campaign and global source fidelity remain unproven by this phase.'])
    (ROOT/'analysis/controlled_palace_phase3_v0309_report.json').write_bytes((json.dumps(result,indent=2)+'\n').encode('utf-8'))
    print('Palace phase3 verified:',len(stages),'exact replays; actual final approach and guard release')


if __name__=='__main__':
    main()
