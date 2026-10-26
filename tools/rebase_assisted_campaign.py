"""Re-execute historical ordinary buttons with current-ROM approach-only guards.

No historical RAM or snapshots are imported. Boss release is detected from
actual current transitions, never copied blindly from historical timing.
"""
import argparse,contextlib,io,json
from run_core import ROOT,run
from rebase_natural_campaign import evidence
from assisted_prefix import prefix_writes,episodes,EPISODE_KEYS,recording
from validate_playable_sprite_limit import symbols
from archive_lossless_evidence import sha

def main():
 p=argparse.ArgumentParser();p.add_argument('--trace',required=True);p.add_argument('--trial',required=True);p.add_argument('--expected-room',type=lambda s:int(s,0),required=True);p.add_argument('--expected-capacity',type=int,required=True);p.add_argument('--expected-item',type=int);p.add_argument('--stop-at-boss',action='store_true');a=p.parse_args()
 source=(ROOT/'validation'/a.trace).resolve();assert source.is_relative_to(ROOT/'validation');capture=json.loads((source/'capture.json').read_bytes());controls=json.loads((source/'controls.json').read_bytes());assist,_=recording(source,capture);prefix_writes(source,capture,True);old_episodes=episodes(assist,capture);assert not capture['sram_input']
 sy=symbols(ROOT/'megadrive/out/release/symbol.txt');rom=ROOT/'gaw-megadrive.bin';digest=sha(rom.read_bytes());folder=ROOT/'validation/natural-dungeon-combat'/a.trial;assert not folder.exists();end=capture['frames'];presses=[tuple(row) for row in capture['presses']]
 for i,row in enumerate(controls):
  stop=controls[i+1]['frame']-1 if i+1<len(controls) else end;presses.extend((row['frame'],min(stop,end),button) for button in row['buttons'] if row['frame']<=end)
 writes=[];new_episodes=[];active=None;next_episode=0;state={};previous=None;failure=None;fail_frame=None;diagnostic_end=None;observed=0;captures={end};events=[];samples=[]
 def observe(f,r):
  nonlocal active,next_episode,previous,failure,fail_frame,diagnostic_end,observed
  observed=f;data=lambda n,k:bytes(r[(sy[n]+i)^1] for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big')
  state.update(room=word('room_id'),game=word('game_state'),hero=word('hero_state'),counter=word('hero_counter'),x=word('hero_x')>>8,y=word('hero_y')>>8,health=word('hero_health'),hurt=word('hero_hurt'),max_health=word('hero_max_health'),dungeon=word('world_dungeon_number'),gold=word('hero_gold'),keys=word('hero_keys'),weapon=word('hero_weapon_level'),selected=word('hero_selected_item'),audio_error=word('sound_unhandled_command'),crystals=list(data('game_save_state',592)[0x1f:0x28]),items=list(data('hero_items',17)))
  if not failure and (state['game']==20 or f>2500 and not state['health'] and state['hero'] in [8,9]):failure='hero_died';fail_frame=f;captures.add(f+1)
  if state['audio_error'] and not failure:failure='native_audio_error';fail_frame=f;captures.add(f+1)
  if not failure and next_episode<len(old_episodes) and f==old_episodes[next_episode]['activation_after_frame']:
   prereq=state['health'] and state['game']==12 and state['crystals'][0]&128
   if active is not None:prereq=prereq and active['first_boss_combat'] is not None and state['dungeon']==0 and state['crystals'][next_episode]&128
   if not prereq:failure='next_approach_prerequisite_mismatch';fail_frame=f;captures.add(f+1)
   else:
    if active:active['end_frame']=f
    active=dict(activation_after_frame=f,boss_room=old_episodes[next_episode]['boss_room'],first_boss_entry=None,release_write_frame=None,first_boss_combat=None,first_boss_damage=None,end_frame=end+1);new_episodes.append(active);next_episode+=1
  if active and f>=active['activation_after_frame'] and not failure:
   if state['room']==active['boss_room'] and active['first_boss_entry'] is None:
    assert state['game']!=12,('Guard would overlap boss simulation',f,state)
    active['first_boss_entry']=dict(frame=f,game=state['game'],health=state['health'],hurt=state['hurt']);active['release_write_frame']=f+1;writes.append((f+1,sy['hero_hurt'],b'\0\0'));captures.add(f+1)
   elif active['first_boss_entry'] is None:
    actor=data('world_actor_state',768);danger=any(actor[i*48]>=16 and actor[i*48+3]&2 for i in range(16));writes.append((f+1,sy['hero_hurt'],b'\0\x81' if danger else b'\0\0'))
   if state['room']==active['boss_room'] and state['game']==12:
    assert active['release_write_frame']<f
    if active['first_boss_combat'] is None:
     assert state['hurt']==0,('Guard remained in boss fight',f,state)
     active['first_boss_combat']=dict(frame=f,health=state['health'],hurt=state['hurt']);captures.add(f+1)
     if a.stop_at_boss:diagnostic_end=f+1
    if previous is not None and state['health']<previous['health'] and active['first_boss_damage'] is None:active['first_boss_damage']=dict(frame=f,before=previous['health'],after=state['health'],hurt=state['hurt'])
  key=state['room'],state['game'],state['health'],state['max_health'],state['dungeon'],tuple(state['crystals']),tuple(state['items'])
  if previous is None or key!=previous['key']:events.append(dict(frame=f,**state));captures.add(f+1)
  if f%100==0:samples.append(dict(frame=f,**state))
  previous=dict(state,key=key)
 with contextlib.redirect_stdout(io.StringIO()):run(rom,end,folder,captures,presses,skip_intro=False,ram_writes=writes,ram_observer=observe,stop_when=lambda:failure is not None and observed>fail_frame or diagnostic_end is not None and observed>=diagnostic_end,core_options=capture['core_options'])
 # Preserve only inputs actually executed before an early diagnostic stop.
 controls=[row for row in controls if row['frame']<=observed]
 actual_capture=json.loads((folder/'capture.json').read_bytes())
 actual_capture['presses']=[(begin,min(stop,observed),button) for begin,stop,button in actual_capture['presses'] if begin<=observed]
 (folder/'capture.json').write_bytes((json.dumps(actual_capture,indent=2)+'\n').encode())
 if not new_episodes:
  report=dict(passed=False,rom_sha256=digest,historical_rom_sha256=capture['rom_sha256'],historical_trace=a.trace,frames=observed,last_state=state,failure=failure or 'no_authorized_approach_reached',ram_injections=False,natural_campaign_proof=False)
  for name,value in [('report',report),('controls',controls),('events',events),('samples',samples)]:(folder/(name+'.json')).write_bytes((json.dumps(value,indent=2)+'\n').encode())
  print(report);return
 new_episodes[-1]['end_frame']=observed+1;last=new_episodes[-1]
 result=dict(assisted_route=True,ram_injections=True,rom_modifications=False,primary_state_imports=0,health_refills=0,boss_assistance=False,invulnerability_value=129,episodes=new_episodes,writes=[dict(frame=f,address=address,data_hex=value.hex()) for f,address,value in writes],historical_trace=a.trace,historical_rom_sha256=capture['rom_sha256'],historical_controls_sha256=sha((source/'controls.json').read_bytes()),current_release_from_live_room_transition=True)
 result.update({key:last[key] for key in EPISODE_KEYS});(folder/'assistance.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());recording(folder,json.loads((folder/'capture.json').read_bytes()))
 passed=not failure and (observed==end or a.stop_at_boss and diagnostic_end==observed) and state['room']==a.expected_room and state['game']==12 and state['hero']==1 and state['health']>0 and state['max_health']==a.expected_capacity and (a.expected_item is None or state['items'][a.expected_item]) and all(ep['first_boss_combat'] for ep in new_episodes)
 report=dict(passed=bool(passed),rom_sha256=digest,historical_rom_sha256=capture['rom_sha256'],historical_trace=a.trace,frames=observed,last_state=state,failure=failure or (None if passed else 'expected_progress_not_reached'),full_dungeon_cleared=bool(passed and not a.stop_at_boss),room_cleared=bool(passed and not a.stop_at_boss),stop_reason='first_unassisted_boss_frame' if a.stop_at_boss else 'historical_end',deaths=int(failure=='hero_died'),assisted_route=True,ram_injections=True,boss_assistance=False,natural_campaign_proof=False,scope='Current-ROM cold execution of historical ordinary inputs. Only hurt-counter approach guards are generated, released from live room transitions. No imported state,equipment,currency or health refill. Independent current fixed replay is still required.')
 for name,value in [('report',report),('controls',controls),('events',events),('samples',samples)]:(folder/(name+'.json')).write_bytes((json.dumps(value,indent=2)+'\n').encode())
 print(report)
if __name__=='__main__':main()
