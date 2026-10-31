"""Real town equipment gift and house exit from a verified cold recording.

Only controller inputs are added. Any approach guard is inherited verbatim.
"""
import argparse
import contextlib
import io
import json
from pathlib import Path

from run_core import ROOT, run, FrameWrites
from natural_dungeon_combat import walk
from validate_playable_sprite_limit import symbols
from archive_lossless_evidence import sha
from assisted_prefix import prefix_writes, recording


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--prefix', required=True)
    p.add_argument('--trial', required=True)
    p.add_argument('--outside', type=lambda s: int(s, 0), required=True)
    p.add_argument('--assisted-prefix', action='store_true')
    a = p.parse_args()
    gifts = {0x27: ('armor', 2), 0x50: ('basic', 2),
             0xb1: ('armor', 3), 0x6a: ('basic', 3)}
    assert a.outside in gifts
    field, level = gifts[a.outside]
    source = ROOT / 'validation/natural-dungeon-route' / a.prefix
    c = json.loads((source / 'capture.json').read_bytes())
    prior = json.loads((source / 'route_report.json').read_bytes())
    assert prior['reached_entrance'] and prior['failure'] is None
    assert prior['house_outside'] == a.outside and prior['house_target'] == 0x4f
    assert c['sram_input'] is None
    writes = prefix_writes(source, c, a.assisted_prefix)
    rom = ROOT / 'gaw-megadrive.bin'
    assert sha(rom.read_bytes()) == c['rom_sha256']
    driver = Path(__file__).read_bytes()
    sy = symbols(ROOT / 'megadrive/out/release/symbol.txt')
    start = c['frames']
    controls = json.loads((source / 'controls.json').read_bytes())
    timeline = [()] * (start + 1)
    for i, row in enumerate(controls):
        end = controls[i + 1]['frame'] - 1 if i + 1 < len(controls) else start
        timeline[row['frame']:end + 1] = [tuple(row['buttons'])] * (end - row['frame'] + 1)
    folder = ROOT / 'validation/natural-service-route' / ('md-' + a.trial)
    assert not folder.exists()
    state = {}
    events = []
    captures = {start}
    first = done = failure = previous = None
    observed = 0
    tilemap = b''
    last_direction = 0
    seen_reward = False

    def achieved():
        return state[field] == level and bool(state['flags'] & 2)

    def observe(f, raw):
        nonlocal first, done, failure, previous, observed, tilemap, seen_reward
        observed = f
        if f < start:
            return
        data = lambda n, k: bytes(raw[(sy[n] + i) ^ 1] for i in range(k))
        word = lambda n: int.from_bytes(data(n, 2), 'big')
        tilemap = data('sms_vram', 16384)[0x3800:0x3e00]
        items = data('hero_items', 17)
        state.update(room=word('room_id'), game=word('game_state'),
                     hero=word('hero_state'), counter=word('hero_counter'),
                     x=word('hero_x') >> 8, y=word('hero_y') >> 8,
                     health=word('hero_health'), max_health=word('hero_max_health'),
                     gold=word('hero_gold'), magic=word('hero_magic'),
                     max_magic=word('hero_max_magic'), fire=items[4], oil=items[8],
                     basic=word('hero_basic_level'), armor=word('hero_armor_level'),
                     selected=word('hero_selected_item'),
                     outside=word('house_return_room'),
                     flags=data('game_save_state', 592)[0x50 + a.outside],
                     modal=word('house_dialogue_active'), reward=word('item_reward_active'),
                     audio_error=word('sound_unhandled_command'))
        if first is None:
            first = dict(state)
            assert first['room'] == 0x4f and first['outside'] == a.outside
            assert first['health'] and first['fire'] and first[field] < level
            assert not first['flags'] & 2
            assert a.outside != 0x50 or first['max_health'] >= 56
        if state['outside'] != a.outside:
            failure = 'outside_context_changed'
        if not state['health'] or state['game'] == 20:
            failure = 'hero_died'
        if state['audio_error']:
            failure = 'native_audio_error'
        if state['reward']:
            seen_reward = True
        key = tuple(state[n] for n in ['room', 'game', field, 'flags', 'modal', 'reward'])
        if key != previous:
            events.append(dict(frame=f, **state))
            captures.add(f + 1)
            previous = key
        if state['room'] == a.outside and state['game'] == 12 and state['hero'] == 1 and achieved() and seen_reward and done is None:
            done = f
            captures.add(f + 150)

    def choose(f):
        nonlocal last_direction
        if f <= start:
            return list(timeline[f])
        if failure or done is not None:
            return []
        if state.get('modal') or state.get('reward') or state.get('game') == 22:
            return [8] if f % 40 == 0 else []
        if state.get('room') != 0x4f or state.get('game') != 12 or state.get('hero') != 1:
            return []
        if state['counter']:
            return [4 + last_direction]
        point = state['x'], state['y']
        goal = (136, 152) if achieved() else (120, 72)
        if point == goal:
            last_direction = 1 if achieved() else 0
            return [4 + last_direction]
        path = walk(tilemap, point, lambda q: q == goal)
        if path:
            last_direction = path[0]
            return [4 + last_direction]
        return []

    def controller(f):
        value = choose(f)
        if f > start and (not controls or controls[-1]['buttons'] != value):
            controls.append(dict(frame=f, buttons=list(value)))
        return value

    with contextlib.redirect_stdout(io.StringIO()):
        run(rom, start + 5000, folder, captures, c['presses'], skip_intro=False,
            input_provider=controller, ram_observer=observe,
            stop_when=lambda: bool(failure) or done is not None and observed >= done + 150,
            core_options=c['core_options'], ram_writes=FrameWrites(writes))
    unchanged = all(state[n] == first[n] for n in ['gold', 'magic', 'max_magic', 'fire', 'oil', 'max_health'])
    passed = done is not None and not failure and unchanged
    result = dict(passed=passed, failure=failure or (None if passed else 'frame_limit_or_unexpected_change'),
                  rom_sha256=c['rom_sha256'], source_prefix=a.prefix, outside=a.outside,
                  gift_field=field, expected_level=level, first_state=first, last_state=state,
                  complete_frame=done, reward_observed=seen_reward,
                  ram_injections=bool(writes), assisted_route=bool(writes), new_assistance_writes=0,
                  sram_checkpoint_injection=False, primary_state_imports=0,
                  driver_sha256=sha(driver),
                  scope='Cold replay, ordinary town NPC contact, actual equipment gift and normal exterior exit. Inherited approach guard only; no equipment, actor, health, currency or progression fixture.')
    for name, value in [('report', result), ('events', events), ('controls', controls)]:
        (folder / (name + '.json')).write_bytes((json.dumps(value, indent=2) + '\n').encode())
    (folder / 'house_quest_driver.py').write_bytes(driver)
    if writes:
        assist = json.loads((source / 'assistance.json').read_bytes())
        assist['writes'] = [dict(frame=f, address=addr, data_hex=data.hex()) for f, addr, data in writes]
        (folder / 'assistance.json').write_bytes((json.dumps(assist, indent=2) + '\n').encode())
        recording(folder, json.loads((folder / 'capture.json').read_bytes()))
    print(result)


if __name__ == '__main__':
    main()
