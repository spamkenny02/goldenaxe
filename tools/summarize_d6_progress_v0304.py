"""Current-ROM Ice Bell approach, real resource ledger and Earth-driver fix."""
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
    prior=load('analysis/d5_campaign_v0304_report.json')
    assert prior['passed'] and prior['md_sha256']==digest and prior['fifth_crystal_and_exterior_exit']
    visited=set();indices={}
    def source_index(name):
        if name in visited:return
        visited.add(name);index=load(name);indices[name]=index
        for item in index['sources'].values():assert sha(read(item['path']))==item['sha256']
        for key in ['inherited_source_index','legacy_boss_controller_index','legacy_earth_source_index']:
            if key in index:source_index(index[key])
    source_index('analysis/d6_progress_v0304_source_index.json')
    old_earth=indices['analysis/d5_supplies_v0304_source_index.json']['sources']['tools/natural_earth_passage.py']['sha256']
    new_earth=indices['analysis/d6_progress_v0304_source_index.json']['sources']['tools/natural_earth_passage.py']['sha256']
    symbol_file='validation/stack-v0304-d5-all/symbol.txt';sy=symbols(ROOT/symbol_file);read(symbol_file)
    def unpack(raw):
        data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k))
        word=lambda n:int.from_bytes(data(n,2),'big')
        return data,word
    bridge=read('validation/natural-dungeon-combat/md-auto-v0304-d5-exit01/ram_121051.bin')
    data,word=unpack(bridge)
    assert word('room_id')==0x49 and data('scratch',4096)[0x84a]==0x0a and data('scratch',4096)[0x85a]==0x6b
    assert data('game_save_state',592)[0x99]&1 and word('hero_keys')==0 and word('hero_magic')==48
    specifications=[('entry01','world',0x187),('east01','clear',0x178),('key01','key',0x168),
        ('warp01','earth',0x138),('key02','key',0x148),('contact01','contact',0x137),('key03','key',0x146),
        ('torch117-01','contact',0x138),('outer01','key',0x116),('earth126-01','earth',0x136),
        ('middle135-02','earth',0x135),('left135-01','earth',0x134),('earth134-01','earth',0x124),
        ('key04','key',0x113),('bell01','item',0x112),('gate125-02','earth',0x125)]
    stages=[];previous=121051;key_value=0;key_gains=key_spends=0;magic_drops=[]
    for suffix,kind,room in specifications:
        trace=('natural-dungeon-route/md-v0304-d6-' if kind=='world' else 'natural-dungeon-combat/md-auto-v0304-d6-')+suffix
        root='validation/'+trace;c=load(root+'/capture.json');r=load(root+('/route_report.json' if kind=='world' else '/report.json'));frame=c['frames']
        proof_root=root+f'-assisted-fixed-replay-{frame}';p=load(proof_root+'/replay_report.json')
        assert c['rom_sha256']==p['rom_sha256']==digest and c['sram_input'] is None and r['prefix_end']==previous
        previous=frame
        assert r['failure'] is None and p['passed'] and p['whole_ram_bytes']==65536 and p['final_png_exact'] and not p['feedback_reads']
        for name,h in p['evidence'].items():assert sha(read(root+'/'+name))==h
        a,w=recording(ROOT/root,c);read(root+'/assistance.json')
        assert a['boss_room']==0x115 and a['activation_after_frame']==121051 and len(a['episodes'])==6
        assert a['first_boss_entry'] is None and a['first_boss_combat'] is None and not a['boss_assistance']
        assert not a['health_refills'] and not a['primary_state_imports'] and not a['rom_modifications']
        assert all(address==sy['hero_hurt'] for _,address,_ in w)
        for stem,ext in [('ram','bin'),('frame','png')]:
            filename=f'/{stem}_{frame:05d}.{ext}';assert read(root+filename)==read(proof_root+filename)
        raw=read(root+f'/ram_{frame:05d}.bin');data,word=unpack(raw)
        assert word('room_id')==room and word('hero_health')==word('hero_max_health')==72
        assert data('game_save_state',592)[0x1f:0x28]==bytes([128]*5+[0]*4)
        assert data('hero_items',17)[12:15]==bytes([1,1,1]) and word('hero_attack_speed')==1 and word('hero_selected_item')==1
        assert data('hero_items',17)[10]==(1 if kind=='item' or suffix=='gate125-02' else 0)
        if kind=='world':assert r['reached_entrance'] and not r['normal_continues']
        else:
            assert not r['deaths']
            for row in load(root+'/events.json'):
                if 'keys' not in row:continue
                delta=row['keys']-key_value;key_gains+=max(0,delta);key_spends+=max(0,-delta);key_value=row['keys']
            assert key_value==word('hero_keys')
        if kind=='key':assert r['new_key_verified'] and r['room_cleared']
        if kind=='clear':assert r['room_cleared']
        if kind=='contact':assert r['contact_route_passed'] and not r['contact_state_writes']
        if kind=='item':assert r['room_cleared'] and r['collect_item_requested']==10 and r['last_state']['item_value']==1
        if kind=='earth':
            assert r['earth_route_passed'] and r['earth_cell_cleared'] and not r['earth_state_writes']
            assert r['earth_controller_sha256']==(new_earth if suffix=='gate125-02' else old_earth)
            rows=load(root+'/earth_events.json')
            for first,last in zip(rows,rows[1:]):
                if last['magic']<first['magic']:
                    assert first['magic']-last['magic']==8 and last['selected']==5
                    magic_drops.append(dict(trace=root,frame=last['frame'],amount=8))
            if suffix in ['middle135-02','gate125-02']:assert r['earth_action_only_requested'] and not r['earth_passage_traversed']
        if suffix=='gate125-02':assert r['earth_sequence_latched'] and word('hero_magic')==word('hero_keys')==0
        stages.append(dict(trace=root,kind=kind,frames=frame,room=room,health=72,keys=word('hero_keys'),magic=word('hero_magic'),whole_ram_png_exact=True))
    assert key_gains==key_spends==5 and len(magic_drops)==7 and sum(x['amount'] for x in magic_drops)==56
    regression='validation/natural-dungeon-combat/md-auto-v0304-d6-middle135-latch01'
    comparison=load(regression+'/regression_comparison.json');r=load(regression+'/report.json')
    assert comparison['passed'] and all(comparison['exact'].values()) and r['earth_route_passed'] and r['earth_sequence_latched']
    assert not r['earth_during_combat_requested'] and r['earth_controller_sha256']==new_earth
    p=load(regression+'-assisted-fixed-replay-138302/replay_report.json');assert p['passed'] and p['whole_ram_bytes']==65536 and p['final_png_exact']
    for name,h in comparison['evidence'].items():assert sha(read(name))==h
    for suffix in ['middle135-01','gate125-01']:
        failed=load('validation/natural-dungeon-combat/md-auto-v0304-d6-'+suffix+'/report.json')
        assert failed['failure']=='controller_stalled' and failed['last_state']['game']==16
    read('tools/summarize_d6_progress_v0304.py')
    result=dict(passed=True,version=304,md_sha256=digest,production_rom_unchanged=True,stages=stages,
                ice_bell_acquired=True,inventory_slot=10,bridge49_cells={'4A':'0A','5A':'6B'},
                keys_obtained=key_gains,keys_spent=key_spends,keys_remaining=0,
                earth_magic_decrease_events=magic_drops,earth_magic_spent=56,initial_magic=48,final_magic=0,
                net_other_magic_change=8,ready_room=0x125,ready_health=72,boss_room=0x115,
                sixth_boss_entered=False,sixth_crystal_validated=False,full_game_validated=False,
                earth_input_ownership_fix_regression_exact=True,evidence=refs,limits=[
                    'Sixteen main stages have independent cold fixed-input full-RAM/PNG replays with logged approach-only hero_hurt writes. No health,keys,magic,equipment,currency,position or progression fixture enters this campaign.',
                    'Five observed key increases and five decreases balance fromzero tozero. Seven8-point magic decreases occur with Earth selected across its six action stages; the reserve balance has a net8-point replenishment outside those decreases. These are current-route observations,not source RNG or full resource-distribution equivalence.',
                    'The failed middle135/gate125 trials stalled in the inventory when enemy activation handed it to the combat controller. The Earth controller now retains a begun input sequence through re-equipping. The fixed default middle135 case matches all controls,assistance,RAM and PNG of the already verified during-combat workaround and has its own cold replay.',
                    'Preparatory middle135 and gate125 actions clear their blocks; they do not claim a room or boss victory. The last main state is125 at72HP,zero keys,zero magic,Ice Bell owned,five crystals;the boss is not yet entered in this checkpoint.',
                    'The sixth crystal,return,D7 onward,ending,saves,global timing/RNG and full video/audio/hardware fidelity require later evidence. The earlier496-byte stack margin remains scoped to the D5 return.'])
    (ROOT/'analysis/d6_progress_v0304_report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('v304:Ice Bell and D6 gate125 ready;16 cold-replayed stages;keys5/5,Earth56MP;controller regression exact;ROM unchanged')


if __name__=='__main__':main()
