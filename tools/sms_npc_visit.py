"""Walk to plain house NPCs, acknowledge their text, leave, all from cold boot.

Use run_sms_dialogue_observed.py so original050C/627A observations prove
entry and completed text rendering. No primary RAM/savestate imports.
"""
import argparse,contextlib,hashlib,io,json
from pathlib import Path
from run_core import ROOT,run,compile_fixed_inputs
from natural_dungeon_combat import walk
from assisted_prefix import prefix_writes,recording
from run_core import FrameWrites

dialogue_events=[]
def main():
 p=argparse.ArgumentParser();p.add_argument('--conditional',action='store_true');p.add_argument('--sms',action='store_true',required=True);p.add_argument('--prefix',required=True);p.add_argument('--out',required=True);p.add_argument('--room',type=lambda x:int(x,0),required=True);p.add_argument('--outside',type=lambda x:int(x,0),required=True);p.add_argument('--frames',type=int,default=18000);p.add_argument('--assisted-prefix',action='store_true');p.add_argument('--quest-hint',action='store_true')
 p.add_argument('--probe-text-variants',action='store_true',help='Accept the actually observed text at each NPC coordinate, including an unknown variant')
 a=p.parse_args()
 prefix=(ROOT/'validation'/a.prefix).resolve();out=(ROOT/'validation'/a.out).resolve();assert prefix.is_relative_to(ROOT/'validation') and out.is_relative_to(ROOT/'validation') and not out.exists()
 cap=json.loads((prefix/'capture.json').read_bytes());assert cap['sram_input'] is None
 writes=prefix_writes(prefix,cap,a.assisted_prefix)
 rom=ROOT/'input/original.sms';assert hashlib.sha256(rom.read_bytes()).hexdigest()==cap['rom_sha256']
 start=cap['frames'];presses=list(map(tuple,cap['presses']));prior=json.loads((prefix/'controls.json').read_bytes())
 for i,row in enumerate(prior):
  last=prior[i+1]['frame']-1 if i+1<len(prior) else start
  presses.extend((row['frame'],min(last,start),key) for key in row['buttons'])
 masks=compile_fixed_inputs(presses,start)
 initial=(prefix/f'ram_{start:05d}.bin').read_bytes();variant=None
 if a.quest_hint:
  assert not a.conditional and a.room==0x4f and a.outside in (0x92,0x50,0x27,0xb1,0x6a)
  assert not initial[0x100+a.outside]&2,'Use a pre-reward branch for the giver/hint pair'
  if not initial[0xe4]:pc=0x8e5c
  elif a.outside==0x92:pc=0x8bea if initial[0xe8] else 0x8fe3
  elif a.outside==0x50:pc=0x8e94 if initial[0xda]>=56 else 0x8ed9
  else:
   field,level={0x27:(0xf1,2),0xb1:(0xf1,3),0x6a:(0xe0,3)}[a.outside]
   assert initial[field]<level,'This hint variant needs the earlier equipment state'
   pc=0x8e94
  targets=[dict(room=a.room,outside=a.outside,coordinate=0x25c,text_pc=pc)]
 elif a.conditional:
  reference=json.loads((ROOT/'analysis/conditional_house_reference.json').read_bytes())
  if a.outside==0xce:
   variant='ninth_crystal_present' if initial[0xd7]&128 else 'ninth_crystal_absent'
   targets=[dict(room=room,outside=outside,coordinate=coordinate,text_pc=reference['text_pcs'][n*2+bool(initial[0xd7]&128)]) for n,(room,outside,coordinate,handler) in enumerate(reference['nodes'][:3]) if room==a.room and outside==a.outside]
  else:
   assert a.outside==0x22 and a.room==7
   choice=6 if not initial[0xd2] else 8 if initial[0xf7] else 7
   variant={6:'prerequisite_absent',7:'collect_actual_100_gold_reward',8:'reward_already_collected'}[choice]
   targets=[dict(room=7,outside=0x22,coordinate=0x2d4,text_pc=reference['text_pcs'][choice])]
 else:
  contexts=json.loads((ROOT/'analysis/plain_house_dialogue_reference.json').read_text())['contexts']
  targets=[x for x in contexts if x['room']==a.room and x['outside']==a.outside]
 assert targets
 for t in targets:
  t['point']=next((x,y) for y in range(8,161,8) for x in range(8,249,8) if (((y-12)&248)<<3)+(((x-12)&255)>>2&62)+126==t['coordinate'])
 controls=[];captures=set();state={};observed=0;cursor=0;active=None;rendered=False;talk_started=0;last_direction=0;visited=[];failure=None;done=None;phase='walk';current=0;entry=None
 def observe(frame,raw):
  nonlocal observed,failure,done
  observed=frame
  if frame<start:return
  state.update(room=int.from_bytes(raw[0xb9:0xbb],'little'),game=raw[0x1d],hero=raw[0x301],counter=raw[0x304],x=raw[0x313],y=raw[0x311],health=raw[0x318],gold=raw[0xdd],reward_flag=raw[0xf7],ninth_crystal=raw[0xd7],tilemap=bytes(raw[0x1600:0x1c00]))
  if not state['health']:failure='hero_died'
  if current==len(targets) and state['room']==a.outside and state['game']==12 and state['hero']==1 and done is None:done=frame;captures.add(frame+30)
 def decide(frame):
  nonlocal cursor,active,rendered,talk_started,last_direction,current,phase,entry,failure
  if frame<=start:return [key for key in range(16) if masks[frame]&(1<<key)]
  if failure or done:return []
  while cursor<len(dialogue_events):
   event=dialogue_events[cursor];cursor+=1
   if event['frame']<=start:continue
   if event['event_pc']==0x50c:
    active=event['text_pc'];entry=event;rendered=False;talk_started=frame;phase='talk'
   elif event['event_pc']==0x627a and active is not None:rendered=True;captures.add(frame)
  if phase=='talk':
   if rendered:
    if state['room']==a.room and state['counter']==0 and entry is not None and (state['x'],state['y'])!=(entry['x'],entry['y']):
     match=next((t for t in targets if (a.probe_text_variants or t['text_pc']==active) and t['coordinate']==(((entry['y']-12)&248)<<3)+(((entry['x']-12)&255)>>2&62)+126),None)
     if match and not any(v['coordinate']==match['coordinate'] if a.probe_text_variants else v['text_pc']==active for v in visited):visited.append(dict(text_pc=active,coordinate=match['coordinate'],entry_frame=entry['frame'],render_completed=True,acknowledged_and_walked_away_frame=frame))
     while current<len(targets) and any(v['coordinate']==targets[current]['coordinate'] if a.probe_text_variants else v['text_pc']==targets[current]['text_pc'] for v in visited):current+=1
     active=None;entry=None;phase='walk';return []
    return [5]
   return [8] if frame-talk_started>=140 and (frame-talk_started)%60==0 else []
  if state.get('room')!=a.room:return []
  target=targets[current]['point'] if current<len(targets) else (136,160)
  if state['hero'] not in (0,1):return []
  if state['counter']:return [4+last_direction]
  point=state['x'],state['y']
  if point==target:
   last_direction=0 if current<len(targets) else 1
   return [4+last_direction]
  route=walk(state['tilemap'],point,lambda q:q==target)
  if route:last_direction=route[0];return [4+last_direction]
  failure='npc_point_unreachable';return []
 def controller(frame):
  value=decide(frame)
  if frame>start and (not controls or controls[-1]['buttons']!=value):controls.append(dict(frame=frame,buttons=value))
  return value
 with contextlib.redirect_stdout(io.StringIO()):run(rom,max(a.frames,start+10000),out,captures,cap['presses'],skip_intro=False,input_provider=controller,ram_observer=observe,ram_writes=FrameWrites(writes),core_options=cap['core_options'],stop_when=lambda:bool(failure) or done is not None and observed>=done+30)
 # Preserve the exact prefix inputs as ordinary intervals in capture.json.
 actual=json.loads((out/'capture.json').read_bytes());actual['presses']=[list(x) for x in presses];(out/'capture.json').write_text(json.dumps(actual,indent=2)+'\n')
 effects_ok=not a.conditional or (state['gold']==min(255,initial[0xdd]+100) and state['reward_flag']==1 if variant=='collect_actual_100_gold_reward' else state['gold']==initial[0xdd] and state['reward_flag']==initial[0xf7])
 report=dict(quest_hint=a.quest_hint,conditional=a.conditional,conditional_variant=variant,conditional_effects_verified=effects_ok if a.conditional else None,passed=effects_ok and done is not None and len(visited)==len(targets) and not failure,failure=failure or (None if done else 'frame_limit'),source_sha256=cap['rom_sha256'],rom_sha256=cap['rom_sha256'],prefix=a.prefix,prefix_end=start,room=a.room,outside=a.outside,visited=visited,required_targets=targets,last_state={k:v for k,v in state.items() if k!='tilemap'},primary_ram_writes=len(writes),new_assistance_writes=0,assisted_route=bool(writes),sram_imports=0,progression_imports=0,scope='Unmodified SMS from cold boot with original text-entry/completion observations and ordinary walking/acknowledgment. Inherited approach protection, if any, is fully recorded; no new writes during this NPC stage. Current-state conditional-house variant only.' if a.conditional else 'Unmodified SMS, original text-entry/completion observation and normal acknowledgment/exit. Inherited approach protection; no new writes during this NPC stage. Plain-house current-state variants only.')
 if writes:
  assist=json.loads((prefix/'assistance.json').read_bytes());(out/'assistance.json').write_text(json.dumps(assist,indent=2)+'\n');recording(out,actual)
 report['probe_text_variants']=a.probe_text_variants
 if a.quest_hint:report['scope']='Original quest hint in a genuine pre-reward state, rendered, acknowledged and exited. No gift, inventory edit or other hint variant claimed.'
 for name,data in [('report',report),('controls',controls)]:(out/(name+'.json')).write_text(json.dumps(data,indent=2)+'\n')
 print(json.dumps(report),flush=True)
 if not report['passed']:raise SystemExit(1)

if __name__=='__main__':main()
