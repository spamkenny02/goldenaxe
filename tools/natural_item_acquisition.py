"""Finish an actual item reward without claiming persistent hazards disappeared.

Only ordinary input is delegated to the existing controller. Ownership, reward
completion and surviving hazard records are observed, never injected or removed.
"""
import argparse
import json
import sys
from pathlib import Path

import natural_dungeon_combat as game
from run_core import ROOT
from archive_lossless_evidence import sha
from validate_playable_sprite_limit import symbols


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--collect-item', type=int, required=True)
    parser.add_argument('--collect-item-value',type=int,choices=range(1,256),default=1)
    args, remaining = parser.parse_known_args()
    finish_item=0 if '--equip-basic' in remaining else 1
    assert 0 <= args.collect_item < 17
    sms = '--sms' in remaining
    flag = '--continuation' if '--continuation' in remaining else '--prefix'
    family = 'natural-dungeon-combat' if flag == '--continuation' else 'natural-dungeon-route'
    name = remaining[remaining.index(flag)+1]
    prefix = json.loads((ROOT/'validation'/family/name/'capture.json').read_bytes())
    start = prefix['frames']
    sy = None if sms else symbols(ROOT/'megadrive/out/release/symbol.txt')
    driver = Path(__file__).read_bytes()
    original = game.run
    state = {}
    result = {}
    first = None
    acquired = None
    complete = None

    def wrapped(*run_args, **kwargs):
        result['folder'] = Path(run_args[2])
        observer = kwargs['ram_observer']
        stop = kwargs.get('stop_when')
        last = [0]

        def observe(frame, ram):
            nonlocal first, acquired, complete
            observer(frame, ram)
            last[0] = frame
            if frame < start:
                return
            if sms:
                actors=ram[0x600:0x900]
                state.update(room=int.from_bytes(ram[0xb9:0xbb],'little'),game=ram[0x1d],hero=ram[0x301],
                             health=ram[0x318],selected=ram[0xdf],reward_active=None,owned=ram[0xe0+args.collect_item])
            else:
                data = lambda n, k: bytes(ram[(sy[n]+i)^1] for i in range(k))
                word = lambda n: int.from_bytes(data(n, 2), 'big')
                actors = data('world_actor_state', 768)
                state.update(room=word('room_id'), game=word('game_state'), hero=word('hero_state'),
                         health=word('hero_health'), selected=word('hero_selected_item'),
                         reward_active=word('item_reward_active'),
                         owned=data('hero_items', 17)[args.collect_item])
            state['zero_hp_actors']=[dict(slot=i,type=actors[i*48],flags=actors[i*48+3])
                                    for i in range(8) if actors[i*48] and not actors[i*48+24]]
            if first is None:
                first = dict(frame=frame, **state)
                assert state['owned']<args.collect_item_value, 'Require a real acquisition or upgrade after the prefix'
            if state['owned']>=args.collect_item_value and acquired is None:
                acquired = frame
                run_args[3].add(frame+1)
            if (acquired is not None and frame-acquired >= 300 and state['owned']>=args.collect_item_value and state['health']
                    and state['game'] == 12 and state['hero'] == 1 and state['selected'] == finish_item
                    and not state['reward_active'] and complete is None):
                complete = frame
                run_args[3].update([frame+1, frame+100])

        kwargs.update(ram_observer=observe,
                      stop_when=lambda: bool(stop and stop()) or complete is not None and last[0] >= complete+100)
        return original(*run_args, **kwargs)

    game.run = wrapped
    sys.argv = [sys.argv[0]] + remaining + ['--collect-item', str(args.collect_item), '--collect-item-value',str(args.collect_item_value), '--continue-after-clear']
    try:
        game.main()
    finally:
        game.run = original
    folder = result['folder']
    report = json.loads((folder/'report.json').read_bytes())
    if complete is not None:
        report.update(passed=True, failure=None, stop_reason='actual_item_reward_finished')
    report.update(item_target_value=args.collect_item_value,item_finish_selected=finish_item,item_acquisition_passed=complete is not None, item_acquired_frame=acquired,
                  item_reward_finished_frame=complete, item_acquisition_first=first,
                  item_acquisition_last=dict(state), item_acquisition_driver_sha256=sha(driver),
                  item_acquisition_state_writes=0, item_acquisition_room_clear_required=False)
    if sms:report['sms_item_scope']='Observed ownership, elapsed acknowledgment input and hero state. A subsequent movement stage is required to confirm the source modal returned; no native reward_active flag exists in this observer.'
    (folder/'item_acquisition_driver.py').write_bytes(driver)
    (folder/'report.json').write_bytes((json.dumps(report, indent=2)+'\n').encode())
    print('Actual item reward finished:', complete is not None)


if __name__ == '__main__':
    main()
