"""Controller-only search of safe left-side axe stances for bosses63/64."""
import collections
import json
import sys
from pathlib import Path
import natural_combat_navigation as nav
from natural_combat_aim import directions
from run_core import ROOT


class SidePlanner(nav.NavigationPlanner):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.horizon = 96

    def prepare_navigation(self):
        super().prepare_navigation()
        if self.current['kind'] not in (0x63, 0x64):
            return
        reverse = self.graphs[self.tilemap]
        goals = [point for point in reverse if point[0] in (104, 112) and
                 any(3 in directions(point, enemy, self.variant) for enemy in self.current['foes'])]
        distance = {point: 0 for point in goals}
        queue = collections.deque(goals)
        while queue:
            point = queue.popleft()
            for previous in reverse[point]:
                if previous not in distance:
                    distance[previous] = distance[point] + 1
                    queue.append(previous)
        self.navdist = distance

    def score(self, ram):
        score = super().score(ram)
        value = self.fields(ram)
        if value['room'] == self.current['room'] and value['health'] and value['kind'] in (0x63, 0x64):
            score += value['health'] * 90
            score -= max(0, value['x'] - 112) * 4
            if value['direction'] == 3:
                score += 1
        return score


def main():
    remaining = list(sys.argv[1:])
    nav.beam.BeamPlanner = SidePlanner
    nav.beam.main()
    trial = remaining[remaining.index('--trial') + 1]
    region = 'pal' if '--pal' in remaining else 'auto'
    path = ROOT / f'validation/natural-dungeon-combat/md-{region}-{trial}/report.json'
    report = json.loads(path.read_bytes())
    report.update(planning_method='96-frame beam,width3,left-side source axe stances,health preservation',
                  side_driver_sha256=nav.beam.generic.base.sha(Path(__file__).read_bytes()))
    path.write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
