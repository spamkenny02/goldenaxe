"""Ordinary-input boss search with longer verified input windows.

Only the disposable secondary core restores snapshots. The primary game and
the independent cold replay retain the existing whole-RAM equivalence gates.
No distributed ROM code or game-state fixtures are changed by this controller.
"""
import argparse
import json
import sys
from pathlib import Path
import assisted_boss_route
import natural_boss_evasive_planner as evasive
from run_core import ROOT
from archive_lossless_evidence import sha


def main():
    parser=argparse.ArgumentParser(add_help=False)
    parser.add_argument('--planning-step',type=int,choices=[8,16,24,32],default=16)
    parser.add_argument('--moving-health-premium',type=int,choices=range(81),default=40)
    args,remaining=parser.parse_known_args()
    assert '--planner' in remaining and remaining[remaining.index('--planner')+1]=='evasive'
    original=evasive.EvasivePlanner
    class CoarsePlanner(original):
        def __init__(self,*values,**options):
            super().__init__(*values,**options)
            assert self.horizon==96 and self.horizon%args.planning_step==0
            self.step=args.planning_step
        def score(self,ram):
            score=super().score(ram)
            value=self.fields(ram)
            if value['room']==self.current['room'] and value['health'] and value['foes'] and value['kind'] not in (0x63,0x64):
                score-=(80-args.moving_health_premium)*value['health']
            return score
    evasive.EvasivePlanner=CoarsePlanner
    sys.argv=[sys.argv[0]]+remaining
    assisted_boss_route.main()
    trial=remaining[remaining.index('--trial')+1]
    region='pal' if '--pal' in remaining else 'auto'
    tag='sms' if '--sms' in remaining else 'md'
    path=ROOT/f'validation/natural-dungeon-combat/{tag}-{region}-{trial}/report.json'
    report=json.loads(path.read_bytes())
    report.update(planning_method=f'96-frame beam,width3,eleven retained paths,{args.planning_step}-frame whole-RAM-verified windows',
                  planning_step=args.planning_step,moving_health_premium=args.moving_health_premium,
                  coarse_driver_sha256=sha(Path(__file__).read_bytes()))
    path.write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'))


if __name__=='__main__':main()
