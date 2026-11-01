"""Audit the actual unguarded ninth-dungeon exit and nine-crystal exterior HUD."""
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
    prior=load('analysis/d9_boss_v0306_report.json');assert prior['passed'] and prior['ninth_crystal_obtained'];digest=prior['md_sha256'];assert sha(read('versions/v0306-3a12380b/gaw-megadrive-v0306.bin'))==digest==sha((ROOT/'gaw-megadrive.bin').read_bytes())
    sy=symbols(ROOT/'megadrive/out/release/symbol.txt');read('megadrive/out/release/symbol.txt');previous=prior['current_campaign_trace'];pc=load(previous+'/capture.json');pa,pw=recording(ROOT/previous,pc)
    root='validation/natural-dungeon-combat/md-auto-v0306-d9-exit01';c=load(root+'/capture.json');r=load(root+'/report.json');f=c['frames'];proof=root+f'-assisted-fixed-replay-{f}';p=load(proof+'/replay_report.json')
    assert c['rom_sha256']==r['rom_sha256']==p['rom_sha256']==digest and c['sram_input'] is None and r['failure'] is None and not r['deaths']
    assert r['recorded_new_game_prefix']==previous.split('/')[-1] and r['prefix_end']==pc['frames'] and f>pc['frames'] and r['full_dungeon_cleared'] and r['dungeon_exit_verified'] and not r['exit_before_crystal_requested']
    assert p['passed'] and p['whole_ram_bytes']==65536 and p['final_png_exact'] and not p['feedback_reads']
    for n,h in p['evidence'].items():assert sha(read(root+'/'+n))==h
    for stem,ext in [('ram','bin'),('frame','png')]:assert read(root+f'/{stem}_{f:05d}.{ext}')==read(proof+f'/{stem}_{f:05d}.{ext}')
    a,w=recording(ROOT/root,c);read(root+'/assistance.json');assert w==pw and a['unassisted_extension'] and a['new_assistance_writes']==0 and a['release_write_frame']==pa['release_write_frame']
    assert all(frame<=a['release_write_frame'] and addr==sy['hero_hurt'] for frame,addr,_ in w) and not a['boss_assistance'] and not a['health_refills'] and not a['primary_state_imports']
    raw=read(root+f'/ram_{f:05d}.bin');data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big');save=data('game_save_state',592);items=data('hero_items',17)
    assert word('room_id')==0xeb and word('world_dungeon_number')==0 and word('game_state')==12 and word('hero_health')>0 and word('hero_max_health')==104 and word('hero_hurt')<=128
    assert save[0x1f:0x28]==bytes([128]*9) and items[1]==1 and items[11]==0 and items[15]==items[16]==1 and word('hero_selected_item')==1 and word('hero_basic_level')==2 and r['equip_axe_requested']
    assert r['full_ram_prediction_matches']==r['verified_persistent_prediction_windows'] and r['stack_only_difference_windows']==0 and r['primary_state_imports']==0
    sms=data('sms_vram',16384);v=read(root+f'/vram_{f:05d}.bin');regs=read(root+f'/vdp_regs_{f:05d}.bin');base=(regs[2]&56)<<10;width=[32,64,32,128][regs[16]&3]
    for n in range(128):
        at=base+((n//32+22)*width+n%32)*2;assert int.from_bytes(v[at:at+2],'little')==translated(int.from_bytes(sms[0x3d00+n*2:0x3d02+n*2],'little'))
    original=read('input/original.sms')
    for n in range(9):
        tile,off=original[0x1edc+n*2:0x1ede+n*2];assert sms[0x3d00+off:0x3d02+off]==bytes([tile,0x59])
    read('tools/natural_exit_planner.py');read('tools/summarize_d9_campaign_v0306.py')
    result=dict(passed=True,version=306,md_sha256=digest,production_rom_unchanged=True,current_campaign_trace=root,campaign_frames=f,room=word('room_id'),health=word('hero_health'),max_health=word('hero_max_health'),magic=word('hero_magic'),gold=word('hero_gold'),keys=word('hero_keys'),nine_crystals_and_exterior_exit=True,ninth_boss_unassisted=True,return_unassisted=True,boss_prediction_windows=prior['full_ram_prediction_windows'],return_prediction_windows=r['full_ram_prediction_matches'],hud_words=128,owned_crystal_markers=9,full_game_validated=False,evidence=refs,limits=['All nine crystals and this return are verified on v0306. No health,resources,actors,progression or SRAM imports.','Optional19C/7B and Balloon,Golden Axe,final boss,ending,saves and broad source fidelity remain unvalidated.','Full instruction stack coverage remains the prior D8 profile. Repeat the broad profile at the final campaign milestone rather than after each ordinary room.'])
    (ROOT/'analysis/d9_campaign_v0306_report.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());print('Nine crystals and exterior return verified:',result['health'],'/',result['max_health'],'HP')

if __name__=='__main__':main()
