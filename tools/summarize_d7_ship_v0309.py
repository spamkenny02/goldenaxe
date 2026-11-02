"""Audit guarded D7 approach resumed after a verified ordinary intermediate victory."""
import json
from run_core import ROOT
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols
from validate_reward_hud_restore import translated

def main():
 refs={}
 def read(name):
  raw=evidence(ROOT/name);refs[name]=sha(raw);return raw
 def load(name):return json.loads(read(name))
 prior=load('analysis/d7_midboss_v0309_report.json');assert prior['passed'] and prior['intermediate_defeated'] and not prior['intermediate_assistance']
 digest=prior['md_sha256'];assert sha((ROOT/'gaw-megadrive.bin').read_bytes())==digest
 sy=symbols(ROOT/'megadrive/out/release/symbol.txt');read('megadrive/out/release/symbol.txt')
 contacts=load('analysis/contact_script_reference.json');remote=next(r for r in contacts['records'] if r['room']==0x1e6 and r['kind']=='stationary_up_passages');assert remote['coordinate']==332 and remote['explicit_registers']['d']==4 and remote['explicit_registers']['e']==0xd6
 rewards=load('analysis/item_rewards_reference.json');ship=next(r for r in rewards['records'] if r['room']==0x1d5);assert ship['inventory_offset']==16 and ship['value']==1
 index={'tools/'+n:h for n,h in load('validation/v0309-d7-ship-sources/source_index.json').items()}
 for name in ['tools/resume_after_intermediate.py','tools/assisted_boss_route.py','tools/natural_item_acquisition.py']:
  assert sha(read('validation/v0309-d7-ship-sources/'+name.split('/')[-1]))==index[name] and sha((ROOT/name).read_bytes())==index[name]
 previous=prior['current_campaign_trace'];pc=load(previous+'/capture.json');pa,pw=recording(ROOT/previous,pc)
 assert pa['approach_closed_early'] and pa['release_write_frame']==prior['guard_release_frame']
 stages=[];final=None;new_guard=None
 for suffix in ['approach-resume01','south01','remote1e6-01','ship02']:
  root='validation/natural-dungeon-combat/md-auto-v0309-d7-'+suffix;c=load(root+'/capture.json');r=load(root+'/report.json');frame=c['frames'];proof=root+f'-assisted-fixed-replay-{frame}';p=load(proof+'/replay_report.json')
  assert c['rom_sha256']==r['rom_sha256']==p['rom_sha256']==digest and c['sram_input'] is None
  assert p['passed'] and p['whole_ram_bytes']==65536 and p['final_png_exact'] and not p['feedback_reads']
  assert r['failure'] is None and not r.get('deaths',0) and r['prefix_end']==pc['frames'] and r['recorded_new_game_prefix']==previous.split('/')[-1]
  for name,h in p['evidence'].items():assert sha(read(root+'/'+name))==h
  for stem,ext in [('ram','bin'),('frame','png')]:assert read(root+f'/{stem}_{frame:05d}.{ext}')==read(proof+f'/{stem}_{frame:05d}.{ext}')
  raw=read(root+f'/ram_{frame:05d}.bin');data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big');save=data('game_save_state',592)
  a,w=recording(ROOT/root,c);read(root+'/assistance.json');assert len(a['episodes'])==8 and a['boss_room']==0x179
  assert all(a[k] is None for k in ['first_boss_entry','release_write_frame','first_boss_combat','first_boss_damage'])
  assert all(address==sy['hero_hurt'] for _,address,_ in w) and not a['health_refills'] and not a['primary_state_imports'] and not a['boss_assistance']
  assert word('game_state')==12 and word('hero_health')>0 and word('hero_max_health')==80 and save[0x1f:0x28]==bytes([128]*6+[0]*3)
  assert data('hero_items',17)[16]==(1 if suffix=='ship02' else 0)
  if suffix=='approach-resume01':
   new_guard=r['new_guard_frame'];assert w==pw+[(new_guard,sy['hero_hurt'],b'\x00\x81')] and word('hero_hurt')==129 and frame==pc['frames']+1
   assert r['passed'] and r['resumed_after_verified_intermediate'] and r['driver_sha256']==index['tools/resume_after_intermediate.py']
   assert a['episodes'][:6]==pa['episodes'][:6]
   ep=a['episodes'][-2];old=pa['episodes'][-1];assert ep['activation_after_frame']==old['activation_after_frame'] and ep['release_write_frame']==old['release_write_frame']
   assert ep['boss_room']==0x1b8 and ep['first_boss_combat']==r['first_intermediate_combat'] and ep['first_boss_combat']['frame']==prior['first_intermediate_combat']['frame'] and ep['first_boss_combat']['hurt']==0
   assert ep['first_boss_damage']==prior['first_intermediate_damage'] and ep['end_frame']==pc['frames'] and a['episodes'][-1]['activation_after_frame']==pc['frames']
   assert a['intermediate_entry_cold_verified'] and a['main_boss_never_entered_in_prefix']
   previous_raw=read(previous+f'/ram_{pc["frames"]:05d}.bin')
   for name,size in [('hero_health',2),('hero_gold',2),('hero_keys',2),('hero_magic',2),('hero_items',17),('game_save_state',592)]:assert data(name,size)==bytes(previous_raw[(sy[name]+i)^1] for i in range(size))
  else:
   assert a['preserve_floor_hurt_requested'] and w[:len(pw)]==pw and a['episodes'][:-1]==pa['episodes'][:-1]
   if suffix=='south01':assert r['room_cleared'] and word('room_id')==0x1d6 and save[0x50+0xb8]&0x40
   if suffix=='remote1e6-01':assert r['contact_route_passed'] and r['contact_state_writes']==0 and r['contact_coordinate']==332 and word('room_id')==0x1d6
   if suffix in ['remote1e6-01','ship02']:assert save[0x50+0xe6]&4 and save[0x50+0xd6]&0x40 and save[0x50+0xd5]&0x80
   if suffix=='ship02':
    assert r['passed'] and r['item_acquisition_passed'] and r['item_acquisition_state_writes']==0 and not r['item_acquisition_first']['owned'] and r['item_acquisition_last']['owned']==1
    assert r['item_acquisition_driver_sha256']==index['tools/natural_item_acquisition.py'] and not word('item_reward_active') and word('hero_state')==1
  stages.append(dict(trace=root,frames=frame,room=word('room_id'),health=word('hero_health'),keys=word('hero_keys'),gold=word('hero_gold'),magic=word('hero_magic'),ship_owned=bool(data('hero_items',17)[16]),whole_ram_png_exact=True))
  previous,pc,pa,pw=root,c,a,w;final=raw
 actors=data('world_actor_state',768);traps=[(i,actors[i*48],actors[i*48+24]) for i in range(8) if actors[i*48]==0x5e];others=[(i,actors[i*48],actors[i*48+24]) for i in range(8) if actors[i*48] and actors[i*48]!=0x5e]
 assert len(traps)==4 and all(hp==0 for _,_,hp in traps) and not r['room_cleared']
 live_actors=[dict(slot=i,kind=actors[i*48],hp=actors[i*48+24]) for i in range(8) if actors[i*48]>=0x20 and actors[i*48+24]]
 sms=data('sms_vram',16384);v=read(previous+f'/vram_{pc["frames"]:05d}.bin');regs=read(previous+f'/vdp_regs_{pc["frames"]:05d}.bin');base=(regs[2]&56)<<10;width=[32,64,32,128][regs[16]&3]
 for n in range(128):
  at=base+((n//32+22)*width+n%32)*2;assert int.from_bytes(v[at:at+2],'little')==translated(int.from_bytes(sms[0x3d00+n*2:0x3d02+n*2],'little'))
 original=read('input/original.sms')
 for n in range(6):
  tile,offset=original[0x1edc+n*2:0x1ede+n*2];assert sms[0x3d00+offset:0x3d02+offset]==bytes([tile,0x59])
 read('tools/summarize_d7_ship_v0309.py')
 result=dict(passed=True,version=309,md_sha256=digest,production_rom_unchanged=True,stages=stages,current_campaign_trace=previous,campaign_frames=pc['frames'],ship_acquired=True,intermediate_victory_without_assistance=True,new_approach_guard_frame=new_guard,main_boss_entered=False,seventh_crystal_obtained=False,six_crystals_preserved=True,final_hud_words_exact=128,source_crystal_markers_exact=6,persistent_floor_traps_retained=4,remaining_live_actors=live_actors,unassisted_south_branch_retested=False,full_game_validated=False,evidence=refs,limits=['The intermediate fight remains unassisted. Approach protection resumes only after its actual verified defeat and must be released before main boss179. No unassisted south-route failure is claimed on this version.','Guard writes affect only hero_hurt. No HP,magic,ownership,actors,progression or SRAM state is imported. The ship window closes through ordinary game input.','Cold RAM/PNG checkpoints and final HUD checks do not prove whole-source RNG,audiovisual fidelity,ending,saves,hardware behavior or an extended stack bound.'])
 (ROOT/'analysis/d7_ship_v0309_report.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());print('D7 ship acquired after unassisted intermediate; four cold gates and128 HUD words exact')
if __name__=='__main__':main()
