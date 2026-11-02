"""Audit ordinary-damage D8 intermediate combat from the verified coastal entry."""
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
 prior=load('analysis/d8_entry_v0309_report.json');assert prior['passed'] and prior['seventh_crystal_preserved']
 digest=sha(read('versions/v0309-7270576d/gaw-megadrive-v0309.bin'));assert digest==prior['md_sha256']==sha((ROOT/'gaw-megadrive.bin').read_bytes())
 sy=symbols(ROOT/'megadrive/out/release/symbol.txt');read('megadrive/out/release/symbol.txt');index=load('validation/v0309-d8-midboss-sources/source_index.json')
 for name,h in index.items():assert sha(read('validation/v0309-d8-midboss-sources/'+name.split('/')[-1]))==h and sha((ROOT/name).read_bytes())==h
 original=read('input/original.sms');assert original[0x3234e+0x1c9*8:0x32356+0x1c9*8]==bytes([0x7a]+[0]*7) and original[0x320ea+(0x7a-0x20)*4:0x320ee+(0x7a-0x20)*4]==bytes([50,18,4,32])
 specs=[('md-auto-v0309-d8-mini-ready02','ready'),('md-auto-v0309-d8-guard-release01','close'),('md-auto-v0309-d8-midboss01','combat')]
 previous=prior['current_campaign_trace'];pc=load(previous+'/capture.json');pa,pw=recording(ROOT/previous,pc);release=None;fixed=None;first=None;damage=None;stages=[];predictions=0;final_report=None
 for name,kind in specs:
  root='validation/natural-dungeon-combat/'+name;c=load(root+'/capture.json');r=load(root+'/report.json');f=c['frames'];proof=root+f'-assisted-fixed-replay-{f}';p=load(proof+'/replay_report.json')
  assert c['rom_sha256']==r['rom_sha256']==p['rom_sha256']==digest and c['sram_input'] is None
  assert p['passed'] and p['whole_ram_bytes']==65536 and p['final_png_exact'] and not p['feedback_reads']
  assert r['recorded_new_game_prefix']==previous.split('/')[-1] and r['prefix_end']==pc['frames'] and not r['deaths'] and f>pc['frames']
  assert r['failure'] is None or kind=='combat' and r['failure']=='frame_limit'
  for filename,h in p['evidence'].items():assert sha(read(root+'/'+filename))==h
  for stem,ext in [('ram','bin'),('frame','png')]:assert read(root+f'/{stem}_{f:05d}.{ext}')==read(proof+f'/{stem}_{f:05d}.{ext}')
  raw=read(root+f'/ram_{f:05d}.bin');data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big')
  a,w=recording(ROOT/root,c);read(root+'/assistance.json');assert len(a['episodes'])==9 and a['boss_room']==0x196 and not a['first_boss_entry'] and not a['first_boss_combat']
  assert all(addr==sy['hero_hurt'] for _,addr,_ in w) and not a['boss_assistance'] and not a['primary_state_imports'] and not a['health_refills']
  assert word('game_state')==12 and word('hero_health')>0 and word('hero_max_health')==88 and data('hero_items',17)[16]==1 and data('game_save_state',592)[0x1f:0x28]==bytes([128]*7+[0]*2)
  if kind=='ready':
   assert r['failure'] is None and r['room_cleared'] and r['retry_isolated_foes_requested'] and r['wake_sentinels_requested'] and word('room_id')==0x1ca
   assert w[:len(pw)]==pw and a['episodes'][:-1]==pa['episodes'][:-1]
  elif kind=='close':
   release=r['guard_release_frame'];assert r['passed'] and a['approach_closed_early'] and a['closed_before_room']==0x1c9 and word('room_id')==0x1ca and word('hero_hurt')==0
   assert w==pw+[(release,sy['hero_hurt'],b'\x00\x00')] and release==f;fixed=w
  else:
   assert w==fixed and all(frame<=release for frame,_,_ in w) and r['unassisted_extension'] and r['new_assistance_writes']==0 and word('hero_hurt')<=128
   assert r['unassisted_controller_sha256']==index['tools/unassisted_dungeon_continuation.py'] and r['primary_state_imports']==0
   assert r['extension_guard_checks_through_frame']==f and r['equip_basic_requested'] and word('hero_selected_item')==0 and word('hero_basic_level')==2 and word('hero_attack')==6
   assert r['full_ram_prediction_matches']==r['verified_persistent_prediction_windows'] and r['stack_only_difference_windows']==0;predictions+=r['full_ram_prediction_matches']
   if first is None:
    first=r['first_intermediate_combat'];assert first['room']==0x1c9 and first['health']>0 and first['hurt']<=128 and first['actors']==[dict(slot=0,kind=0x7a,hp=50)] and release<first['frame']
   if damage is None and r['first_extension_damage']:damage=r['first_extension_damage']
   observed_events=load(root+'/events.json');assert not any(e.get('room')==0x196 for e in observed_events)
   hp_events=[e for e in observed_events if 'health' in e]
   drops=[(new['frame'],before['health'],new['health']) for before,new in zip(hp_events,hp_events[1:]) if new['health']<before['health']]
   assert all(before>after>0 and before-after==original[0x320ea+(0x7a-0x20)*4+1] for _,before,after in drops)
  stages.append(dict(trace=root,kind=kind,frames=f,room=word('room_id'),health=word('hero_health'),keys=word('hero_keys'),gold=word('hero_gold'),magic=word('hero_magic'),whole_ram_png_exact=True));previous,pc,pa,pw=root,c,a,w;final_report=r
 actors=data('world_actor_state',768);remaining=[actors[i*48+24] for i in range(8) if actors[i*48]==0x7a and actors[i*48+24]];won=bool(final_report['room_cleared']);assert won and not remaining and final_report['failure'] is None
 read('tools/summarize_d8_midboss_v0309.py')
 result=dict(passed=True,version=309,md_sha256=digest,production_rom_unchanged=True,stages=stages,current_campaign_trace=previous,campaign_frames=pc['frames'],intermediate_defeated=won,remaining_intermediate_hp=remaining,intermediate_assistance=False,guard_release_frame=release,first_intermediate_combat=first,first_extension_damage=damage,full_ram_prediction_windows=predictions,ordinary_reentry_count=json.loads((ROOT/'validation/natural-dungeon-combat/md-auto-v0309-d8-mini-ready02/report.json').read_bytes())['isolated_foe_retries'],seven_crystals_preserved=True,eighth_main_boss_entered=False,eighth_crystal_obtained=False,full_game_validated=False,evidence=refs,limits=['Approach and combat follow ordinary input after the declared guard release. Any ordinary reentries are counted from the actual ready report; no actor or resource is edited.','All intermediate fight writes are exactly the closed prefix list. No guard is reactivated during the fight; no resources,actors,progression or SRAM are imported.','Cold RAM/PNG and prediction equality are not whole-source RNG,audiovisual,ending,save or hardware proof. The stack bound remains the prior D7 checkpoint.'])
 (ROOT/'analysis/d8_midboss_v0309_report.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());print('D8 intermediate checkpoint gates verified; defeated=',won,'prediction windows=',predictions)
if __name__=='__main__':main()
