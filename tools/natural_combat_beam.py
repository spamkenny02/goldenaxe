"""Experimental multi-step controller search; all game inputs remain ordinary.

Only the disposable secondary core loads snapshots. The primary game's cold
official-core replay must reproduce RAM and image before claiming progress.
"""
import ctypes as c,json,sys
from pathlib import Path
import natural_combat_lookahead as generic
from run_core import ROOT


class BeamSecondary(generic.PhaseSecondary):
 def snapshot(self):
  raw=super().snapshot();self.dll.gaw_refresh_get.restype=c.c_int
  return raw,self.dll.gaw_refresh_get()


class BeamPlanner(generic.CombatPlanner):
 width=3
 def fields(self,r):
  v=super().fields(r)
  if self.sms:
   v.update(hero=r[0x301],direction=r[0x302],counter=r[0x304],hurt=r[0x305],projectiles=generic.base.sha(r[0x780:0x900]))
  else:
   word=lambda n:int.from_bytes(bytes(r[(self.sy[n]+i)^1] for i in range(2)),'big')
   v.update(hero=word('hero_state'),direction=word('hero_direction'),counter=word('hero_counter'),hurt=word('hero_hurt'),projectiles=generic.base.sha(bytes(r[(self.sy['world_actor_state']+384+i)^1] for i in range(384))))
  return v
 def choose(self,f,fallback):
  if f<self.until:return list(self.schedule[f-self.start])
  if not self.active or self.state is None:return fallback
  assert self.frame==f-1
  actions=[(),(4,),(5,),(6,),(7,),(4,8),(5,8),(6,8),(7,8),(8,)]
  schedules=[('hold-'+str(a),[a]*self.step) for a in actions]
  schedules += [(f'pulse-{d}',[(d,8) if n%3==1 else () for n in range(self.step)]) for d in [4,5,6,7]]
  beam=[dict(state=self.state,path=[],first_ram=None,score=0)]
  for depth in range(self.horizon//self.step):
   kept=[];keys={}
   for parent in beam:
    for name,buttons in schedules:
     self.secondary.restore(parent['state'])
     for action in buttons:self.secondary.advance(action,1)
     ram=self.secondary.ram();score=self.score(ram);v=self.fields(ram)
     key=(v['room'],v['game'],v['health'],v['x'],v['y'],v['hero'],v['direction'],v['counter'],v['hurt'],v['projectiles'],tuple((e['slot'],e['kind'],e['hp'],e['x'],e['y']) for e in v['foes']))
     if key in keys and keys[key]>=score:continue
     if len(kept)>=self.width and score<min(n['score'] for n in kept):continue
     node=dict(state=self.secondary.snapshot(),path=parent['path']+[(name,buttons)],first_ram=parent['first_ram'] or ram,score=score,key=key)
     kept=[n for n in kept if n['key']!=key];kept.append(node);kept.sort(key=lambda n:n['score'],reverse=True);kept=kept[:self.width];keys={n['key']:n['score'] for n in kept}
   assert kept;beam=kept
  best=max(beam,key=lambda n:n['score']);self.schedule=best['path'][0][1];self.start=f;self.until=f+self.step
  self.expected_ram=best['first_ram'];self.expected=generic.base.sha(self.expected_ram);self.verify_at=f+self.step-1
  self.decisions.append(dict(frame=f,action=best['path'][0][0],path=[n for n,b in best['path']],buttons=self.schedule,score=best['score'],primary=dict(self.current)))
  if self.diagnostics and len(self.decisions)%8==0:
   (self.diagnostics/'planning_live.json').write_bytes((json.dumps(dict(verified_windows=self.verified,primary_state_imports=0,decisions=self.decisions),indent=2)+'\n').encode())
  return list(self.schedule[0])


def main():
 remaining=list(sys.argv[1:]);generic.PhaseSecondary=BeamSecondary;generic.CombatPlanner=BeamPlanner;generic.main()
 trial=remaining[remaining.index('--trial')+1];tag='sms' if '--sms' in remaining else 'md';region='pal' if '--pal' in remaining else 'auto'
 path=ROOT/f'validation/natural-dungeon-combat/{tag}-{region}-{trial}/report.json';r=json.loads(path.read_bytes())
 r.update(planning_method='64-frame beam,8-frame steps,width3,14 held/pulsed input schedules',beam_driver_sha256=generic.base.sha(Path(__file__).read_bytes()))
 path.write_bytes((json.dumps(r,indent=2)+'\n').encode())


if __name__=='__main__':main()
