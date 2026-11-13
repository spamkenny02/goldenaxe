"""Spend actual owned Earth II casts for financial branches; never write MP."""
import argparse,contextlib,io,json,hashlib
from run_core import ROOT,run,FrameWrites,compile_fixed_inputs
from validate_playable_sprite_limit import symbols
from md_readonly_view import md_to_sms_view
from assisted_prefix import prefix_writes,recording

def main():
 p=argparse.ArgumentParser();p.add_argument('--rom',required=True);p.add_argument('--trace',required=True);p.add_argument('--trial',required=True);p.add_argument('--target-magic',type=int,required=True);a=p.parse_args();source=ROOT/'validation'/a.trace;cap=json.loads((source/'capture.json').read_bytes());assert cap['sram_input'] is None
 rom=ROOT/a.rom;assert hashlib.sha256(rom.read_bytes()).hexdigest()==cap['rom_sha256'];sy=symbols(ROOT/'megadrive/out/release/symbol.txt');start=cap['frames'];initial=md_to_sms_view((source/f'ram_{start:05d}.bin').read_bytes(),sy);assert initial[0xe5]==2 and initial[0xdf]==5 and 0<=a.target_magic<initial[0xdb] and (initial[0xdb]-a.target_magic)%8==0
 presses=list(map(tuple,cap['presses']));old=json.loads((source/'controls.json').read_bytes());controls=list(old)
 for i,row in enumerate(old):
  last=old[i+1]['frame']-1 if i+1<len(old) else start;presses.extend((row['frame'],min(last,start),k) for k in row['buttons'])
 masks=compile_fixed_inputs(presses,start);writes=FrameWrites(prefix_writes(source,cap,True));inherited_count=len(writes);out=ROOT/'validation/natural-service-route'/('md-'+a.trial);assert not out.exists();state={};events=[];done=None;failure=None;observed=0;captures={start};last_mp=initial[0xdb]
 def observe(frame,raw):
  nonlocal done,failure,observed,last_mp
  observed=frame
  if frame<start:return
  word=lambda n:raw[sy[n]]|raw[sy[n]+1]<<8;r=md_to_sms_view(raw,sy);spell=raw[sy['world_spell_state']^1]
  actors=bytes(raw[(sy['world_actor_state']+i)^1] for i in range(768));assert not any(actors[n+24] and (0x63<=actors[n]<=0x6d or 0x78<=actors[n]<=0x7c) for n in range(0,768,48)),'Preparation guard over live boss'
  writes.append((frame+1,sy['hero_hurt'],b'\0\x81'))
  state.update(room=word('room_id'),game=word('game_state'),hero=word('hero_state'),counter=word('hero_counter'),magic=word('hero_magic'),spell=spell,health=word('hero_health'),selected=word('hero_selected_item'),audio_error=word('sound_unhandled_command'))
  assert r[0xcf:0xdb]==initial[0xcf:0xdb] and r[0xdc:0xf3]==initial[0xdc:0xf3],'Casting changed resources other than MP'
  assert state['room']==int.from_bytes(initial[0xb9:0xbb],'little') and not state['audio_error'] and state['health']
  assert a.target_magic<=state['magic']<=initial[0xdb] and (initial[0xdb]-state['magic'])%8==0
  if state['magic']!=last_mp:events.append(dict(frame=frame,**state));captures.add(frame+1);last_mp=state['magic']
  if state['magic']==a.target_magic and not spell and state['game']==12 and state['hero']==1 and not state['counter'] and done is None:done=frame;captures.add(frame+40)
 def control(frame):
  if frame<=start:value=[k for k in range(16) if masks[frame]&(1<<k)]
  else:
   value=[8] if done is None and state['magic']>a.target_magic and not state['spell'] and state['hero']==1 and not state['counter'] and frame%20==0 else []
   if not controls or controls[-1]['buttons']!=value:controls.append(dict(frame=frame,buttons=value))
  return value
 with contextlib.redirect_stdout(io.StringIO()):run(rom,start+12000,out,captures,cap['presses'],skip_intro=False,input_provider=control,ram_observer=observe,ram_writes=writes,core_options=cap['core_options'],stop_when=lambda:done is not None and observed>=done+40)
 r=dict(passed=done is not None,failure=None if done else 'frame_limit',rom_sha256=cap['rom_sha256'],source_trace=a.trace,initial_magic=initial[0xdb],target_magic=a.target_magic,actual_casts=(initial[0xdb]-state['magic'])//8,complete_frame=done,last_state=state,resource_or_actor_writes=0,new_assistance_writes=len(writes)-inherited_count,declared_approach_guard=True,primary_state_imports=0,scope='Actual C-triggered Earth II projectiles;8 MP per cast. No MP, inventory, HP, currency or quest fixtures. Non-boss approach hurt protection is explicitly recorded during preparation. Actual terrain effects are allowed and remain game-produced.')
 for name,value in [('report',r),('controls',controls),('events',events)]:(out/(name+'.json')).write_bytes((json.dumps(value,indent=2)+'\n').encode())
 if writes:
  aid=json.loads((source/'assistance.json').read_bytes());aid['writes']=[dict(frame=f,address=at,data_hex=data.hex()) for f,at,data in writes];actual=json.loads((out/'capture.json').read_bytes())
  if 'episodes' in aid:aid['episodes'][-1]['end_frame']=actual['frames']+1
  (out/'assistance.json').write_bytes((json.dumps(aid,indent=2)+'\n').encode());recording(out,actual)
 print(json.dumps(r),flush=True);assert r['passed']

if __name__=='__main__':main()
