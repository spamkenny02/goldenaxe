"""Real gifts, one purchased key, healer and D5 mechanisms on the current ROM."""
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
    prior=load('analysis/d5_progress_v0304_report.json')
    assert prior['passed'] and prior['md_sha256']==digest and prior['supply_exit_verified']
    sources=load('analysis/d5_supplies_v0304_source_index.json')
    inherited=load(sources['inherited_source_index'])
    for item in list(inherited['sources'].values())+list(sources['sources'].values()):assert sha(read(item['path']))==item['sha256']
    symbol_path='validation/stack-v0304-d4-all/symbol.txt';sy=symbols(ROOT/symbol_path);read(symbol_path)
    specifications=[
        ('natural-dungeon-route/md-v0304-d5-golda1-route01','route',0x3f,50,0,22,40),
        ('natural-service-route/md-v0304-d5-golda1-service01','gift',0xa1,50,0,52,40),
        ('natural-dungeon-route/md-v0304-d5-goldb4-route03','route',0x3f,50,0,52,40),
        ('natural-service-route/md-v0304-d5-goldb4-service01','gift',0xb4,50,0,82,40),
        ('natural-dungeon-route/md-v0304-d5-merchant94-route01','route',0,50,0,82,40),
        ('natural-service-route/md-v0304-d5-keys94-service01','purchase',0x94,64,1,22,40),
        ('natural-dungeon-route/md-v0304-d5-return-route01','route',0x186,64,1,22,40),
        ('natural-dungeon-combat/md-auto-v0304-d5-warp01','earth',0x162,64,1,None,32),
        ('natural-dungeon-combat/md-auto-v0304-d5-contact02','contact',0x172,64,1,None,32)]
    stages=[];previous_frame=96329
    for trace,kind,room,hp,keys,gold,magic in specifications:
        root='validation/'+trace;c=load(root+'/capture.json');frame=c['frames']
        r=load(root+('/route_report.json' if kind=='route' else '/report.json'))
        proof_root=root+f'-assisted-fixed-replay-{frame}';p=load(proof_root+'/replay_report.json')
        assert c['rom_sha256']==p['rom_sha256']==digest and c['sram_input'] is None
        assert r['failure'] is None and frame>previous_frame
        if kind in ('route','earth','contact'):assert r['prefix_end']==previous_frame
        previous_frame=frame
        assert p['passed'] and p['whole_ram_bytes']==65536 and p['final_png_exact'] and not p['feedback_reads']
        for name,h in p['evidence'].items():assert sha(read(root+'/'+name))==h
        a,w=recording(ROOT/root,c);read(root+'/assistance.json')
        assert a['boss_room']==0x163 and a['activation_after_frame']==86158 and len(a['episodes'])==5
        assert a['first_boss_entry'] is None and a['first_boss_combat'] is None and not a['boss_assistance']
        assert not a['health_refills'] and not a['primary_state_imports'] and not a['rom_modifications']
        assert all(address==sy['hero_hurt'] for _,address,_ in w)
        for stem,ext in [('ram','bin'),('frame','png')]:
            filename=f'/{stem}_{frame:05d}.{ext}';assert read(root+filename)==read(proof_root+filename)
        raw=read(root+f'/ram_{frame:05d}.bin');data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k))
        word=lambda n:int.from_bytes(data(n,2),'big')
        assert word('room_id')==room and word('hero_health')==hp and word('hero_max_health')==64
        assert word('hero_keys')==keys and word('hero_magic')==magic and not word('sound_unhandled_command')
        if gold is not None:assert word('hero_gold')==gold
        assert data('hero_items',17)[12:15]==bytes([1,1,1]) and word('hero_attack_speed')==1
        assert data('game_save_state',592)[0x1f:0x28]==bytes([128]*4+[0]*5)
        if kind=='route':
            assert r['reached_entrance'] and r['directional_probe_succeeded'] and not r['normal_continues']
            if 'golda1-route' not in trace:
                assert r['route_driver_sha256']==sources['sources']['tools/natural_dungeon_route.py']['sha256']
                assert r['required_chop_waits_for_settled_position']
        else:assert r['passed']
        if kind=='gift':
            assert r['new_assistance_writes']==0 and r['last_state']['gold']-r['first_state']['gold']==30
            assert not r['first_state']['outside_flags']&2 and r['last_state']['outside_flags']&2
        if kind=='purchase':
            assert r['keys_bought']==1 and r['unit_price']==60 and r['new_assistance_writes']==0
            assert not r['currency_or_inventory_fixtures'] and r['free_healing_completed']
            assert r['first_state']['gold']==82 and r['first_state']['health']==50 and r['first_state']['keys']==0
        if kind=='earth':
            assert r['earth_route_passed'] and r['earth_passage_traversed'] and not r['earth_state_writes']
            assert r['earth_passage_room']==0x153 and r['earth_cell']==0x44
            assert r['earth_before']['magic']-r['earth_opened']['magic']==8
            assert r['earth_controller_sha256']==sources['sources']['tools/natural_earth_passage.py']['sha256']
        if kind=='contact':
            assert r['contact_route_passed'] and r['contact_room']==0x162 and r['contact_destination']==0x172
            assert not r['contact_state_writes'] and r['avoided_portal_rooms']==[0x162]
            assert r['contact_controller_sha256']==sources['sources']['tools/natural_contact_passage.py']['sha256']
        stages.append(dict(trace=root,kind=kind,frames=frame,room=room,health=hp,max_health=64,keys=keys,
                           gold=word('hero_gold'),magic=magic,whole_ram_png_exact=True))
    failed=load('validation/natural-dungeon-combat/md-auto-v0304-d5-contact01/report.json')
    assert failed['failure']=='frame_limit' and failed['last_state']['room']==0x153 and not failed['contact_route_passed']
    for trial in ['01','02']:read(f'validation/v0304-d5-goldb4-route{trial}.log')
    read('tools/summarize_d5_supplies_v0304.py')
    result=dict(passed=True,version=304,md_sha256=digest,production_rom_unchanged=True,stages=stages,
                gold_gifts=[30,30],keys_bought=1,key_price=60,actual_free_healing=True,post_supply_health=64,
                earth_warp_room=0x153,earth_warp_cell=0x44,earth_warp_destination=0x162,
                contact_room=0x162,contact_destination=0x172,ready_health=64,ready_keys=1,ready_magic=32,
                scope_ends_before_boss=True,fifth_crystal_validated=False,full_game_validated=False,
                controller_room_loading_wait_fixed=True,evidence=refs,limits=[
                    'Nine completed stages have independent fixed-input cold whole-RAM/PNG replays. Logged approach assistance only writes hero_hurt. Gifts,purchase,healing,Earth and mechanisms execute normally; no inventory,currency,position,health or progression fixture enters the primary game.',
                    'The B4 route01/02 assertions are controller diagnostics,not game-ROM defects. The route controller now waits for a settled interior walking point before replanning after a prerequisite flag. The successful route03 and later fixed replay validate the ordinary input path; ROM bytes remain unchanged.',
                    'Contact01 recrosses the reciprocal portal and reaches its frame limit in153. It is not a completed mechanism proof. Contact02 avoids the162 portal tile through ordinary navigation,opens the mechanism and reaches172.',
                    'One key is actually bought for60 gold; two30-gold gifts suffice from the prior22. This differs from the historical two-key supply trip. Boss5 entry,its crystal/return,ending,saves and global source/video/audio/hardware fidelity remain unproved at this checkpoint.'])
    (ROOT/'analysis/d5_supplies_v0304_report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('v304:nine supply/mechanism stages cold-replayed;one real key and healer;ready172 at64HP;ROM unchanged')


if __name__=='__main__':main()
