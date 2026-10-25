"""Experimental controller search in a second core, never state imports in game.

Must pass the inherited persistent-RAM prediction checks and a separate cold
fixed-input replay before a successful route can be treated as evidence.
"""
import argparse,ctypes as c,json
from pathlib import Path
import natural_boss_lookahead as base
from run_core import ROOT

ROOMS=set()
ACTIVATE_AFTER=0


class PhaseSecondary(base.Secondary):
 def restore(self,state):
  snapshot,refresh=state
  super().restore(snapshot)
  self.dll.gaw_refresh_set.argtypes=[c.c_int];self.dll.gaw_refresh_set(refresh)


class CombatPlanner(base.Planner):
 def __init__(self,*args,**kwargs):
  super().__init__(*args,**kwargs,horizon=64)
 def fields(self,r):
  v=super().fields(r)
  if self.sms:
   raw=r[0x600:0x780];v['room_flags']=r[0x100+(v['room']&255)]
  else:
   raw=bytes(r[(self.sy['world_actor_state']+i)^1] for i in range(384))
   v['room_flags']=r[(self.sy['game_save_state']+0x50+(v['room']&255))^1]
  v['foes']=[dict(slot=i,kind=raw[i*48],hp=raw[i*48+24],x=raw[i*48+19],y=raw[i*48+17]) for i in range(8) if raw[i*48]>=0x20 and raw[i*48+24]]
  return v
 def observe(self,f,r):
  super().observe(f,r)
  v=self.current
  self.active=f>=ACTIVATE_AFTER and v['room'] in ROOMS and v['game']==12 and v['health']>0 and bool(v['foes']) and (v['room']!=0x151 or v['room_flags']&4)
  if self.active:
   assert self.primary.retro_serialize(self.buffer,len(self.buffer))
   self.primary.gaw_refresh_get.restype=c.c_int;self.state=(self.buffer.raw,self.primary.gaw_refresh_get())
 def score(self,r):
  v=self.fields(r)
  if not v['health']:return -1000000
  if v['room']!=self.current['room']:return -100000
  if v['game']!=12:return -100000
  if not v['foes']:return 20000+v['health']*10
  distance=min(abs(v['x']-e['x'])+abs(v['y']-e['y']) for e in v['foes'])
  return v['health']*10-len(v['foes'])*250-sum(e['hp'] for e in v['foes'])*70-abs(distance-24)*0.2
 def choose(self,f,fallback):
  if f<self.until:return list(self.schedule[f-self.start])
  if not self.active or self.state is None:return fallback
  assert self.frame==f-1
  actions=[(),(4,),(5,),(6,),(7,),(4,8),(5,8),(6,8),(7,8),(8,)]
  candidates=[('hold-'+str(a),[a]*self.horizon) for a in actions]
  for direction in [4,5,6,7]:
   for period in [3,12]:candidates.append((f'pulse-{direction}-{period}',[(direction,8) if n%period==1 else () for n in range(self.horizon)]))
   candidates.append((f'fresh-{direction}',[()]+[(direction,8)]*(self.horizon-1)))
  choices=[]
  for name,schedule in candidates:
   self.secondary.restore(self.state);first_ram=None
   for n,buttons in enumerate(schedule):
    self.secondary.advance(buttons,1)
    if n==self.step-1:first_ram=self.secondary.ram()
   choices.append(dict(name=name,schedule=schedule[:self.step],first_ram=first_ram,score=self.score(self.secondary.ram())))
  best=max(choices,key=lambda v:v['score']);self.schedule=best['schedule'];self.start=f;self.until=f+self.step
  self.expected_ram=best['first_ram'];self.expected=base.sha(self.expected_ram);self.verify_at=f+self.step-1
  self.decisions.append(dict(frame=f,action=best['name'],buttons=self.schedule,score=best['score'],primary=dict(self.current)))
  return list(self.schedule[0])


def main():
 global ROOMS,ACTIVATE_AFTER
 import sys
 p=argparse.ArgumentParser(add_help=False);p.add_argument('--lookahead-rooms',default='0x151,0x152');args,remaining=p.parse_known_args()
 ROOMS={int(n,0) for n in args.lookahead_rooms.split(',')};sys.argv=[sys.argv[0]]+remaining
 flag='--continuation' if '--continuation' in remaining else '--prefix';assert flag in remaining,'Explicit recorded prefix required'
 name=remaining[remaining.index(flag)+1];family='natural-dungeon-combat' if flag=='--continuation' else 'natural-dungeon-route'
 ACTIVATE_AFTER=json.loads((ROOT/'validation'/family/name/'capture.json').read_bytes())['frames']
 base.Planner=CombatPlanner;base.Secondary=PhaseSecondary
 base.main(ROOT.parents[1]/'work/genesis-plus-gx/genesis_plus_gx_planning_libretro.dll')
 trial=remaining[remaining.index('--trial')+1];tag='sms' if '--sms' in remaining else 'md';region='pal' if '--pal' in remaining else 'auto'
 report=ROOT/f'validation/natural-dungeon-combat/{tag}-{region}-{trial}/report.json';r=json.loads(report.read_bytes())
 r.update(planning_method='64-frame held/fresh/pulsed attacks and directions',planning_wrapper_sha256=base.sha(Path(__file__).read_bytes()),planning_rooms=sorted(ROOMS),activation_after_frame=ACTIVATE_AFTER,secondary_refresh_phase_restored=True,primary_extra_state_writes=0)
 report.write_bytes((json.dumps(r,indent=2)+'\n').encode())


if __name__=='__main__':main()
