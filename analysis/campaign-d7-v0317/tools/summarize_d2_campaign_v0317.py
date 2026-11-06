"""Audit current v317 D2 controller checkpoints and the unguarded boss."""
import json
from pathlib import Path
from run_core import ROOT
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols
from validate_reward_hud_restore import translated


def main():
    refs={}
    def read(p):
        raw=evidence(p);refs[p.relative_to(ROOT).as_posix()]=sha(raw);return raw
    def load(p):return json.loads(read(p))
    target=ROOT/'analysis/d2_campaign_v0317_report.json';assert not target.exists()
    prior=load(ROOT/'analysis/d2_approach_v0317_report.json')
    digest=sha(read(ROOT/'gaw-megadrive.bin'))
    assert prior['passed'] and prior['dungeon2_entered'] and prior['md_sha256']==digest
    symbol_file=ROOT/'megadrive/out/release/symbol.txt';read(symbol_file);sy=symbols(symbol_file)
    original=read(ROOT/'input/original.sms');kind=original[0x3234e+0x144*8]
    hp=original[0x320ea+(kind-0x20)*4];assert kind==0x63 and hp==30
    previous=ROOT/prior['stages'][-1]['trace'];pc=load(previous/'capture.json')
    pa,pw=recording(previous,pc);stages=[];release=None;fixed=None;combat=None;boss=None
    specs=[('key101',0x160),('key201',0x152),('key301',0x131),('pre-boss01',0x143),
           ('release01',0x143),('boss02',0x144),('exit01',0xd6)]
    for number,(suffix,room) in enumerate(specs):
        folder=ROOT/'validation/natural-dungeon-combat'/('md-auto-v0317-d2-'+suffix)
        c=load(folder/'capture.json');r=load(folder/'report.json');end=c['frames']
        a,w=recording(folder,c);read(folder/'assistance.json')
        assert c['rom_sha256']==digest and c['sram_input'] is None and end>pc['frames']
        assert r['failure'] is None and not r['deaths'] and r['prefix_end']==pc['frames']
        assert r['recorded_new_game_prefix']==previous.name
        assert len(a['episodes'])==2 and a['boss_room']==0x144
        assert not a['boss_assistance'] and not a['primary_state_imports'] and not a['health_refills']
        assert w[:len(pw)]==pw and all(addr==sy['hero_hurt'] for _,addr,_ in w)
        proof=folder.with_name(folder.name+f'-assisted-fixed-replay-{end}')
        q=load(proof/'replay_report.json')
        assert q['passed'] and q['rom_sha256']==digest and q['whole_ram_bytes']==65536
        assert q['final_png_exact'] and not q['feedback_reads']
        for n,h in q['evidence'].items():assert sha(read(folder/n))==h
        for stem,ext in [('ram','bin'),('frame','png')]:
            n=f'{stem}_{end:05d}.{ext}';assert read(folder/n)==read(proof/n)
        raw=read(folder/f'ram_{end:05d}.bin')
        data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k))
        word=lambda n:int.from_bytes(data(n,2),'big')
        assert word('room_id')==room and word('game_state')==12 and not word('sound_unhandled_command')
        assert 0<word('hero_health')<=word('hero_max_health')
        assert word('hero_selected_item')==word('hero_weapon_level')==1 and data('hero_items',17)[1]==1
        assert data('game_save_state',592)[0x1f:0x28]==bytes(([128,128]+[0]*7) if number>=5 else ([128]+[0]*8))
        if number<4:
            assert a['first_boss_entry'] is None and a['release_write_frame'] is None
            if number<3:assert r['new_key_verified'] and word('hero_keys')==[1,2,2][number]
            else:assert r['room_cleared']
        elif number==4:
            release=end;fixed=w
            assert r['passed'] and a['closed_before_room']==0x144 and word('hero_hurt')==0
            assert w==pw+[(end,sy['hero_hurt'],b'\0\0')]
        else:
            assert w==fixed and w[-1][0]==release and word('hero_hurt')<=128
            assert r['unassisted_extension'] and not r['new_assistance_writes'] and not r['primary_state_imports']
            assert r['extension_guard_checks_through_frame']==end
            if number==5:
                combat=r['first_intermediate_combat'];boss=r
                assert combat['room']==0x144 and combat['frame']>release and combat['hurt']==0
                assert combat['actors']==[dict(slot=0,kind=kind,hp=hp)] and r['room_cleared']
                assert r['full_ram_prediction_matches']==r['verified_persistent_prediction_windows']>0
                assert not r['stack_only_difference_windows']
            else:
                assert r['dungeon_exit_verified'] and r['full_dungeon_cleared'] and not word('world_dungeon_number')
                assert not word('item_reward_active') and word('hero_max_health')==48
                sms=data('sms_vram',16384);vram=read(folder/f'vram_{end:05d}.bin')
                regs=read(folder/f'vdp_regs_{end:05d}.bin');base=(regs[2]&56)<<10
                width=[32,64,32,128][regs[16]&3]
                for n in range(128):
                    at=base+((n//32+22)*width+n%32)*2
                    assert int.from_bytes(vram[at:at+2],'little')==translated(int.from_bytes(sms[0x3d00+n*2:0x3d02+n*2],'little'))
                for n in range(2):
                    tile,off=original[0x1edc+n*2:0x1ede+n*2]
                    assert sms[0x3d00+off:0x3d02+off]==bytes([tile,0x59])
        stages.append(dict(trace=folder.relative_to(ROOT).as_posix(),frames=end,room=room,
            health=word('hero_health'),max_health=word('hero_max_health'),keys=word('hero_keys'),
            whole_ram_bytes=65536,final_png_exact=True))
        previous,pc,pa,pw=folder,c,a,w
    rejected=ROOT/'validation/natural-dungeon-combat/md-auto-v0317-d2-boss01'
    failed=load(rejected/'report.json')
    assert failed['failure']=='frame_limit' and not failed['room_cleared']
    assert not failed['last_state']['audio_error'] and not failed['new_assistance_writes']
    result=dict(passed=True,version=317,md_sha256=digest,second_crystal_and_exterior_return=True,
        current_campaign_trace=stages[-1]['trace'],campaign_frames=pc['frames'],stages=stages,
        guard_release_frame=release,first_boss_combat=combat,boss_damage=boss['first_extension_damage'],
        verified_prediction_windows=boss['full_ram_prediction_matches'],primary_state_imports=0,
        resource_writes=0,boss_assistance=False,exit_new_assistance_writes=0,
        physical_hud_words_exact=128,source_crystal_markers_exact=2,full_game_validated=False,
        failed_controller_trials=[dict(trace=rejected.relative_to(ROOT).as_posix(),
            failure=failed['failure'],accepted=False)],
        evidence=refs,driver_sha256=sha(Path(__file__).read_bytes()),
        limits=['Current receiving binary played from New Game. Approach guards end before the second boss; no life, equipment, actor, progression or SRAM imports.',
                'Selected endpoints reproduce complete RAM and PNG on cold fixed replay. This does not prove every framebuffer, source campaign RNG/audio cadence, PAL campaign, optional content or later dungeons.'])
    target.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('V317 second crystal and exterior return audited:',pc['frames'],'frames')


if __name__=='__main__':main()
