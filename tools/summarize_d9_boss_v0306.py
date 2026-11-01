"""Audit ordinary-damage ninth main boss; optional content remains explicit."""
import json
from run_core import ROOT
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols
from validate_reward_hud_restore import translated


def main():
    refs={}
    def read(n):
        raw=evidence(ROOT/n);refs[n]=sha(raw);return raw
    def load(n):return json.loads(read(n))
    prior=load('analysis/d9_navigation_v0306_report.json');assert prior['passed'] and not prior['main_boss_entered']
    digest=sha(read('versions/v0306-3a12380b/gaw-megadrive-v0306.bin'));assert digest==prior['md_sha256']==sha((ROOT/'gaw-megadrive.bin').read_bytes())
    sy=symbols(ROOT/'megadrive/out/release/symbol.txt');read('megadrive/out/release/symbol.txt');source=read('input/original.sms')
    assert source[0x3234e+0x1ac*8:0x32356+0x1ac*8]==bytes([0x6c]+[0]*7) and source[0x320ea+(0x6c-0x20)*4:0x320ee+(0x6c-0x20)*4]==bytes([90,30,6,64])
    index=load('validation/v0306-d9-navigation-sources/source_index.json')
    for n,h in index.items():assert sha(read('validation/v0306-d9-navigation-sources/'+n.split('/')[-1]))==h==sha((ROOT/n).read_bytes())
    selection=load('analysis/d9_boss_v0306_selection.json');previous=prior['ready_trace'];pc=load(previous+'/capture.json');pa,pw=recording(ROOT/previous,pc)
    stages=[];release=first=damage=fixed=None;predictions=0;crystal=False
    for name in selection['combat_traces']:
        root='validation/natural-dungeon-combat/'+name;c=load(root+'/capture.json');r=load(root+'/report.json');f=c['frames'];proof=root+f'-assisted-fixed-replay-{f}';p=load(proof+'/replay_report.json')
        assert c['rom_sha256']==r['rom_sha256']==p['rom_sha256']==digest and c['sram_input'] is None
        assert p['passed'] and p['whole_ram_bytes']==65536 and p['final_png_exact'] and not p['feedback_reads']
        assert r['recorded_new_game_prefix']==previous.split('/')[-1] and r['prefix_end']==pc['frames'] and f>pc['frames'] and not r['deaths']
        assert r['failure'] in [None,'frame_limit'] and r['full_ram_prediction_matches']==r['verified_persistent_prediction_windows'] and r['stack_only_difference_windows']==0 and r['primary_state_imports']==0
        predictions+=r['full_ram_prediction_matches']
        for n,h in p['evidence'].items():assert sha(read(root+'/'+n))==h
        for stem,ext in [('ram','bin'),('frame','png')]:assert read(root+f'/{stem}_{f:05d}.{ext}')==read(proof+f'/{stem}_{f:05d}.{ext}')
        a,w=recording(ROOT/root,c);read(root+'/assistance.json');assert len(a['episodes'])==12 and a['boss_room']==0x1ac and not a['boss_assistance'] and not a['health_refills'] and not a['primary_state_imports']
        if release is None:
            release=a['release_write_frame'];first=a['first_boss_combat'];assert release<first['frame'] and first['health']==96 and first['hurt']==0
            assert w[:len(pw)]==pw and w[-1]==(release,sy['hero_hurt'],b'\x00\x00');fixed=w
            assert r['entry_boss_kind']==0x6c and r['entry_resource_or_actor_writes']==0 and r['entry_completed_rooms']==[0x1ac] and r['entry_inputs'] and all(row['buttons']==[4] for row in r['entry_inputs'])
            assert sha(read(root+'/entry_controller.py'))==r['entry_controller_sha256']==index['tools/entered_boss_route.py']
        else:assert w==fixed and a['release_write_frame']==release and a['first_boss_combat']==first
        assert all(addr==sy['hero_hurt'] and frame<=release for frame,addr,_ in w)
        if damage is None and a['first_boss_damage']:damage=a['first_boss_damage']
        raw=read(root+f'/ram_{f:05d}.bin');data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big');save=data('game_save_state',592);actors=data('world_actor_state',768)
        assert word('game_state')==12 and word('room_id')==0x1ac and word('hero_health')>0 and word('hero_hurt')<=128
        assert r['equip_basic_requested'] and word('hero_selected_item')==0 and word('hero_basic_level')==2 and word('hero_attack')==6
        assert save[0x1f:0x27]==bytes([128]*8) and data('hero_items',17)[11]==0 and data('hero_items',17)[15]==data('hero_items',17)[16]==1
        if save[0x27]==128:
            assert word('hero_max_health')==104 and word('hero_health')==104 and word('hero_magic')==word('hero_max_magic') and r['room_cleared'] and not word('item_reward_active');crystal=True
        else:assert save[0x27] in [0,1] and word('hero_max_health')==96
        stages.append(dict(trace=root,frames=f,health=word('hero_health'),max_health=word('hero_max_health'),magic=word('hero_magic'),gold=word('hero_gold'),keys=word('hero_keys'),progress=save[0x27],remaining_boss_hp=[actors[i*48+24] for i in range(8) if actors[i*48]==0x6c and actors[i*48+24]],whole_ram_png_exact=True));previous,pc,pa,pw=root,c,a,w
    if crystal:
        sms=data('sms_vram',16384);v=read(previous+f'/vram_{pc["frames"]:05d}.bin');regs=read(previous+f'/vdp_regs_{pc["frames"]:05d}.bin');base=(regs[2]&56)<<10;width=[32,64,32,128][regs[16]&3]
        for n in range(128):
            at=base+((n//32+22)*width+n%32)*2;assert int.from_bytes(v[at:at+2],'little')==translated(int.from_bytes(sms[0x3d00+n*2:0x3d02+n*2],'little'))
        for n in range(9):
            tile,offset=source[0x1edc+n*2:0x1ede+n*2];assert sms[0x3d00+offset:0x3d02+offset]==bytes([tile,0x59])
    rejected=load('validation/natural-dungeon-combat/md-auto-v0306-d9-boss01/report.json');assert rejected['failure']=='frame_limit' and not rejected['room_cleared'] and rejected['full_ram_prediction_matches']==71
    read('tools/summarize_d9_boss_v0306.py')
    result=dict(passed=True,version=306,md_sha256=digest,production_rom_unchanged=True,stages=stages,current_campaign_trace=previous,campaign_frames=pc['frames'],ninth_crystal_obtained=crystal,main_boss_assistance=False,guard_release_frame=release,first_boss_combat=first,first_boss_damage=damage,full_ram_prediction_windows=predictions,full_game_validated=False,evidence=refs,limits=['Original6C stats90HP,30damage,6armor. Real LongSword2 strength6,ordinary entry UP,then16-frame input search. No boss or resource fixtures.','Initial boss01 controller repeatedly left the bottom doorway and made no boss progress; excluded.','Nine crystals,when verified,do not prove exterior return,optional19C/Balloon,Golden Axe,ending,saves,global source RNG,audiovisual fidelity or hardware. Stack still covers D8 only.'])
    (ROOT/'analysis/d9_boss_v0306_report.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());print('D9 main checkpoint verified; ninth crystal=',crystal,'windows=',predictions)

if __name__=='__main__':main()
