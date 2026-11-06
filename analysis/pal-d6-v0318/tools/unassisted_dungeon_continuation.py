"""Plan ordinary inputs after a declared early guard release; add no RAM writes."""
import argparse,json,sys
from pathlib import Path
import natural_dungeon_combat as game
from run_core import ROOT
from assisted_prefix import prefix_writes,recording,controlled_sram_input
from rebase_natural_campaign import evidence
from validate_playable_sprite_limit import symbols
from archive_lossless_evidence import sha

def main():
 p=argparse.ArgumentParser(add_help=False);p.add_argument('--planner',choices=['ordinary','contact','earth','item','evasive','cautious','exit'],default='ordinary');p.add_argument('--planning-step',type=int,choices=[8,16,24,32],default=8);p.add_argument('--entry-boss-kind',type=lambda v:int(v,0),help='Walk UP inside this boss room before predictive sidesteps');p.add_argument('--stop-on-ending',action='store_true',help='Capture the real final-boss handoff before a separate ordinary-input ending continuation');a,args=p.parse_known_args()
 assert '--assisted-prefix' in args and '--continuation' in args
 name=args[args.index('--continuation')+1];source=ROOT/'validation/natural-dungeon-combat'/name;c=json.loads((source/'capture.json').read_bytes());assist,writes=recording(source,c)
 assert assist.get('approach_closed_early') and assist['release_write_frame']<=c['frames']
 assert writes[-1][0]==assist['release_write_frame'] and writes[-1][2]==b'\x00\x00'
 assert prefix_writes(source,c,True,controlled='--controlled-sram-prefix' in args)==writes
 expected=evidence(source/f"ram_{c['frames']:05d}.bin");sy=symbols(ROOT/'megadrive/out/release/symbol.txt');start=c['frames'];original=game.run;folder=None;first_entry=None;first_combat=None;first_fight_damage=None;first_damage=None;previous=None;observed=0;ending_handoff=None
 if a.stop_on_ending:assert assist['closed_before_room']==0x14c
 def wrapped(*values,**kwargs):
  nonlocal folder
  folder=Path(values[2]);assert list(kwargs.get('ram_writes',()))==writes
  observer=kwargs['ram_observer'];stop=kwargs.get('stop_when');terminal=[None]
  def observe(frame,raw):
   nonlocal first_entry,first_combat,first_fight_damage,first_damage,previous,observed,ending_handoff
   observed=frame
   if frame==start:assert raw==expected,'Verified full RAM must replay before extension'
   # Re-observe the complete fight after this episode's release, including
   # inherited inputs. A continuation may begin during the death animation.
   if frame>=start or frame>assist['release_write_frame']:
    data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big')
    state=dict(frame=frame,room=word('room_id'),game=word('game_state'),health=word('hero_health'),hurt=word('hero_hurt'))
    assert state['hurt']<=128,'No held test guard may exist after early release'
    if frame>assist['release_write_frame'] and state['room']==assist['closed_before_room'] and first_entry is None:
     assert state['game']!=12,'Require the observed room transition before combat'
     first_entry=dict(state)
    if frame>assist['release_write_frame'] and state['room']==assist['closed_before_room'] and state['game']==12 and first_combat is None:
     actors=data('world_actor_state',768);first_combat=dict(**state,actors=[dict(slot=i,kind=actors[i*48],hp=actors[i*48+24]) for i in range(8) if actors[i*48]>=0x20 and actors[i*48+24]])
    if first_combat is not None and state['room']==assist['closed_before_room'] and state['game']==12 and previous is not None and state['health']<previous['health'] and first_fight_damage is None:
     first_fight_damage=dict(frame=frame,before=previous['health'],after=state['health'],hurt=state['hurt'])
    if frame>start and previous is not None and state['health']<previous['health'] and first_damage is None:first_damage=dict(**state,before=previous['health'])
    previous=state
   observer(frame,raw)
   if a.stop_on_ending and frame>start and state['game']==14 and ending_handoff is None:
    assert state['room']==0x14c and state['health']>0
    assert first_combat and any(e['kind']==0x6d and e['hp'] for e in first_combat['actors'])
    assert data('game_save_state',592)[0x28]==1,'Require the real final-dungeon defeat flag'
    ending_handoff=dict(**state,final_dungeon_defeated=True)
   if terminal[0] is None and (ending_handoff is not None or stop and stop()):
    terminal[0]=frame+1;values[3].add(frame+1)
  # Video runs before the observer: request the next frame, then stop there.
  values[3].add(values[1])
  kwargs['ram_observer']=observe
  kwargs['stop_when']=lambda:terminal[0] is not None and observed>=terminal[0]
  return original(*values,**kwargs)
 if a.planner in ('evasive','cautious') and '--lookahead-rooms' not in args:args+=['--lookahead-rooms',hex(assist['closed_before_room'])]
 if a.planner=='exit' and '--lookahead-rooms' not in args:args+=['--lookahead-rooms',args[args.index('--rooms')+1]]
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
   import natural_exit_planner
   exit_base=natural_exit_planner.ExitPlanner
   class SteppedExit(exit_base):
    def __init__(self,*values,**options):
     super().__init__(*values,**options);assert self.horizon%a.planning_step==0;self.step=a.planning_step
   natural_exit_planner.ExitPlanner=SteppedExit;natural_exit_planner.main()
  elif a.planner=='cautious':
   import natural_boss_cautious_planner;natural_boss_cautious_planner.main()
  else:
   import natural_boss_evasive_planner as planner
   base=planner.EvasivePlanner
   class Stepped(base):
    def __init__(self,*values,**options):
     super().__init__(*values,**options);assert self.horizon==96 and self.horizon%a.planning_step==0;self.step=a.planning_step;self.entry_ready=set()
    def observe(self,frame,ram):
     super().observe(frame,ram)
     if self.active and self.current['kind']==a.entry_boss_kind and self.current['y']<=144:self.entry_ready.add(self.current['room'])
    def choose(self,frame,fallback):
     if a.entry_boss_kind is not None and frame>=self.until and self.active and self.current['kind']==a.entry_boss_kind and self.current['room'] not in self.entry_ready:return [4]
     return super().choose(frame,fallback)
   planner.EvasivePlanner=Stepped;planner.main()
 finally:
  game.run=original
  if folder is not None and (folder/'capture.json').exists():
   nc=json.loads((folder/'capture.json').read_bytes());assert nc['test_ram_writes']==c['test_ram_writes']
   completed=json.loads(json.dumps(assist))
   # A main boss's declared episode can now contain its observed entry and
   # combat. This lets a later verified exterior exit start the next episode
   # without reactivating protection during the current return journey.
   # Intermediate fights keep their separate pending-main-boss metadata.
   if assist['boss_room']==assist['closed_before_room'] and first_combat is not None:
    assert first_entry is not None and first_entry['frame']<first_combat['frame']
    fields=dict(first_boss_entry=first_entry,first_boss_combat={k:first_combat[k] for k in ['frame','health','hurt']},first_boss_damage=first_fight_damage)
    completed.update(fields)
    completed['episodes'][-1].update(fields,end_frame=nc['frames']+1,natural_cooldown_observed=bool(first_combat['hurt']))
   (folder/'assistance.json').write_bytes((json.dumps(completed,indent=2)+'\n').encode());recording(folder,nc)
   report=json.loads((folder/'report.json').read_bytes());report.update(primary_state_imports=int(bool(c['sram_input'])),unassisted_extension=True,new_assistance_writes=0,guard_release_frame=assist['release_write_frame'],closed_before_room=assist['closed_before_room'],first_intermediate_combat=first_combat,first_extension_damage=first_damage,unassisted_controller_sha256=sha(Path(__file__).read_bytes()),planning_step=a.planning_step if a.planner in ('evasive','exit') else None,entry_boss_kind=a.entry_boss_kind,assisted_route=True,natural_campaign_proof=False,extension_guard_checks_through_frame=observed)
   if ending_handoff is not None:report.update(passed=True,failure=None,ending_handoff_passed=True,ending_handoff=ending_handoff,stop_reason='real_final_boss_ending_handoff',ending_complete=False)
   (folder/'report.json').write_bytes((json.dumps(report,indent=2)+'\n').encode())
if __name__=='__main__':main()
