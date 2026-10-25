"""Ordinary-input boss search that values avoiding a damaging trade.

This changes only the controller's secondary-core search, never the game.
"""
import json
import sys
from pathlib import Path
import natural_combat_navigation as nav
from run_core import ROOT

class CautiousPlanner(nav.NavigationPlanner):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.horizon=96
        self.width=4
    def score(self,ram):
        score=super().score(ram)
        value=self.fields(ram)
        if value['room']==self.current['room'] and value['health'] and value['foes']:
            score+=value['health']*80
        return score

def main():
    remaining=list(sys.argv[1:]);nav.beam.BeamPlanner=CautiousPlanner;nav.beam.main()
    trial=remaining[remaining.index('--trial')+1];tag='sms' if '--sms' in remaining else 'md';region='pal' if '--pal' in remaining else 'auto'
    path=ROOT/f'validation/natural-dungeon-combat/{tag}-{region}-{trial}/report.json';report=json.loads(path.read_bytes())
    report.update(planning_method='96-frame beam,width4,source collision navigation,90 points per hero HP while enemies remain',cautious_driver_sha256=nav.beam.generic.base.sha(Path(__file__).read_bytes()))
    path.write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
