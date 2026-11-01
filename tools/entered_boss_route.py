"""Finish an ordinary boss doorway entry before expensive lookahead begins."""
import argparse,json,sys
from pathlib import Path
import assisted_boss_coarse_route as coarse
import natural_boss_evasive_planner as evasive
from run_core import ROOT
from archive_lossless_evidence import sha


def main():
    p=argparse.ArgumentParser(add_help=False);p.add_argument('--entry-boss-kind',type=lambda x:int(x,0),required=True);a,remaining=p.parse_known_args()
    assert 0x63<=a.entry_boss_kind<=0x6d
    original=evasive.EvasivePlanner;instances=[];driver=Path(__file__).read_bytes()
    class Entered(original):
        def __init__(self,*args,**kwargs):
            super().__init__(*args,**kwargs);self.entry_complete=set();self.entry_actions=[];instances.append(self)
        def observe(self,frame,ram):
            super().observe(frame,ram)
            if self.active and self.current['kind']==a.entry_boss_kind and self.current['y']<=144:
                self.entry_complete.add(self.current['room'])
        def choose(self,frame,fallback):
            if frame>=self.until and self.active and self.current['kind']==a.entry_boss_kind and self.current['room'] not in self.entry_complete:
                self.entry_actions.append(dict(frame=frame,room=self.current['room'],x=self.current['x'],y=self.current['y'],health=self.current['health'],buttons=[4]));return [4]
            return super().choose(frame,fallback)
    evasive.EvasivePlanner=Entered;sys.argv=[sys.argv[0]]+remaining
    try:coarse.main()
    finally:evasive.EvasivePlanner=original
    trial=remaining[remaining.index('--trial')+1];region='pal' if '--pal' in remaining else 'auto';tag='sms' if '--sms' in remaining else 'md';folder=ROOT/f'validation/natural-dungeon-combat/{tag}-{region}-{trial}'
    r=json.loads((folder/'report.json').read_bytes());r.update(entry_controller_sha256=sha(driver),entry_boss_kind=a.entry_boss_kind,entry_inputs=[row for item in instances for row in item.entry_actions],entry_completed_rooms=sorted({room for item in instances for room in item.entry_complete}),entry_resource_or_actor_writes=0)
    (folder/'report.json').write_bytes((json.dumps(r,indent=2)+'\n').encode());(folder/'entry_controller.py').write_bytes(driver)

if __name__=='__main__':main()
