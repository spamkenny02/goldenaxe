"""Fourth crystal and unassisted return on v304, following the same live fight."""
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
    prior=load('analysis/d4_canoe_v0304_report.json')
    assert prior['passed'] and prior['md_sha256']==digest and prior['canoe_acquired']
    sources=load('analysis/d4_campaign_v0304_source_index.json')
    assert sources['inherited_source_index']=='analysis/d2_campaign_v0304_source_index.json'
    inherited=load(sources['inherited_source_index'])
    for item in list(inherited['sources'].values())+list(sources['sources'].values()):
        assert sha(read(item['path']))==item['sha256']
    symbol_file='validation/stack-v0304-d4-all/symbol.txt'
    sy=symbols(ROOT/symbol_file);read(symbol_file)
    original=read('input/original.sms')
    kinds=original[0x3234e+0x180*8:0x32356+0x180*8]
    assert kinds==bytes([0x6a]+[0]*7)
    assert original[0x320ea+(0x6a-0x20)*4:0x320ee+(0x6a-0x20)*4]==bytes.fromhex('1e100240')
    stages=[];first_writes=None;previous_frame=76662
    for suffix,previous in [('boss01','md-auto-v0304-d4-boss-key01'),('boss02','md-auto-v0304-d4-boss01'),
                            ('exit01','md-auto-v0304-d4-boss02')]:
        root='validation/natural-dungeon-combat/md-auto-v0304-d4-'+suffix
        c=load(root+'/capture.json');r=load(root+'/report.json');frame=c['frames']
        proof_root=root+f'-assisted-fixed-replay-{frame}'
        p=load(proof_root+'/replay_report.json')
        assert c['rom_sha256']==p['rom_sha256']==digest and c['sram_input'] is None
        assert r['recorded_new_game_prefix']==previous and r['prefix_end']==previous_frame
        previous_frame=frame
        assert p['passed'] and p['whole_ram_bytes']==65536 and p['final_png_exact'] and not p['feedback_reads']
        for name,h in p['evidence'].items():assert sha(read(root+'/'+name))==h
        assist,writes=recording(ROOT/root,c);read(root+'/assistance.json')
        assert assist['boss_room']==0x180 and len(assist['episodes'])==4 and not assist['boss_assistance']
        assert assist['release_write_frame']==78342 and assist['first_boss_combat']==dict(frame=78388,health=56,hurt=0)
        assert max(f for f,_,_ in writes)==78342 and all(address==sy['hero_hurt'] for _,address,_ in writes)
        if first_writes is None:first_writes=writes
        else:assert first_writes==writes
        assert not assist['primary_state_imports'] and not assist['health_refills'] and not assist['rom_modifications']
        assert not r['primary_state_imports'] and not r['deaths']
        assert r['verified_persistent_prediction_windows']==r['full_ram_prediction_matches'] and not r['stack_only_difference_windows']
        for stem,ext in [('ram','bin'),('frame','png')]:
            filename=f'/{stem}_{frame:05d}.{ext}'
            assert read(root+filename)==read(proof_root+filename)
        raw=read(root+f'/ram_{frame:05d}.bin')
        data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k))
        word=lambda n:int.from_bytes(data(n,2),'big')
        hp=word('hero_health');capacity=word('hero_max_health');room=word('room_id')
        assert word('hero_selected_item')==word('hero_weapon_level')==1
        assert data('hero_items',17)[12:14]==bytes([1,1]) and data('hero_items',17)[5]==1
        crystals=3 if suffix=='boss01' else 4
        assert data('game_save_state',592)[0x1f:0x28]==bytes([128]*crystals+[0]*(9-crystals))
        if suffix=='boss01':
            assert frame==82388 and hp==capacity==56 and room==0x180
            assert r['failure']=='frame_limit' and not r['room_cleared'] and assist['test_stop_reason']=='boss_frame_budget'
            assert data('world_actor_state',768)[0]==0x6a and data('world_actor_state',768)[24]==12
            assert assist['first_boss_damage'] is None and r['full_ram_prediction_matches']==500
        else:
            assert r['failure'] is None and r['room_cleared'] and capacity==64
            assert assist['first_boss_damage']==dict(frame=82870,before=56,after=32,hurt=47)
        if suffix=='boss02':
            assert frame==83593 and hp==64 and room==0x180 and not word('item_reward_active')
            assert word('hero_magic')==word('hero_max_magic')==48
            assert r['planning_step']==16 and r['moving_health_premium']==0 and r['full_ram_prediction_matches']==33
            assert r['coarse_driver_sha256']==sources['sources']['tools/assisted_boss_coarse_route.py']['sha256']
        if suffix=='exit01':
            assert room==0x10 and 0<hp<=capacity and word('world_dungeon_number')==0
            assert r['full_dungeon_cleared'] and r['dungeon_exit_verified'] and assist['new_assistance_writes']==0
        stages.append(dict(trace=root,frames=frame,room=room,health=hp,max_health=capacity,crystals=crystals,
                           whole_ram_png_exact=True,prediction_windows=r['full_ram_prediction_matches'],partial_combat_only=suffix=='boss01'))
    final=stages[-1]
    stack=load('validation/stack-v0304-d4-all/stack_report.json')
    assert stack['md_sha256']==digest and stack['frames']==final['frames'] and stack['all_instructions']
    assert not stack['invalid_heap_examples']
    boundary=stack['heap_changes'][-1]['end']+2;margin=stack['minimum_sp']-boundary
    assert margin>0
    for stem,ext in [('ram','bin'),('frame','png')]:
        filename=f'/{stem}_{final["frames"]:05d}.{ext}'
        assert read('validation/stack-v0304-d4-all'+filename)==read(final['trace']+filename)
    read('tools/summarize_d4_campaign_v0304.py')
    result=dict(passed=True,version=304,md_sha256=digest,production_rom_unchanged=True,stages=stages,
                fourth_crystal_and_exterior_exit=True,exit_room=0x10,exit_health=final['health'],max_health=64,
                axe_equipped=True,canoe_owned=True,rope_owned=True,boss_assistance=False,
                primary_state_imports=0,health_refills=0,guard_release_lead_frames=46,
                observed_stack_margin_bytes=margin,stack_frames=final['frames'],full_game_validated=False,
                source_boss_fight_compared=False,evidence=refs,
                limits=['The first4000-frame boss segment ends alive with56 heroHP and12 bossHP. Its independent cold replay gates continuation of the same fight without health,boss,state or progression resets.',
                        'All logged approach assistance ends78342,46 frames before ordinary combat78388. Ordinary damage56-to32 occurs82870. Reward healing to64 is part of the game. The exit adds no assistance.',
                        'The new controller chooses ordinary buttons in16-frame windows with a lower health preference. All33 completed windows match the full primary RAM and the independent fixed replay reproduces final RAM/PNG. This does not change ROM behavior or establish global cadence.',
                        'Four crystals and exterior returns are established on this ROM. D5 onward,ending,saves,global RNG,complete source campaign and full video/audio/hardware fidelity remain unproved. Stack margin is observed only along this recorded route.'])
    (ROOT/'analysis/d4_campaign_v0304_report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(f'v304:fourth crystal and exterior10 return independently replayed;{margin}-byte observed stack margin;ROM unchanged')


if __name__=='__main__':main()
