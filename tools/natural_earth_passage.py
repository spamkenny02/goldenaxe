"""Use acquired Earth magic, through ordinary inventory/cast buttons, at D4's rock.

The primary game boots normally. This controller never imports or writes state.
An outer assisted-route wrapper may provide explicitly logged approach guards.
"""
import argparse,json,sys
from pathlib import Path
import natural_dungeon_combat as game
from run_core import ROOT
from archive_lossless_evidence import sha
from validate_playable_sprite_limit import symbols

def main():
 p=argparse.ArgumentParser(add_help=False);p.add_argument('--earth-during-combat',action='store_true',help='Use real Earth input before clearing the room');p.add_argument('--passage-destination',type=lambda v:int(v,0),default=0x1d1);p.add_argument('--earth-cell',type=lambda v:int(v,0),default=0x58);p.add_argument('--earth-room',type=lambda v:int(v,0),default=0x1e1);p.add_argument('--earth-action-only',action='store_true',help='Stop after a preparatory brick is cleared,without claiming a passage');p.add_argument('--earth-cast-x',type=lambda v:int(v,0));p.add_argument('--earth-cast-y',type=lambda v:int(v,0));p.add_argument('--earth-direction',type=int,choices=range(4),default=0);a,remaining=p.parse_known_args();sys.argv=[sys.argv[0]]+remaining+(['--continue-after-clear'] if a.earth_action_only else [])
 assert 0<=a.earth_cell<160
 cast_x=(a.earth_cell&15)*16+8 if a.earth_cast_x is None else a.earth_cast_x;cast_y=(a.earth_cell&240)+32 if a.earth_cast_y is None else a.earth_cast_y
 assert not a.earth_action_only or a.passage_destination==a.earth_room
 assert 8<=cast_x<=248 and 8<=cast_y<=168
 behind=(cast_x+[0,0,8,-8][a.earth_direction],cast_y+[8,-8,0,0][a.earth_direction])
 sms='--sms' in remaining;flag='--continuation' if '--continuation' in remaining else '--prefix';name=remaining[remaining.index(flag)+1];family='natural-dungeon-combat' if flag=='--continuation' else 'natural-dungeon-route';prefix=json.loads((ROOT/'validation'/family/name/'capture.json').read_bytes());start=prefix['frames'];sy=None if sms else symbols(ROOT/'megadrive/out/release/symbol.txt')
 original=game.run;result={};actual=[];state={};events=[];before=None;last_direction=0;approached=False;sequence_start=None;done=None;cached={};driver=Path(__file__).read_bytes()
 def wrapped(*args,**kwargs):
  nonlocal before,done
  result['folder']=Path(args[2]);observer=kwargs['ram_observer'];controller=kwargs['input_provider'];stop=kwargs.get('stop_when');last_frame=[0]
  def observe(f,r):
   nonlocal before,done
   observer(f,r);last_frame[0]=f
   if f<=start:return
   if sms:
    state.update(room=int.from_bytes(r[0xb9:0xbb],'little'),game=r[0x1d],hero=r[0x301],counter=r[0x304],x=r[0x313],y=r[0x311],direction=r[0x30a],selected=r[0xdf],slot=r[0xa0],level=r[0xe5],magic=r[0xdb],flags=r[0x100+(a.earth_room&255)],cell=r[0x1c00+a.earth_cell],spell=r[0x330],tilemap=bytes(r[0x1600:0x1c00]),enemies=any(r[0x600+i*48]>=0x20 and r[0x600+i*48+0x18] and r[0x600+i*48+3]&2 for i in range(8)))
   else:
    data=lambda n,k:bytes(r[(sy[n]+i)^1] for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big');actors=data('world_actor_state',768)
    state.update(room=word('room_id'),game=word('game_state'),hero=word('hero_state'),counter=word('hero_counter'),x=word('hero_x')>>8,y=word('hero_y')>>8,direction=word('hero_direction'),selected=word('hero_selected_item'),slot=word('inventory_slot'),level=data('hero_items',17)[5],magic=word('hero_magic'),flags=data('game_save_state',592)[0x50+(a.earth_room&255)],cell=data('scratch',4096)[0x800+a.earth_cell],spell=data('world_spell_state',48)[0],tilemap=data('sms_vram',16384)[0x3800:0x3e00],enemies=any(actors[i*48]>=0x20 and actors[i*48+0x18] and actors[i*48+3]&2 for i in range(8)))
   if done is None and events and any((a.earth_action_only or e['flags']&4) and e['cell']!=0x0b for e in events) and state['room']==a.passage_destination and state['game']==12 and state['hero']==1 and state['selected']==1:
    done=f;args[3].add(f+100)
   if state['room']==a.earth_room and state['game']==12:
    assert state['level'],'Earth must be acquired, never injected'
    row={k:v for k,v in state.items() if k not in ['tilemap','enemies']}
    if before is None:before=dict(frame=f,**row);assert state['cell']==0x0b and not state['flags']&4
    if not events or any(row[k]!=events[-1][k] for k in ['selected','slot','magic','flags','cell','spell']):events.append(dict(frame=f,**row));args[3].add(f+1)
  def choose(f):
   nonlocal last_direction,approached,sequence_start
   if cached.get('frame')==f:return cached['buttons']
   terrain_done=bool(state and (state['flags']&4 or a.earth_action_only and state['cell']!=0x0b))
   active=f>start and state.get('room')==a.earth_room and (a.earth_during_combat or not state['enemies'] or sequence_start is not None) and (not terrain_done or state['selected']!=1 or state['game']==16)
   if done is not None:value=[]
   elif not active:value=controller(f)
   elif state['selected']!=(1 if terrain_done else 5) or state['game']==16:
    value=[];wanted=1 if terrain_done else 5
    if f%20==0:
     if state['game']==12 and state['hero']==1:value=[0]
     elif state['game']==16:
      if state['selected']==wanted:value=[0]
      elif state['slot']//4!=wanted//4:value=[5 if state['slot']//4<wanted//4 else 4]
      elif state['slot']%4!=wanted%4:value=[7 if state['slot']%4<wanted%4 else 6]
      else:value=[8]
   elif state['game']!=12 or state['hero'] not in [0,1]:value=[]
   elif state['spell']:value=[]
   elif (state['x'],state['y'])==(cast_x,cast_y) and state['direction']==a.earth_direction:
    last_direction=a.earth_direction;value=[] if state['counter'] or f%3==0 else [8]
   elif state['counter']:value=[4+last_direction]
   else:
    if (state['x'],state['y'])==behind:approached=True
    target=(cast_x,cast_y) if approached else behind
    route=game.walk(state['tilemap'],(state['x'],state['y']),lambda q:q==target);value=[]
    if route:last_direction=route[0];value=[4+last_direction]
   # Enemy activation must not hand an open inventory to the combat driver.
   # Keep ownership from the first ordinary Earth input through re-equipping.
   if active and value and sequence_start is None:sequence_start=f
   cached.update(frame=f,buttons=value)
   if not actual or actual[-1]['buttons']!=value:actual.append(dict(frame=f,buttons=list(value)))
   return value
  kwargs.update(ram_observer=observe,input_provider=choose,stop_when=lambda: bool(stop and stop()) or done is not None and last_frame[0]>=done+100);return original(*args,**kwargs)
 game.run=wrapped
 try:game.main()
 finally:game.run=original
 folder=result['folder'];(folder/'controls.json').write_text(json.dumps(actual,indent=2)+'\n');(folder/'earth_events.json').write_text(json.dumps(events,indent=2)+'\n');report=json.loads((folder/'report.json').read_bytes());opened=next((r for r in events if (a.earth_action_only or r['flags']&4) and r['cell']!=0x0b),None)
 if done is not None:report.update(passed=True,failure=None,stop_reason='earth_cell_cleared' if a.earth_action_only else 'earth_passage_traversed',destination_combat_cleared=report['room_cleared'])
 report.update(earth_sequence_start_frame=sequence_start,earth_sequence_latched=sequence_start is not None,earth_action_only_requested=a.earth_action_only,earth_cast_position=[cast_x,cast_y],earth_cast_direction=a.earth_direction,earth_cell_cleared=bool(opened),earth_passage_traversed=done is not None and not a.earth_action_only,earth_during_combat_requested=a.earth_during_combat,earth_route_passed=done is not None,earth_route_complete_frame=done,earth_passage_room=a.earth_room,earth_cell=a.earth_cell,earth_passage_opened=bool(opened) and not a.earth_action_only,earth_before=before,earth_opened=opened,earth_controller_sha256=sha(driver),earth_state_writes=0);(folder/'report.json').write_text(json.dumps(report,indent=2)+'\n')
 print('Earth passage opened:',bool(opened))
if __name__=='__main__':main()
