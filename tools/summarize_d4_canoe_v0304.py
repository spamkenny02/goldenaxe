"""Current v304 acquired canoe/warp campaign and bounded natural SMS comparison."""
import json
from run_core import ROOT
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols
from audit_item_reward_visuals import sms_pixels, md_pixels


def main():
    refs={}
    def read(name):
        raw=evidence(ROOT/name);refs[name]=sha(raw);return raw
    def load(name):return json.loads(read(name))
    digest=sha(read('versions/v0304-b7b4e150/gaw-megadrive-v0304.bin'))
    sms_digest=sha(read('input/original.sms'))
    prior=load('analysis/d4_earth_v0304_report.json')
    assert prior['passed'] and prior['md_sha256']==digest and prior['earth_passage_traversed']
    sy=symbols(ROOT/'validation/stack-v0304-d3-all/symbol.txt');read('validation/stack-v0304-d3-all/symbol.txt')
    def extract(raw,sms=False):
        if sms:return dict(cells=raw[0x1c00:0x1ca0],map=raw[0x1600:0x1b00],items=raw[0xe0:0xf1],flags=raw[0x100:0x200])
        data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k))
        return dict(cells=data('scratch',4096)[0x800:0x8a0],map=data('sms_vram',16384)[0x3800:0x3d00],
                    items=data('hero_items',17),flags=data('game_save_state',592)[0x50:0x150])
    stages=[];current={}
    for suffix,frame,room,keys,magic,canoe in [('a1-key02',71684,0x1a1,2,48,0),('canoe01',74012,0x1a2,0,48,1),
                                           ('warp01',75052,0x192,0,40,1),('boss-key01',76662,0x182,1,40,1)]:
        root='validation/natural-dungeon-combat/md-auto-v0304-d4-'+suffix
        c=load(root+'/capture.json');r=load(root+'/report.json')
        proof_root=root+f'-assisted-fixed-replay-{frame}'
        p=load(proof_root+'/replay_report.json')
        assert c['frames']==frame and c['rom_sha256']==p['rom_sha256']==digest and c['sram_input'] is None
        assert p['passed'] and p['whole_ram_bytes']==65536 and p['final_png_exact'] and not p['feedback_reads']
        assert r['failure'] is None and not r['deaths']
        for n,h in p['evidence'].items():assert sha(read(root+'/'+n))==h
        assist,writes=recording(ROOT/root,c);read(root+'/assistance.json')
        assert assist['activation_after_frame']==53755 and assist['boss_room']==0x180
        assert assist['first_boss_entry'] is None and not assist['boss_assistance'] and not assist['health_refills']
        assert not assist['primary_state_imports'] and not assist['rom_modifications']
        assert all(address==sy['hero_hurt'] for _,address,_ in writes)
        for stem,ext in [('ram','bin'),('frame','png')]:
            filename=f'/{stem}_{frame:05d}.{ext}'
            assert read(root+filename)==read(proof_root+filename)
        raw=read(root+f'/ram_{frame:05d}.bin')
        data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k))
        word=lambda n:int.from_bytes(data(n,2),'big')
        assert word('room_id')==room and word('hero_health')==56 and word('hero_max_health')==56
        assert word('hero_keys')==keys and word('hero_magic')==magic and data('hero_items',17)[12]==canoe
        assert data('hero_items',17)[13]==1 and data('hero_items',17)[5]==1 and word('hero_selected_item')==1
        assert data('game_save_state',592)[0x1f:0x28]==bytes([128]*3+[0]*6)
        if suffix in ('a1-key02','boss-key01'):assert r['new_key_verified'] and r['room_cleared']
        if suffix=='a1-key02':assert r['settle_attacks_requested']
        if suffix=='canoe01':
            assert r['room_cleared'] and r['collect_item_requested']==12
            final=extract(raw);assert final['cells'][0x24]==0x4c
            final['vram']=read(root+f'/vram_{frame:05d}.bin');current['canoe_chest']=final
        if suffix=='warp01':
            assert r['earth_route_passed'] and r['earth_passage_traversed'] and not r['destination_combat_cleared']
            assert r['earth_before']['magic']-r['earth_opened']['magic']==8 and not r['earth_state_writes']
            opened=r['earth_opened']['frame']+1
            final=extract(read(root+f'/ram_{opened:05d}.bin'))
            assert final['cells'][0x5c]==12 and final['flags'][0xa3]==21
            final['vram']=read(root+f'/vram_{opened:05d}.bin');current['earth_warp']=final
        if suffix in ('canoe01','warp01'):
            assert p['water_observer'] and p['water_moving_frames']>0 and p['shallow_water_flag']==32
            samples=load(proof_root+'/water_samples.json')
            assert all(s['owned'] and s['water_flag']==32 for s in samples)
        stages.append(dict(trace=root,frames=frame,room=room,health=56,keys=keys,magic=magic,canoe=canoe,
                           whole_ram_png_exact=True,water_moving_frames=p.get('water_moving_frames')))
    comparisons=[]
    for label,source_name,index in [('canoe_chest','sms-auto-v0292-source-d4-canoe07',0x24),
                                    ('earth_warp','sms-auto-v0292-source-d4-warp02',0x5c)]:
        root='validation/natural-dungeon-combat/'+source_name
        c=load(root+'/capture.json');r=load(root+'/report.json')
        p=load(root+f'-assisted-fixed-replay-{c["frames"]}/replay_report.json')
        assert c['rom_sha256']==p['rom_sha256']==sms_digest and c['sram_input'] is None
        assert p['passed'] and p['whole_ram_bytes']==8192 and p['final_png_exact'] and not r['failure']
        for n,h in p['evidence'].items():assert sha(read(root+'/'+n))==h
        assist,writes=recording(ROOT/root,c)
        assert not assist['boss_assistance'] and all(address==0x305 for _,address,_ in writes)
        frame=c['frames'] if label=='canoe_chest' else r['earth_opened']['frame']+1
        source=extract(read(root+f'/ram_{frame:05d}.bin'),True)
        source['vram']=read(root+f'/vram_{frame:05d}.bin')
        native=current[label]
        for field in ['cells','map','items']:assert source[field]==native[field],(label,field)
        tiles=set()
        for dy in range(2):
            for dx in range(2):
                y=(index>>4)*2+dy;x=(index&15)*2+dx;off=y*64+x*2
                w=int.from_bytes(source['vram'][0x3800+off:0x3802+off],'little')
                assert source['vram'][0x3800+off:0x3802+off]==source['map'][off:off+2]
                translated=((w>>11)&1)<<13|((w>>12)&1)<<15|((w>>10)&1)<<12|((w>>9)&1)<<11|16+(w&511)
                pos=0xe000+(y+2)*128+x*2
                assert int.from_bytes(native['vram'][pos:pos+2],'little')==translated
                tiles.add(w&511)
        if label=='canoe_chest':
            for tile in tiles:assert sms_pixels(source['vram'],tile)==md_pixels(native['vram'],tile+16)
        comparisons.append(dict(kind=label,cells=160,map_bytes=1280,inventory_bytes=17,hardware_map_words=4,
                                static_tile_color_indices_exact=label=='canoe_chest'))
    read('tools/summarize_d4_canoe_v0304.py')
    result=dict(passed=True,version=304,md_sha256=digest,source_sha256=sms_digest,production_rom_unchanged=True,
                stages=stages,cross_source_native=comparisons,canoe_acquired=True,earth_warp_traversed=True,
                thief_room_cleared_with_different_inputs=True,source_softlock_not_patched=True,
                fourth_crystal_validated=False,full_game_validated=False,evidence=refs,
                limits=['Four native stages have independent fixed-input cold RAM/PNG replays with recorded approach-only hero_hurt writes. Equipment,keys,currency,position,health and progression are never injected.',
                        'Stationary axe starts alter the controller inputs and avoid the previously documented simultaneous lethal thief capture. No claim that the source edge case is repaired.',
                        'Two earlier natural SMS segments use the unchanged original ROM and their own verified recordings. Only specified cells,map,inventory,VDP words and static chest tile indices compare; actors,HP,gold,paths,timing,animated warp pixels,full image and audio do not.',
                        'The boss,crystal,return,ending,saves and full global fidelity require later evidence.'])
    (ROOT/'analysis/d4_canoe_v0304_report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('v304:canoe/warp/keys cold-replayed; bounded natural SMS chest/warp data comparisons exact;ROM unchanged')


if __name__=='__main__':main()
