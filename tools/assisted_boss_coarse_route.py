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
    parser.add_argument('--enter-boss-up',action='store_true',help='Use ordinary UP to finish entering boss65 before starting search')
    parser.add_argument('--target-satellites',action='store_true',help='Include attackable type66 orbiters in boss65 input-search targets')
    args,remaining=parser.parse_known_args()
    assert '--planner' in remaining and remaining[remaining.index('--planner')+1]=='evasive'
    original=evasive.EvasivePlanner
    instances=[]
    class CoarsePlanner(original):
        def __init__(self,*values,**options):
            super().__init__(*values,**options)
            assert self.horizon==96 and self.horizon%args.planning_step==0
            self.step=args.planning_step
            self.entry_ready=set();self.entry_inputs=[];instances.append(self)
        def observe(self,frame,ram):
            super().observe(frame,ram)
            if self.active and self.current['kind']==0x65 and self.current['y']<=144:
                self.entry_ready.add(self.current['room'])
        def choose(self,frame,fallback):
            if (args.enter_boss_up and frame>=self.until and self.active and
                self.current['kind']==0x65 and self.current['room'] not in self.entry_ready):
                self.entry_inputs.append(dict(frame=frame,room=self.current['room'],
                                              x=self.current['x'],y=self.current['y'],
                                              health=self.current['health'],buttons=[4]))
                return [4]
            return super().choose(frame,fallback)
        def fields(self,ram):
            value=super().fields(ram)
            if args.target_satellites and value['kind']==0x65:
                if self.sms:actors=ram[0x600:0x900]
                else:actors=bytes(ram[(self.sy['world_actor_state']+i)^1] for i in range(768))
                for slot in range(8,16):
                    actor=actors[slot*48:(slot+1)*48]
                    if actor[0]==0x66 and actor[24]:
                        value['foes'].append(dict(slot=slot,kind=0x66,hp=actor[24],x=actor[19],y=actor[17],
                                                 hit_box=actor[27],contact_box=actor[28]))
            return value
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
                  target_satellites=args.target_satellites,
                  ordinary_entry_up_requested=args.enter_boss_up,
                  ordinary_entry_inputs=[row for instance in instances for row in instance.entry_inputs],
                  coarse_driver_sha256=sha(Path(__file__).read_bytes()))
    path.write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'))


if __name__=='__main__':main()
