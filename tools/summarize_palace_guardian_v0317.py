"""Audit cold palace guardian and actual Golden Axe acquisition."""
import json
from run_core import ROOT
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols
from validate_reward_hud_restore import translated

SPECS=[('switch12c01','switch'),('pre-guardian01','approach'),('guardian-release01','release'),('guardian01','guardian'),('resume-final01','resume'),('goldenaxe01','axe')]
def main():
 refs={}
 def read(p):
  raw=evidence(p);refs[p.relative_to(ROOT).as_posix()]=sha(raw);return raw
 def load(p):return json.loads(read(p))
 prior=load(ROOT/'analysis/cold_palace_inner_v0317_report.json');assert prior['passed'] and prior['cold_palace_inner_mechanisms_verified'] and not prior['primary_state_imports']
 digest=prior['md_sha256'];assert digest==sha((ROOT/'gaw-megadrive.bin').read_bytes())
 source=ROOT/'validation/v0317-palace-sources/guardian-tools';index=load(source/'source_index.json')
 for n,h in index.items():assert sha(read(source/n.split('/')[-1]))==h
 sy=symbols(ROOT/'megadrive/out/release/symbol.txt');original=read(ROOT/'input/original.sms')
 rewards=load(ROOT/'analysis/item_rewards_reference.json');assert rewards['source_sha256']==sha(original)
 axe_source=next(row for row in rewards['records'] if row['room']==0x11d)
 assert axe_source['kind']=='stationary_item_reward' and axe_source['inventory_offset']==1 and axe_source['value']==2
 label=bytes.fromhex(axe_source['label_hex']);at=axe_source['label_pointer']+0x4000;assert original[at:at+len(label)]==label
 call=axe_source['call_site'];assert original[call:call+3]==bytes([0xcd,axe_source['target']&255,axe_source['target']>>8])
 handler=axe_source['handler'];assert original[handler:handler+5]==bytes([0x3e,2,0x32,0xe1,0xc0])
 assert original[0x3234e+0x11e*8:0x32356+0x11e*8]==bytes([0x7c]+[0]*7)
 assert original[0x320ea+(0x7c-0x20)*4:0x320ee+(0x7c-0x20)*4]==bytes([60,24,6,32])
 previous=ROOT/prior['current_campaign_trace'];pc=load(previous/'capture.json');pa,pw=recording(previous,pc)
 stages=[];release=None;fixed=None;combat=None;damage=None;guardian_report=None
 for suffix,kind in SPECS:
  p=ROOT/'validation/natural-dungeon-combat'/('md-auto-v0317-cold-palace-'+suffix);c=load(p/'capture.json');r=load(p/'report.json');a,w=recording(p,c);f=c['frames']
  assert c['rom_sha256']==r['rom_sha256']==digest and c['sram_input'] is None and r['failure'] is None and not r['deaths']
  if kind in ('switch','approach','guardian','axe'):assert r['driver_sha256']==index['tools/natural_dungeon_combat.py']
  assert r['prefix_end']==pc['frames'] and r['recorded_new_game_prefix']==previous.name and f>pc['frames']
  proofp=p.with_name(p.name+'-assisted-fixed-replay-'+str(f));proof=load(proofp/'replay_report.json')
  assert proof['passed'] and proof['whole_ram_bytes']==65536 and proof['final_png_exact'] and not proof['feedback_reads'] and proof['rom_sha256']==digest
  for n,h in proof['evidence'].items():assert sha(read(p/n))==h
  for stem,ext in [('ram','bin'),('frame','png')]:assert read(p/f'{stem}_{f:05d}.{ext}')==read(proofp/f'{stem}_{f:05d}.{ext}')
  assert len(a['episodes'])==(16 if kind in ('resume','axe') else 15) and a['boss_room']==0x14c and a['first_boss_entry'] is None
  assert not a['boss_assistance'] and not a['primary_state_imports'] and not a['health_refills']
  assert all(addr==sy['hero_hurt'] and value in (b'\0\0',b'\0\x81')for _,addr,value in w)
  raw=read(p/f'ram_{f:05d}.bin');data=lambda n,k:bytes(raw[(sy[n]+i)^1]for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big')
  items=data('hero_items',17);save=data('game_save_state',592);actors=data('world_actor_state',768)
  assert word('game_state')==12 and word('world_dungeon_number')==10 and 0<word('hero_health')<=104 and word('hero_max_health')==104 and not word('sound_unhandled_command')
  assert save[0x1f:0x28]==bytes([128]*9) and items[1]==(2 if kind=='axe' else 1) and items[10]==items[11]==items[15]==items[16]==1
  assert word('hero_selected_item')==(1 if kind=='axe' else 0) and word('hero_basic_level')==2
  if kind in ('switch','approach'):
   assert w[:len(pw)]==pw and a['episodes'][:-1]==pa['episodes'][:-1] and a['release_write_frame'] is None
   assert word('room_id')==(0x12c if kind=='switch'else 0x12e)
   if kind=='switch':
    assert r['contact_route_passed'] and not r['contact_state_writes'] and r['contact_room']==r['contact_destination']==0x12c and save[0x7c]&4 and save[0x7c]&0x80
   else:
    assert r['room_cleared'] and not any(actors[i*48] and (i<8 or actors[i*48+24]) for i in range(16))
    assert r['itinerary']==[0x12c,0x11c,0x11b,0x12b,0x12c,0x12d,0x12e] and 0x12c in r['rush_rooms']
  elif kind=='release':
   release=f;fixed=w;assert r['passed'] and a['closed_before_room']==0x11e and word('room_id')==0x12e and word('hero_hurt')==0
   assert w==pw+[(f,sy['hero_hurt'],b'\0\0')]
  elif kind=='guardian':
   assert word('room_id')==0x11e and r['room_cleared'] and w==fixed and all(t<=release for t,_,_ in w)
   assert r['unassisted_extension'] and not r['new_assistance_writes'] and not r['primary_state_imports'] and r['guard_release_frame']==release and r['extension_guard_checks_through_frame']==f
   combat=r['first_intermediate_combat'];assert combat['room']==0x11e and combat['frame']>release and combat['health']>0 and combat['hurt']<=128 and combat['actors']==[dict(slot=0,kind=0x7c,hp=60)]
   assert word('hero_hurt')<=128 and word('hero_attack')==6 and not any(actors[i*48]==0x7c and actors[i*48+24]for i in range(16))
   assert r['full_ram_prediction_matches']==r['verified_persistent_prediction_windows']>0 and not r['stack_only_difference_windows']
   events=load(p/'events.json');hp=[e for e in events if 'health'in e];damage=[dict(frame=b['frame'],room=b['room'],before=a['health'],after=b['health'])for a,b in zip(hp,hp[1:])if b['health']<a['health']]
   assert not any(e.get('room')==0x14c for e in events);guardian_report=r
  elif kind=='resume':
   assert r['passed'] and r['resumed_after_verified_intermediate'] and r['new_guard_frame']==f and word('room_id')==0x11e and word('hero_hurt')==129
   assert w==pw+[(f,sy['hero_hurt'],b'\0\x81')] and r['driver_sha256']==index['tools/resume_after_intermediate.py']
  else:
   assert word('room_id')==0x11d and r['item_acquisition_passed'] and not r['item_acquisition_state_writes'] and r['collect_item_requested']==1 and r['collect_item_target_value']==2 and word('hero_weapon_level')==2
   assert r['item_acquisition_first']['owned']==1 and r['item_acquisition_last']['owned']==2 and not r['item_acquisition_last']['reward_active']
   assert r['item_acquisition_driver_sha256']==index['tools/natural_item_acquisition.py'] and r['item_reward_finished_frame']>=r['item_acquired_frame']+300
   assert w[:len(pw)]==pw and a['episodes'][:-1]==pa['episodes'][:-1] and a['release_write_frame'] is None
  stages.append(dict(trace=p.relative_to(ROOT).as_posix(),kind=kind,frames=f,room=word('room_id'),health=word('hero_health'),magic=word('hero_magic'),gold=word('hero_gold'),keys=word('hero_keys'),whole_ram_png_exact=True))
  read(p/'controls.json');read(p/'assistance.json');previous,pc,pa,pw=p,c,a,w
 sms=data('sms_vram',16384);vram=read(previous/f'vram_{pc["frames"]:05d}.bin');regs=read(previous/f'vdp_regs_{pc["frames"]:05d}.bin');base=(regs[2]&56)<<10;width=[32,64,32,128][regs[16]&3]
 for n in range(128):
  at=base+((n//32+22)*width+n%32)*2;assert int.from_bytes(vram[at:at+2],'little')==translated(int.from_bytes(sms[0x3d00+n*2:0x3d02+n*2],'little'))
 for n in range(9):
  tile,off=original[0x1edc+n*2:0x1ede+n*2];assert sms[0x3d00+off:0x3d02+off]==bytes([tile,0x59])
 result=dict(passed=True,version=317,md_sha256=digest,production_rom_unchanged=True,current_campaign_trace=stages[-1]['trace'],campaign_frames=pc['frames'],stages=stages,cold_palace_guardian_defeated=True,actual_golden_axe_acquired=True,original_axe_reward=axe_source,guard_release_frame=release,first_guardian_combat=combat,observed_health_drops=damage,full_ram_prediction_windows=guardian_report['full_ram_prediction_matches'],physical_hud_words_exact=128,source_crystal_markers_exact=9,primary_state_imports=0,full_game_validated=False,evidence=refs,limits=['Actual cold campaign with nine crystals and owned Balloon. Approach guard is removed before11E;no writes during guardian combat. Guard resumes only after canonical victory. Golden Axe is acquired through real11D item handling.','Final14C remains pending. This does not prove whole-source RNG,timing,saves,optional content or hardware.'])
 (ROOT/'analysis/cold_palace_guardian_v0317_report.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());print('Cold palace guardian and Golden Axe verified')
if __name__=='__main__':main()
