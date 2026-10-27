"""Verify the corrected approach guard and the first D7 key."""
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
    digest=sha(read('gaw-megadrive.bin'));sy=symbols(ROOT/'megadrive/out/release/symbol.txt')
    prior=load('analysis/d7_entry_v0293_report.json');assert prior['passed'] and prior['md_sha256']==digest
    stages=[];recordings=[]
    for family,name in [('natural-dungeon-route','md-v0293-d7-route02'),('natural-dungeon-route','md-v0293-d7-route03'),('natural-dungeon-combat','md-auto-v0293-d7-key02')]:
        root='validation/'+family+'/'+name;c=load(root+'/capture.json');r=load(root+('/route_report.json' if family=='natural-dungeon-route' else '/report.json'))
        p=load(root+f'-assisted-fixed-replay-{c["frames"]}/replay_report.json');a,w=recording(ROOT/root,c);read(root+'/assistance.json')
        assert c['rom_sha256']==p['rom_sha256']==digest and c['sram_input'] is None
        assert p['passed'] and p['whole_ram_bytes']==65536 and p['final_png_exact'] and not p['feedback_reads']
        for n,h in p['evidence'].items():assert sha(read(root+'/'+n))==h
        assert r['failure'] is None and a['boss_room']==0x179 and a['first_boss_entry'] is None
        assert not a['primary_state_imports'] and not a['health_refills'] and not a['boss_assistance']
        driver=read(root+'/assisted_route_driver.py');assert sha(driver)==a['driver_sha256']
        if not name.endswith('route02'):assert driver==read('tools/assisted_boss_route.py')
        assert all(address==sy['hero_hurt'] for _,address,_ in w)
        raw=read(root+f'/ram_{c["frames"]:05d}.bin');read(root+f'/frame_{c["frames"]:05d}.png')
        data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big')
        assert data('game_save_state',592)[0x1f:0x25]==bytes([128]*6) and word('hero_max_health')==80
        if name.endswith('route02'):assert word('hero_health')==2
        else:assert a['preserve_floor_hurt_requested'] and word('hero_health')==58
        if name.endswith('key02'):
            assert r['room_cleared'] and r['new_key_verified'] and not r['deaths']
            assert word('room_id')==0x1cb and word('hero_keys')==r['target_entry_keys']+1==1
        else:assert r['reached_entrance'] and r['directional_probe_succeeded'] and not r['normal_continues']
        stages.append(dict(trace=root,frames=c['frames'],health=word('hero_health'),room=word('room_id'),whole_ram_bytes=65536,final_png_exact=True))
        recordings.append((c,read(root+'/controls.json'),w))
    old,old_controls,old_w=recordings[0];new,new_controls,new_w=recordings[1]
    assert old['frames']==new['frames'] and old['presses']==new['presses'] and old_controls==new_controls
    old_local=[row for row in old_w if row[0]>151975];new_local=[row for row in new_w if row[0]>151975]
    assert [row for row in old_local if row[2]==b'\0\x81']==[row for row in new_local if row[2]==b'\0\x81']
    new_set=set(new_local);old_set=set(old_local)
    removed=[row for row in old_local if row not in new_set]
    assert len(removed)==867 and all(row[2]==b'\0\0' for row in removed)
    assert all(row in old_set for row in new_local)
    for n in ['assisted_boss_route.py','summarize_d7_approach_v0293.py','plan_d7_source_route.py']:read('tools/'+n)
    proposal=load('analysis/d7_source_route_proposal.json');assert proposal['source_sha256']==sha(read('input/original.sms')) and not proposal['live_progression_proof']
    out=dict(passed=True,version=293,md_sha256=digest,production_rom_unchanged=True,stages=stages,
             approach_controls_exact=True,guard129_schedule_exact=True,redundant_executed_zero_writes_removed=867,
             first_d7_key_obtained=True,health=58,max_health=80,boss_entered=False,dungeon7_completed=False,
             health_refills=0,primary_state_imports=0,source_campaign_compared=False,full_game_validated=False,evidence=refs,
             limits=['Approach assistance is test-only and explicitly logged. Ordinary terrain damage remains; no health,inventory or currency is injected. The ROM is unchanged.',
                     'Identical controls and129 guard schedule isolate the removal of867 executed zero writes. One additional old zero write was queued after the final frame and was not executed. This is a controller correction,not a source-ROM speed or fidelity comparison.',
                     'Only the first key is confirmed in D7. Source topology is a proposal; ship,boss,crystal,exit,later dungeons,ending and global fidelity remain unverified.'])
    (ROOT/'analysis/d7_approach_v0293_report.json').write_text(json.dumps(out,indent=2)+'\n')
    print('D7 first key at58/80HP; cold replays exact;867 executed cooldown resets removed,ROM unchanged')


if __name__=='__main__':main()
