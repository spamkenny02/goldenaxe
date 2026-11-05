"""Include boss65's attackable satellites in controller-only input search.

The ordinary unassisted continuation enforces the same early guard release,
unchanged RAM-write list and independent cold replay requirement. Only the
secondary planner's target list changes; neither cartridge nor game rules do.
"""
import json
import sys
from pathlib import Path

from archive_lossless_evidence import sha
from run_core import ROOT
import natural_boss_evasive_planner as evasive
import unassisted_dungeon_continuation as continuation


def main():
    arguments = list(sys.argv[1:])
    assert '--planner' in arguments and arguments[arguments.index('--planner') + 1] == 'evasive'
    base = evasive.EvasivePlanner

    class SatellitePlanner(base):
        def fields(self, ram):
            value = super().fields(ram)
            if value['kind'] != 0x65:
                return value
            if self.sms:
                actors = ram[0x600:0x900]
            else:
                actors = bytes(ram[(self.sy['world_actor_state'] + i) ^ 1] for i in range(768))
            for slot in range(8, 16):
                actor = actors[slot * 48:(slot + 1) * 48]
                if actor[0] == 0x66 and actor[24]:
                    value['foes'].append(dict(slot=slot, kind=0x66, hp=actor[24],
                                             x=actor[19], y=actor[17],
                                             hit_box=actor[27], contact_box=actor[28]))
            value['satellite_targets'] = sum(foe['kind'] == 0x66 for foe in value['foes'])
            return value

    evasive.EvasivePlanner = SatellitePlanner
    continuation.main()
    trial = arguments[arguments.index('--trial') + 1]
    region = 'pal' if '--pal' in arguments else 'auto'
    path = ROOT / f'validation/natural-dungeon-combat/md-{region}-{trial}/report.json'
    report = json.loads(path.read_bytes())
    assert report['unassisted_extension'] and report['new_assistance_writes'] == 0
    assert report['primary_state_imports'] == 0
    report.update(satellites_in_input_search=True, satellite_controller_sha256=sha(Path(__file__).read_bytes()))
    path.write_bytes((json.dumps(report, indent=2) + '\n').encode())


if __name__ == '__main__':
    main()
