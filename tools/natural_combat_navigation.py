"""Guide secondary-core beam search with the source collision graph.

The distance field is only a search heuristic. Every selected input still
executes in the actual game; prediction and official cold replay gates remain.
"""
import collections,json,sys
from pathlib import Path
import natural_combat_beam as beam
from run_core import ROOT
from movement_reference import Hero,collision_cache,choose_collision_direction
from natural_combat_aim import directions


class NavigationPlanner(beam.BeamPlanner):
 def __init__(self,*args,**kwargs):
  super().__init__(*args,**kwargs);self.graphs={};self.navdist={};self.tilemap=b'';self.variant=2;self.canoe=False
 def fields(self,r):
  v=super().fields(r)
  for e in v['foes']:
   offset=e['slot']*48
   if self.sms:e.update(hit_box=r[0x600+offset+27],contact_box=r[0x600+offset+28])
   else:e.update(hit_box=r[(self.sy['world_actor_state']+offset+27)^1],contact_box=r[(self.sy['world_actor_state']+offset+28)^1])
  return v
 def observe(self,f,r):
  super().observe(f,r)
  if self.active:
   canoe=bool(r[0xec]) if self.sms else bool(r[(self.sy['hero_items']+12)^1])
   if canoe!=self.canoe:self.graphs.clear()
   self.canoe=canoe
   if self.sms:self.tilemap=r[0x1600:0x1c00];self.variant=r[0xe1]+1 if r[0xdf]==1 else 0
   else:
    self.tilemap=bytes(r[(self.sy['sms_vram']+0x3800+i)^1] for i in range(1536))
    word=lambda n:int.from_bytes(bytes(r[(self.sy[n]+i)^1] for i in range(2)),'big')
    self.variant=word('hero_weapon_level')+1 if word('hero_selected_item')==1 else 0
 def prepare_navigation(self):
  if self.tilemap not in self.graphs:
   reverse={(x,y):[] for y in range(8,169,8) for x in range(8,249,8)}
   for point in reverse:
    cache=collision_cache(self.tilemap,Hero(x=point[0]<<8,y=point[1]<<8),canoe=self.canoe)
    for direction,(dx,dy) in enumerate([(0,-8),(0,8),(-8,0),(8,0)]):
     nxt=point[0]+dx,point[1]+dy
     if nxt in reverse and choose_collision_direction(direction,cache)==direction:reverse[nxt].append(point)
   self.graphs[self.tilemap]=reverse
  reverse=self.graphs[self.tilemap]
  goals=[p for p in reverse if any(directions(p,e,self.variant) for e in self.current['foes'])]
  distance={p:0 for p in goals};queue=collections.deque(goals)
  while queue:
   point=queue.popleft()
   for previous in reverse[point]:
    if previous not in distance:distance[previous]=distance[point]+1;queue.append(previous)
  self.navdist=distance
 def score(self,r):
  score=super().score(r);v=self.fields(r)
  if v['health'] and v['game']==12 and v['foes'] and v['room']==self.current['room']:
   nearest=min(v['foes'],key=lambda e:abs(e['x']-v['x'])+abs(e['y']-v['y']))
   distance=abs(nearest['x']-v['x'])+abs(nearest['y']-v['y'])
   if self.navdist:
    score+=abs(distance-24)*0.2
    point=min(248,max(8,round(v['x']/8)*8)),min(168,max(8,round(v['y']/8)*8))
    score-=self.navdist.get(point,200)*2
   dx=nearest['x']-v['x'];dy=nearest['y']-v['y'];direction=(3 if dx>=0 else 2) if abs(dx)>abs(dy) else (1 if dy>=0 else 0)
   if v['direction']==direction:score+=1
  return score
 def choose(self,f,fallback):
  if f>=self.until and self.active:self.prepare_navigation()
  return super().choose(f,fallback)


def main():
 remaining=list(sys.argv[1:]);beam.BeamPlanner=NavigationPlanner;beam.main()
 trial=remaining[remaining.index('--trial')+1];tag='sms' if '--sms' in remaining else 'md';region='pal' if '--pal' in remaining else 'auto'
 path=ROOT/f'validation/natural-dungeon-combat/{tag}-{region}-{trial}/report.json';r=json.loads(path.read_bytes())
 r.update(planning_method='64-frame beam,width3,source collision distance field and facing tie-break',navigation_driver_sha256=beam.generic.base.sha(Path(__file__).read_bytes()),navigation_source_rom_sha256=beam.generic.base.sha((ROOT/'input/original.sms').read_bytes()))
 path.write_bytes((json.dumps(r,indent=2)+'\n').encode())


if __name__=='__main__':main()
