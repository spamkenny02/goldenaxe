"""Audit final cold-v314 palace route,boss,credits and return to title flow."""
import json
from run_core import ROOT
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols
from validate_reward_hud_restore import translated

SPECS=[('earth13e01',0x16a),('switch17c01',0x17c),('portal13c01',0x13c),('switch14b01',0x14b),('portal15a01',0x15a),('earth15b01',0x16b),('switch16c01',0x16c),('pre-final01',0x15c),('release01',0x15c),('final01',0x14c),('ending01',None)]
def main():
 refs={}
 def read(p):
  raw=evidence(p);refs[p.relative_to(ROOT).as_posix()]=sha(raw);return raw
 def load(p):return json.loads(read(p))
 prior=load(ROOT/'analysis/cold_palace_guardian_v0314_report.json');assert prior['passed'] and prior['cold_palace_guardian_defeated'] and prior['actual_golden_axe_acquired'] and not prior['primary_state_imports']
 digest=prior['md_sha256'];assert sha((ROOT/'gaw-megadrive.bin').read_bytes())==digest
 source=ROOT/'validation/v0314-palace-sources/final-tools';index=load(source/'source_index.json')
 for n,h in index.items():assert sha(read(source/n.split('/')[-1]))==h
 retry_source=source
 retry_index=load(retry_source/'source_index.json')
 for n,h in retry_index.items():assert sha(read(retry_source/n.split('/')[-1]))==h
 proposal=load(source/'cold_palace_final_route_proposal_v0309.json');assert proposal['status']=='unexecuted_proposal'
 sy=symbols(ROOT/'megadrive/out/release/symbol.txt');original=read(ROOT/'input/original.sms')
 assert original[0x3234e+0x14c*8:0x32356+0x14c*8]==bytes([0x6d]+[0]*7)
 assert original[0x320ea+(0x6d-0x20)*4]==90
 def reader(raw):
  data=lambda n,k:bytes(raw[(sy[n]+i)^1]for i in range(k))
  return data,lambda n:int.from_bytes(data(n,2),'big')
 previous=ROOT/prior['current_campaign_trace'];pc=load(previous/'capture.json');pa,pw=recording(previous,pc)
 stages=[];release=None;fixed=None;combat=None;fight=None;ending=None;hud=None;victory=None
 for i,(suffix,room) in enumerate(SPECS):
  p=ROOT/'validation/natural-dungeon-combat'/('md-auto-v0314-cold-palace-'+suffix);c=load(p/'capture.json');r=load(p/'report.json');a,w=recording(p,c);f=c['frames']
  assert c['rom_sha256']==r['rom_sha256']==digest and c['sram_input'] is None and r['failure'] is None and not r.get('deaths',0) and not r['primary_state_imports']
  if suffix=='ending01':assert r['recorded_victory_prefix']=='natural-dungeon-combat/'+previous.name
  else:assert r['prefix_end']==pc['frames'] and r['recorded_new_game_prefix']==previous.name
  assert f>pc['frames']
  proofp=p.with_name(p.name+'-assisted-fixed-replay-'+str(f));proof=load(proofp/'replay_report.json')
  assert proof['passed'] and proof['whole_ram_bytes']==65536 and proof['final_png_exact'] and not proof['feedback_reads'] and proof['rom_sha256']==digest
  for n,h in proof['evidence'].items():assert sha(read(p/n))==h
  for stem,ext in [('ram','bin'),('frame','png')]:assert read(p/f'{stem}_{f:05d}.{ext}')==read(proofp/f'{stem}_{f:05d}.{ext}')
  assert len(a['episodes'])==16 and a['boss_room']==0x14c and not a['boss_assistance'] and not a['primary_state_imports'] and not a['health_refills']
  assert all(addr==sy['hero_hurt'] and value in (b'\0\0',b'\0\x81') for _,addr,value in w)
  assert w[:len(pw)]==pw
  raw=read(p/f'ram_{f:05d}.bin');data,word=reader(raw);items=data('hero_items',17);save=data('game_save_state',592);actors=data('world_actor_state',768)
  assert word('hero_health')>0 and not word('sound_unhandled_command')
  if i<10:
   assert word('room_id')==room and word('world_dungeon_number')==10 and word('hero_max_health')==104
   assert items[1]==2 and items[10]==items[11]==items[15]==items[16]==1 and save[0x1f:0x28]==bytes([128]*9) and word('hero_selected_item')==1 and word('hero_weapon_level')==2
  if i<8:
   assert word('game_state')==12 and a['first_boss_entry'] is None and a['release_write_frame'] is None and a['episodes'][:-1]==pa['episodes'][:-1]
   assert r['driver_sha256']==(index if i==0 else retry_index)['tools/natural_dungeon_combat.py']
   planned=proposal['stages'][i];assert r['itinerary']==[int(v,0)for v in planned['rooms'].split(',')]
   if planned['planner']=='earth':
    assert r['earth_route_passed'] and r['earth_passage_traversed'] and r['earth_passage_opened'] and not r['earth_state_writes'] and r['earth_passage_room']==int(planned['earth_room'],0) and r['earth_cell']==int(planned['earth_cell'],0) and r['earth_restore_item']==1
    assert r['earth_controller_sha256']==index['tools/natural_earth_passage.py']
   elif planned['planner']=='contact':
    assert r['contact_route_passed'] and not r['contact_state_writes'] and r['contact_room']==room and r['contact_destination']==room
    assert r['contact_controller_sha256']==index['tools/natural_contact_passage.py']
    if room==0x17c:
     assert r['contact_remote_room']==0x17b and save[0xcb]&4
     decisions=load(p/'pilot_decisions.json')
     retries=[e for e in decisions if e['reason']=='no_reachable_attack_reenter_room']
     returns=[e for e in decisions if e['reason']=='isolated_foe_reentry_complete']
     assert len(retries)==len(returns)==r['isolated_foe_retries']
     assert all(e['room'] in [int(v,0) for v in planned['rooms'].split(',')] for e in retries)
     assert [e['room'] for e in returns]==[e['room'] for e in retries]
    else:assert save[0x50+(room&255)]&4
    if room==0x16c:assert save[0xbc]&0x20
   else:
    assert r['room_cleared'] and not any(actors[j*48] and (j<8 or actors[j*48+24])for j in range(16))
   if suffix=='pre-final01':hud=(p,f,raw)
  elif i==8:
   release=f;fixed=w;assert r['driver_sha256']==index['tools/close_assisted_approach.py']
   assert r['passed'] and a['closed_before_room']==0x14c and a['first_boss_entry'] is None and word('game_state')==12 and word('hero_hurt')==0
   assert w==pw+[(f,sy['hero_hurt'],b'\0\0')] and f==pc['frames']+1
   old=reader(read(previous/f'ram_{pc["frames"]:05d}.bin'))[1]
   for n in ['hero_health','hero_magic','hero_gold','hero_keys']:assert word(n)==old(n)
  else:
   assert w==fixed and all(t<=release for t,_,_ in w) and r['unassisted_extension'] and not r['new_assistance_writes'] and word('hero_hurt')<=128 and save[0x28]==1
   assert a['first_boss_entry'] and a['first_boss_entry']['frame']>release and a['release_write_frame']==release
   if i==9:
    assert r['unassisted_controller_sha256']==index['tools/unassisted_dungeon_continuation.py'] and r['driver_sha256']==retry_index['tools/natural_dungeon_combat.py']
    assert r['ending_handoff_passed'] and r['ending_handoff']['game']==word('game_state')==14 and r['ending_handoff']['final_dungeon_defeated']
    combat=r['first_intermediate_combat'];assert combat['frame']>release and combat['room']==0x14c and combat['health']>0 and combat['hurt']<=128 and any(e['kind']==0x6d and e['hp']==90 for e in combat['actors'])
    assert r['full_ram_prediction_matches']==r['verified_persistent_prediction_windows']>0 and not r['stack_only_difference_windows'] and r['extension_guard_checks_through_frame']==f
    fight=r;victory=r['ending_handoff']
   else:
    assert r['passed'] and r['ending_complete'] and word('game_state')==r['last_state']['game']==0 and r['last_state']['descriptor']==0 and r['last_state']['credits_done']
    assert r['nine_gems_visible_frame']<r['credits_started_frame']<r['credits_finished_frame']<r['acknowledgement_frame']<=r['title_flow_return_frame']
    assert r['credits_finished_frame']-r['credits_started_frame']>=7000 and (data('title_phase',1)!=b'\0' or word('intro_running'))
    assert r['driver_sha256']==index['tools/continue_recorded_ending.py']
    gemframe=r['nine_gems_visible_frame']+1;gd,gw=reader(read(p/f'ram_{gemframe:05d}.bin'));ga=gd('world_actor_state',768)
    assert gw('ending_hero_descriptor')==0x8495 and sum(ga[j*48]==6 and bool(ga[j*48+3]&1)for j in range(9))==9
    read(p/f'frame_{gemframe:05d}.png');ending=r
  stages.append(dict(trace=p.relative_to(ROOT).as_posix(),frames=f,room=word('room_id'),game=word('game_state'),health=word('hero_health'),magic=word('hero_magic'),whole_ram_png_exact=True))
  read(p/'controls.json');read(p/'assistance.json');previous,pc,pa,pw=p,c,a,w
 p,hf,raw=hud;data,word=reader(raw);sms=data('sms_vram',16384);vram=read(p/f'vram_{hf:05d}.bin');regs=read(p/f'vdp_regs_{hf:05d}.bin');base=(regs[2]&56)<<10;width=[32,64,32,128][regs[16]&3]
 for n in range(128):
  at=base+((n//32+22)*width+n%32)*2;assert int.from_bytes(vram[at:at+2],'little')==translated(int.from_bytes(sms[0x3d00+n*2:0x3d02+n*2],'little'))
 for n in range(9):
  tile,off=original[0x1edc+n*2:0x1ede+n*2];assert sms[0x3d00+off:0x3d02+off]==bytes([tile,0x59])
 result=dict(passed=True,version=314,md_sha256=digest,production_rom_unchanged=True,campaign_from_new_game_completed=True,approach_guards_used=True,final_boss_assistance=False,primary_state_imports=0,full_game_validated=False,current_campaign_trace=stages[-1]['trace'],campaign_frames=pc['frames'],guard_release_frame=release,first_final_combat=combat,final_victory=victory,prediction_windows_exact=fight['full_ram_prediction_matches'],ending_complete=True,nine_gems_visible_frame=ending['nine_gems_visible_frame'],credits_started_frame=ending['credits_started_frame'],credits_finished_frame=ending['credits_finished_frame'],title_flow_return_frame=ending['title_flow_return_frame'],music_requests=ending['music_requests'],physical_pre_final_hud_words_exact=128,source_crystal_markers_exact=9,stages=stages,evidence=refs,limits=['Actual cold-v314 New Game campaign,nine crystals,Balloon,Golden Axe and real final victory. Logged hurt guards only on approaches;all bosses fought without protection. No health,inventory,actor,progression or SRAM imports.','Full recorded boss and ending replay independently from boot. Own-ROM exact replay does not prove whole-source RNG/framebuffer/audio/phase equivalence,saves,all optional content or hardware;the full port goal stays open.'])
 (ROOT/'analysis/cold_palace_final_v0314_report.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());print('Cold-v314 campaign reached actual victory,complete credits and title flow')
if __name__=='__main__':main()
