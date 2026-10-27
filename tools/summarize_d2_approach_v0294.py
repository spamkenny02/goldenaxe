"""Current-ROM axe supply excursion, first life fairy and D2 entrance."""
import json
from run_core import ROOT
from archive_lossless_evidence import sha
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols

STAGES=[('natural-dungeon-route','md-v0294-d1-return-axe01','route'),('natural-dungeon-combat','md-auto-v0294-d1-axe-key03','key'),('natural-dungeon-combat','md-auto-v0294-d1-axe02','axe'),('natural-dungeon-combat','md-auto-v0294-d1-axe-exit02','exit'),('natural-dungeon-route','md-v0294-fairy-route01','route'),('natural-service-route','md-v0294-fairy-service01','fairy'),('natural-dungeon-route','md-v0294-d2-entry01','route')]


def main():
    refs={}
    def read(name):
        raw=(ROOT/name).read_bytes();refs[name]=sha(raw);return raw
    def load(name):return json.loads(read(name))
    digest=sha(read('gaw-megadrive.bin'));prior=load('analysis/d1_campaign_v0294_report.json')
    assert prior['passed'] and prior['md_sha256']==digest and prior['native_d1_completed']
    sy=symbols(ROOT/'megadrive/out/release/symbol.txt');stages=[]
    for index,(family,name,kind) in enumerate(STAGES):
        root='validation/'+family+'/'+name;c=load(root+'/capture.json');r=load(root+('/route_report.json' if family=='natural-dungeon-route' else '/report.json'))
        p=load(root+f'-assisted-fixed-replay-{c["frames"]}/replay_report.json');a,w=recording(ROOT/root,c);read(root+'/assistance.json')
        assert c['rom_sha256']==p['rom_sha256']==digest and c['sram_input'] is None
        assert p['passed'] and p['whole_ram_bytes']==65536 and p['final_png_exact'] and not p['feedback_reads']
        for n,h in p['evidence'].items():assert sha(read(root+'/'+n))==h
        assert a['boss_room']==0x144 and a['first_boss_entry'] is None and a['first_boss_combat'] is None
        assert a['activation_after_frame']==15025 and len(a['episodes'])==2
        old=a['episodes'][0];assert old['boss_room']==0x175 and old['release_write_frame']==12338 and old['first_boss_combat']['frame']==12409
        assert not a['health_refills'] and not a['primary_state_imports'] and not a['boss_assistance'] and a['preserve_floor_hurt_requested']
        assert all(address==sy['hero_hurt'] for _,address,_ in w) and r['failure'] is None
        raw=read(root+f'/ram_{c["frames"]:05d}.bin');read(root+f'/frame_{c["frames"]:05d}.png')
        data=lambda n,k:bytes(raw[(sy[n]+j)^1] for j in range(k));word=lambda n:int.from_bytes(data(n,2),'big')
        save=data('game_save_state',592);items=data('hero_items',17)
        assert save[0x1f:0x28]==bytes([128]+[0]*8) and word('hero_max_health')==(40 if index>=5 else 32)
        assert word('hero_health')==([28,32,32,32,32,40,40][index]) and not word('sound_unhandled_command')
        assert items[1]==(1 if index>=2 else 0)
        if family=='natural-dungeon-route':assert r['reached_entrance'] and r['directional_probe_succeeded'] and not r['normal_continues']
        if kind=='key':assert r['new_key_verified'] and word('hero_keys')==1 and r['target_entry_keys']==0
        if kind=='axe':assert r['room_cleared'] and r['last_state']['item_value']==1
        if kind in ['axe','exit']:assert word('hero_keys')==0 and not r['deaths']
        if kind=='exit':assert r['dungeon_exit_verified'] and word('room_id')==0xb9 and word('hero_selected_item')==1
        if kind=='fairy':
            assert r['passed'] and r['new_assistance_writes']==0
            assert r['initial_state']['max_health']==32 and r['last_state']['max_health']==r['last_state']['health']==40
            assert save[0x50+0xc9]&2 and not r['initial_state']['outside_flags']&2 and word('room_id')==0xc9
        if index==6:assert word('room_id')==0x171 and word('world_dungeon_number')==2 and word('hero_selected_item')==1
        stages.append(dict(trace=root,role=kind,frames=c['frames'],health=word('hero_health'),max_health=word('hero_max_health'),room=word('room_id'),whole_ram_bytes=65536,final_png_exact=True))
    for n in ['summarize_d2_approach_v0294.py','natural_fairy_service.py','assisted_boss_route.py','natural_dungeon_combat.py','natural_dungeon_route.py']:read('tools/'+n)
    out=dict(passed=True,version=294,md_sha256=digest,production_rom_unchanged=True,stages=stages,official_cold_replays=7,
             native_d1_completed=True,axe_acquired_and_equipped=True,life_fairy_reward=True,dungeon2_entered=True,
             health=40,max_health=40,health_refills=0,primary_state_imports=0,dungeon2_boss_entered=False,dungeon2_completed=False,
             full_game_validated=False,source_campaign_compared=False,evidence=refs,
             limits=['The second approach begins after the verified first exit and covers a return for the axe,the life-fairy road and D2 entrance. Logged hurt protection remains test-only; no life,equipment,currency or primary snapshots are injected.',
                     'The first D1 boss was ordinary; D2 boss144 has not been entered. The return with the axe is a supply excursion after the same first crystal,not another dungeon victory.',
                     'Final whole RAM and PNG match cold fixed-input replays. Original SMS full campaign,all intermediate framebuffers,audio/hardware cadence,later dungeons and ending remain unproven.'])
    (ROOT/'analysis/d2_approach_v0294_report.json').write_text(json.dumps(out,indent=2)+'\n')
    print('v294 axe,life fairy and D2 entrance at40/40HP:7 cold replays exact;boss144 pending')


if __name__=='__main__':main()
