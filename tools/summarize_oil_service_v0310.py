"""Audit the real late oil gift, both stairs and unchanged inherited aid."""
import json
from run_core import ROOT
from archive_lossless_evidence import sha
from assisted_prefix import recording,prefix_writes
from validate_playable_sprite_limit import symbols
from validate_reward_hud_restore import translated

def main():
    refs={}
    def read(name):
        raw=(ROOT/name).read_bytes();refs[name]=sha(raw);return raw
    def load(name):return json.loads(read(name))
    prior=load('analysis/d2_campaign_v0310_report.json');digest=sha((ROOT/'gaw-megadrive.bin').read_bytes());assert prior['passed']and prior['md_sha256']==digest
    sy=symbols(ROOT/'megadrive/out/release/symbol.txt');roots=['validation/natural-dungeon-route/md-v0310-oil-route01','validation/natural-service-route/md-v0310-oil-service01'];writes=[];stages=[]
    for n,root in enumerate(roots):
        c=load(root+'/capture.json');r=load(root+('/route_report.json'if n==0 else'/report.json'));end=c['frames'];a,w=recording(ROOT/root,c)
        proof_root=root+f'-assisted-fixed-replay-{end}';p=load(proof_root+'/replay_report.json')
        assert c['rom_sha256']==digest and c['sram_input']is None and p['passed']and p['whole_ram_bytes']==65536 and p['final_png_exact']and not p['feedback_reads']
        assert prefix_writes(ROOT/root,c,True)==w and all(addr==sy['hero_hurt']for _,addr,_ in w)and len(a['episodes'])==3 and a['first_boss_entry']is None
        assert not a['health_refills']and not a['primary_state_imports']and not a['boss_assistance']and r['failure']is None
        for name,h in p['evidence'].items():assert sha(read(root+'/'+name))==h
        for stem,ext in [('ram','bin'),('frame','png')]:assert read(root+f'/{stem}_{end:05d}.{ext}')==read(proof_root+f'/{stem}_{end:05d}.{ext}')
        raw=read(root+f'/ram_{end:05d}.bin');data=lambda name,k:bytes(raw[(sy[name]+i)^1]for i in range(k));word=lambda name:int.from_bytes(data(name,2),'big')
        assert not word('sound_unhandled_command')and word('hero_health')==31 and word('hero_gold')==2 and word('hero_magic')==24
        assert data('game_save_state',592)[0x1f:0x28]==bytes([128,128]+[0]*7)
        if n==0:assert r['reached_entrance']and word('room_id')==0x1f and not data('hero_items',17)[8]
        else:
            assert r['passed']and r['new_assistance_writes']==0 and r['primary_state_imports']==0 and word('room_id')==0xc7 and data('hero_items',17)[8]==1 and data('game_save_state',592)[0x117]&2
            assert r['driver_sha256']==sha(read(root+'/oil_stairs_driver.py'))
            events=load(root+'/events.json');rooms=[]
            for event in events:
                if not rooms or rooms[-1]!=event['room']:rooms.append(event['room'])
            assert rooms==[0x1f,0x0f,0x1f,0xc7],rooms
            controls=load(root+'/controls.json');previous=load(roots[0]+'/controls.json');assert controls[:len(previous)]==previous and all(row['frame']>r['first_state'].get('frame',load(roots[0]+'/capture.json')['frames'])for row in controls[len(previous):])
            sms=data('sms_vram',16384);vram=read(root+f'/vram_{end:05d}.bin');regs=read(root+f'/vdp_regs_{end:05d}.bin');base=(regs[2]&56)<<10;width=[32,64,32,128][regs[16]&3]
            for cell in range(128):
                at=base+((cell//32+22)*width+cell%32)*2;assert int.from_bytes(vram[at:at+2],'little')==translated(int.from_bytes(sms[0x3d00+cell*2:0x3d02+cell*2],'little'))
        writes.append(w);stages.append(dict(trace=root,frames=end,room=word('room_id'),oil=data('hero_items',17)[8],health=word('hero_health'),whole_ram_bytes=65536,final_png_exact=True))
    assert writes[0]==writes[1]
    result=dict(passed=True,md_sha256=digest,stages=stages,real_oil_gift=True,stairs_and_return_rooms=[0x1f,0x0f,0x1f,0xc7],gold_unchanged=2,magic_unchanged=24,health_unchanged=31,new_test_writes=0,resource_writes=0,primary_state_imports=0,physical_hud_words_exact=128,full_game_validated=False,evidence=refs,limits=['Late visit after two crystals,with the unchanged canonical approach-only hurt writes inherited. No resource/actor/progression writes,SRAM or primary snapshots.','One real gift and indoor stair roundtrip;source timing/global R/IRQ and whole-game fidelity are not established.'])
    (ROOT/'analysis/oil_service_v0310_report.json').write_bytes((json.dumps(result,indent=2)+'\n').encode())
    print('Oil gift,stairs,exit and unchanged inherited aid audited')

if __name__=='__main__':main()
