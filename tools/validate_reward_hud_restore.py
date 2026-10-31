"""Compare actual SMS/MD HUD VRAM after controlled item and crystal windows."""
import argparse,contextlib,io,json
from run_core import ROOT,run
from archive_lossless_evidence import sha
from validate_playable_sprite_limit import symbols
from validate_actor_tick import PRESSES
from validate_key_door_gameplay import initial_room,rle_planes,maps
from audit_item_reward_visuals import sms_pixels,md_pixels


def translated(word):
    return ((word>>11)&1)<<13|((word>>12)&1)<<15|((word>>10)&1)<<12|((word>>9)&1)<<11|16+(word&511)


def main():
    p=argparse.ArgumentParser();p.add_argument('--trial',required=True);p.add_argument('--expect-bug',action='store_true');a=p.parse_args()
    out=ROOT/'validation'/a.trial;assert not out.exists();out.mkdir()
    source=ROOT/'input/original.sms';native=ROOT/'gaw-megadrive.bin';rom=source.read_bytes()
    sy=symbols(ROOT/'megadrive/out/release/symbol.txt')
    _,ext,_,_,arrays,_=initial_room(rom)
    patterns=bytearray(16384);meta=bytearray(2048)
    end,_=rle_planes(arrays['world_dungeon_background_rle'],0,patterns,0,4)
    rle_planes(arrays['world_dungeon_background_rle'],end,meta,0,2)
    def cells(room):
        raw=bytearray(160);offset=int.from_bytes(arrays['world_room_index'][room*2:room*2+2],'little')
        rle_planes(arrays['world_room_streams'],offset,raw,0,1);return bytes(raw)
    door=next(x for x in json.loads((ROOT/'analysis/doors_reference.json').read_bytes())['direct_unconditional_dungeon_doors'] if x['room']==16)
    outside=cells(16);osms,omd=maps(outside,ext)
    records={x['room']:x for x in json.loads((ROOT/'analysis/item_rewards_reference.json').read_bytes())['records']}
    rows=[]
    for region in ['auto','pal']:
        for kind,number,capacity in [('item',0x1b6,24),('item',0x1a2,24)]+[('gem',d,24 if d==1 else 56) for d in range(1,10)]:
            name=f'{kind}-{number:03x}-{region}';post=[3900,3920] if kind=='item' else [3400,3420]
            window=3500 if kind=='item' else 3700;post=post if kind=='item' else [4000,4020];finish=post[-1];folders={};states={}
            for tag,path in [('sms',source),('md',native)]:
                folder=out/(name+'-'+tag);folders[tag]=folder;writes=[]
                def w(frame,key,value,n=2):writes.append((frame,sy[key],value.to_bytes(n,'big')))
                presses=([(200,220,0)] if tag=='sms' else [])+(PRESSES if kind=='item' else PRESSES[:8])
                if kind=='item':
                    record=records[number];coord=record['coordinate']
                    x,y=next((x,y) for y in range(32,161,8) for x in range(32,225,8) if (((y-12)&248)*8+(((x-12)>>2)&62)+126)==coord)
                    room=cells(number);bg,md=maps(room,meta);flags=bytearray(256);flags[number&255]=16
                    actors=bytearray(768);actors[0]=1;actors[6]=255
                    if tag=='sms':
                        writes=[(3120,0xb9,b'\x10\0'),(3120,0xa4,door['script_entry'].to_bytes(2,'little')),(3120,0x1c00,outside),(3120,0x1600,osms),(3120,0x600,bytes(768)),(3120,0x310,((door['y']+8)<<8).to_bytes(2,'little')+(door['x']<<8).to_bytes(2,'little')),
                                (3400,0xb9,number.to_bytes(2,'little')),(3400,0xa4,record['entry'].to_bytes(2,'little')),(3400,0x100,bytes(flags)),(3400,0x1c00,room),(3400,0x1600,bg),(3400,0x600,actors),(3400,0x4b0,bytes(336)),(3400,0x310,(y<<8).to_bytes(2,'little')+(x<<8).to_bytes(2,'little')+bytes(4)),(3400,0x304,b'\0'),(3400,0x30a,b'\0'),(3400,0x64,b'\0'),(3400,0x62,coord.to_bytes(2,'little')),(3400,0xa8,b'\0'),(3400,0xa9,b'\0'),(3400,0xde,b'\x02')]
                    else:
                        for f,k,v in [(3120,'room_id',16),(3120,'world_graphics_class',0),(3120,'hero_y',(door['y']+8)<<8),(3120,'hero_x',door['x']<<8),(3400,'room_id',number),(3400,'world_actor_count',1),(3400,'hero_x',x<<8),(3400,'hero_y',y<<8),(3400,'hero_counter',0),(3400,'hero_dx',0),(3400,'hero_dy',0),(3400,'hero_keys',2),(3400,'hero_direction',0),(3400,'room_shutter_state',0),(3400,'room_shutter_direction',0),(3400,'room_script_coordinate_pending',1)]:w(f,k,v)
                        writes += [(3120,sy['scratch']+0x800,outside),(3120,sy['sms_vram']+0x3800,osms),(3120,sy['world_new_md'],omd),(3120,sy['world_actor_state'],bytes(768)),(3400,sy['game_save_state']+0x50,bytes(flags)),(3400,sy['scratch']+0x800,room),(3400,sy['sms_vram']+0x3800,bg),(3400,sy['world_new_md'],md),(3400,sy['md_map'],md),(3400,sy['world_spell_state'],bytes(48)),(3400,sy['world_loot_state'],bytes(336)),(3400,sy['world_actor_state'],actors),(3400,sy['dungeon_animation_scan'],b'\0'),(3400,sy['dungeon_animation_phase'],b'\0')]
                    presses += [(3125,3129,4),(3410,3440,4),(3700,3700,8)]
                else:
                    actor=bytearray(768);actor[0]=15
                    if tag=='sms':
                        writes=[(2800,0x600,actor),(2800,0x37,bytes([number])),(2800,0xae,b'\x55'),(2800,0xda,bytes([capacity,5,24])),(2800,0x318,bytes([24 if capacity==24 else capacity-8])),(3000,0x603,b'\x07')]
                    else:
                        writes=[(2800,sy['world_actor_state'],actor),(3000,sy['world_actor_state']+3,b'\x07')]
                        for k,v,n in [('world_dungeon_number',number,2),('world_boss_state',0x55,1),('hero_max_health',capacity,2),('hero_health',24 if capacity==24 else capacity-8,2),('hero_magic',5,2),('hero_max_magic',24,2)]:w(2800,k,v,n)
                    # Match the real dungeon-entry context rather than seeding a gem in the exterior.
                    writes=[(f+600,address,value) for f,address,value in writes]
                    if tag=='sms':
                        writes += [(3120,0xb9,b'\x10\0'),(3120,0xa4,door['script_entry'].to_bytes(2,'little')),(3120,0x1c00,outside),(3120,0x1600,osms),(3120,0x600,bytes(768)),(3120,0x310,((door['y']+8)<<8).to_bytes(2,'little')+(door['x']<<8).to_bytes(2,'little'))]
                    else:
                        for k,v in [('room_id',16),('world_graphics_class',0),('hero_y',(door['y']+8)<<8),('hero_x',door['x']<<8)]:w(3120,k,v)
                        writes += [(3120,sy['scratch']+0x800,outside),(3120,sy['sms_vram']+0x3800,osms),(3120,sy['world_new_md'],omd),(3120,sy['world_actor_state'],bytes(768))]
                    writes.sort(key=lambda row:row[0])
                    presses=([(200,220,0)] if tag=='sms' else [])+PRESSES+[(3125,3129,4),(3850,3853,8)]
                observed={}
                def observe(frame,raw):
                    if frame not in post:return
                    if tag=='sms':observed[frame]=dict(game=raw[0x1d],health=raw[0x318],capacity=raw[0xda],magic=raw[0xdb],hud=bytes(raw[0x1b00:0x1c00]).hex(),items=bytes(raw[0xe0:0xf1]).hex())
                    else:
                        data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big')
                        observed[frame]=dict(game=word('game_state'),health=word('hero_health'),capacity=word('hero_max_health'),magic=word('hero_magic'),active=word('item_reward_active'),hud=data('sms_vram',16384)[0x3d00:0x3e00].hex(),items=(bytes([word('hero_basic_level'),word('hero_weapon_level')])+data('hero_items',17)[2:]).hex())
                with contextlib.redirect_stdout(io.StringIO()):run(path,finish,folder,{window,*post},presses,ram_writes=writes,ram_observer=observe,core_options={'genesis_plus_gx_region_detect':region})
                states[tag]=observed
            for frame in post:
                left=states['sms'][frame];right=states['md'][frame]
                assert left['game']==right['game']==12 and not right['active'],(name,frame,'window did not close',left,right)
                assert all(left[k]==right[k] for k in ['health','capacity','magic','items']),(name,frame,'semantic mismatch')
                if kind=='item':assert bytes.fromhex(right['items'])[records[number]['inventory_offset']]==records[number]['value']
                else:assert right['capacity']==min(128,capacity+8) and right['health']==right['capacity'] and right['magic']==24
                sv=(folders['sms']/f'vram_{frame:05d}.bin').read_bytes();mv=(folders['md']/f'vram_{frame:05d}.bin').read_bytes();regs=(folders['md']/f'vdp_regs_{frame:05d}.bin').read_bytes();base=(regs[2]&56)<<10;width=[32,64,32,128][regs[16]&3]
                source_words=[int.from_bytes(sv[0x3d00+i*2:0x3d02+i*2],'little') for i in range(128)]
                mirror=bytes.fromhex(right['hud']);mirror_words=[int.from_bytes(mirror[i*2:i*2+2],'little') for i in range(128)]
                logical_bad=[i for i,(x,y) in enumerate(zip(source_words,mirror_words)) if (x&8191)!=(y&8191)];logical=len(logical_bad)
                if a.expect_bug and kind=='gem':assert logical_bad==[rom[0x1edc+(number-1)*2+1]//2],(name,frame,'unexpected software HUD difference',logical_bad)
                else:assert logical==0,(name,frame,'software HUD differs',logical)
                bad=[]
                for i,word in enumerate(source_words):
                    at=base+((i//32+22)*width+i%32)*2;actual=int.from_bytes(mv[at:at+2],'little')
                    if actual!=translated(word):bad.append(i)
                tiles=sorted({w&511 for w in source_words});pixel_bad=[t for t in tiles if sms_pixels(sv,t)!=md_pixels(mv,t+16)]
                row=dict(case=name,frame=frame,source_software_hud_exact=logical==0,software_word_mismatches=logical,hud_words=128,physical_word_mismatches=len(bad),first_word_mismatches=bad[:8],used_tiles=len(tiles),tile_pixel_mismatches=pixel_bad,window_closed=True,semantic_state_exact=True)
                rows.append(row);print(name,frame,'physical HUD differences',len(bad),'tile differences',len(pixel_bad),flush=True)
    passed=all(r['physical_word_mismatches']>0 for r in rows) if a.expect_bug else all(not r['physical_word_mismatches'] and not r['tile_pixel_mismatches'] for r in rows)
    result=dict(passed=passed,baseline_bug_expected=a.expect_bug,md_sha256=sha(native.read_bytes()),source_sha256=sha(source.read_bytes()),cases=rows,full_game_validated=False,scope='Two actual dungeon-item scripts and all nine crystal windows in both regions,two settled snapshots each. Explicit room/actor/contact/stat fixtures isolate restoration;not a natural campaign or full frame/audio/timing comparison.')
    (out/'report.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());assert passed,result


if __name__=='__main__':main()
