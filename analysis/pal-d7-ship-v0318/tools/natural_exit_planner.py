"""Search ordinary evasive input toward real dungeon doors and contact portals."""
import argparse,collections,json,sys
from pathlib import Path
import natural_boss_escape_planner as escape
from run_core import ROOT
WAYPOINTS={}

class ExitPlanner(escape.EscapePlanner):
    def choose(self, frame, fallback):
        current=getattr(self,'current',None)
        goal=WAYPOINTS.get(current['room']) if current else None
        # A portal arrival can place the hero on another portal's contact
        # coordinate. Source flags30 require leaving and re-entering it.
        if frame>=self.until and self.active and self.state is not None and goal and goal['moving_contact'] and (self.current['x'],self.current['y'])==goal['point']:
            self.secondary.restore(self.state)
            self.schedule=[(5,)]*self.step
            for buttons in self.schedule:self.secondary.advance(buttons,1)
            self.expected_ram=self.secondary.ram();self.expected=escape.side.nav.beam.generic.base.sha(self.expected_ram)
            self.start=frame;self.until=frame+self.step;self.verify_at=self.until-1
            self.decisions.append(dict(frame=frame,action='leave-portal-contact-down',buttons=self.schedule,score=self.score(self.expected_ram),primary=dict(self.current)))
            return list(self.schedule[0])
        return super().choose(frame,fallback)
    def prepare_navigation(self):
        super().prepare_navigation()
        if self.current['room'] not in WAYPOINTS:return
        goal=WAYPOINTS[self.current['room']]['point'];reverse=self.graphs[self.tilemap]
        distance={goal:0};queue=collections.deque([goal])
        while queue:
            point=queue.popleft()
            for previous in reverse.get(point,[]):
                if previous not in distance:distance[previous]=distance[point]+1;queue.append(previous)
        self.navdist=distance
    def score(self,ram):
        v=self.fields(ram)
        if not v['health'] or v['game']==20:return -1000000
        goal=WAYPOINTS.get(self.current['room'])
        if not goal:return super().score(ram)
        if v['room']==goal['next_room']:return 20000+v['health']*90
        if v['room']!=self.current['room']:return -100000
        if v['game']!=12:return -100000
        point=min(248,max(8,round(v['x']/8)*8)),min(168,max(8,round(v['y']/8)*8))
        distance=self.navdist.get(point,200)
        fine=abs(v['x']-goal['point'][0])+abs(v['y']-goal['point'][1])
        return v['health']*90-distance*12-fine*0.05

def main():
    global WAYPOINTS
    p=argparse.ArgumentParser(add_help=False);p.add_argument('--rooms',required=True);p.add_argument('--target-room',type=lambda v:int(v,0),required=True);p.add_argument('--exit-dungeon',action='store_true');a,_=p.parse_known_args()
    assert a.exit_dungeon
    rooms=[int(v,0) for v in a.rooms.split(',')];reference=json.loads((ROOT/'analysis/contact_script_reference.json').read_bytes())
    assert reference['source_sha256']==escape.side.nav.beam.generic.base.sha((ROOT/'input/original.sms').read_bytes())
    portals={(r['room'],r['destination_room']):r for r in reference['records'] if r['kind']=='moving_aligned_portal'}
    for n,room in enumerate(rooms):
        if n==len(rooms)-1:point=(128,168);next_room=a.target_room
        else:
            next_room=rooms[n+1]
            if (room,next_room) in portals:
                coordinate=portals[room,next_room]['coordinate']
                point=next((x,y) for y in range(8,169,8) for x in range(8,249,8) if (((y-12)&248)<<3)+(((x-12)&255)>>2&62)+126==coordinate)
            else:
                direction={-16:0,16:1,-1:2,1:3}[next_room-room]
                point=[(128,8),(128,168),(8,88),(248,88)][direction]
        assert room not in WAYPOINTS,'Use a non-repeating exit itinerary'
        WAYPOINTS[room]=dict(point=point,next_room=next_room,moving_contact=(room,next_room) in portals)
    remaining=list(sys.argv[1:]);escape.side.SidePlanner=ExitPlanner;escape.side.main()
    trial=remaining[remaining.index('--trial')+1];region='pal' if '--pal' in remaining else 'auto';path=ROOT/f'validation/natural-dungeon-combat/md-{region}-{trial}/report.json';report=json.loads(path.read_bytes())
    report.update(planning_method='96-frame beam with eleven retained evasion paths,ROM doorway/portal distance and ordinary room-change reward',exit_waypoints=WAYPOINTS,exit_driver_sha256=escape.side.nav.beam.generic.base.sha(Path(__file__).read_bytes()))
    path.write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
