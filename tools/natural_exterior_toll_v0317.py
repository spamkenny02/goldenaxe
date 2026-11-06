"""Earn a toll through real exterior combat and dropped coins; no new RAM writes."""
import contextlib,io,json
from run_core import ROOT,run,FrameWrites
from rebase_natural_campaign import evidence
from archive_lossless_evidence import sha
from assisted_prefix import prefix_writes,recording
from validate_playable_sprite_limit import symbols
import natural_dungeon_combat as nav
from natural_combat_aim import directions

GUARDED=False
TRIAL="md-v0317-d9-earned-toll01"

def outdoor_walk(tilemap,start,goal):
 # Exterior transitions trigger on the border at arbitrary coordinates.
 # Never let an intra-room combat/coin path silently traverse that border.
 from collections import deque
 from movement_reference import Hero,collision_cache,choose_collision_direction
 queue=deque([start]);parents={start:None};finish=None
 while queue:
  point=queue.popleft()
  if goal(point):finish=point;break
  cache=collision_cache(tilemap,Hero(x=point[0]<<8,y=point[1]<<8),canoe=nav.CANOE_OWNED,ship=nav.SHIP_OWNED)
  for direction,(dx,dy)in enumerate(((0,-8),(0,8),(-8,0),(8,0))):
   nxt=point[0]+dx,point[1]+dy
   if nxt in parents or not(16<=nxt[0]<=240 and 16<=nxt[1]<=152):continue
   if choose_collision_direction(direction,cache)!=direction:continue
   parents[nxt]=point,direction;queue.append(nxt)
 if finish is None:return None
 path=[]
 while parents[finish]is not None:previous,direction=parents[finish];path.append(direction);finish=previous
 return path[::-1]

