"""Ordinary recorded route, house gold gift or teacher visit, then normal exit."""
import argparse,contextlib,io,json
from run_core import ROOT,run,FrameWrites
from validate_playable_sprite_limit import symbols
from archive_lossless_evidence import sha
from assisted_prefix import prefix_writes,recording

def main():
 p=argparse.ArgumentParser();p.add_argument('--assisted-prefix',action='store_true');p.add_argument('--sms',action='store_true');p.add_argument('--prefix',required=True);p.add_argument('--trial',required=True);p.add_argument('--outside',type=lambda s:int(s,0),required=True);p.add_argument('--kind',choices=['gold','teacher'],required=True);p.add_argument('--teacher',type=int,default=0);p.add_argument('--expected-level',type=int,default=0);p.add_argument('--gold-gain',type=int,default=50);a=p.parse_args()
 source=ROOT/'validation/natural-dungeon-route'/a.prefix;c=json.loads((source/'capture.json').read_bytes());prior=json.loads((source/'route_report.json').read_bytes());recorded=json.loads((source/'controls.json').read_bytes());rom=ROOT/'input/original.sms' if a.sms else ROOT/'gaw-megadrive.bin';digest=sha(rom.read_bytes());assert c['rom_sha256']==digest and prior['reached_entrance'] and not prior['failure'] and c['sram_input'] is None
 writes=prefix_writes(source,c,a.assisted_prefix)
 start=c['frames'];timeline=[()]*(start+1)
 for i,row in enumerate(recorded):
  end=recorded[i+1]['frame']-1 if i+1<len(recorded) else start;timeline[row['frame']:end+1]=[tuple(row['buttons'])]*(end-row['frame']+1)
 tag='sms' if a.sms else 'md';folder=ROOT/f'validation/natural-service-route/{tag}-{a.trial}';assert not folder.exists();sy=None if a.sms else symbols(ROOT/'megadrive/out/release/symbol.txt');state={};events=[];controls=list(recorded);captures={start};first=None;seen=False;done=None;failure=None;observed=0;previous=None;house=0x3f if a.kind=='gold' else 0xbf;target_y=88 if a.kind=='gold' else 56
 def achieved():
  if first is None:return False
  if a.kind=='gold':return state['gold']==min(255,first['gold']+a.gold_gain) and state['outside_flags']&2
  return seen and state['level']==a.expected_level and (a.teacher!=0 or state['intro']!=0)
 def observe(f,r):
  nonlocal first,seen,done,failure,observed,previous
  observed=f
  if f<start:return
  if a.sms:state.update(room=int.from_bytes(r[0xb9:0xbb],'little'),game=r[0x1d],hero=r[0x301],counter=r[0x304],x=r[0x313],y=r[0x311],health=r[0x318],gold=r[0xdd],magic=r[0xdb],max_magic=r[0xdc],outside_flags=r[0x100+a.outside],level=r[0xe4+a.teacher],intro=r[0xf3],modal=r[0x1d]==22,audio_error=0)
  else:
   data=lambda n,k:bytes(r[(sy[n]+i)^1] for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big');state.update(room=word('room_id'),game=word('game_state'),hero=word('hero_state'),counter=word('hero_counter'),x=word('hero_x')>>8,y=word('hero_y')>>8,health=word('hero_health'),gold=word('hero_gold'),magic=word('hero_magic'),max_magic=word('hero_max_magic'),outside_flags=data('game_save_state',592)[0x50+a.outside],level=data('hero_items',17)[4+a.teacher],intro=data('game_save_state',592)[0x43],modal=word('house_dialogue_active'),audio_error=word('sound_unhandled_command'))
  if first is None:first=dict(state);assert first['room']==house and first['health']
  if state['game']==22:seen=True
  if not state['health'] or state['game']==20:failure='hero_died'
  if state['audio_error']:failure='native_audio_error'
  key=tuple(state.values())
  if key!=previous:
   if previous is None or any(state[n]!=(events[-1].get(n)) for n in ['room','game','gold','level','intro','modal']):events.append(dict(frame=f,**state));captures.add(f+1)
   previous=key
  if state['room']==a.outside and state['game']==12 and state['hero']==1 and achieved() and done is None:done=f;captures.add(f+150)
 def choose(f):
  if f<=start:return list(timeline[f])
  if failure or done:return []
  if state.get('modal') or state.get('game')==22:return [8] if f%40==0 else []
  if state.get('room')!=house:return []
  if state['x']!=136:return [7 if state['x']<136 else 6]
  if achieved():return [5,8] if a.sms and f%40==0 else [5]
  if a.kind=='gold' and state['outside_flags']&2:return [8] if f%40==0 else []
  return [4]
 def controller(f):
  buttons=choose(f)
  if f>start and (not controls or controls[-1]['buttons']!=buttons):controls.append(dict(frame=f,buttons=buttons))
  return buttons
 with contextlib.redirect_stdout(io.StringIO()):run(rom,start+5000,folder,captures,c['presses'],skip_intro=False,input_provider=controller,ram_observer=observe,stop_when=lambda:bool(failure) or done is not None and observed>=done+150,core_options=c['core_options'],ram_writes=FrameWrites(writes))
 result=dict(passed=done is not None and not failure,rom_sha256=digest,source_prefix=a.prefix,kind=a.kind,teacher=a.teacher if a.kind=='teacher' else None,expected_level=a.expected_level if a.kind=='teacher' else None,complete_frame=done,failure=failure or (None if done else 'frame_limit'),first_state=first,last_state=state,ram_injections=bool(writes),assisted_route=bool(writes),new_assistance_writes=0,sram_checkpoint_injection=False,scope='Cold boot and recorded ordinary buttons with explicitly inherited approach assistance if present, real house interaction and normal exterior exit. No actor removal, ownership, currency or progression fixture.')
 for name,value in [('report',result),('events',events),('controls',controls)]:(folder/(name+'.json')).write_bytes((json.dumps(value,indent=2)+'\n').encode())
 if writes:
  assist=json.loads((source/'assistance.json').read_bytes());assist['writes']=[dict(frame=f,address=addr,data_hex=data.hex()) for f,addr,data in writes];(folder/'assistance.json').write_bytes((json.dumps(assist,indent=2)+'\n').encode());recording(folder,json.loads((folder/'capture.json').read_bytes()))
 print(result)
if __name__=='__main__':main()
