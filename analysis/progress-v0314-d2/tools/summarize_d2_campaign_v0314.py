"""Audit the selected D2 route, actual boss victory, crystal and exterior return."""
import json
from run_core import ROOT
from archive_lossless_evidence import sha
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols
from validate_reward_hud_restore import translated

SPECS=[('key101',0x160),('key201',0x152),('key301',0x131),('pre-boss01',0x143),
       ('release01',0x143),('boss03',0x144),('crystal01',0x144),('exit01',0xd6)]


def main():
    refs={}
    def read(p):
        raw=p.read_bytes();refs[p.relative_to(ROOT).as_posix()]=sha(raw);return raw
    def load(p):return json.loads(read(p))
    prior=load(ROOT/'analysis/d2_approach_v0314_report.json')
    digest=sha((ROOT/'gaw-megadrive.bin').read_bytes())
    assert prior['passed'] and prior['md_sha256']==digest and prior['dungeon2_entered']
    source=ROOT/'validation/v0314-d2-sources';index=load(source/'source_index.json')
    for name,h in index.items():assert sha(read(source/name.split('/')[-1]))==h
    fast=sha(read(source/'fast_prediction_zero_windows_fix.py'))
    sy=symbols(ROOT/'megadrive/out/release/symbol.txt');original=read(ROOT/'input/original.sms')
    kind=original[0x3234e+0x144*8];hp=original[0x320ea+(kind-0x20)*4]
    assert kind==0x63 and hp==30
    previous=ROOT/prior['stages'][-1]['trace'];pc=load(previous/'capture.json');pa,pw=recording(previous,pc)
    stages=[];fixed=None;release=None;combat=None;boss=None
    for number,(suffix,room) in enumerate(SPECS):
        p=ROOT/'validation/natural-dungeon-combat'/('md-auto-v0314-d2-'+suffix)
        c=load(p/'capture.json');r=load(p/'report.json');f=c['frames'];a,w=recording(p,c)
        assert r['failure'] is None and not r['deaths'] and c['sram_input'] is None
        assert c['rom_sha256']==r['rom_sha256']==digest and r['prefix_end']==pc['frames']
        assert r['recorded_new_game_prefix']==previous.name and f>pc['frames']
        assert len(a['episodes'])==2 and a['boss_room']==0x144
        assert not a['primary_state_imports'] and not a['health_refills'] and not a['boss_assistance']
        assert all(addr==sy['hero_hurt'] and value in (b'\0\0',b'\0\x81')for _,addr,value in w)
        assert w[:len(pw)]==pw
        proof=p.with_name(p.name+'-assisted-fixed-replay-'+str(f));q=load(proof/'replay_report.json')
        assert q['passed'] and q['rom_sha256']==digest and q['whole_ram_bytes']==65536 and q['final_png_exact'] and not q['feedback_reads']
        for name,h in q['evidence'].items():assert sha(read(p/name))==h
        for stem,ext in [('ram','bin'),('frame','png')]:assert read(p/f'{stem}_{f:05d}.{ext}')==read(proof/f'{stem}_{f:05d}.{ext}')
        raw=read(p/f'ram_{f:05d}.bin');data=lambda n,k:bytes(raw[(sy[n]+i)^1]for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big')
        assert word('room_id')==room and word('game_state')==12 and not word('sound_unhandled_command')
        assert word('hero_selected_item')==word('hero_weapon_level')==1 and data('hero_items',17)[1]==1
        assert word('hero_max_health')==(48 if number>=6 else 40) and 0<word('hero_health')<=word('hero_max_health')
        assert data('game_save_state',592)[0x1f:0x28]==bytes(([128,128]+[0]*7) if number>=5 else ([128]+[0]*8))
        if number<4:
            assert a['first_boss_entry'] is None and a['release_write_frame'] is None
            if number<3:assert r['new_key_verified'] and word('hero_keys')==[1,2,2][number]
            else:assert r['room_cleared']
            assert r['driver_sha256']==index['tools/natural_dungeon_combat.py']
        elif number==4:
            release=f;fixed=w
            assert r['passed'] and a['closed_before_room']==0x144 and word('hero_hurt')==0
            assert w==pw+[(f,sy['hero_hurt'],b'\0\0')]
        else:
            assert w==fixed and all(t<=release for t,_,_ in w)
            assert r['unassisted_extension'] and not r['new_assistance_writes'] and not r['primary_state_imports']
            assert r['prediction_video_wrapper_sha256']==fast
            assert r['extension_guard_checks_through_frame']==f and word('hero_hurt')<=128
            if number==5:
                combat=r['first_intermediate_combat'];boss=r
                assert combat['room']==0x144 and combat['frame']>release and combat['hurt']==0 and combat['health']==40
                assert combat['actors']==[dict(slot=0,kind=kind,hp=hp)]
                assert r['room_cleared'] and r['first_extension_damage'] is None and word('hero_health')==40
                assert r['full_ram_prediction_matches']==r['verified_persistent_prediction_windows']>0 and not r['stack_only_difference_windows']
            else:
                assert word('hero_health')==48
                if number==6:assert r['first_extension_damage'] is None
                assert not r['secondary_instances_created'] and not r['secondary_video_suppressed']
                assert 'full_ram_prediction_matches' not in r
                if number==6:assert r['collect_gem_requested'] and not r['last_state']['reward_active']
                else:assert r['dungeon_exit_verified'] and r['full_dungeon_cleared'] and word('world_dungeon_number')==0
        if number>=6:
            sms=data('sms_vram',16384);vram=read(p/f'vram_{f:05d}.bin');regs=read(p/f'vdp_regs_{f:05d}.bin');base=(regs[2]&56)<<10;width=[32,64,32,128][regs[16]&3]
            for n in range(128):
                at=base+((n//32+22)*width+n%32)*2
                assert int.from_bytes(vram[at:at+2],'little')==translated(int.from_bytes(sms[0x3d00+n*2:0x3d02+n*2],'little'))
            for n in range(2):
                tile,off=original[0x1edc+n*2:0x1ede+n*2];assert sms[0x3d00+off:0x3d02+off]==bytes([tile,0x59])
        stages.append(dict(trace=p.relative_to(ROOT).as_posix(),frames=f,room=room,health=word('hero_health'),max_health=word('hero_max_health'),keys=word('hero_keys'),whole_ram_bytes=65536,final_png_exact=True))
        read(p/'controls.json');read(p/'assistance.json');previous,pc,pa,pw=p,c,a,w
    failed=[]
    for suffix in ('boss01','boss02'):
        p=ROOT/'validation/natural-dungeon-combat'/('md-auto-v0314-d2-'+suffix)/'report.json';r=load(p)
        assert r['failure'];failed.append(dict(trace=p.parent.relative_to(ROOT).as_posix(),failure=r['failure'],accepted=False))
    result=dict(passed=True,version=314,md_sha256=digest,second_crystal_and_exterior_return=True,
        current_campaign_trace=stages[-1]['trace'],campaign_frames=pc['frames'],stages=stages,
        guard_release_frame=release,first_boss_combat=combat,boss_damage=None,
        verified_prediction_windows=boss['full_ram_prediction_matches'],first_return_damage=r['first_extension_damage'],primary_state_imports=0,
        resource_writes=0,exit_new_assistance_writes=0,physical_hud_words_exact_each=128,
        source_crystal_markers_exact_each=2,failed_controller_trials=failed,evidence=refs,
        full_game_validated=False,limits=['Actual cold New Game chain. Three real keys, guard released before144, cautious boss combat without damage, real crystal acquisition and return at48/48HP. Failed controller trials are explicitly excluded.',
        'Independent complete RAM/PNG replay at every selected endpoint; no resource, actor, progression or SRAM imports. Whole-source RNG/IRQ, later campaign, optional content and hardware remain open.'])
    (ROOT/'analysis/d2_campaign_v0314_report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('v314 second crystal and exterior return at48/48HP audited; all selected cold replays exact')


if __name__=='__main__':main()
