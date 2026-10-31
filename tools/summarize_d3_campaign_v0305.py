"""Audit v305 rope, source passage puzzle, third crystal and exterior return."""
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
    digest=sha((ROOT/'gaw-megadrive.bin').read_bytes())
    prior=load('analysis/d2_campaign_v0305_report.json')
    assert prior['passed'] and prior['md_sha256']==digest and prior['second_crystal_and_exterior_return']
    production=load('validation/v0305-indoor-sources/after.json')
    assert production['rom_sha256']==digest
    assert all(sha((ROOT/n).read_bytes())==h for n,h in production['production_sources'].items())
    for name in ['gaw-title-megadrive.bin','versions/v0305-83dfaf69/gaw-megadrive-v0305.bin']:
        assert sha((ROOT/name).read_bytes())==digest
    sy=symbols(ROOT/'megadrive/out/release/symbol.txt')
    # Follow only the actual winner's recorded parent chain,not alternate trials.
    family='validation/natural-dungeon-combat/'
    exit_root=family+'md-auto-v0305-d3-exit01'
    name=load(exit_root+'/report.json')['recorded_new_game_prefix'];boss_chain=[]
    while name!='md-auto-v0305-d3-rope01':
        assert name.startswith('md-auto-v0305-d3-boss') and name not in boss_chain
        boss_chain.append(name);r=load(family+name+'/report.json');name=r['recorded_new_game_prefix']
    boss_chain.reverse();assert boss_chain[0]=='md-auto-v0305-d3-boss08'
    roots=[('validation/natural-dungeon-route/md-v0305-d3-entry01','entry'),
           (family+'md-auto-v0305-d3-rope01','rope')]
    roots += [(family+n,'boss' if i==len(boss_chain)-1 else 'boss-partial') for i,n in enumerate(boss_chain)]
    roots.append((exit_root,'exit'))
    stages=[];previous_writes=[];boss_writes=None;boss_a=None;puzzle_seen=False
    for index,(root,kind) in enumerate(roots):
        c=load(root+'/capture.json');f=c['frames']
        r=load(root+('/route_report.json' if kind=='entry' else '/report.json'))
        assert c['rom_sha256']==r['rom_sha256']==digest and c['sram_input'] is None and not r['sram_checkpoint_injection']
        a,writes=recording(ROOT/root,c);read(root+'/assistance.json')
        assert len(a['episodes'])==3 and a['boss_room']==0x1c3 and a['activation_after_frame']==40562
        assert a['episodes'][0]['release_write_frame']==14835 and a['episodes'][1]['release_write_frame']==36726
        assert not a['health_refills'] and not a['primary_state_imports'] and not a['boss_assistance']
        assert all(addr==sy['hero_hurt'] for _,addr,_ in writes)
        assert writes[:len(previous_writes)]==previous_writes
        previous_writes=writes
        if kind=='entry':
            assert r['failure'] is None and r['reached_entrance'] and r['directional_probe_succeeded']
            assert not r['normal_continues'] and r['recorded_combat_prefix']=='md-auto-v0305-d2-exit01'
        else:
            assert not r['deaths'] and not r.get('primary_state_imports',0)
            assert r['driver_sha256']==sha(read(root+'/combat_driver.py'))
            assert r['prefix_end']==stages[-1]['frames']
            if kind=='boss-partial':
                assert r['failure']=='frame_limit' and not r['room_cleared']
                assert a['test_stop_reason']=='boss_frame_budget' and r['last_state']['health']>0
            else:assert r['failure'] is None and r['room_cleared']
        if kind in ('entry','rope'):
            assert a['first_boss_entry'] is None and a['first_boss_combat'] is None
        else:
            first=a['first_boss_combat'];assert first['hurt']==0 and first['health']>0
            assert writes[-1][0]==a['release_write_frame']<first['frame'] and writes[-1][2]==b'\0\0'
            if boss_writes is None:boss_writes=writes
            else:assert boss_writes==writes
            boss_a=dict(release=a['release_write_frame'],first_combat=first,first_damage=a['first_boss_damage'])
            plan=load(root+'/planning_partial.json')
            assert plan['verified_windows']==plan['full_ram_matches'] and not plan['stack_only_difference_windows']
            assert not plan['primary_state_imports']
        proof=root+f'-assisted-fixed-replay-{f}';p=load(proof+'/replay_report.json')
        assert p['passed'] and p['rom_sha256']==digest and p['whole_ram_bytes']==65536
        assert p['final_png_exact'] and not p['feedback_reads']
        for n,h in p['evidence'].items():assert sha(read(root+'/'+n))==h
        raw=read(root+f'/ram_{f:05d}.bin')
        for stem,ext in [('ram','bin'),('frame','png')]:
            name=f'/{stem}_{f:05d}.{ext}';assert read(root+name)==read(proof+name)
        data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k))
        word=lambda n:int.from_bytes(data(n,2),'big')
        save=data('game_save_state',592);items=data('hero_items',17)
        crystals=sum(x==128 for x in save[0x1f:0x28])
        assert items[8]==1 and save[0x117]&2 and save[0x1f:0x21]==bytes([128,128])
        assert word('hero_weapon_level')==word('hero_selected_item')==1 and not word('sound_unhandled_command')
        if kind!='entry':assert items[13]==1
        if kind=='rope':assert r['collect_item_requested']==13 and word('room_id')==0x1f4
        if index==2:
            assert r['rush_rooms']==[0x1e3] and r['puzzle_first_when_blocked_requested']
            events=load(root+'/events.json')
            assert any(e['room']==0x1e3 and e['room_flags']&4 and e['room_flags']&32 for e in events)
            puzzle_seen=True
        if kind in ('boss','exit'):assert crystals==3 and word('hero_max_health')==56
        if kind=='exit':
            assert word('room_id')==0x62 and not word('world_dungeon_number')
            assert r['full_dungeon_cleared'] and r['dungeon_exit_verified'] and not a['new_assistance_writes']
        stages.append(dict(trace=root,kind=kind,frames=f,room=word('room_id'),health=word('hero_health'),
                           max_health=word('hero_max_health'),crystals=crystals,rope_owned=bool(items[13]),
                           oil_owned=True,whole_ram_png_exact=True))
    assert puzzle_seen
    stack='validation/stack-v0305-d3-all';s=load(stack+'/stack_report.json')
    assert s['md_sha256']==digest and s['frames']==stages[-1]['frames'] and s['read_only'] and s['all_instructions']
    assert s['logged_assistance_replayed'] and not s['invalid_heap_examples']
    assert s['minimum_instruction_sp']==min(x['sp'] for x in s['instruction_minima'])
    assert s['minimum_sp']==min(s['minimum_instruction_sp'],s['minimum_sampled_sp'])
    margin=s['minimum_sp']-max(x['end']+2 for x in s['heap_changes']);assert margin>0
    for stem,ext in [('ram','bin'),('frame','png')]:
        name=f'/{stem}_{s["frames"]:05d}.{ext}';assert read(stack+name)==read(exit_root+name)
    for suffix in range(1,8):
        root=family+f'md-auto-v0305-d3-boss{suffix:02d}'
        r=load(root+'/report.json');a=load(root+'/assistance.json')
        assert r['failure']=='frame_limit' and not r['room_cleared'] and a['first_boss_entry'] is None
        assert r['driver_sha256']==sha(read(root+'/combat_driver.py'))
    # Keep the successful partial diagnostic replay separate from the campaign winner.
    root=family+'md-auto-v0305-d3-ring01';r=load(root+'/report.json');c=load(root+'/capture.json')
    assert r['failure']=='unreachable_attack_position' and not r['room_cleared']
    assert load(root+f"-assisted-fixed-replay-{c['frames']}/replay_report.json")['passed']
    assert r['driver_sha256']==sha(read(root+'/combat_driver.py'))
    assert read('tools/natural_dungeon_combat.py')==read('validation/v0305-d3-reentry-sources/before.py')
    read('tools/summarize_d3_campaign_v0305.py')
    result=dict(passed=True,version=305,md_sha256=digest,production_rom_unchanged=True,
                three_crystals_and_exterior_exit=True,stages=stages,boss_assistance=boss_a,
                source_puzzle_coordinate=856,experimental_controller_restored=True,
                instruction_stack_margin_bytes=margin,stack_frames=s['frames'],full_game_validated=False,evidence=refs,
                limits=['Current-ROM cold replay of each campaign stage,whole65536RAM and finalPNG exact. Approach protection writes only hero_hurt;no HP,actor,inventory,progression or SRAM fixture.',
                        'The real stationary-UP puzzle at120,104 opens the third-dungeon passage while foes remain. The controller crosses this room without claiming its enemies were all defeated. Experimental reentry/component strategies were rejected and the published combat controller restored byte-for-byte.',
                        'Seven unsuccessful approaches and one separately replayed alive diagnostic are excluded from the winner chain. The main boss has no protection after its recorded release,and the exterior return adds none.',
                        'Only first three crystals/returns on v305. Later campaign,ending,saves,source RNG/global phase and complete source audio/video/hardware fidelity remain unproved.'])
    (ROOT/'analysis/d3_campaign_v0305_report.json').write_bytes((json.dumps(result,indent=2)+'\n').encode())
    print(f'v305:rope,real passage puzzle,third crystal and exterior62 return verified;stack margin{margin} bytes')


if __name__=='__main__':main()
