"""Controlled Continue-fixture route to the palace; never a cold campaign proof."""
import argparse,contextlib,io,json
from pathlib import Path
from run_core import ROOT,run,FrameWrites
from validate_playable_sprite_limit import symbols
from archive_lossless_evidence import sha
from natural_dungeon_route import World,Hero,collision_cache,choose_collision_direction
from world_persisted_projection import render_persisted


def main():
 p=argparse.ArgumentParser();p.add_argument('--fixture',required=True);p.add_argument('--trial',required=True);p.add_argument('--frames',type=int,default=20000);a=p.parse_args()
 fixture=ROOT/f'validation/palace-save-fixture-{a.fixture}';provenance=json.loads((ROOT/f'analysis/palace_save_fixture_{a.fixture}_report.json').read_bytes());assert provenance['passed'] and provenance['controlled_sram_fixture'] and not provenance['natural_campaign_proof']
 sram=fixture/'controlled-derived.srm';assert sha(sram.read_bytes())==provenance['sram_sha256'];rom=ROOT/'gaw-megadrive.bin';assert sha(rom.read_bytes())==provenance['md_sha256'];sy=symbols(ROOT/'megadrive/out/release/symbol.txt')
 cap=json.loads((fixture/'boot/capture.json').read_bytes());prefix=provenance['first_playable']['frame']+1;initial=(fixture/f'boot/ram_{prefix:05d}.bin').read_bytes();get=lambda n,k:bytes(initial[(sy[n]+i)^1] for i in range(k));save=get('game_save_state',592);items=get('hero_items',17)
 class Projection(World):
  def render_cells(self,room,cells,meta=None):return render_persisted(self,room,cells,save[0x50:0x150],meta,project_palace=True)
 world=Projection(10);world.ship_owned=bool(items[16]);world.canoe_owned=bool(items[12]);world.boots_owned=bool(items[14]);world.axe_terrain=world.rope_terrain=True
 start=(int.from_bytes(get('room_id',2),'big'),int.from_bytes(get('hero_x',2),'big')>>8,int.from_bytes(get('hero_y',2),'big')>>8)
 world.live_room=start[0];world.live_map=get('sms_vram',16384)[0x3800:0x3e00];path,nodes=world.route(start);assert path is not None,(start,'no proposed palace route');print('plan',len(path),'steps',nodes,'nodes',flush=True)
 out=ROOT/f'validation/controlled-palace-route-{a.trial}';assert not out.exists();state={};events=[];controls=[];writes=FrameWrites();captures={prefix};cursor=0;last_progress=prefix;observed=0;failure=None;failed_frame=None;ready=None;gate_started=None;gate_opened=None;cached_frame=-1;cached=[];replans=set()
 def observe(f,raw):
  nonlocal observed,failed_frame,ready,gate_started,gate_opened,failure
  observed=f
  if f<prefix:return
  data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k));w=lambda n:int.from_bytes(data(n,2),'big')
  current=dict(frame=f,room=w('room_id'),game=w('game_state'),hero=w('hero_state'),counter=w('hero_counter'),health=w('hero_health'),hurt=w('hero_hurt'),x=w('hero_x')>>8,y=w('hero_y')>>8,maze=data('forest_maze_progress',1)[0],resume=w('resume_phase'),loading=data('door_transition_loading',1)[0],seen=data('game_save_state',592)[0x48],audio_error=w('sound_unhandled_command'))
  state.update(current,cells=data('scratch',4096)[0x800:0x8a0],tilemap=data('sms_vram',16384)[0x3800:0x3e00])
  if world.live_room is not None and current['room']!=world.live_room:world.live_room=world.live_map=None
  if not events or any(current[n]!=events[-1][n] for n in ['room','game','health','seen']):events.append(current);captures.add(f+1)
  if current['room']==0x8b and current['seen'] and gate_started is None:gate_started=current;captures.add(f+1)
  if current['room']==0x8b and current['seen'] and state['cells'][0x30]==0x30 and gate_opened is None:gate_opened=current;captures.add(f+1)
  if not failure and (current['game']==20 or current['audio_error']):failure='died_or_audio_error';failed_frame=f;captures.add(f+1)
  # Approaches only. Publish the release before either final-area boss simulates.
  if f>=prefix and current['room'] not in [0x11e,0x14c]:
   actors=data('world_actor_state',768);assert not any(actors[i] in list(range(0x67,0x6e))+list(range(0x78,0x7d)) and actors[i+3]&2 for i in range(0,768,48)),('Unexpected boss on guarded approach',current)
   danger=any(actors[i]>=16 and actors[i+3]&2 for i in range(0,768,48))
   if danger or current['hurt']>128:writes.append((f+1,sy['hero_hurt'],b'\0\x81' if danger else b'\0\0'))
  elif current['hurt']>128:writes.append((f+1,sy['hero_hurt'],b'\0\0'))
  if current['room']==0x18d and current['game']==12 and current['hero']==1 and not current['resume'] and not current['loading'] and ready is None:ready=f;captures.add(f+1)
 def choose(f):
  nonlocal cursor,last_progress,path,failure,failed_frame
  if f<=prefix or not state or ready is not None or failure:return []
  if state['game']!=12 or state['hero'] not in [0,1] or state['resume'] or state['loading']:last_progress=f;return []
  if state['room']==0x8b and state['seen'] and state['cells'][0x30]!=0x30:last_progress=f;return []
  point=state['room'],state['x'],state['y']
  while cursor<len(path) and point==tuple(path[cursor][2][:3]):cursor+=1;last_progress=f
  if cursor==len(path):return [4]
  previous,d,nxt=path[cursor]
  if not state['counter'] and point!=tuple(previous[:3]):
   matches=[i for i,row in enumerate(path) if tuple(row[0][:3])==point]
   if matches:cursor=min(matches,key=lambda i:abs(i-cursor));previous,d,nxt=path[cursor];last_progress=f
   else:
    path,_=world.route((*point,state['maze']));cursor=0;last_progress=f
    if not path:failure='no_proposed_route_after_displacement';failed_frame=f;captures.add(f+1);return []
    previous,d,nxt=path[0]
  if not state['counter'] and state['hero']==1:
   cache=collision_cache(state['tilemap'],Hero(x=point[1]<<8,y=point[2]<<8),canoe=world.canoe_owned,ship=world.ship_owned)
   if choose_collision_direction(d,cache)!=d:
    nearby=any(0x80<=cell<=0x84 and abs((n&15)*16+8-point[1])<=32 and abs((n>>4)*16+8-point[2])<=40 for n,cell in enumerate(state['cells']))
    if nearby:return [4+d,8] if f%3 else []
    key=(point,d,sha(state['tilemap']))
    if key not in replans:
     replans.add(key);world.live_room=point[0];world.live_map=state['tilemap'];replacement,_=world.route((*point,state['maze']))
     if replacement:path=replacement;cursor=0;previous,d,nxt=path[0];last_progress=f
  if f-last_progress>600:failure='no_route_progress';failed_frame=f;captures.add(f+1);return []
  return [4+d]
 def control(f):
  nonlocal cached_frame,cached
  if f!=cached_frame:
   cached_frame=f;cached=choose(f)
   if f>prefix and (not controls or controls[-1]['buttons']!=cached):controls.append(dict(frame=f,buttons=list(cached)))
  return cached
 with contextlib.redirect_stdout(io.StringIO()):run(rom,a.frames,out,captures,cap['presses'],ram_writes=writes,ram_observer=observe,input_provider=control,sram_in=sram,skip_intro=False,stop_when=lambda:ready is not None and observed>ready or failure is not None and observed>failed_frame)
 clean={k:v for k,v in state.items() if k not in ['cells','tilemap']};report=dict(passed=ready is not None and gate_opened is not None,failure=failure or (None if ready else 'frame_limit'),frames=observed,last_state=clean,first_ready=ready,gate_started=gate_started,gate_opened=gate_opened,controlled_sram_fixture=True,natural_campaign_proof=False,game_written_save=False,md_sha256=sha(rom.read_bytes()),sram_fixture=sram.relative_to(ROOT).as_posix(),sram_sha256=sha(sram.read_bytes()),scope='Controlled palace integration route using normal input and approach-only hurt guards after a synthetic Continue fixture. Not a whole-campaign proof.')
 assist=dict(assisted_route=True,ram_injections=True,rom_modifications=False,health_refills=0,boss_assistance=False,primary_state_imports=1,controlled_sram_fixture=True,sram_initialization_import=True,game_written_save=False,sram_sha256=sha(sram.read_bytes()),activation_after_frame=prefix,boss_room=0x11e,first_boss_entry=None,release_write_frame=None,first_boss_combat=None,first_boss_damage=None)
 assist['episodes']=[{k:assist[k] for k in ['activation_after_frame','boss_room','first_boss_entry','release_write_frame','first_boss_combat','first_boss_damage']}|dict(end_frame=observed+1)]
 assist['writes']=[dict(frame=f,address=ad,data_hex=v.hex()) for f,ad,v in writes]
 for name,value in [('assistance',assist),('report',report),('events',events),('controls',controls),('approach_writes',[dict(frame=f,address=ad,data_hex=v.hex()) for f,ad,v in writes])]: (out/(name+'.json')).write_bytes((json.dumps(value,indent=2)+'\n').encode())
 (ROOT/f'analysis/controlled_palace_route_{a.trial}_report.json').write_bytes((json.dumps(report,indent=2)+'\n').encode());print(json.dumps(report,indent=2))

if __name__=='__main__':main()
