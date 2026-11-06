"""Complete bottom-door arrivals before predictive combat, also after reentry."""
import json,sys
from pathlib import Path
import natural_boss_evasive_planner as evasive
import unassisted_fast_prediction as fast
from archive_lossless_evidence import sha
from run_core import ROOT

def main():
    assert '--entry-boss-kind' in sys.argv
    kind=int(sys.argv[sys.argv.index('--entry-boss-kind')+1],0)
    base=evasive.EvasivePlanner
    class ArrivalPlanner(base):
        def choose(self,frame,fallback):
            if frame>=self.until and self.active and self.current['kind']==kind and (self.current['hero']==0 or self.current['y']>144):return [4]
            return super().choose(frame,fallback)
    evasive.EvasivePlanner=ArrivalPlanner
    try:fast.main()
    finally:evasive.EvasivePlanner=base
    trial=sys.argv[sys.argv.index('--trial')+1];region='pal' if '--pal' in sys.argv else 'auto'
    p=ROOT/f'validation/natural-dungeon-combat/md-{region}-{trial}/report.json';r=json.loads(p.read_bytes())
    r.update(arrival_checked_on_every_entry=True,arrival_controller_sha256=sha(Path(__file__).read_bytes()))
    p.write_text(json.dumps(r,indent=2)+'\n')
if __name__=='__main__':main()
