"""Purchase actual keys after an ordinary recorded merchant approach (native)."""
import argparse,contextlib,io,json
from run_core import ROOT,run,FrameWrites
from natural_dungeon_combat import walk
from validate_playable_sprite_limit import symbols
from assisted_prefix import prefix_writes,recording
from archive_lossless_evidence import sha

def main():
 p=argparse.ArgumentParser();p.add_argument('--prefix',required=True);p.add_argument('--outside',type=lambda x:int(x,0),required=True);p.add_argument('--count',type=int,default=2);p.add_argument('--trial',required=True);p.add_argument('--heal-after',action='store_true');p.add_argument('--assisted-prefix',action='store_true');a=p.parse_args();assert 1<=a.count<=10
 source=ROOT/'validation/natural-dungeon-route'/a.prefix;c=json.loads((source/'capture.json').read_bytes());prior=json.loads((source/'route_report.json').read_bytes());assert prior['reached_entrance'] and prior['failure'] is None and prior['house_outside']==a.outside and prior['house_target'] in [0,1,0x2f] and c['sram_input'] is None
 assert not str(c['rom']).endswith('.sms');rom=ROOT/'gaw-megadrive.bin';assert c['rom_sha256']==sha(rom.read_bytes());sy=symbols(ROOT/'megadrive/out/release/symbol.txt');house=prior['house_target'];assert not a.heal_after or a.outside==0x94 and house==0
 assets=json.loads((ROOT/'analysis/merchant_assets.json').read_bytes());town=next(r for r in assets['towns'] if r[0]==a.outside);assert town[1]==0;selection=next(i for i,v in enumerate(assets['goods'][town[2]]) if v[0]==30);price=assets['goods'][town[2]][selection][1];node=next(r for r in assets['nodes'] if r[0]==house);nx,ny=node[1:]
 writes=prefix_writes(source,c,a.assisted_prefix);recorded=json.loads((source/'controls.json').read_bytes());start=c['frames'];timeline=[()]*(start+1)
 for i,row in enumerate(recorded):
  end=recorded[i+1]['frame']-1 if i+1<len(recorded) else start;timeline[row['frame']:end+1]=[tuple(row['buttons'])]*(end-row['frame']+1)
 folder=ROOT/'validation/natural-service-route'/('md-'+a.trial);assert not folder.exists();state={};first=None;done=None;failure=None;observed=0;controls=list(recorded);events=[];captures={start,start+6000};last=None;tilemap=b'';last_direction=0
 def trade_complete():return first is not None and state['keys']==first['keys']+a.count and state['gold']==first['gold']-price*a.count
 def achieved():return trade_complete() and (not a.heal_after or state['health']==state['max_health'])
 def observe(f,r):
  nonlocal first,done,failure,observed,last,tilemap
  observed=f
  if f<start:return
  word=lambda n:int.from_bytes(bytes(r[(sy[n]+i)^1] for i in range(2)),'big')
  tilemap=bytes(r[(sy['sms_vram']+0x3800+i)^1] for i in range(1536))
  state.update(room=word('room_id'),game=word('game_state'),hero=word('hero_state'),counter=word('hero_counter'),x=word('hero_x')>>8,y=word('hero_y')>>8,health=word('hero_health'),max_health=word('hero_max_health'),gold=word('hero_gold'),keys=word('hero_keys'),phase=word('merchant_phase'),selection=word('merchant_selection'),audio_error=word('sound_unhandled_command'))
  if first is None:first=dict(state);assert first['room']==house and first['gold']>=price*a.count and first['keys']+a.count<=99
  if not state['health'] or state['game']==20:failure='hero_died'
  if state['audio_error']:failure='native_audio_error'
  k=tuple(state[n] for n in ['room','game','gold','keys','phase','selection'])
  if k!=last:events.append(dict(frame=f,**state));captures.add(f+1);last=k
  if state['room']==a.outside and state['game']==12 and state['hero']==1 and achieved() and done is None:done=f;captures.add(f+150)
 def choose(f):
  nonlocal last_direction
  if f<=start:return list(timeline[f])
  if failure or done:return []
  if state.get('game')==22:
   if f%40:return []
   if achieved() or state['phase'] and trade_complete():return [0]
   if state['phase']==1 and state['selection']!=selection:return [4 if state['selection']>selection else 5]
   return [8]
  if state.get('room')!=house:return []
  if state['counter']:return [4+last_direction]
  point=state['x'],state['y'];goal=(136,144) if achieved() else (216,88) if a.heal_after and trade_complete() else (nx,ny)
  if point==goal or achieved() and point[0]==136 and point[1]>=144:last_direction=1 if achieved() else 0;return [4+last_direction]
  route=walk(tilemap,point,lambda q:q==goal)
  if route:last_direction=route[0];return [4+last_direction]
  return []
 def controller(f):
  value=choose(f)
  if f>start and (not controls or controls[-1]['buttons']!=value):controls.append(dict(frame=f,buttons=list(value)))
  return value
 with contextlib.redirect_stdout(io.StringIO()):run(rom,start+6000,folder,captures,c['presses'],skip_intro=False,input_provider=controller,ram_observer=observe,stop_when=lambda:bool(failure) or done is not None and observed>=done+150,core_options=c['core_options'],ram_writes=FrameWrites(writes))
 result=dict(passed=done is not None and not failure,failure=failure or (None if done else 'frame_limit'),rom_sha256=c['rom_sha256'],source_prefix=a.prefix,outside=a.outside,keys_bought=a.count,unit_price=price,complete_frame=done,first_state=first,last_state=state,ram_injections=bool(writes),assisted_route=bool(writes),new_assistance_writes=0,primary_state_imports=0,currency_or_inventory_fixtures=False,free_healing_requested=a.heal_after,free_healing_completed=bool(a.heal_after and achieved()))
 for name,value in [('report',result),('events',events),('controls',controls)]:(folder/(name+'.json')).write_text(json.dumps(value,indent=2)+'\n')
 if writes:
  assist=json.loads((source/'assistance.json').read_bytes());assist['writes']=[dict(frame=f,address=address,data_hex=data.hex()) for f,address,data in writes];(folder/'assistance.json').write_text(json.dumps(assist,indent=2)+'\n');recording(folder,json.loads((folder/'capture.json').read_bytes()))
 print(result)

if __name__=='__main__':main()
