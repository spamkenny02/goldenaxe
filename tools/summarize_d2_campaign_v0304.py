"""Version-bound axe,fairy,D2 crystal/exit and D3 rope cold-replay evidence."""
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
    prior=load('analysis/burst_cadence_v0304_report.json');assert prior['passed'] and prior['md_sha256']==digest
    source_index=load('analysis/d2_campaign_v0304_source_index.json')
    for item in source_index['sources'].values():assert sha(read(item['path']))==item['sha256']
    sy=symbols(ROOT/'validation/stack-v0304-d2-all/symbol.txt');read('validation/stack-v0304-d2-all/symbol.txt')
    # family,name,room,health,capacity,axe,selected,crystals,rope
    specs=[
        ('natural-dungeon-route','md-v0304-d1-return-axe01',0x1e4,28,32,False,0,1,False),
        ('natural-dungeon-combat','md-auto-v0304-d1-axe-key01',0x1c5,28,32,False,0,1,False),
        ('natural-dungeon-combat','md-auto-v0304-d1-axe01',0x1b6,28,32,True,0,1,False),
        ('natural-dungeon-combat','md-auto-v0304-d1-axe-exit01',0xb9,28,32,True,1,1,False),
        ('natural-dungeon-route','md-v0304-fairy-route01',0xaf,28,32,True,1,1,False),
        ('natural-service-route','md-v0304-fairy-service01',0xc9,40,40,True,1,1,False),
        ('natural-dungeon-route','md-v0304-d2-entry01',0x171,40,40,True,1,1,False),
        ('natural-dungeon-combat','md-auto-v0304-d2-key01',0x160,40,40,True,1,1,False),
        ('natural-dungeon-combat','md-auto-v0304-d2-key02',0x152,40,40,True,1,1,False),
        ('natural-dungeon-combat','md-auto-v0304-d2-key03',0x131,40,40,True,1,1,False),
        ('natural-dungeon-combat','md-auto-v0304-d2-boss02',0x144,48,48,True,1,2,False),
        ('natural-dungeon-combat','md-auto-v0304-d2-exit01',0xd6,31,48,True,1,2,False),
        ('natural-dungeon-route','md-v0304-d3-entry01',0x1f8,31,48,True,1,2,False),
        ('natural-dungeon-combat','md-auto-v0304-d3-rope01',0x1f4,31,48,True,1,2,True)]
    stages=[]
    for family,name,room,hp,capacity,axe,selected,crystals,rope in specs:
        root='validation/'+family+'/'+name
        capture=load(root+'/capture.json');report=load(root+('/route_report.json' if family=='natural-dungeon-route' else '/report.json'))
        proof=load(root+f'-assisted-fixed-replay-{capture["frames"]}/replay_report.json')
        assist,writes=recording(ROOT/root,capture);read(root+'/assistance.json')
        assert capture['rom_sha256']==proof['rom_sha256']==digest and capture['sram_input'] is None
        assert proof['passed'] and proof['whole_ram_bytes']==65536 and proof['final_png_exact'] and not proof['feedback_reads']
        for n,h in proof['evidence'].items():assert sha(read(root+'/'+n))==h
        assert report['failure'] is None and not report.get('deaths',0)
        assert not assist['primary_state_imports'] and assist['health_refills']==0 and not assist['boss_assistance']
        assert all(address==sy['hero_hurt'] for _,address,_ in writes)
        raw=read(root+f'/ram_{capture["frames"]:05d}.bin');read(root+f'/frame_{capture["frames"]:05d}.png')
        data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big')
        assert word('room_id')==room and word('hero_health')==hp and word('hero_max_health')==capacity
        assert word('hero_selected_item')==selected and bool(data('hero_items',17)[1])==axe and bool(data('hero_items',17)[13])==rope
        assert data('game_save_state',592)[0x1f:0x28]==bytes([128]*crystals+[0]*(9-crystals))
        if name=='md-v0304-fairy-service01':assert report['passed'] and report['new_assistance_writes']==0 and data('game_save_state',592)[0x50+0xc9]&2
        if name.startswith('md-auto-v0304-d2-key'):assert report['new_key_verified'] and assist['first_boss_combat'] is None
        if name in ['md-auto-v0304-d2-boss02','md-auto-v0304-d2-exit01']:
            assert assist['release_write_frame']==33162 and assist['first_boss_combat']==dict(frame=33219,health=40,hurt=0)
            assert assist['first_boss_damage']==dict(frame=33485,before=40,after=32,hurt=47) and max(f for f,_,_ in writes)==33162
            assert report['full_ram_prediction_matches']==report['verified_persistent_prediction_windows'] and not report['stack_only_difference_windows']
            assert report['primary_state_imports']==0
        if name=='md-auto-v0304-d2-exit01':assert report['full_dungeon_cleared'] and assist['new_assistance_writes']==0 and capture['frames']==37005
        if name=='md-auto-v0304-d3-rope01':assert report['collect_item_requested']==13 and report['room_cleared'] and assist['first_boss_combat'] is None
        stages.append(dict(trace=root,frames=capture['frames'],room=room,health=hp,max_health=capacity,crystals=crystals,axe_owned=axe,rope_owned=rope,whole_ram_png_exact=True))
    failed=load('validation/natural-dungeon-combat/md-auto-v0304-d2-boss01/report.json')
    assert failed['failure']=='continuation_route_died' and not failed['room_cleared']
    stack=load('validation/stack-v0304-d2-all/stack_report.json')
    assert stack['md_sha256']==digest and stack['frames']==37005 and stack['all_instructions'] and not stack['invalid_heap_examples']
    boundary=stack['heap_changes'][-1]['end']+2;assert stack['minimum_sp']-boundary==496
    assert read('validation/stack-v0304-d2-all/ram_37005.bin')==read('validation/natural-dungeon-combat/md-auto-v0304-d2-exit01/ram_37005.bin')
    assert read('validation/stack-v0304-d2-all/frame_37005.png')==read('validation/natural-dungeon-combat/md-auto-v0304-d2-exit01/frame_37005.png')
    read('tools/summarize_d2_campaign_v0304.py')
    result=dict(passed=True,version=304,md_sha256=digest,production_rom_unchanged=True,stages=stages,
                second_crystal_and_exterior_exit=True,exit_health=31,max_health=48,axe_equipped=True,keys_remaining=1,
                d3_entrance_and_rope_replayed=True,third_crystal_validated=False,boss_assistance=False,
                health_refills=0,primary_state_imports=0,guard_release_lead_frames=57,
                observed_stack_margin_bytes=496,stack_frames=37005,failed_boss_attempts_preserved=1,
                full_game_validated=False,source_campaign_compared=False,evidence=refs,
                limits=['The campaign retains explicitly logged approach protection. Both D1/D2 boss fights and returns add no assistance. Rewards,keys,axe,life capacity and rope are acquired by ordinary inputs,not imported game state.',
                        'Independent cold replays match all65536 RAM bytes and final PNGs for14 stages. The first D2 side-search attempt dies;only the later cautious victory is promoted. Secondary planning snapshots never enter the primary game.',
                        'D3 is reached and its rope acquired;its boss/crystal and remaining campaign are not proved here. Stack depth covers instructions through the D2 exterior exit only. Complete source campaign,global RNG and video/audio/hardware fidelity remain unproved.'])
    (ROOT/'analysis/d2_campaign_v0304_report.json').write_text(json.dumps(result,indent=2)+'\n')
    print('v304:14 stages cold-replayed;second crystal/exit and D3 rope exact;496-byte observed stack margin;ROM unchanged')


if __name__=='__main__':main()
