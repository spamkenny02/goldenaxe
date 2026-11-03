"""Audit fresh v310 New Game -> first crystal -> exterior, with bounded aid."""
import json
from run_core import ROOT
from archive_lossless_evidence import sha
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols
from validate_reward_hud_restore import translated

def main():
    refs={}
    def read(name):
        raw=(ROOT/name).read_bytes();refs[name]=sha(raw);return raw
    def load(name):return json.loads(read(name))
    digest=sha(read('gaw-megadrive.bin'));assert digest=='32fe75a653d7152f7cbf873a32f2ffef14234ea190885ae8a8235f2ccd10e071'
    sy=symbols(ROOT/'megadrive/out/release/symbol.txt');stages=[];assisted=[]
    for family,name,kind in [('natural-dungeon-route','md-v0310-d1-entry01','entry'),('natural-dungeon-combat','md-auto-v0310-d1-key01','key'),('natural-dungeon-combat','md-auto-v0310-d1-gem03','crystal'),('natural-dungeon-combat','md-auto-v0310-d1-exit01','exit')]:
        root='validation/'+family+'/'+name;c=load(root+'/capture.json');r=load(root+('/route_report.json'if kind=='entry'else'/report.json'));end=c['frames']
        assert c['rom_sha256']==digest and c['sram_input']is None and r['failure']is None
        proof_root=root+(f'-assisted-fixed-replay-{end}'if kind in ['crystal','exit']else'-fixed-replay')
        proof=load(proof_root+'/replay_report.json');assert proof['passed'] and proof['rom_sha256']==digest and proof['whole_ram_bytes']==65536 and proof['final_png_exact'] and not proof['feedback_reads']
        for n,h in proof['evidence'].items():assert sha(read(root+'/'+n))==h
        raw=read(root+f'/ram_{end:05d}.bin')
        for stem,ext in [('ram','bin'),('frame','png')]:assert read(root+f'/{stem}_{end:05d}.{ext}')==read(proof_root+f'/{stem}_{end:05d}.{ext}')
        data=lambda n,k:bytes(raw[(sy[n]+i)^1]for i in range(k))
        word=lambda n:int.from_bytes(data(n,2),'big')
        assert word('hero_health')>0 and not word('sound_unhandled_command') and data('hero_items',17)==bytes(17)
        if kind in ['entry','key']:
            assert not c['test_ram_writes'] and not r['ram_injections'] and word('hero_health')==14
            if kind=='entry':assert r['reached_entrance'] and r['directional_probe_succeeded'] and word('room_id')==0x1e4
            else:assert r['new_key_verified'] and word('hero_keys')==1 and word('room_id')==0x1e5
        else:
            a,w=recording(ROOT/root,c);read(root+'/assistance.json');driver=read(root+'/assisted_route_driver.py');assert sha(driver)==a['driver_sha256']
            assert a['activation_after_frame']==4989 and a['release_write_frame']==13546 and a['first_boss_combat']==dict(frame=13617,health=10,hurt=0)
            assert a['first_boss_damage']==dict(frame=13709,before=10,after=6,hurt=47)
            assert not a['health_refills'] and not a['primary_state_imports'] and not a['boss_assistance'] and all(address==sy['hero_hurt'] and 4989<f<=13546 for f,address,_ in w)
            assisted.append(w)
            assert data('game_save_state',592)[0x1f:0x28]==bytes([128]+[0]*8)
            assert word('hero_max_health')==32 and r['planning_decisions']==r['verified_persistent_prediction_windows']==r['full_ram_prediction_matches']==(32 if kind=='crystal'else 16)
            if kind=='crystal':assert r['room_cleared'] and word('hero_health')==32 and word('room_id')==0x175
            else:assert r['dungeon_exit_verified'] and r['full_dungeon_cleared'] and word('room_id')==0xb9 and word('hero_health')==28 and a['new_assistance_writes']==0 and a['unassisted_extension']
            sms=data('sms_vram',16384);vram=read(root+f'/vram_{end:05d}.bin');regs=read(root+f'/vdp_regs_{end:05d}.bin');base=(regs[2]&56)<<10;width=[32,64,32,128][regs[16]&3]
            for n in range(128):
                at=base+((n//32+22)*width+n%32)*2;assert int.from_bytes(vram[at:at+2],'little')==translated(int.from_bytes(sms[0x3d00+n*2:0x3d02+n*2],'little'))
            original=(ROOT/'input/original.sms').read_bytes();tile,off=original[0x1edc:0x1ede];assert sms[0x3d00+off:0x3d02+off]==bytes([tile,0x59])
        stages.append(dict(kind=kind,trace=root,frames=end,room=word('room_id'),health=word('hero_health'),max_health=word('hero_max_health'),whole_ram_bytes=65536,final_png_exact=True))
    assert assisted[0]==assisted[1]
    failed=load('validation/natural-dungeon-combat/md-auto-v0310-d1-gem01/events.json');drops=[];last=14
    for e in failed:
        if e['health']<last:drops.append(dict(frame=e['frame'],before=last,after=e['health']))
        last=e['health']
    assert drops[-4:]==[dict(frame=13481+n,before=14-n*4,after=max(0,10-n*4))for n in range(4)]
    out=dict(passed=True,version=310,md_sha256=digest,production_rom_unchanged=True,stages=stages,first_crystal_and_exit_verified=True,source_campaign_compared=False,approach_assistance_after_frame=4989,last_assistance_write=13546,first_boss_combat_frame=13617,hero_health_at_boss_entry=10,boss_assistance=False,health_refills=0,resource_writes=0,primary_state_imports=0,exit_new_assistance_writes=0,full_ram_prediction_matches=48,physical_hud_words_exact_each=128,crystal_marker_exact_each=1,excluded_old_guard_drops=drops[-4:],evidence=refs,full_game_validated=False,limits=['Fresh v310 cold New Game,first key without aid;logged hurt-counter protection on later approach only. Boss and return have no guard,resource writes or imported primary state.','One NTSC first-dungeon path. The completed v309 full campaign remains historical;later v310 dungeons,optional content,global SMS R/IRQ fidelity and hardware remain open.','The excluded gem01 pilot erased normal terrain cooldown;gem02 died in real boss combat. Successful gem03 uses cautious ordinary-input planning,with independent full RAM/PNG replay.'])
    (ROOT/'analysis/d1_campaign_v0310_report.json').write_bytes((json.dumps(out,indent=2)+'\n').encode())
    print('v310 first crystal and outsideB9 audited:28/32HP,48 exact predictions,4 cold replays')

if __name__=='__main__':main()
