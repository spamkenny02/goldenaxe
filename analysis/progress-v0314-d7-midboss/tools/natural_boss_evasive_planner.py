"""Retain full evasion paths for moving bosses, with ordinary combat damage."""
import json,sys
from pathlib import Path
import natural_boss_escape_planner as escape
from run_core import ROOT

class EvasivePlanner(escape.EscapePlanner):
    def score(self,ram):
        score=super().score(ram);value=self.fields(ram)
        if value['room']==self.current['room'] and value['health'] and value['foes'] and value['kind'] not in (0x63,0x64):
            score+=value['health']*80
        return score

def main():
    remaining=list(sys.argv[1:]);escape.side.SidePlanner=EvasivePlanner;escape.side.main()
    trial=remaining[remaining.index('--trial')+1];region='pal' if '--pal' in remaining else 'auto'
    tag='sms' if '--sms' in remaining else 'md'
    path=ROOT/f'validation/natural-dungeon-combat/{tag}-{region}-{trial}/report.json';report=json.loads(path.read_bytes())
    report.update(planning_method='96-frame beam,width3,eleven retained evasion paths,90 points per hero HP against moving bosses',evasive_driver_sha256=escape.side.nav.beam.generic.base.sha(Path(__file__).read_bytes()))
    path.write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
