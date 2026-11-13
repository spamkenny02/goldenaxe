"""Walk toward actual enemies, with and without the title-menu life option."""
import json,sys,hashlib
from run_core import ROOT,run
from validate_konami_menu import inputs
from validate_playable_sprite_limit import symbols
from natural_dungeon_combat import walk
from natural_dungeon_route import World

def main():
 rom=ROOT/'validation/konami04/candidate.bin';sy=symbols(ROOT/'megadrive/out/release/symbol.txt');results=[]
 for mode in ['off','life']:
  world=World();world.goal=dict(room=0xa4,x=136,y=112);path,_=world.route((0x95,136,112),arrive_in_room=True);assert path;cursor=0
  state={};events=[];direction=1;first_contact=None;first_damage=None;protected=0;captures={7000};observed=0
  def observe(f,r):
   nonlocal first_contact,first_damage,protected,observed
   observed=f
   if f<4000:return
   w=lambda n:int.from_bytes(r[sy[n]:sy[n]+2],'little');data=lambda n,k:bytes(r[(sy[n]+i)^1]for i in range(k))
   state.update(room=w('room_id'),game=w('game_state'),hero=w('hero_state'),counter=w('hero_counter'),x=w('hero_x')>>8,y=w('hero_y')>>8,health=w('hero_health'),max_health=w('hero_max_health'),hurt=w('hero_hurt'),loading=data('door_transition_loading',1)[0],resume=w('resume_phase'),graphics=w('world_graphics_class'),tilemap=data('sms_vram',16384)[0x3800:0x3e00],actors=data('world_actor_state',768))
   assert w('sound_unhandled_command')==0
   if state['game']==12 and state['room']==0xa4 and state['hero']==1 and not state['resume'] and not state['loading']:
    if mode=='life':assert state['health']==state['max_health'] and state['hurt']==129
    for n in range(16):
     e=state['actors'][n*48:(n+1)*48]
     if 0x10<=e[0]<0x63 and e[24] and abs(e[19]-state['x'])<=10 and abs(e[17]-state['y'])<=10:
      if first_contact is None:first_contact=f;captures.add(f+1)
      protected+=1
    if state['health']<state['max_health'] and first_damage is None:first_damage=f;captures.add(f+1)
  def choose(f):
   nonlocal direction,cursor
   if f<=4000 or not state:return []
   if state['game']!=12 or state['hero']!=1 or state['resume'] or state['loading']:return []
   if state['counter']:return [4+direction]
   point=state['x'],state['y']
   if state['room']!=0xa4:
    here=(state['room'],*point)
    while cursor<len(path) and here==path[cursor][2][:3]:cursor+=1
    if cursor<len(path):direction=path[cursor][1];return [4+direction]
    return []
   else:
    choices=[]
    for n in range(16):
     e=state['actors'][n*48:(n+1)*48]
     if 0x10<=e[0]<0x63 and e[24]:choices.append((abs(e[19]-point[0])+abs(e[17]-point[1]),e[19],e[17]))
    if not choices:return []
    _,x,y=min(choices);goal=(max(16,min(240,round(x/8)*8)),max(16,min(160,round(y/8)*8)))
   route=walk(state['tilemap'],point,lambda q:q==goal)
   if route:direction=route[0];return [4+direction]
   if state['room']==0xa4:direction=2 if goal[0]<point[0] else 3 if goal[0]>point[0] else 0 if goal[1]<point[1] else 1;return [4+direction]
   return []
  folder=ROOT/f'validation/konami04-life-contact-v2-{mode}'
  run(rom,8000,folder,captures,inputs(mode),skip_intro=False,input_provider=choose,ram_observer=observe,stop_when=lambda:bool(first_damage and mode=='off' and observed>first_damage+2 or mode=='life' and first_contact and observed>first_contact+240))
  passed=(first_damage is not None) if mode=='off' else first_contact is not None and protected>=10 and first_damage is None
  r=dict(passed=passed,mode=mode,first_contact=first_contact,first_damage=first_damage,enemy_overlap_frames=protected,final={k:v for k,v in state.items()if k not in ['actors','tilemap']},external_ram_writes=0,primary_state_imports=0);(folder/'report.json').write_bytes((json.dumps(r,indent=2)+'\n').encode());results.append(r);print(json.dumps(r),flush=True);assert passed
 (ROOT/'analysis/konami_life_contact_v0323_report.json').write_bytes((json.dumps(dict(passed=True,md_sha256=hashlib.sha256(rom.read_bytes()).hexdigest(),cases=results),indent=2)+'\n').encode())
if __name__=='__main__':main()
