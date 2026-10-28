"""Version-bound ordinary D3 combat continuation,third crystal and exterior exit."""
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
    prior=load('analysis/d2_campaign_v0304_report.json');assert prior['passed'] and prior['md_sha256']==digest and prior['d3_entrance_and_rope_replayed']
    sources=load('analysis/d2_campaign_v0304_source_index.json')
    for item in sources['sources'].values():assert sha(read(item['path']))==item['sha256']
    sy=symbols(ROOT/'validation/stack-v0304-d3-all/symbol.txt');read('validation/stack-v0304-d3-all/symbol.txt')
    stages=[];first_writes=None
    for suffix,frame,hp,capacity,room,crystals in [('boss01',50610,39,48,0x1c3,2),('boss02',52469,56,56,0x1c3,3),('exit01',53755,46,56,0x62,3)]:
        root='validation/natural-dungeon-combat/md-auto-v0304-d3-'+suffix
        capture=load(root+'/capture.json');report=load(root+'/report.json')
        proof=load(root+f'-assisted-fixed-replay-{frame}/replay_report.json')
        assist,writes=recording(ROOT/root,capture);read(root+'/assistance.json')
        assert capture['frames']==frame and capture['rom_sha256']==proof['rom_sha256']==digest and capture['sram_input'] is None
        assert proof['passed'] and proof['whole_ram_bytes']==65536 and proof['final_png_exact'] and not proof['feedback_reads']
        for n,h in proof['evidence'].items():assert sha(read(root+'/'+n))==h
        assert len(assist['episodes'])==3 and assist['boss_room']==0x1c3 and not assist['boss_assistance']
        assert assist['first_boss_combat']==dict(frame=48810,health=39,hurt=0) and assist['release_write_frame']==48776
        assert max(f for f,_,_ in writes)==48776 and all(address==sy['hero_hurt'] for _,address,_ in writes)
        if first_writes is None:first_writes=writes
        else:assert writes==first_writes
        assert not report['primary_state_imports'] and not report['deaths']
        assert report['full_ram_prediction_matches']==report['verified_persistent_prediction_windows'] and not report['stack_only_difference_windows']
        raw=read(root+f'/ram_{frame:05d}.bin');read(root+f'/frame_{frame:05d}.png')
        data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big')
        assert word('room_id')==room and word('hero_health')==hp and word('hero_max_health')==capacity
        assert word('hero_selected_item')==word('hero_weapon_level')==1 and data('hero_items',17)[13]==1
        assert data('game_save_state',592)[0x1f:0x28]==bytes([128]*crystals+[0]*(9-crystals))
        if suffix=='boss01':
            assert report['failure']=='frame_limit' and not report['room_cleared'] and assist['test_stop_reason']=='boss_frame_budget'
            assert data('world_actor_state',768)[24]==18 and assist['first_boss_damage'] is None
        else:
            assert report['failure'] is None and report['room_cleared']
            assert assist['first_boss_damage']==dict(frame=51735,before=39,after=31,hurt=47)
        if suffix=='exit01':assert report['full_dungeon_cleared'] and report['dungeon_exit_verified'] and assist['new_assistance_writes']==0
        stages.append(dict(trace=root,frames=frame,room=room,health=hp,max_health=capacity,crystals=crystals,
                           whole_ram_png_exact=True,prediction_windows=report['verified_persistent_prediction_windows'],partial_combat_only=suffix=='boss01'))
    stack=load('validation/stack-v0304-d3-all/stack_report.json')
    assert stack['md_sha256']==digest and stack['frames']==53755 and stack['all_instructions'] and not stack['invalid_heap_examples']
    boundary=stack['heap_changes'][-1]['end']+2;assert stack['minimum_sp']-boundary==496
    assert read('validation/stack-v0304-d3-all/ram_53755.bin')==read('validation/natural-dungeon-combat/md-auto-v0304-d3-exit01/ram_53755.bin')
    assert read('validation/stack-v0304-d3-all/frame_53755.png')==read('validation/natural-dungeon-combat/md-auto-v0304-d3-exit01/frame_53755.png')
    read('tools/summarize_d3_campaign_v0304.py')
    result=dict(passed=True,version=304,md_sha256=digest,production_rom_unchanged=True,stages=stages,
                three_crystals_and_exterior_exit=True,exit_room=0x62,exit_health=46,max_health=56,
                axe_equipped=True,rope_owned=True,boss_assistance=False,primary_state_imports=0,health_refills=0,
                guard_release_lead_frames=34,observed_stack_margin_bytes=496,stack_frames=53755,
                full_game_validated=False,source_campaign_compared=False,evidence=refs,
                limits=['The first1800-frame boss segment ends alive at39HP with18 bossHP. Its independent cold replay gates a continuation of the same fight; no captured state enters the primary game and no health or boss reset is performed.',
                        'All logged approach writes end48776,before normal combat48810. The later39-to31 damage is ordinary. Boss and exterior return add no assistance. The entire campaign retains earlier logged approach protection.',
                        'Three crystals and returns are now proved on this ROM. D4 onward,ending,saves,complete source campaign,global RNG and full video/audio/hardware fidelity remain unproved. Stack scope is this route through the third exterior exit.'])
    (ROOT/'analysis/d3_campaign_v0304_report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('v304:third crystal and exterior62 exit46/56HP independently replayed;496-byte observed stack margin;ROM unchanged')


if __name__=='__main__':main()
