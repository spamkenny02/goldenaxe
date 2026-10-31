"""Audit real gold/teacher/Earth/canoe/D4 campaign transactions on v305."""
import json
from run_core import ROOT
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols

BASE_STAGES=[
    ('natural-dungeon-route','md-v0305-gold-entry01','route'),
    ('natural-service-route','md-v0305-gold50-01','gold'),
    ('natural-dungeon-route','md-v0305-earth-entry01','route'),
    ('natural-service-route','md-v0305-earth-learn01','teacher'),
    ('natural-dungeon-route','md-v0305-d4-entry01','route'),
    ('natural-dungeon-combat','md-auto-v0305-d4-key01','key'),
    ('natural-dungeon-combat','md-auto-v0305-d4-earth02','earth'),
    ('natural-dungeon-combat','md-auto-v0305-d4-a1-key02','key'),
    ('natural-dungeon-combat','md-auto-v0305-d4-canoe01','canoe'),
    ('natural-dungeon-combat','md-auto-v0305-d4-warp02','warp'),
    ('natural-dungeon-combat','md-auto-v0305-d4-boss-key01','key')]


def main():
    refs={}
    def read(name):
        raw=evidence(ROOT/name);refs[name]=sha(raw);return raw
    def load(name):return json.loads(read(name))
    digest=sha((ROOT/'gaw-megadrive.bin').read_bytes())
    prior=load('analysis/d3_campaign_v0305_report.json')
    assert prior['passed'] and prior['md_sha256']==digest and prior['three_crystals_and_exterior_exit']
    production=load('validation/v0305-indoor-sources/after.json')
    assert production['rom_sha256']==digest
    assert all(sha((ROOT/n).read_bytes())==h for n,h in production['production_sources'].items())
    for n in ['gaw-title-megadrive.bin','versions/v0305-83dfaf69/gaw-megadrive-v0305.bin']:
        assert sha((ROOT/n).read_bytes())==digest
    source_index=load('validation/v0305-d4-sources/source_index.json')
    for n,h in source_index.items():assert sha(read('validation/v0305-d4-sources/'+n.split('/')[-1]))==h
    sy=symbols(ROOT/'megadrive/out/release/symbol.txt')
    family='validation/natural-dungeon-combat/'
    exit_root=family+'md-auto-v0305-d4-exit01'
    name=load(exit_root+'/report.json')['recorded_new_game_prefix'];boss_chain=[]
    while name!='md-auto-v0305-d4-boss-key01':
        assert name.startswith('md-auto-v0305-d4-boss') and name not in boss_chain
        boss_chain.append(name);name=load(family+name+'/report.json')['recorded_new_game_prefix']
    boss_chain.reverse();assert boss_chain[0]=='md-auto-v0305-d4-boss01'
    entries=[(f'validation/{f}/{n}',k) for f,n,k in BASE_STAGES]
    entries += [(family+n,'boss' if i==len(boss_chain)-1 else 'boss-partial') for i,n in enumerate(boss_chain)]
    entries.append((exit_root,'exit'))
    stages=[];previous_writes=[];boss_writes=None;boss_a=None;water_frames=None
    previous_frame=55110
    for index,(root,kind) in enumerate(entries):
        c=load(root+'/capture.json');r=load(root+('/route_report.json' if kind=='route' else '/report.json'));f=c['frames']
        assert c['rom_sha256']==r['rom_sha256']==digest and c['sram_input'] is None and not r['sram_checkpoint_injection']
        assert f>previous_frame
        if 'prefix_end' in r:assert r['prefix_end']==previous_frame
        previous_frame=f
        a,writes=recording(ROOT/root,c);read(root+'/assistance.json')
        assert len(a['episodes'])==4 and a['boss_room']==0x180 and a['activation_after_frame']==55110
        assert [e['release_write_frame'] for e in a['episodes'][:3]]==[14835,36726,52210]
        assert not a['health_refills'] and not a['primary_state_imports'] and not a['boss_assistance']
        assert all(addr==sy['hero_hurt'] for _,addr,_ in writes)
        assert writes[:len(previous_writes)]==previous_writes;previous_writes=writes
        if kind=='route':
            assert r['failure'] is None and r['reached_entrance'] and r['directional_probe_succeeded'] and not r['normal_continues']
            assert r['route_driver_sha256']==source_index['tools/natural_dungeon_route.py']
        elif kind in ('gold','teacher'):
            assert r['passed'] and r['failure'] is None and not r['new_assistance_writes']
        elif kind in ('earth','warp'):
            assert r['failure'] is None and r['earth_route_passed'] and r['earth_passage_traversed'] and r['earth_cell_cleared']
            assert r['earth_controller_sha256']==source_index['tools/natural_earth_passage.py'] and not r['earth_state_writes']
            assert r['earth_before']['cell']==11 and r['earth_before']['magic']-r['earth_opened']['magic']==8
            assert r['earth_opened']['flags']&4 and r['earth_before']['level']==1
        elif kind=='boss-partial':
            assert r['failure']=='frame_limit' and not r['room_cleared'] and r['last_state']['health']>0
            assert a['test_stop_reason']=='boss_frame_budget'
        else:assert r['failure'] is None and r['room_cleared']
        if 'driver_sha256' in r:assert r['driver_sha256']==source_index['tools/natural_dungeon_combat.py']
        if 'deaths' in r:assert not r['deaths']
        if kind in ('boss','boss-partial','exit'):
            first=a['first_boss_combat'];assert first['hurt']==0 and first['health']>0
            assert writes[-1][0]==a['release_write_frame']<first['frame'] and writes[-1][2]==b'\0\0'
            if boss_writes is None:boss_writes=writes
            else:assert boss_writes==writes
            boss_a=dict(release=a['release_write_frame'],first_combat=first,first_damage=a['first_boss_damage'])
            plan=load(root+'/planning_partial.json')
            assert plan['verified_windows']==plan['full_ram_matches'] and not plan['stack_only_difference_windows']
            assert not plan['primary_state_imports']
        else:assert a['first_boss_entry'] is None and a['first_boss_combat'] is None
        proof=root+f'-assisted-fixed-replay-{f}';p=load(proof+'/replay_report.json')
        assert p['passed'] and p['rom_sha256']==digest and p['whole_ram_bytes']==65536 and p['final_png_exact'] and not p['feedback_reads']
        for n,h in p['evidence'].items():assert sha(read(root+'/'+n))==h
        raw=read(root+f'/ram_{f:05d}.bin')
        for stem,ext in [('ram','bin'),('frame','png')]:
            n=f'/{stem}_{f:05d}.{ext}';assert read(root+n)==read(proof+n)
        data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k))
        word=lambda n:int.from_bytes(data(n,2),'big')
        save=data('game_save_state',592);items=data('hero_items',17)
        assert items[8]==items[13]==1 and save[0x117]&2 and save[0x1f:0x22]==bytes([128]*3)
        assert word('hero_weapon_level')==1 and not word('sound_unhandled_command')
        if index>=3:assert items[5]==1 and word('hero_max_magic')==48
        if index>=8:assert items[12]==1
        if kind=='gold':
            assert r['first_state']['gold']==3 and r['last_state']['gold']==53 and save[0x144]&2
        if kind=='teacher':
            assert r['first_state']['gold']==53 and r['last_state']['gold']==3
            assert r['first_state']['level']==0 and r['last_state']['level']==1
            assert r['first_state']['magic']==24 and r['last_state']['magic']==48
        if kind=='key':assert r['new_key_verified']
        if kind=='canoe':assert r['collect_item_requested']==12 and r['last_state']['item_value']==1
        if kind=='warp':
            assert p['water_observer'] and p['water_moving_frames']>0 and p['shallow_water_flag']==32
            samples=load(proof+'/water_samples.json');assert samples and all(x['owned'] for x in samples)
            water_frames=p['water_moving_frames']
        if kind in ('boss','exit'):assert save[0x22]==128 and word('hero_max_health')==64
        if kind=='exit':
            assert word('room_id')==0x10 and not word('world_dungeon_number')
            assert r['full_dungeon_cleared'] and r['dungeon_exit_verified'] and not a['new_assistance_writes']
        stages.append(dict(trace=root,kind=kind,frames=f,room=word('room_id'),health=word('hero_health'),
                           max_health=word('hero_max_health'),magic=word('hero_magic'),keys=word('hero_keys'),
                           crystals=sum(x==128 for x in save[0x1f:0x28]),earth_level=items[5],canoe_owned=bool(items[12]),
                           oil_owned=True,whole_ram_png_exact=True))
    stack='validation/stack-v0305-d4-all';s=load(stack+'/stack_report.json')
    assert s['md_sha256']==digest and s['frames']==stages[-1]['frames'] and s['read_only'] and s['all_instructions']
    assert s['logged_assistance_replayed'] and not s['invalid_heap_examples']
    assert s['minimum_instruction_sp']==min(x['sp'] for x in s['instruction_minima'])
    assert s['minimum_sp']==min(s['minimum_instruction_sp'],s['minimum_sampled_sp'])
    margin=s['minimum_sp']-max(x['end']+2 for x in s['heap_changes']);assert margin>0
    for stem,ext in [('ram','bin'),('frame','png')]:
        n=f'/{stem}_{s["frames"]:05d}.{ext}';assert read(stack+n)==read(exit_root+n)
    for suffix in ['earth01','a1-key01','warp01']:
        root=family+'md-auto-v0305-d4-'+suffix;r=load(root+'/report.json');a=load(root+'/assistance.json')
        assert a['first_boss_entry'] is None
        if suffix=='earth01':assert r['failure'] is None and r['earth_route_passed'] and not r['room_cleared']
        else:assert r['failure'] in ('frame_limit','controller_stalled')
    read('tools/summarize_d4_campaign_v0305.py')
    result=dict(passed=True,version=305,md_sha256=digest,production_rom_unchanged=True,
                four_crystals_and_exterior_exit=True,known_reward_hud_physical_map_bug=True,stages=stages,boss_assistance=boss_a,
                canoe_water_moving_frames=water_frames,instruction_stack_margin_bytes=margin,
                stack_frames=s['frames'],full_game_validated=False,evidence=refs,
                limits=['Current-ROM cold boot,real50-horn gift and50-horn Earth purchase,two8MP casts,canoe reward,water movement,real portal,main boss and return. Every stage has independent whole65536RAM/finalPNG replay.',
                        'Logged approach protection only writes hero_hurt. No HP,MP,currency,ownership,actor,progression or SRAM fixture. Guard ends before D4 main-boss combat and never resumes on the return;earlier approaches remain explicitly assisted.',
                        'Two failed controllers and one longer alternate Earth route are preserved and excluded. Optional B0 mechanism is deferred on the route;C0 mechanism and both Earth obstacles are handled by ordinary game inputs.',
                        'Known physical HUD-map restoration bug after acquisition windows;progression and replay equivalence do not validate that rendering. First four crystals/returns only on v305. Later campaign,ending,saves,source RNG/global phase and complete SMS audio/video/hardware fidelity remain unproved.'])
    (ROOT/'analysis/d4_campaign_v0305_report.json').write_bytes((json.dumps(result,indent=2)+'\n').encode())
    print(f'v305:Earth/canoe,fourth crystal and exterior10 return verified;stack margin{margin} bytes')


if __name__=='__main__':main()
