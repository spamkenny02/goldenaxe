"""Plan ordinary inputs after a declared early guard release; add no RAM writes."""
import argparse,json,sys
from pathlib import Path
import natural_dungeon_combat as game
from run_core import ROOT
from assisted_prefix import prefix_writes,recording
from rebase_natural_campaign import evidence
from validate_playable_sprite_limit import symbols
from archive_lossless_evidence import sha

def main():
 p=argparse.ArgumentParser(add_help=False);p.add_argument('--planner',choices=['ordinary','contact','earth','item','evasive','cautious','exit'],default='ordinary');p.add_argument('--planning-step',type=int,choices=[8,16,24,32],default=8);a,args=p.parse_known_args()
 assert '--assisted-prefix' in args and '--continuation' in args
 name=args[args.index('--continuation')+1];source=ROOT/'validation/natural-dungeon-combat'/name;c=json.loads((source/'capture.json').read_bytes());assist,writes=recording(source,c)
 assert assist.get('approach_closed_early') and assist['release_write_frame']<=c['frames']
 assert writes[-1][0]==assist['release_write_frame'] and writes[-1][2]==b'\x00\x00'
 assert prefix_writes(source,c,True)==writes
 expected=evidence(source/f"ram_{c['frames']:05d}.bin");sy=symbols(ROOT/'megadrive/out/release/symbol.txt');start=c['frames'];original=game.run;folder=None;first_combat=None;first_damage=None;previous=None;observed=0
 def wrapped(*values,**kwargs):
  nonlocal folder
  folder=Path(values[2]);assert list(kwargs.get('ram_writes',()))==writes
  observer=kwargs['ram_observer'];stop=kwargs.get('stop_when');terminal=[None]
  def observe(frame,raw):
   nonlocal first_combat,first_damage,previous,observed
   observed=frame
   if frame==start:assert raw==expected,'Verified full RAM must replay before extension'
   if frame>=start:
    data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big')
    state=dict(frame=frame,room=word('room_id'),game=word('game_state'),health=word('hero_health'),hurt=word('hero_hurt'))
    assert state['hurt']<=128,'No held test guard may exist after early release'
    if frame>start and state['room']==assist['closed_before_room'] and state['game']==12 and first_combat is None:
     actors=data('world_actor_state',768);first_combat=dict(**state,actors=[dict(slot=i,kind=actors[i*48],hp=actors[i*48+24]) for i in range(8) if actors[i*48]>=0x20 and actors[i*48+24]])
    if frame>start and previous is not None and state['health']<previous['health'] and first_damage is None:first_damage=dict(**state,before=previous['health'])
    previous=state
   observer(frame,raw)
   if terminal[0] is None and stop and stop():
    terminal[0]=frame+1;values[3].add(frame+1)
  # Video runs before the observer: request the next frame, then stop there.
  values[3].add(values[1])
  kwargs['ram_observer']=observe
  kwargs['stop_when']=lambda:terminal[0] is not None and observed>=terminal[0]
  return original(*values,**kwargs)
 game.run=wrapped;sys.argv=[sys.argv[0]]+args
 try:
  if a.planner=='ordinary':game.main()
  elif a.planner=='contact':
   import natural_contact_passage;natural_contact_passage.main()
  elif a.planner=='earth':
   import natural_earth_passage;natural_earth_passage.main()
  elif a.planner=='item':
   import natural_item_acquisition;natural_item_acquisition.main()
  elif a.planner=='exit':
   import natural_exit_planner;natural_exit_planner.main()
  elif a.planner=='cautious':
   import natural_boss_cautious_planner;natural_boss_cautious_planner.main()
  else:
   import natural_boss_evasive_planner as planner
   base=planner.EvasivePlanner
   class Stepped(base):
    def __init__(self,*values,**options):
     super().__init__(*values,**options);assert self.horizon==96 and self.horizon%a.planning_step==0;self.step=a.planning_step
   planner.EvasivePlanner=Stepped;planner.main()
 finally:
  game.run=original
  if folder is not None and (folder/'capture.json').exists():
   nc=json.loads((folder/'capture.json').read_bytes());assert nc['test_ram_writes']==c['test_ram_writes']
   (folder/'assistance.json').write_bytes((source/'assistance.json').read_bytes());recording(folder,nc)
   report=json.loads((folder/'report.json').read_bytes());report.update(unassisted_extension=True,new_assistance_writes=0,guard_release_frame=assist['release_write_frame'],closed_before_room=assist['closed_before_room'],first_intermediate_combat=first_combat,first_extension_damage=first_damage,unassisted_controller_sha256=sha(Path(__file__).read_bytes()),planning_step=a.planning_step if a.planner=='evasive' else None,assisted_route=True,natural_campaign_proof=False,extension_guard_checks_through_frame=observed)
   (folder/'report.json').write_bytes((json.dumps(report,indent=2)+'\n').encode())
if __name__=='__main__':main()
