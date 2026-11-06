"""Try short positioning followed by a stationary swing in secondary forecasts."""
import json,sys
from pathlib import Path
import natural_boss_evasive_planner as evasive
import unassisted_arrival_prediction as arrival
from archive_lossless_evidence import sha
from run_core import ROOT

def main():
    base=evasive.EvasivePlanner
    class StancePlanner(base):
        def choose(self,frame,fallback):
            searching=frame>=self.until and self.active and self.state is not None and self.current['kind'] in (0x63,0x64)
            buttons=super().choose(frame,fallback)
            if not searching:return buttons
            best=self.decisions[-1]
            for direction in (4,5,6,7):
                for delay in (4,8,12,16):
                    schedule=[(direction,) if tick<delay else (7,8) if tick%3==1 else () for tick in range(self.horizon)]
                    self.secondary.restore(self.state);first_ram=None
                    for tick,action in enumerate(schedule):
                        self.secondary.advance(action,1)
                        if tick==self.step-1:first_ram=self.secondary.ram()
                    score=self.score(self.secondary.ram())
                    if score<=best['score']:continue
                    assert first_ram is not None
                    self.schedule=schedule[:self.step];self.expected_ram=first_ram;self.expected=sha(first_ram)
                    best.update(action=f'stance-{direction}-{delay}-then-right-pulse',path=[f'stance-{direction}-{delay}'],buttons=self.schedule,score=score,short_stance_candidate=True)
            if self.diagnostics and len(self.decisions)%8==0:
                (self.diagnostics/'planning_live.json').write_text(json.dumps(dict(verified_windows=self.verified,primary_state_imports=0,decisions=self.decisions),indent=2)+'\n')
            return list(self.schedule[0])
    evasive.EvasivePlanner=StancePlanner
    try:arrival.main()
    finally:evasive.EvasivePlanner=base
    trial=sys.argv[sys.argv.index('--trial')+1];region='pal' if '--pal' in sys.argv else 'auto'
    p=ROOT/f'validation/natural-dungeon-combat/md-{region}-{trial}/report.json';r=json.loads(p.read_bytes())
    assert r['full_ram_prediction_matches']==r['verified_persistent_prediction_windows']>0 and not r['stack_only_difference_windows']
    assert not r['primary_state_imports'] and not r['new_assistance_writes']
    r.update(short_stance_candidates=True,stance_controller_sha256=sha(Path(__file__).read_bytes()))
    p.write_text(json.dumps(r,indent=2)+'\n')
if __name__=='__main__':main()
