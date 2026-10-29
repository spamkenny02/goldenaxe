"""D5 boots and supply exit on v304, plus bounded SMS movement comparisons."""
import json
from run_core import ROOT
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols


def main():
    refs={}
    def read(name):
        raw=evidence(ROOT/name);refs[name]=sha(raw);return raw
    def load(name):return json.loads(read(name))
    digest=sha(read('versions/v0304-b7b4e150/gaw-megadrive-v0304.bin'))
    prior=load('analysis/d4_campaign_v0304_report.json')
    assert prior['passed'] and prior['md_sha256']==digest and prior['fourth_crystal_and_exterior_exit']
    sources=load('analysis/d5_progress_v0304_source_index.json')
    inherited=load(sources['inherited_source_index'])
    for item in list(inherited['sources'].values())+list(sources['sources'].values()):
        assert sha(read(item['path']))==item['sha256']
    symbol_file='validation/stack-v0304-d4-all/symbol.txt';sy=symbols(ROOT/symbol_file);read(symbol_file)
    stages=[];previous=86158
    specifications=[('natural-dungeon-route/md-v0304-d5-entry01',91661,0x186,62,0,48,0),
                    ('natural-dungeon-combat/md-auto-v0304-d5-key01',92664,0x176,62,1,48,0),
                    ('natural-dungeon-combat/md-auto-v0304-d5-earth01',93117,0x166,62,1,40,0),
                    ('natural-dungeon-combat/md-auto-v0304-d5-boots01',95655,0x157,50,0,40,1),
                    ('natural-dungeon-combat/md-auto-v0304-d5-supply-exit01',96329,0x49,50,0,40,1)]
    for trace,frame,room,hp,keys,magic,boots in specifications:
        root='validation/'+trace;c=load(root+'/capture.json')
        world=trace.startswith('natural-dungeon-route/')
        r=load(root+('/route_report.json' if world else '/report.json'))
        proof_root=root+f'-assisted-fixed-replay-{frame}'
        p=load(proof_root+'/replay_report.json')
        assert c['frames']==frame and c['rom_sha256']==p['rom_sha256']==digest and c['sram_input'] is None
        assert r['prefix_end']==previous and r['failure'] is None
        previous=frame
        assert p['passed'] and p['whole_ram_bytes']==65536 and p['final_png_exact'] and not p['feedback_reads']
        for name,h in p['evidence'].items():assert sha(read(root+'/'+name))==h
        assist,writes=recording(ROOT/root,c);read(root+'/assistance.json')
        assert assist['boss_room']==0x163 and assist['activation_after_frame']==86158 and len(assist['episodes'])==5
        assert assist['first_boss_entry'] is None and assist['first_boss_combat'] is None and not assist['boss_assistance']
        assert not assist['primary_state_imports'] and not assist['health_refills'] and not assist['rom_modifications']
        assert all(address==sy['hero_hurt'] for _,address,_ in writes)
        for stem,ext in [('ram','bin'),('frame','png')]:
            filename=f'/{stem}_{frame:05d}.{ext}';assert read(root+filename)==read(proof_root+filename)
        raw=read(root+f'/ram_{frame:05d}.bin')
        data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k))
        word=lambda n:int.from_bytes(data(n,2),'big')
        assert word('room_id')==room and word('hero_health')==hp and word('hero_max_health')==64
        assert word('hero_keys')==keys and word('hero_magic')==magic and not word('sound_unhandled_command')
        assert data('hero_items',17)[12:14]==bytes([1,1]) and data('hero_items',17)[14]==boots
        assert word('hero_attack_speed')==boots
        assert data('game_save_state',592)[0x1f:0x28]==bytes([128]*4+[0]*5)
        if world:
            assert r['reached_entrance'] and r['canoe_acquired_in_prefix'] and not r['normal_continues']
        else:assert not r['deaths']
        if trace.endswith('key01'):assert r['new_key_verified'] and r['room_cleared']
        if trace.endswith('earth01'):
            assert r['earth_route_passed'] and r['earth_passage_traversed'] and not r['earth_state_writes']
            assert r['earth_passage_room']==0x176 and r['earth_cell']==0x4a
            assert r['earth_before']['magic']-r['earth_opened']['magic']==8
        if trace.endswith('boots01'):
            assert r['room_cleared'] and r['collect_item_requested']==14 and r['last_state']['item_value']==1
        if trace.endswith('supply-exit01'):
            assert r['dungeon_exit_verified'] and r['exit_before_crystal_requested'] and not r['full_dungeon_cleared']
            assert r['last_state']['completed_dungeon_progress']==0 and word('world_dungeon_number')==0
            assert word('hero_gold')==22
        stages.append(dict(trace=root,frames=frame,room=room,health=hp,max_health=64,keys=keys,magic=magic,
                           boots_owned=bool(boots),speed_selector=boots,whole_ram_png_exact=True))
    bench=load('analysis/terrain_walk_v0304_game_report.json')
    sms_digest=sha(read('input/original.sms'))
    assert bench['passed'] and bench['md_sha256']==digest and bench['source_sha256']==sms_digest and bench['controlled_fixture']
    assert len(bench['cases'])==48 and len(bench['results'])==2
    regions=[]
    for result in bench['results']:
        assert not result['differences'] and result['cases']==48 and result['frames']==1536
        region=result['region'];observations={}
        for tag in ['sms','md']:
            root=f'validation/terrain-walk-v0304-01/{region}-{tag}'
            c=load(root+'/capture.json')
            assert c['rom_sha256']==(sms_digest if tag=='sms' else digest) and c['test_ram_writes']
            observations[tag]=load(root+'/observations.json')
            assert len(observations[tag])==1536
        assert observations['sms']==observations['md']
        regions.append(region)
    assert set(regions)=={'auto','pal'}
    read('tools/summarize_d5_progress_v0304.py')
    result=dict(passed=True,version=304,md_sha256=digest,production_rom_unchanged=True,stages=stages,
                boots_acquired=True,actual_acquired_speed_selector=1,four_crystals_retained=True,
                supply_exit_verified=True,exit_room=0x49,exit_health=50,gold=22,keys=0,
                fifth_boss_entered=False,fifth_crystal_validated=False,full_game_validated=False,
                movement_comparison=dict(controlled_fixture=True,regions=regions,cases=96,frames=3072,differences=0,
                                         fields=['y_fixed8_8','x_fixed8_8','direction','animation','walking_counter',
                                                 'dy_fixed8_8','dx_fixed8_8','terrain_context']),
                evidence=refs,limits=[
                    'Five current native stages have independent fixed-input cold RAM/PNG replays. Logged approach protection is restricted to hero_hurt. No position,equipment,keys,currency,health or progression fixtures enter this campaign.',
                    'The supply exit precedes the fifth crystal; it is not a completed dungeon. The current exterior49 prefix retains boots,canoe,rope,four crystals,50/64HP and22 gold. Boss5 and its return remain unproved.',
                    'The distinct96-case movement bench injects terrain,boots/speed,hero and actor fixtures and resets HP per case. It compares3072 frame samples,not natural paths or accumulated hazard damage.',
                    'No complete video/audio,transition cadence,global clock/RNG,ending,saves or hardware equivalence is claimed. The previously observed496-byte stack margin remains scoped to the D4 return,not extended by this milestone.'])
    (ROOT/'analysis/d5_progress_v0304_report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('v304:D5 boots/supply exit cold-replayed;96 movement cases and3072 SMS/native frames exact;ROM unchanged')


if __name__=='__main__':main()
