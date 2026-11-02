"""Audit resumed D8 approach, remote mechanisms and real thief-key acquisition."""
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
 prior=load('analysis/d8_midboss_v0309_report.json');assert prior['passed'] and prior['intermediate_defeated'] and not prior['intermediate_assistance']
 digest=sha(read('versions/v0309-7270576d/gaw-megadrive-v0309.bin'));assert digest==prior['md_sha256']==sha((ROOT/'gaw-megadrive.bin').read_bytes())
 sy=symbols(ROOT/'megadrive/out/release/symbol.txt');read('megadrive/out/release/symbol.txt');index=load('validation/v0309-d8-thief-sources/source_index.json')
 for name,h in index.items():assert sha(read('validation/v0309-d8-thief-sources/'+name.split('/')[-1]))==h and sha((ROOT/name).read_bytes())==h
 recipes=load('validation/v0309-d8-thief-sources/thief_recipes.json');assert len(recipes)==7
 for recipe in recipes:
  if recipe['historical']:assert sha(read(recipe['historical']))==recipe['sha256']
 original=read('input/original.sms');assert original[0x3234e+0x196*8]==0x6b and original[0x320ea+(0x6b-0x20)*4:0x320ee+(0x6b-0x20)*4]==bytes([80,16,2,64])
 previous=prior['current_campaign_trace'];pc=load(previous+'/capture.json');pa,pw=recording(ROOT/previous,pc);stages=[];new_guard=None
 specs=[('approach-resume01',0x1c9),('post-mini-c8-01',0x1c8),('switch1eb-01',0x1eb),('switch1ec-02',0x1eb),('earth1e8-01',0x1aa),('thief-key01',0x1a9),('switch19a-01',0x1aa),('approach01',0x1a6)]
 for suffix,room in specs:
  root='validation/natural-dungeon-combat/md-auto-v0309-d8-'+suffix;c=load(root+'/capture.json');r=load(root+'/report.json');f=c['frames'];proof=root+f'-assisted-fixed-replay-{f}';p=load(proof+'/replay_report.json')
  assert c['rom_sha256']==r['rom_sha256']==p['rom_sha256']==digest and c['sram_input'] is None and r['failure'] is None and not r['deaths']
  assert p['passed'] and p['whole_ram_bytes']==65536 and p['final_png_exact'] and not p['feedback_reads']
  assert r['recorded_new_game_prefix']==previous.split('/')[-1] and r['prefix_end']==pc['frames'] and f>pc['frames']
  for name,h in p['evidence'].items():assert sha(read(root+'/'+name))==h
  for stem,ext in [('ram','bin'),('frame','png')]:assert read(root+f'/{stem}_{f:05d}.{ext}')==read(proof+f'/{stem}_{f:05d}.{ext}')
  a,w=recording(ROOT/root,c);read(root+'/assistance.json');assert len(a['episodes'])==10 and a['boss_room']==0x196 and all(a[k] is None for k in ['first_boss_entry','release_write_frame','first_boss_combat','first_boss_damage'])
  assert all(addr==sy['hero_hurt'] for _,addr,_ in w) and not a['boss_assistance'] and not a['health_refills'] and not a['primary_state_imports']
  raw=read(root+f'/ram_{f:05d}.bin');data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big');save=data('game_save_state',592);flags=save[0x50:0x150];items=data('hero_items',17)
  assert word('room_id')==room and word('game_state')==12 and word('hero_health')>0 and word('hero_max_health')==88 and word('world_dungeon_number')==8
  assert save[0x1f:0x28]==bytes([128]*7+[0]*2) and items[10] and items[16] and items[12:15]==bytes([1,1,1])
  owns_key=suffix in ['thief-key01','switch19a-01','approach01'];assert items[15]==int(owns_key)
  if suffix=='approach-resume01':
   new_guard=r['new_guard_frame'];assert r['passed'] and r['resumed_after_verified_intermediate'] and w==pw+[(new_guard,sy['hero_hurt'],b'\x00\x81')] and word('hero_hurt')==129
   assert a['episodes'][:8]==pa['episodes'][:8];ep=a['episodes'][-2];assert ep['boss_room']==0x1c9 and ep['release_write_frame']==prior['guard_release_frame'] and ep['first_boss_combat']['frame']==prior['first_intermediate_combat']['frame'] and ep['first_boss_combat']['hurt']==0
   assert ep['first_boss_damage']==prior['first_extension_damage'] and a['episodes'][-1]['activation_after_frame']==pc['frames']
   assert a['intermediate_entry_cold_verified'] and a['main_boss_never_entered_in_prefix']
   before=read(previous+f'/ram_{pc["frames"]:05d}.bin')
   for name,size in [('hero_health',2),('hero_magic',2),('hero_gold',2),('hero_keys',2),('hero_items',17)]:assert data(name,size)==bytes(before[(sy[name]+i)^1] for i in range(size))
  else:
   assert w[:len(pw)]==pw and a['episodes'][:-1]==pa['episodes'][:-1] and a['preserve_floor_hurt_requested']
   assert not save[0x150+0xc9], 'The defeated intermediate remains absent'
   events=load(root+'/events.json');assert not any(e.get('room')==0x1c9 and any(x.get('type')==0x7a and x.get('hp',0)>0 for x in e.get('actors',[])) for e in events)
   if suffix=='post-mini-c8-01':assert r['room_cleared'] and word('hero_health')>0
   if suffix.startswith('switch'):
    assert r['contact_route_passed'] and r['contact_state_writes']==0 and r['contact_opened']['flags']&4
   if suffix=='switch1eb-01':assert r['contact_remote_room']==0x1c8 and r['contact_coordinate']==332 and r['contact_before']['remote_flags']==144 and r['contact_opened']['remote_flags']==148
   if suffix in ['switch1ec-02','earth1e8-01','thief-key01','switch19a-01','approach01']:assert flags[0xc8]&4 and flags[0xeb]&0x40 and flags[0xea]&0x80
   if suffix=='earth1e8-01':
    assert r['earth_route_passed'] and r['earth_cell_cleared'] and r['earth_passage_traversed'] and r['earth_state_writes']==0
    assert r['earth_before']['cell']==11 and r['earth_opened']['cell']==12 and r['earth_before']['magic']-r['earth_opened']['magic']==8
    assert all(n in [e['room'] for e in events] for n in [0x1c8,0x1d8,0x1e8,0x1aa])
   if suffix=='thief-key01':assert r['item_acquisition_passed'] and r['collect_item_requested']==15 and r['item_acquisition_state_writes']==0 and not r['item_acquisition_first']['owned'] and r['item_acquisition_last']['owned']==1 and not word('item_reward_active')
   if suffix in ['switch19a-01','approach01']:assert flags[0xd8]&0x40 and flags[0xd7]&0x80
   if suffix=='approach01':assert r['room_cleared'] and not any(x['slot']<8 for x in r['last_actors'])
  stages.append(dict(trace=root,frames=f,room=room,health=word('hero_health'),keys=word('hero_keys'),gold=word('hero_gold'),magic=word('hero_magic'),thief_key_owned=bool(items[15]),whole_ram_png_exact=True));previous,pc,pa,pw=root,c,a,w
 sms=data('sms_vram',16384);v=read(previous+f'/vram_{pc["frames"]:05d}.bin');regs=read(previous+f'/vdp_regs_{pc["frames"]:05d}.bin');base=(regs[2]&56)<<10;width=[32,64,32,128][regs[16]&3]
 for n in range(128):
  at=base+((n//32+22)*width+n%32)*2;assert int.from_bytes(v[at:at+2],'little')==translated(int.from_bytes(sms[0x3d00+n*2:0x3d02+n*2],'little'))
 for n in range(7):
  tile,offset=original[0x1edc+n*2:0x1ede+n*2];assert sms[0x3d00+offset:0x3d02+offset]==bytes([tile,0x59])
 read('tools/summarize_d8_thief_v0309.py')
 result=dict(passed=True,version=309,md_sha256=digest,production_rom_unchanged=True,stages=stages,current_campaign_trace=previous,ready_trace=previous,campaign_frames=pc['frames'],thief_key_acquired=True,intermediate_victory_without_assistance=True,new_approach_guard_frame=new_guard,defeated_intermediate_not_respawned=True,actual_c8_floor_traversed=True,main_boss_room=0x196,main_boss_kind=0x6b,source_boss_stats='50100240',eighth_boss_entered=False,eighth_crystal_obtained=False,final_hud_words_exact=128,source_crystal_markers_exact=7,full_game_validated=False,evidence=refs,limits=['Protection resumes only after the verified ordinary intermediate victory. No living7A reappears on the return through1C9. Main196 remains unentered; its guard must be released before combat.','Ordinary game input grants the thief key and opens the mechanisms. Only hero_hurt test writes are used; no resources,actors,progression or SRAM state is imported.','Owning the thief key alone is not proof of every thief-key door. Cold RAM/PNG equality is not complete source RNG,audiovisual,ending,save,hardware or extended stack validation.'])
 (ROOT/'analysis/d8_thief_v0309_report.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());print('D8 thief key and main approach: eight cold checkpoints exact')
if __name__=='__main__':main()
