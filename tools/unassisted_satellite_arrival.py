"""Finish the physical arrival before predictive sidesteps, including reentries."""
import json,sys
from pathlib import Path
import natural_boss_evasive_planner as evasive
import natural_combat_beam as beam
import unassisted_satellite_boss as satellites
from prediction_video_skip import enable_prediction_video_skip
from archive_lossless_evidence import sha
from run_core import ROOT

def main():
    base=evasive.EvasivePlanner;ctor=beam.BeamSecondary.__init__
    class ArrivalPlanner(base):
        def choose(self,frame,fallback):
            if frame>=self.until and self.active and self.current['kind']==0x65 and (self.current['hero']==0 or self.current['y']>144):
                return [4]
            return super().choose(frame,fallback)
    def initialize(secondary,*args,**kwargs):
        ctor(secondary,*args,**kwargs);enable_prediction_video_skip(secondary)
    evasive.EvasivePlanner=ArrivalPlanner;beam.BeamSecondary.__init__=initialize
    try:satellites.main()
    finally:evasive.EvasivePlanner=base;beam.BeamSecondary.__init__=ctor
    trial=sys.argv[sys.argv.index('--trial')+1];region='pal' if '--pal' in sys.argv else 'auto'
    p=ROOT/f'validation/natural-dungeon-combat/md-{region}-{trial}/report.json';r=json.loads(p.read_bytes())
    assert r['full_ram_prediction_matches']==r['verified_persistent_prediction_windows']>0 and not r['stack_only_difference_windows']
    assert not r['primary_state_imports'] and not r['new_assistance_writes']
    r.update(arrival_checked_on_every_entry=True,arrival_controller_sha256=sha(Path(__file__).read_bytes()),secondary_video_suppressed=True,primary_video_suppressed=False,secondary_audio_enabled=True,prediction_video_adapter_sha256=sha((ROOT/'tools/prediction_video_skip.py').read_bytes()))
    p.write_text(json.dumps(r,indent=2)+'\n')
if __name__=='__main__':main()
