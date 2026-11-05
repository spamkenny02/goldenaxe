"""Controller-only first life-fairy visit, dialogue, capacity reward and exit."""
import argparse,contextlib,io,json
from run_core import ROOT,run,FrameWrites
from validate_playable_sprite_limit import symbols
from archive_lossless_evidence import sha
from assisted_prefix import prefix_writes,recording

def main():
 p=argparse.ArgumentParser();p.add_argument('--assisted-prefix',action='store_true');p.add_argument('--sms',action='store_true');p.add_argument('--prefix',required=True);p.add_argument('--trial',required=True);p.add_argument('--outside',type=lambda v:int(v,0),default=0xc9);a=p.parse_args()
 source=ROOT/'validation/natural-dungeon-route'/a.prefix;c=json.loads((source/'capture.json').read_bytes());prior=json.loads((source/'route_report.json').read_bytes());recorded=json.loads((source/'controls.json').read_bytes())
 rom=ROOT/'input/original.sms' if a.sms else ROOT/'gaw-megadrive.bin';digest=sha(rom.read_bytes());assert c['rom_sha256']==digest and prior['reached_entrance'] and not prior['failure'] and c['sram_input'] is None
 writes=prefix_writes(source,c,a.assisted_prefix)
 end=c['frames'];timeline=[()]*(end+1)
 for n,row in enumerate(recorded):
  stop=recorded[n+1]['frame']-1 if n+1<len(recorded) else end
  timeline[row['frame']:min(stop,end)+1]=[tuple(row['buttons'])]*(min(stop,end)-row['frame']+1)
 tag='sms' if a.sms else 'md';folder=ROOT/'validation/natural-service-route'/(tag+'-'+a.trial);assert not folder.exists()
 sy=None if a.sms else symbols(ROOT/'megadrive/out/release/symbol.txt');state={};events=[];controls=list(recorded);captures={end};done=None;observed=0;failure=None;initial=None;previous=None
 def observe(f,r):
  nonlocal done,observed,failure,initial,previous
  observed=f
  if a.sms:state.update(room=int.from_bytes(r[0xb9:0xbb],'little'),game=r[0x1d],hero=r[0x301],counter=r[0x304],x=r[0x313],y=r[0x311],health=r[0x318],max_health=r[0xda],outside_flags=r[0x100+a.outside],first_crystal=r[0xcf],modal=0,audio_error=0)
  else:
   data=lambda n,k:bytes(r[(sy[n]+i)^1] for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big')
   state.update(room=word('room_id'),game=word('game_state'),hero=word('hero_state'),counter=word('hero_counter'),x=word('hero_x')>>8,y=word('hero_y')>>8,health=word('hero_health'),max_health=word('hero_max_health'),outside_flags=data('game_save_state',592)[0x50+a.outside],first_crystal=data('game_save_state',592)[0x1f],modal=word('house_dialogue_active') or word('item_reward_active'),audio_error=word('sound_unhandled_command'))
  if f<end:return
  if initial is None:initial=dict(state);assert initial['room']==0xaf and initial['max_health']==32 and not initial['outside_flags']&2
  key=tuple(state[n] for n in ['room','health','max_health','outside_flags','modal','game'])
  if key!=previous:events.append(dict(frame=f,**state));captures.add(f+1);previous=key
  if not state['health']:failure='hero_died'
  if state['audio_error']:failure='native_audio_error'
  if state['room']==a.outside and state['game']==12 and state['hero']==1 and state['health']==state['max_health']==40 and state['outside_flags']&2 and not state['modal'] and done is None:done=f;captures.add(f+150)
 def choose(f):
  if f<=end:return list(timeline[f])
  if failure or done is not None:return []
  if state.get('room')!=0xaf:return []
  if state['max_health']<40:
   if state['outside_flags']&2:return [8] if f%20==0 else []
   if state['x']!=136:return [7 if state['x']<136 else 6]
   return [4] if state['y']>=72 else []
  if state['health']<state['max_health']:return []
  if state['modal']:return [8] if f%20==0 else []
  if state['x']!=136:return [7 if state['x']<136 else 6]
  return [5]
 def controller(f):
  buttons=choose(f)
  if f>end and (not controls or controls[-1]['buttons']!=buttons):controls.append(dict(frame=f,buttons=list(buttons)))
  return buttons
 with contextlib.redirect_stdout(io.StringIO()):run(rom,end+5000,folder,captures,c['presses'],skip_intro=False,input_provider=controller,ram_observer=observe,stop_when=lambda:bool(failure) or done is not None and observed>=done+150,core_options=c['core_options'],ram_writes=FrameWrites(writes))
 result=dict(passed=done is not None and failure is None,rom_sha256=digest,source_prefix=a.prefix,prefix_end=end,outside=a.outside,complete_frame=done,failure=failure or (None if done else 'frame_limit'),initial_state=initial,last_state=state,ram_injections=bool(writes),assisted_route=bool(writes),new_assistance_writes=0,sram_checkpoint_injection=False,scope='Ordinary cold boot/controller prefix then first life-fairy dialogue,capacity reward,full health and normal house exit. No complete campaign or source raster/audio claim.')
 for name,obj in [('report',result),('events',events),('controls',controls)]:(folder/(name+'.json')).write_bytes((json.dumps(obj,indent=2)+'\n').encode())
 if writes:
  assist=json.loads((source/'assistance.json').read_bytes());assist['writes']=[dict(frame=f,address=address,data_hex=value.hex()) for f,address,value in writes];(folder/'assistance.json').write_bytes((json.dumps(assist,indent=2)+'\n').encode());recording(folder,json.loads((folder/'capture.json').read_bytes()))
 print(result)

if __name__=='__main__':main()
