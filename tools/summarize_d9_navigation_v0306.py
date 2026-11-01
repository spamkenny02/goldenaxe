"""Audit grouped D9 navigation and ordinary persistent mechanisms before main6C."""
import json
from run_core import ROOT
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols


def main():
    refs={}
    def read(n):
        raw=evidence(ROOT/n);refs[n]=sha(raw);return raw
    def load(n):return json.loads(read(n))
    prior=load('analysis/d9_midboss_v0306_report.json');assert prior['passed'] and prior['first_intermediate_defeated']
    digest=sha(read('versions/v0306-3a12380b/gaw-megadrive-v0306.bin'));assert digest==prior['md_sha256']==sha((ROOT/'gaw-megadrive.bin').read_bytes())
    sy=symbols(ROOT/'megadrive/out/release/symbol.txt');read('megadrive/out/release/symbol.txt')
    index=load('validation/v0306-d9-navigation-sources/source_index.json')
    for n,h in index.items():assert sha(read('validation/v0306-d9-navigation-sources/'+n.split('/')[-1]))==h==sha((ROOT/n).read_bytes())
    original=read('input/original.sms');assert original[0x3234e+0x1ac*8:0x32356+0x1ac*8]==bytes([0x6c]+[0]*7)
    previous=prior['current_campaign_trace'];pc=load(previous+'/capture.json');pa,pw=recording(ROOT/previous,pc);stages=[]
    specs=[('approach-resume01','resume',0x1be),('switch1ad-01','contact',0x1ad),('portal19e-ready01','portal_ready',0x19e),('main-approach01','main_ready',0x1bc)]
    for trial,kind,room in specs:
        root='validation/natural-dungeon-combat/md-auto-v0306-d9-'+trial;c=load(root+'/capture.json');r=load(root+'/report.json');f=c['frames'];proof=root+f'-assisted-fixed-replay-{f}';p=load(proof+'/replay_report.json')
        assert c['rom_sha256']==r['rom_sha256']==p['rom_sha256']==digest and c['sram_input'] is None
        assert r['failure'] is None and not r['deaths'] and r['recorded_new_game_prefix']==previous.split('/')[-1] and r['prefix_end']==pc['frames'] and f>pc['frames']
        assert p['passed'] and p['whole_ram_bytes']==65536 and p['final_png_exact'] and not p['feedback_reads']
        for n,h in p['evidence'].items():assert sha(read(root+'/'+n))==h
        for stem,ext in [('ram','bin'),('frame','png')]:assert read(root+f'/{stem}_{f:05d}.{ext}')==read(proof+f'/{stem}_{f:05d}.{ext}')
        raw=read(root+f'/ram_{f:05d}.bin');data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big')
        a,w=recording(ROOT/root,c);read(root+'/assistance.json');assert len(a['episodes'])==12 and a['boss_room']==0x1ac and all(a[n] is None for n in ['first_boss_entry','release_write_frame','first_boss_combat','first_boss_damage'])
        assert not a['boss_assistance'] and not a['primary_state_imports'] and not a['health_refills'] and all(addr==sy['hero_hurt'] for _,addr,_ in w)
        assert word('room_id')==room and word('game_state')==12 and word('hero_health')>0 and word('hero_max_health')==96 and word('hero_keys')==1
        items=data('hero_items',17);save=data('game_save_state',592);assert items[11]==0 and items[15]==items[16]==1 and save[0x1f:0x28]==bytes([128]*8+[0])
        if kind=='resume':
            assert r['passed'] and r['new_assistance_writes']==1 and r['new_guard_frame']==f and a['resumed_after_verified_intermediate']
            assert w==pw+[(f,sy['hero_hurt'],b'\x00\x81')] and a['episodes'][:-2]==pa['episodes'][:-1]
            assert a['episodes'][-2]['boss_room']==0x1be and a['episodes'][-2]['first_boss_combat']['frame']==250692 and a['episodes'][-2]['release_write_frame']==250496 and a['episodes'][-2]['first_boss_combat']['hurt']==0
            assert a['intermediate_entry_cold_verified'] and a['main_boss_never_entered_in_prefix'] and word('hero_health')==48
            actors=data('world_actor_state',768);assert not any(actors[i*48]==0x79 and actors[i*48+24] for i in range(8))
        else:
            assert save[0x150+0xbe]==0  # Mask commits on leaving BE, not immediately on death.
            assert w[:len(pw)]==pw and a['episodes'][:-1]==pa['episodes'][:-1] and a['preserve_floor_hurt_requested']
            events=load(root+'/events.json');assert not any(e.get('room') in [0x19c,0x1ac] for e in events)
            if kind=='contact':
                assert r['passed'] and r['contact_route_passed'] and r['contact_room']==r['contact_destination']==0x1ad and r['contact_coordinate']==332 and r['contact_state_writes']==0
                assert r['contact_opened']['flags']&4 and save[0x50+0x9d]&0x40 and save[0x50+0x9c]&0x80
                read(root+'/contact_events.json')
            elif kind=='portal_ready':
                assert r['room_cleared'] and r['avoided_portal_rooms']==[0x19e] and data('scratch',4096)[0x848]==0x0c and save[0x50+0x9e]&4
            else:
                assert r['passed'] and r['contact_route_passed'] and r['contact_room']==0x1bd and r['contact_destination']==0x1bc and r['contact_coordinate']==360
                assert r['target_room']==0x1ac and not r['entered_room'] and r['avoided_portal_rooms']==[0x1cc] and r['contact_state_writes']==0
                assert save[0x50+0xbc]&0x20 and save[0x50+0xbc]&4 and save[0x50+0xbd]&4 and data('scratch',4096)[0x817:0x819]==b'\x00\x00'
                assert any(e.get('room')==0x1cc for e in events) and any(e.get('room')==0x1bd for e in events);read(root+'/contact_events.json')
        stages.append(dict(trace=root,kind=kind,frames=f,room=room,health=word('hero_health'),magic=word('hero_magic'),gold=word('hero_gold'),keys=word('hero_keys'),whole_ram_png_exact=True));previous,pc,pa,pw=root,c,a,w
    rejected=load('validation/natural-dungeon-combat/md-auto-v0306-d9-giant-ready01/report.json');assert rejected['failure']=='frame_limit' and rejected['last_state']['room']==0x19d
    assert len(rejected['last_actors'])==4 and all(e['type']==0x62 and e['hp']==0 for e in rejected['last_actors'])
    read('tools/summarize_d9_navigation_v0306.py')
    result=dict(passed=True,version=306,md_sha256=digest,production_rom_unchanged=True,stages=stages,ready_trace=previous,campaign_frames=pc['frames'],main_boss_entered=False,eight_crystals_preserved=True,optional_giant_entered=False,balloon_obtained=False,grouped_portal_and_two_mechanisms=True,full_game_validated=False,evidence=refs,limits=['Approach assistance changes only hero_hurt. No resources,actors,progression or SRAM imports.','The optional19D attempt is not promoted: its four original62 actors have zero HP and cannot be treated as ordinary killable enemies. Main progression returns to the verified19E checkpoint.','The grouped final route crosses the real19E->1CC portal, the BC puzzle and BD contact, then stops in BC before6C. Optional19C/7B and Balloon remain pending.','Latest stack profile remains D8; source RNG,audiovisual fidelity,ending,saves and hardware remain unproven.'])
    (ROOT/'analysis/d9_navigation_v0306_report.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());print('D9 grouped mandatory approach verified:',stages[-1]['health'],'HP; main boss not entered')

if __name__=='__main__':main()
