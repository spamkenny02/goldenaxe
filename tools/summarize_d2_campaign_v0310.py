"""Audit current v310 D2 keys, crystal and return from the cold D1 chain."""
import json
from run_core import ROOT
from archive_lossless_evidence import sha
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols
from validate_reward_hud_restore import translated

def main():
    refs={}
    def read(path):
        data=(ROOT/path).read_bytes();refs[path]=sha(data);return data
    def load(path):return json.loads(read(path))
    prior=load('analysis/d2_approach_v0310_report.json');digest=sha((ROOT/'gaw-megadrive.bin').read_bytes());assert prior['passed'] and prior['md_sha256']==digest
    sy=symbols(ROOT/'megadrive/out/release/symbol.txt');stages=[];all_writes=[];release=None;first=None;damage=None
    for suffix in ['key02','key03','key04','boss01','exit01']:
        root='validation/natural-dungeon-combat/md-auto-v0310-d2-'+suffix
        c=load(root+'/capture.json');r=load(root+'/report.json');end=c['frames'];proof_root=root+f'-assisted-fixed-replay-{end}'
        p=load(proof_root+'/replay_report.json');a,w=recording(ROOT/root,c);read(root+'/assistance.json')
        assert c['rom_sha256']==p['rom_sha256']==digest and c['sram_input']is None and p['passed'] and p['whole_ram_bytes']==65536 and p['final_png_exact'] and not p['feedback_reads']
        for n,h in p['evidence'].items():assert sha(read(root+'/'+n))==h
        for stem,ext in [('ram','bin'),('frame','png')]:assert read(root+f'/{stem}_{end:05d}.{ext}')==read(proof_root+f'/{stem}_{end:05d}.{ext}')
        assert len(a['episodes'])==2 and a['boss_room']==0x144 and not a['boss_assistance'] and not a['health_refills'] and not a['primary_state_imports'] and all(addr==sy['hero_hurt']for _,addr,_ in w)
        assert r['failure']is None and not r['deaths']
        raw=read(root+f'/ram_{end:05d}.bin');data=lambda n,k:bytes(raw[(sy[n]+i)^1]for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big')
        assert data('hero_items',17)[1]==1 and word('hero_selected_item')==word('hero_weapon_level')==1 and not word('sound_unhandled_command')
        save=data('game_save_state',592)
        if suffix.startswith('key'):
            assert r['new_key_verified'] and word('hero_health')==word('hero_max_health')==40 and a['first_boss_entry']is None
            assert save[0x1f:0x28]==bytes([128]+[0]*8)
        else:
            assert save[0x1f:0x28]==bytes([128,128]+[0]*7) and word('hero_max_health')==48
            assert a['release_write_frame']<a['first_boss_combat']['frame'] and a['first_boss_combat']['hurt']==0 and max(f for f,_,_ in w)==a['release_write_frame']
            release=a['release_write_frame'];first=a['first_boss_combat'];damage=a['first_boss_damage']
            if suffix=='boss01':
                assert r['room_cleared'] and word('room_id')==0x144 and word('hero_health')==48
                events=load(root+'/events.json')
                assert any(e.get('room')==0x144 and any(actor.get('type')==0x63 and actor.get('hp')==30 for actor in e.get('actors',[]))for e in events)
                assert first['health']==40
            else:assert r['full_dungeon_cleared'] and r['dungeon_exit_verified'] and word('room_id')==0xd6 and word('hero_health')>0 and a['unassisted_extension'] and a['new_assistance_writes']==0
            sms=data('sms_vram',16384);vram=read(root+f'/vram_{end:05d}.bin');regs=read(root+f'/vdp_regs_{end:05d}.bin');base=(regs[2]&56)<<10;width=[32,64,32,128][regs[16]&3]
            for n in range(128):
                at=base+((n//32+22)*width+n%32)*2;assert int.from_bytes(vram[at:at+2],'little')==translated(int.from_bytes(sms[0x3d00+n*2:0x3d02+n*2],'little'))
            original=(ROOT/'input/original.sms').read_bytes()
            for n in range(2):
                tile,off=original[0x1edc+n*2:0x1ede+n*2];assert sms[0x3d00+off:0x3d02+off]==bytes([tile,0x59])
        all_writes.append(w)
        stages.append(dict(trace=root,frames=end,room=word('room_id'),health=word('hero_health'),max_health=word('hero_max_health'),keys=word('hero_keys'),whole_ram_bytes=65536,final_png_exact=True,verified_prediction_windows=r.get('full_ram_prediction_matches',0)))
    assert all_writes[-1]==all_writes[-2]
    result=dict(passed=True,version=310,md_sha256=digest,second_crystal_and_exterior_return=True,production_rom_unchanged=True,stages=stages,release_frame=release,first_boss_combat=first,first_boss_damage=damage,boss_assistance=False,resource_writes=0,primary_state_imports=0,exit_new_assistance_writes=0,physical_hud_words_exact_each=128,crystal_markers_exact_each=2,source_campaign_compared=False,full_game_validated=False,evidence=refs,limits=['Cold New Game chain,with recorded approach-only hurt-counter aid;no resources,actors,progression or SRAM imported. D2 boss in144 is type63,not satellite type65.','Independent fixed full-RAM/PNG replay at every promoted checkpoint. Whole-game source R/IRQ,pixel/audio fidelity,later v310 progression and hardware remain open.'])
    (ROOT/'analysis/d2_campaign_v0310_report.json').write_bytes((json.dumps(result,indent=2)+'\n').encode())
    print('v310 D2 keys,second crystal and exterior return audited')

if __name__=='__main__':main()
