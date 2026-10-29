"""Fifth crystal, source mechanisms and unassisted return on the current ROM."""
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
    prior=load('analysis/d5_supplies_v0304_report.json')
    assert prior['passed'] and prior['md_sha256']==digest and prior['ready_keys']==1
    sources=load('analysis/d5_campaign_v0304_source_index.json')
    supply_sources=load(sources['inherited_source_index'])
    base_sources=load(supply_sources['inherited_source_index'])
    legacy=load(sources['legacy_boss_controller_index'])
    for index in [sources,supply_sources,base_sources,legacy]:
        for item in index['sources'].values():assert sha(read(item['path']))==item['sha256']
    symbol_file='validation/stack-v0304-d5-all/symbol.txt';sy=symbols(ROOT/symbol_file);read(symbol_file)
    original=read('input/original.sms')
    assert original[0x3234e+0x163*8:0x32356+0x163*8]==bytes([0x65]+[0]*7)
    assert original[0x320ea+(0x65-0x20)*4:0x320ee+(0x65-0x20)*4]==bytes.fromhex('480c0240')
    stages=[];first_writes=None;previous=112233
    for suffix,frame,room,capacity,crystals in [('boss01',117521,0x163,64,4),
            ('boss02',119965,0x163,72,5),('return-contact01',120313,0x174,72,5),('exit01',121051,0x49,72,5)]:
        root='validation/natural-dungeon-combat/md-auto-v0304-d5-'+suffix
        c=load(root+'/capture.json');r=load(root+'/report.json');proof_root=root+f'-assisted-fixed-replay-{frame}'
        p=load(proof_root+'/replay_report.json')
        assert c['frames']==frame and r['prefix_end']==previous and c['rom_sha256']==p['rom_sha256']==digest
        previous=frame
        assert c['sram_input'] is None and p['passed'] and p['whole_ram_bytes']==65536 and p['final_png_exact'] and not p['feedback_reads']
        for name,h in p['evidence'].items():assert sha(read(root+'/'+name))==h
        a,w=recording(ROOT/root,c);read(root+'/assistance.json')
        assert a['boss_room']==0x163 and len(a['episodes'])==5 and not a['boss_assistance']
        assert a['release_write_frame']==114294 and a['first_boss_combat']==dict(frame=114321,health=64,hurt=0)
        assert a['first_boss_damage'] is None and max(f for f,_,_ in w)==114294
        assert not a['primary_state_imports'] and not a['health_refills'] and not a['rom_modifications']
        assert all(address==sy['hero_hurt'] for _,address,_ in w)
        if first_writes is None:first_writes=w
        else:assert first_writes==w
        assert not r['deaths']
        if 'verified_persistent_prediction_windows' in r:
            assert r['verified_persistent_prediction_windows']==r['full_ram_prediction_matches'] and not r['stack_only_difference_windows']
            assert not r['primary_state_imports']
        for stem,ext in [('ram','bin'),('frame','png')]:
            filename=f'/{stem}_{frame:05d}.{ext}';assert read(root+filename)==read(proof_root+filename)
        raw=read(root+f'/ram_{frame:05d}.bin');data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k))
        word=lambda n:int.from_bytes(data(n,2),'big')
        assert word('room_id')==room and word('hero_max_health')==capacity and word('hero_health')==capacity
        assert word('hero_keys')==0 and word('hero_selected_item')==word('hero_weapon_level')==1
        assert data('hero_items',17)[12:15]==bytes([1,1,1]) and word('hero_attack_speed')==1
        assert data('game_save_state',592)[0x1f:0x28]==bytes([128]*crystals+[0]*(9-crystals))
        if suffix=='boss01':
            assert r['failure']=='frame_limit' and not r['room_cleared'] and a['test_stop_reason']=='boss_frame_budget'
            actors=data('world_actor_state',768)
            assert actors[0]==0x65 and actors[24]==72 and not actors[3]&2
            assert sorted(actors[i*48+24] for i in range(8,16) if actors[i*48]==0x66)==[4,8]
            assert r['full_ram_prediction_matches']==200 and not r.get('target_satellites',False)
            assert r['coarse_driver_sha256']==legacy['sources']['tools/assisted_boss_coarse_route.py']['sha256']
        else:assert r['failure'] is None
        if suffix=='boss02':
            assert r['room_cleared'] and not word('item_reward_active') and word('hero_magic')==48
            assert r['planning_step']==16 and r['moving_health_premium']==40 and r['target_satellites']
            assert r['full_ram_prediction_matches']==112
            assert r['coarse_driver_sha256']==sources['sources']['tools/assisted_boss_coarse_route.py']['sha256']
        if suffix=='return-contact01':
            assert r['contact_route_passed'] and r['contact_room']==0x173 and r['contact_destination']==0x174
            assert not r['contact_state_writes'] and a['new_assistance_writes']==0
        if suffix=='exit01':
            assert r['full_dungeon_cleared'] and r['dungeon_exit_verified'] and a['new_assistance_writes']==0
            assert word('world_dungeon_number')==0 and r['full_ram_prediction_matches']==12
        stages.append(dict(trace=root,frames=frame,room=room,health=capacity,max_health=capacity,crystals=crystals,
                           whole_ram_png_exact=True,prediction_windows=r.get('full_ram_prediction_matches'),partial_combat_only=suffix=='boss01'))
    stack=load('validation/stack-v0304-d5-all/stack_report.json')
    assert stack['md_sha256']==digest and stack['frames']==121051 and stack['all_instructions'] and not stack['invalid_heap_examples']
    boundary=stack['heap_changes'][-1]['end']+2;margin=stack['minimum_sp']-boundary;assert margin>0
    for stem,ext in [('ram','bin'),('frame','png')]:
        filename=f'/{stem}_121051.{ext}'
        assert read('validation/stack-v0304-d5-all'+filename)==read(stages[-1]['trace']+filename)
    read('tools/summarize_d5_campaign_v0304.py')
    result=dict(passed=True,version=304,md_sha256=digest,production_rom_unchanged=True,stages=stages,
                fifth_crystal_and_exterior_exit=True,exit_room=0x49,exit_health=72,max_health=72,keys_remaining=0,
                boots_owned=True,canoe_owned=True,rope_owned=True,axe_equipped=True,boss_assistance=False,
                primary_state_imports=0,injected_health_refills=0,guard_release_lead_frames=27,
                source_boss_stats='480c0240',satellite_targets_added_to_controller=True,
                observed_stack_margin_bytes=margin,stack_frames=121051,source_boss_fight_compared=False,
                full_game_validated=False,evidence=refs,limits=[
                    'The first3200-frame combat segment ends at64 heroHP with72 coreHP and two remaining orbiters at8/4HP. Its independent cold replay gates continuation of the same fight without health,boss or progression resets.',
                    'The input-search controller now counts attackable type66 orbiters in slots8..15 as targets for boss65. Original native boss logic already requires their removal before core vulnerability. Only ordinary buttons change; no ROM patch is introduced.',
                    'All approach writes end114294,27 frames before ordinary combat114321 withhurt0. No hero damage is observed during this boss fight. Crystal healing raises capacity/health to72. Return mechanism and exterior exit add no assistance.',
                    'Four stages independently reproduce full RAM/PNG from cold boot;200 and112 boss windows and12 exit windows match complete primary RAM. The prior supply report covers nine more current-ROM stages.',
                    'Five crystals and returns are now established on this ROM. D6 onward,ending,saves,global RNG,complete source campaign and full video/audio/hardware fidelity remain unproved. Stack margin is observed only on this recorded route.'])
    (ROOT/'analysis/d5_campaign_v0304_report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(f'v304:fifth crystal and exterior49 return independently replayed;{margin}-byte observed stack margin;ROM unchanged')


if __name__=='__main__':main()
