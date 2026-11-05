"""Audit source D9 mechanisms and an ordinary-damage first intermediate fight."""
import json
from run_core import ROOT
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols


def main():
    refs = {}
    def read(name):
        raw = evidence(ROOT/name); refs[name] = sha(raw); return raw
    def load(name): return json.loads(read(name))
    prior = load('analysis/d9_entry_v0313_report.json')
    assert prior['passed'] and prior['eight_crystals_preserved']
    digest = sha(read('versions/v0313-48fb6e92/gaw-megadrive-v0313.bin'))
    assert digest == prior['md_sha256'] == sha((ROOT/'gaw-megadrive.bin').read_bytes())
    sy = symbols(ROOT/'megadrive/out/release/symbol.txt'); read('megadrive/out/release/symbol.txt')
    index = {'tools/'+k:v for k,v in load('validation/v0313-d9-sources02/entry-tools/source_index.json').items()}
    for name, h in index.items():
        assert sha(read('validation/v0313-d9-sources02/entry-tools/'+name.split('/')[-1])) == h == sha((ROOT/name).read_bytes())
    original = read('input/original.sms')
    assert original[0x3234e+0x1be*8:0x32356+0x1be*8] == bytes([0x79]+[0]*7)
    assert original[0x320ea+(0x79-0x20)*4:0x320ee+(0x79-0x20)*4] == bytes([60,20,4,32])
    selection = dict(stages=[dict(name='md-auto-v0313-d9-'+n,kind=k) for n,k in [('switch1de-02','earth_contact'),('earth1ce-01','earth'),('mini-ready01','ready'),('guard-release01','close'),('midboss01','combat')]])
    previous = prior['current_campaign_trace']; pc = load(previous+'/capture.json'); pa,pw = recording(ROOT/previous,pc)
    stages=[];release=fixed=first=damage=None;predictions=0;hp_drops=[];final_report=None;close_health=None
    for spec in selection['stages']:
        kind=spec['kind']; root='validation/natural-dungeon-combat/'+spec['name']
        c=load(root+'/capture.json');r=load(root+'/report.json');f=c['frames'];proof=root+f'-assisted-fixed-replay-{f}';p=load(proof+'/replay_report.json')
        assert c['rom_sha256']==r['rom_sha256']==p['rom_sha256']==digest and c['sram_input'] is None
        assert p['passed'] and p['whole_ram_bytes']==65536 and p['final_png_exact'] and not p['feedback_reads']
        assert r['recorded_new_game_prefix']==previous.split('/')[-1] and r['prefix_end']==pc['frames'] and not r['deaths'] and f>pc['frames']
        assert r['failure'] is None
        for name,h in p['evidence'].items(): assert sha(read(root+'/'+name))==h
        for stem,ext in [('ram','bin'),('frame','png')]: assert read(root+f'/{stem}_{f:05d}.{ext}')==read(proof+f'/{stem}_{f:05d}.{ext}')
        raw=read(root+f'/ram_{f:05d}.bin');data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big')
        a,w=recording(ROOT/root,c);read(root+'/assistance.json')
        assert len(a['episodes'])==11 and a['boss_room']==0x1ac and not a['first_boss_entry'] and not a['first_boss_combat']
        assert all(addr==sy['hero_hurt'] for _,addr,_ in w) and not a['boss_assistance'] and not a['primary_state_imports'] and not a['health_refills']
        assert word('game_state')==12 and word('hero_health')>0 and word('hero_max_health')==96
        assert data('hero_items',17)[10]==data('hero_items',17)[15]==data('hero_items',17)[16]==1 and data('game_save_state',592)[0x1f:0x28]==bytes([128]*8+[0])
        if kind in ['earth_contact','earth','ready']:
            assert w[:len(pw)]==pw and a['episodes'][:-1]==pa['episodes'][:-1] and a['preserve_floor_hurt_requested'] and release is None
            assert word('room_id')==0x1ce and word('hero_selected_item')==1
            if kind=='earth_contact':
                assert r['passed'] and r['earth_route_passed'] and r['contact_route_passed'] and r['earth_state_writes']==r['contact_state_writes']==0
                assert r['earth_passage_room']==r['contact_room']==0x1de and r['earth_cell']==0x34 and r['contact_coordinate']==332 and r['contact_destination']==0x1ce
                assert r['earth_before']['cell']==0x0b and r['earth_opened']['cell']==0 and r['earth_opened']['flags']&4
                assert r['earth_before']['magic']-r['earth_opened']['magic']==8 and r['earth_controller_sha256']==index['tools/natural_earth_then_contact.py']
                assert r['contact_controller_sha256']==index['tools/natural_contact_passage.py'];read(root+'/earth_events.json');read(root+'/contact_events.json')
            elif kind=='earth':
                assert r['passed'] and r['earth_action_only_requested'] and r['earth_route_passed'] and r['earth_passage_room']==0x1ce and r['earth_cell']==0x56
                assert r['earth_before']['cell']==0x0b and r['earth_opened']['cell']!=0x0b and r['earth_state_writes']==0
                read(root+'/earth_events.json')
            else: assert r['room_cleared']
        elif kind=='close':
            release=r['guard_release_frame'];assert r['passed'] and a['approach_closed_early'] and a['closed_before_room']==0x1be and word('room_id')==0x1ce and word('hero_hurt')==0
            assert w==pw+[(release,sy['hero_hurt'],b'\x00\x00')] and release==f;fixed=w;close_health=word('hero_health')
        else:
            assert kind=='combat' and w==fixed and all(frame<=release for frame,_,_ in w) and r['unassisted_extension'] and r['new_assistance_writes']==0 and word('hero_hurt')<=128
            assert r['unassisted_controller_sha256']==index['tools/unassisted_dungeon_continuation.py'] and r['primary_state_imports']==0 and r['extension_guard_checks_through_frame']==f
            assert r['equip_basic_requested'] and word('hero_selected_item')==0 and word('hero_basic_level')==2 and word('hero_attack')==6
            assert r['full_ram_prediction_matches']==r['verified_persistent_prediction_windows'] and r['stack_only_difference_windows']==0;predictions+=r['full_ram_prediction_matches']
            if first is None:
                first=r['first_intermediate_combat'];assert first['room']==0x1be and first['health']==close_health and first['hurt']==0 and first['actors']==[dict(slot=0,kind=0x79,hp=60)] and release<first['frame']
            if damage is None and r['first_extension_damage']:damage=r['first_extension_damage']
            events=load(root+'/events.json');assert not any(e.get('room')==0x1ac for e in events)
            hp=[e for e in events if 'health' in e]
            hp_drops += [dict(frame=n['frame'],before=b['health'],after=n['health']) for b,n in zip(hp,hp[1:]) if n['health']<b['health']]
        stages.append(dict(trace=root,kind=kind,frames=f,room=word('room_id'),health=word('hero_health'),magic=word('hero_magic'),gold=word('hero_gold'),keys=word('hero_keys'),whole_ram_png_exact=True))
        previous,pc,pa,pw,final_report=root,c,a,w,r
    actors=data('world_actor_state',768);remaining=[actors[i*48+24] for i in range(8) if actors[i*48]==0x79 and actors[i*48+24]]
    won=bool(final_report['room_cleared']);assert won and not remaining and final_report['failure'] is None
    read('tools/summarize_d9_midboss_v0313.py')
    result=dict(passed=True,version=313,md_sha256=digest,production_rom_unchanged=True,stages=stages,current_campaign_trace=previous,campaign_frames=pc['frames'],first_intermediate_defeated=won,remaining_intermediate_hp=remaining,intermediate_assistance=False,guard_release_frame=release,first_intermediate_combat=first,first_extension_damage=damage,observed_health_drops=hp_drops,full_ram_prediction_windows=predictions,eight_crystals_preserved=True,ninth_main_boss_entered=False,ninth_crystal_obtained=False,full_game_validated=False,evidence=refs,limits=['Real Earth input clears the DE rock before the UP mechanism; the current route is verified through actual controls. No actor or resource is edited.','All fight writes are exactly the closed prefix list. No guard is reactivated during the fight; no resources,actors,progression or SRAM are imported.','The second intermediate19C/7B and main1AC/6C remain unentered. The stack bound remains the prior D8 checkpoint; whole-source RNG,audiovisual,ending,saves and hardware remain unproven.'])
    (ROOT/'analysis/d9_midboss_v0313_report.json').write_bytes((json.dumps(result,indent=2)+'\n').encode())
    print('D9 first intermediate gates verified; defeated=',won,'prediction windows=',predictions)

if __name__=='__main__':main()
