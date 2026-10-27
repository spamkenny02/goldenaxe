"""Press UP at a ROM-derived contact mechanism using ordinary game input."""
import argparse,json,sys
from pathlib import Path
import natural_dungeon_combat as game
from run_core import ROOT
from archive_lossless_evidence import sha
from validate_playable_sprite_limit import symbols

def main():
 p=argparse.ArgumentParser(add_help=False);p.add_argument('--mechanism-during-combat',action='store_true',help='Use an ordinary UP mechanism before clearing separated live actors');p.add_argument('--contact-room',type=lambda v:int(v,0),required=True);p.add_argument('--contact-destination',type=lambda v:int(v,0),required=True);a,remaining=p.parse_known_args();sys.argv=[sys.argv[0]]+remaining
 ref=json.loads((ROOT/'analysis/contact_script_reference.json').read_bytes());assert ref['source_sha256']==sha((ROOT/'input/original.sms').read_bytes())
 row=next((r for r in ref['records'] if r['room']==a.contact_room and r['kind'] in ['stationary_up_passages','stationary_up_cell']),None);mechanism_source='contact_script_reference'
 if row is None:
  puzzles=json.loads((ROOT/'analysis/room_puzzles_reference.json').read_bytes());assert puzzles['source_sha256']==ref['source_sha256'];row=next(r for r in puzzles['records'] if r['room']==a.contact_room and r['kind']=='open_blocked_passages');mechanism_source='room_puzzles_reference'
 coordinate=row.get('coordinate',0x168)
 point=next((x,y) for y in range(8,169,8) for x in range(8,249,8) if (((y-12)&248)<<3)+(((x-12)&255)>>2&62)+126==coordinate)
 sms='--sms' in remaining;flag='--continuation' if '--continuation' in remaining else '--prefix';name=remaining[remaining.index(flag)+1];family='natural-dungeon-combat' if flag=='--continuation' else 'natural-dungeon-route';prefix=json.loads((ROOT/'validation'/family/name/'capture.json').read_bytes());start=prefix['frames'];sy=None if sms else symbols(ROOT/'megadrive/out/release/symbol.txt')
 original=game.run;result={};actual=[];state={};events=[];done=None;last_direction=0;cached={};before=None;opened=None;driver=Path(__file__).read_bytes()
 def wrapped(*args,**kwargs):
  result['folder']=Path(args[2]);observer=kwargs['ram_observer'];controller=kwargs['input_provider'];stop=kwargs.get('stop_when');last_frame=[0]
  def observe(f,r):
   nonlocal before,opened,done
   observer(f,r);last_frame[0]=f
   if f<=start:return
   if sms:
    state.update(room=int.from_bytes(r[0xb9:0xbb],'little'),game=r[0x1d],hero=r[0x301],counter=r[0x304],x=r[0x313],y=r[0x311],flags=r[0x100+(a.contact_room&255)],marker=r[0x1c1b],tilemap=bytes(r[0x1600:0x1c00]),enemies=any(r[0x600+i*48]>=0x20 and r[0x600+i*48+0x18] for i in range(8)),active_enemies=any(r[0x600+i*48]>=0x20 and r[0x600+i*48+0x18] and r[0x600+i*48+3]&2 for i in range(8)))
   else:
    data=lambda n,k:bytes(r[(sy[n]+i)^1] for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big');actors=data('world_actor_state',768)
    state.update(room=word('room_id'),game=word('game_state'),hero=word('hero_state'),counter=word('hero_counter'),x=word('hero_x')>>8,y=word('hero_y')>>8,flags=data('game_save_state',592)[0x50+(a.contact_room&255)],marker=r[(sy['scratch']+0x81b)^1],tilemap=data('sms_vram',16384)[0x3800:0x3e00],enemies=any(actors[i*48]>=0x20 and actors[i*48+0x18] for i in range(8)),active_enemies=any(actors[i*48]>=0x20 and actors[i*48+0x18] and actors[i*48+3]&2 for i in range(8)))
   if state['room']==a.contact_room and state['game']==12:
    value={k:v for k,v in state.items() if k not in ['tilemap','enemies']}
    if before is None:before=dict(frame=f,**value)
    if not events or any(value[k]!=events[-1][k] for k in ['flags','marker']):events.append(dict(frame=f,**value));args[3].add(f+1)
    if opened is None and (state['marker']==0x4d if row['kind']=='stationary_up_cell' else state['flags']&4):opened=dict(frame=f,**value)
   if done is None and opened and state['room']==a.contact_destination and state['game']==12 and state['hero']==1:done=f;args[3].add(f+100)
  def choose(f):
   nonlocal last_direction
   if cached.get('frame')==f:return cached['buttons']
   active=f>start and state.get('room')==a.contact_room and (a.mechanism_during_combat or not state['enemies']) and opened is None
   if done is not None:value=[]
   elif f>start and state.get('room')==a.contact_room and opened is None and not a.mechanism_during_combat and state['enemies'] and not state['active_enemies']:value=[] # Wait for actual spawn/contact activation before combat navigation.
   elif not active:value=controller(f)
   elif state['game']!=12 or state['hero'] not in [0,1]:value=[]
   elif state['counter']:value=[4+last_direction]
   elif (state['x'],state['y'])==point:last_direction=0;value=[4]
   else:
    route=game.walk(state['tilemap'],(state['x'],state['y']),lambda q:q==point);value=[]
    if route:last_direction=route[0];value=[4+last_direction]
   cached.update(frame=f,buttons=value)
   if not actual or actual[-1]['buttons']!=value:actual.append(dict(frame=f,buttons=list(value)))
   return value
  kwargs.update(ram_observer=observe,input_provider=choose,stop_when=lambda: bool(stop and stop()) or done is not None and last_frame[0]>=done+100);return original(*args,**kwargs)
 game.run=wrapped
 try:game.main()
 finally:game.run=original
 folder=result['folder'];(folder/'controls.json').write_text(json.dumps(actual,indent=2)+'\n');(folder/'contact_events.json').write_text(json.dumps(events,indent=2)+'\n');r=json.loads((folder/'report.json').read_bytes())
 if done is not None:r.update(passed=True,failure=None,stop_reason='source_contact_passage_traversed',destination_combat_cleared=r['room_cleared'])
 r.update(mechanism_during_combat_requested=a.mechanism_during_combat,mechanism_source=mechanism_source,contact_route_passed=done is not None,contact_route_complete_frame=done,contact_room=a.contact_room,contact_destination=a.contact_destination,contact_coordinate=coordinate,contact_before=before,contact_opened=opened,contact_controller_sha256=sha(driver),contact_state_writes=0);(folder/'report.json').write_text(json.dumps(r,indent=2)+'\n');print('Contact passage traversed:',done is not None)

if __name__=='__main__':main()