def main():
 source=ROOT/'validation/natural-dungeon-combat/md-auto-v0317-d8-exit01'
 out=ROOT/'validation/natural-service-route'/TRIAL
 assert not out.exists()
 cap=json.loads((source/'capture.json').read_bytes());start=cap['frames'];digest=sha((ROOT/'gaw-megadrive.bin').read_bytes());assert cap['rom_sha256']==digest and cap['sram_input']is None
 writes=prefix_writes(source,cap,True);controls=json.loads((source/'controls.json').read_bytes());timeline=[()]*(start+1)
 for i,row in enumerate(controls):
  end=controls[i+1]['frame']if i+1<len(controls)else start+1
  timeline[row['frame']:end]=[tuple(row['buttons'])]*(end-row['frame'])
 sy=symbols(ROOT/'megadrive/out/release/symbol.txt');state={};events=[];captures={start};actors=[];loot=[];tilemap=b'';first=None;done=None;failure=None;observed=0;last=0;key=None;empty_since=None;no_path_since=None;visits={};visited_room=None
 def observe(f,r):
  nonlocal actors,loot,tilemap,first,done,failure,observed,key,empty_since,visited_room
  observed=f
  if f<start:return
  data=lambda n,k:bytes(r[(sy[n]+i)^1]for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big')
  state.update(room=word('room_id'),game=word('game_state'),hero=word('hero_state'),counter=word('hero_counter'),direction=word('hero_direction'),x=word('hero_x')>>8,y=word('hero_y')>>8,health=word('hero_health'),max_health=word('hero_max_health'),gold=word('hero_gold'),selected=word('hero_selected_item'),inventory_slot=word('inventory_slot'),weapon=word('hero_weapon_level'),audio_error=word('sound_unhandled_command'))
  if state['room']!=visited_room:
   visits[state['room']]=visits.get(state['room'],0)+1;visited_room=state['room']
  raw=data('world_actor_state',768);lr=data('world_loot_state',336);tilemap=data('sms_vram',16384)[0x3800:0x3e00]
  actors=[dict(slot=i,type=raw[i*48],hp=raw[i*48+24],flags=raw[i*48+3],hit_box=raw[i*48+27],contact_box=raw[i*48+28],x=raw[i*48+19],y=raw[i*48+17])for i in range(16)if raw[i*48]]
  loot=[dict(type=lr[i*48],x=lr[i*48+19],y=lr[i*48+17])for i in range(7)if lr[i*48]]
  assert not any(e['hp']and 0x63<=e['type']<=0x7c for e in actors),'Unexpected boss'
  if first is None:first=dict(state);assert first['gold']==6 and first['room']==0x29
  nav.CANOE_OWNED=bool(data('hero_items',17)[12]);nav.SHIP_OWNED=bool(data('hero_items',17)[16])
  if not state['health']or state['game']==20:failure='hero_died'
  if state['audio_error']:failure='native_audio_error'
  if state['gold']>=10 and state['game']==12 and state['hero']==1 and not state['counter']and done is None:done=f;captures.add(f+1)
  k=(state['room'],state['game'],state['gold'],state['health'],tuple((e['slot'],e['type'],e['hp'])for e in actors),tuple((e['type'],e['x'],e['y'])for e in loot))
  if k!=key:events.append(dict(frame=f,**state,actors=actors,loot=loot));captures.add(f+1);key=k
  if any(e['hp']and e['type']>=0x20 for e in actors)or loot:empty_since=None
  elif empty_since is None:empty_since=f
 def choose(f):
  nonlocal last,no_path_since
  if f<=start:return list(timeline[f])
  if done or failure:return []
  if state.get('selected')!=0 or state.get('game')==16:
   if f%20:return []
   if state.get('game')==12 and state.get('hero')==1:return [0]
   if state.get('game')==16:
    if state['selected']==0:return [0]
    if state['inventory_slot']!=0:return [6]
    return [8]
   return []
  if state.get('game')!=12:return []
  p=state['x'],state['y'];enemies=[e for e in actors if e['hp']and e['type']>=0x20 and e['flags']&2]
  near=sorted(enemies,key=lambda e:abs(e['x']-p[0])+abs(e['y']-p[1]))
  cash=[e for e in loot if e['type']in(8,9)]
  useful=cash or[e for e in loot if e['type']in(10,11)and state['health']<state['max_health']]
  variant=state['weapon']+1 if state['selected']==1 else 0
  if near and(state['hero']in(2,3,4,5)or directions(p,near[0],variant,safe=False)):
   ds=directions(p,near[0],variant,safe=False)
   if ds:last=ds[0]
   return [4+last,8]if f%3 else []
  if state['counter']:return [4+last]
  if useful:goal=lambda q:any(abs(q[0]-e['x'])<8 and abs(q[1]-e['y'])<8 for e in useful)
  elif near:goal=lambda q:any(directions(q,e,variant,safe=False)for e in near)
  elif empty_since is not None and f-empty_since>120:
   edges={0:lambda q:q[1]<=16,1:lambda q:q[1]>=152,2:lambda q:q[0]<=16,3:lambda q:q[0]>=240}
   for direction in sorted([2,1,3,0],key=lambda d:visits.get((state['room']+[-16,16,-1,1][d])&255,0)):
    route=outdoor_walk(tilemap,p,edges[direction])
    if route is None:continue
    if edges[direction](p):last=direction;return [4+last]
    if route:last=route[0];return [4+last]
   return []
  else:return []
  path=outdoor_walk(tilemap,p,goal)
  if not path and useful and near:
   path=outdoor_walk(tilemap,p,lambda q:any(directions(q,e,variant,safe=False)for e in near))
  if not path and near:
   # Source emerging shooters can be hidden with zero attack boxes. Patrol
   # rather than idling forever at an unreachable melee stance.
   point=(48,72)if(f//128)&1 else(208,136)
   path=outdoor_walk(tilemap,p,lambda q:q==point)
  if path:
   no_path_since=None;last=path[0];return [4+last]
  if no_path_since is None:no_path_since=f
  if f-no_path_since>180:
   # Some exterior spawns occupy terrain disconnected from the hero. Move
   # normally to a reachable neighboring screen instead of claiming a clear.
   edges={0:lambda q:q[1]<=16,1:lambda q:q[1]>=152,2:lambda q:q[0]<=16,3:lambda q:q[0]>=240}
   for direction in sorted([3,1,2,0],key=lambda d:visits.get((state['room']+[-16,16,-1,1][d])&255,0)):
    route=outdoor_walk(tilemap,p,edges[direction])
    if route is None:continue
    if edges[direction](p):last=direction;return [4+last]
    if route:last=route[0];return [4+last]
  return []
 def controller(f):
  buttons=choose(f)
  if f>start and(not controls or controls[-1]['buttons']!=buttons):controls.append(dict(frame=f,buttons=buttons))
  return buttons
 with contextlib.redirect_stdout(io.StringIO()):run(ROOT/'gaw-megadrive.bin',start+12000,out,captures,cap['presses'],skip_intro=False,input_provider=controller,ram_observer=observe,stop_when=lambda:bool(failure)or done is not None and observed>=done+1,core_options=cap['core_options'],ram_writes=FrameWrites(writes))
 result=dict(passed=done is not None and not failure,rom_sha256=digest,source_prefix=source.name,first_state=first,last_state=state,complete_frame=done,failure=failure or(None if done else'frame_limit'),new_assistance_writes=0,primary_state_imports=0,currency_or_inventory_fixtures=False,sram_checkpoint_injection=False,rom_modifications=False,driver_sha256=sha(__import__('pathlib').Path(__file__).read_bytes()),scope='Real exterior foes, ordinary directional/C buttons and coin pickups; inherited approach writes only, no new writes or resource fixtures.')
 for name,value in [('report',result),('events',events),('controls',controls)]: (out/(name+'.json')).write_bytes((json.dumps(value,indent=2)+'\n').encode())
 if not GUARDED:
  (out/'assistance.json').write_bytes((source/'assistance.json').read_bytes());recording(out,json.loads((out/'capture.json').read_bytes()))
 else:(out/'route_report.json').write_bytes((out/'report.json').read_bytes())
 print(json.dumps(result,indent=2),flush=True)
if __name__=='__main__':main()
