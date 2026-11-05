"""Audit a fresh game on candidate08; the rejected historical route stays rejected."""
import json
from run_core import ROOT
from archive_lossless_evidence import sha
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols
from validate_reward_hud_restore import translated


def main():
    project=ROOT/'validation/intro-audio-v0313/candidate08'
    refs={}
    def read(p):
        raw=p.read_bytes();refs[p.relative_to(ROOT).as_posix()]=sha(raw);return raw
    def load(p):return json.loads(read(p))
    digest=sha(read(project/'gaw-megadrive.bin'))
    audio=load(ROOT/'analysis/intro_audio_candidate08_v0313_report.json')
    assert audio['passed'] and audio['md_sha256']==digest and not audio['candidate_promoted']
    sy=symbols(project/'megadrive/out/release/symbol.txt');read(project/'megadrive/out/release/symbol.txt')
    specs=[('natural-dungeon-route','md-audio08-fresh-d1-entry01','entry',0x1e4),
        ('natural-dungeon-combat','md-auto-audio08-fresh-d1-key01','key1',0x1e5),
        ('natural-dungeon-combat','md-auto-audio08-fresh-d1-ready01','approach1',0x185),
        ('natural-dungeon-combat','md-auto-audio08-fresh-d1-second-key01','key2',0x193),
        ('natural-dungeon-combat','md-auto-audio08-fresh-d1-ready02','approach2',0x185),
        ('natural-dungeon-combat','md-auto-audio08-fresh-d1-release02','release',0x185),
        ('natural-dungeon-combat','md-auto-audio08-fresh-d1-boss02','boss',0x175),
        ('natural-dungeon-combat','md-auto-audio08-fresh-d1-exit01','exit',0xb9)]
    previous=None;old_cap=None;old_writes=[];release=None;fixed=None;stages=[];reports={}
    for family,name,kind,room in specs:
        folder=project/'validation'/family/name
        cap=load(folder/'capture.json');r=load(folder/('route_report.json' if kind=='entry' else 'report.json'))
        f=cap['frames'];assert cap['rom_sha256']==r['rom_sha256']==digest and cap['sram_input'] is None
        assert r['failure'] is None and not r.get('deaths',r.get('normal_continues',0))
        proof_folder=folder.with_name(name+('-fixed-replay' if kind=='entry' else f'-assisted-fixed-replay-{f}'))
        proof=load(proof_folder/'replay_report.json')
        assert proof['passed'] and proof['whole_ram_bytes']==65536 and proof['final_png_exact'] and not proof['feedback_reads']
        assert proof['rom_sha256']==digest
        for n,h in proof['evidence'].items():assert sha(read(folder/n))==h
        for stem,ext in [('ram','bin'),('frame','png')]:
            assert read(folder/f'{stem}_{f:05d}.{ext}')==read(proof_folder/f'{stem}_{f:05d}.{ext}')
        if kind=='entry':
            assert not cap['test_ram_writes'] and r['reached_entrance'] and r['directional_probe_succeeded']
            writes=[]
        else:
            a,writes=recording(folder,cap);read(folder/'assistance.json')
            assert not a['primary_state_imports'] and not a['health_refills'] and not a['boss_assistance']
            assert len(a['episodes'])==1 and a['boss_room']==0x175
            assert all(address==sy['hero_hurt'] for _,address,_ in writes)
            assert writes[:len(old_writes)]==old_writes
            assert r['recorded_new_game_prefix']==previous.name and r['prefix_end']==old_cap['frames']
            if kind=='release':
                release=f;fixed=writes
                assert a['closed_before_room']==0x175 and writes==old_writes+[(f,sy['hero_hurt'],b'\0\0')]
            elif kind in ('boss','exit'):
                assert writes==fixed and all(t<=release for t,_,_ in writes)
                assert r['unassisted_extension'] and not r['new_assistance_writes'] and not r['primary_state_imports']
                assert r['extension_guard_checks_through_frame']==f and r['guard_release_frame']==release
                assert r['full_ram_prediction_matches']==r['verified_persistent_prediction_windows']
                assert not r['stack_only_difference_windows']
        raw=read(folder/f'ram_{f:05d}.bin')
        def data(n,k):return bytes(raw[(sy[n]+i)^1] for i in range(k))
        def word(n):return int.from_bytes(data(n,2),'big')
        assert word('room_id')==room and word('game_state')==12 and word('hero_health')>0
        assert not word('sound_unhandled_command') and data('hero_items',17)==bytes(17)
        if kind in ('key1','key2'):assert r['new_key_verified'] and word('hero_keys')==1
        if kind=='approach2':assert r['room_cleared'] and word('hero_keys')==1
        if kind=='release':assert word('hero_hurt')==0 and word('hero_keys')==1
        if kind in ('boss','exit'):
            assert data('game_save_state',592)[0x1f:0x28]==bytes([128]+[0]*8)
            assert word('hero_max_health')==32 and word('hero_hurt')<=128
            sms=data('sms_vram',16384);vram=read(folder/f'vram_{f:05d}.bin')
            regs=read(folder/f'vdp_regs_{f:05d}.bin');base=(regs[2]&56)<<10;width=[32,64,32,128][regs[16]&3]
            for n in range(128):
                at=base+((n//32+22)*width+n%32)*2
                assert int.from_bytes(vram[at:at+2],'little')==translated(int.from_bytes(sms[0x3d00+n*2:0x3d02+n*2],'little'))
            original=read(ROOT/'input/original.sms');tile,off=original[0x1edc:0x1ede]
            assert sms[0x3d00+off:0x3d02+off]==bytes([tile,0x59])
        if kind=='boss':assert r['room_cleared'] and word('hero_health')==32
        if kind=='exit':assert r['full_dungeon_cleared'] and r['dungeon_exit_verified'] and not word('world_dungeon_number')
        stages.append(dict(trace=folder.relative_to(ROOT).as_posix(),kind=kind,frames=f,room=room,
                           health=word('hero_health'),magic=word('hero_magic'),keys=word('hero_keys'),whole_ram_png_exact=True))
        previous,old_cap,old_writes=folder,cap,writes;reports[kind]=r
    first=reports['boss']['first_intermediate_combat']
    assert release<first['frame'] and first['room']==0x175 and first['hurt']==0 and first['health']==18
    result=dict(passed=True,md_sha256=digest,public_md_sha256=audio['public_md_sha256'],candidate_promoted=False,
        fresh_game_first_crystal_and_exterior_return=True,stages=stages,
        current_campaign_trace=stages[-1]['trace'],campaign_frames=old_cap['frames'],
        guard_release_frame=release,first_boss_combat=first,boss_first_damage=reports['boss']['first_extension_damage'],
        boss_prediction_windows=reports['boss']['full_ram_prediction_matches'],
        return_prediction_windows=reports['exit']['full_ram_prediction_matches'],
        primary_state_imports=0,health_or_inventory_imports=0,full_game_validated=False,evidence=refs,
        limits=['Fresh recorded controls,not the rejected historical fixed recording. Eight independent cold RAM/image endpoints. No source game state or SRAM is imported.',
                'Only explicitly logged approach hurt guards are used. Release occurs before175; no new writes during the boss or exterior return. Two keys are obtained through normal input.',
                'This proves the first crystal on the candidate. Later campaign,save/global audiovisual/R/IRQ/hardware fidelity are outside this proof.'])
    (ROOT/'analysis/intro_audio_fresh_d1_v0313_report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('Candidate08 fresh first crystal and exterior return verified; frames',old_cap['frames'])


if __name__=='__main__':main()
