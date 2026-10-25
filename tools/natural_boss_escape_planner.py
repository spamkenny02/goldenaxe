"""Keep complete evasion candidates alongside the locally pruned beam."""
import json
import sys
from pathlib import Path
import natural_boss_side_planner as side
from run_core import ROOT


class EscapePlanner(side.SidePlanner):
    def choose(self, frame, fallback):
        searching = frame >= self.until and self.active and self.state is not None
        buttons = super().choose(frame, fallback)
        if not searching:
            return buttons
        best = self.decisions[-1]
        candidates = [(f'escape-hold-{direction}', [(direction,)] * self.horizon)
                      for direction in (4, 5, 6, 7)]
        candidates += [('stationary-right-pulse', [(7, 8) if tick % 3 == 1 else ()
                                                   for tick in range(self.horizon)])]
        for direction in (4, 5):
            for delay in (8, 24, 40):
                candidates.append((f'left-{delay}-then-{direction}',
                                   [(6,) if tick < delay else (direction,)
                                    for tick in range(self.horizon)]))
        for name, schedule in candidates:
            self.secondary.restore(self.state)
            first_ram = None
            for tick, action in enumerate(schedule):
                self.secondary.advance(action, 1)
                if tick == self.step - 1:
                    first_ram = self.secondary.ram()
            score = self.score(self.secondary.ram())
            if score <= best['score']:
                continue
            self.schedule = schedule[:self.step]
            self.expected_ram = first_ram
            self.expected = side.nav.beam.generic.base.sha(first_ram)
            best.update(action=name, path=[name], buttons=self.schedule, score=score,
                        preserved_evasion_candidate=True)
        if self.diagnostics and len(self.decisions) % 8 == 0:
            (self.diagnostics / 'planning_live.json').write_text(json.dumps(dict(
                verified_windows=self.verified, primary_state_imports=0, decisions=self.decisions), indent=2) + '\n')
        return list(self.schedule[0])


def main():
    remaining = list(sys.argv[1:])
    side.SidePlanner = EscapePlanner
    side.main()
    trial = remaining[remaining.index('--trial') + 1]
    region = 'pal' if '--pal' in remaining else 'auto'
    path = ROOT / f'validation/natural-dungeon-combat/md-{region}-{trial}/report.json'
    report = json.loads(path.read_bytes())
    report.update(planning_method='96-frame side beam plus eleven independently retained evasion/attack paths',
                  escape_driver_sha256=side.nav.beam.generic.base.sha(Path(__file__).read_bytes()))
    path.write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
