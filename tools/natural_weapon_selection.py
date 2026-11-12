"""Select an owned sword/axe using the real menu after a verified recording."""
import argparse
import contextlib
import io
import json
from pathlib import Path
from run_core import ROOT, run, FrameWrites
from archive_lossless_evidence import sha
from assisted_prefix import prefix_writes, recording
from validate_playable_sprite_limit import symbols


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--trace', required=True)
    p.add_argument('--slot', type=int, choices=[0, 1], required=True)
    p.add_argument('--trial', required=True)
    p.add_argument('--assisted-prefix', action='store_true')
    p.add_argument('--sms', action='store_true')
    a = p.parse_args()
    source = (ROOT / 'validation' / a.trace).resolve()
    assert source.is_relative_to(ROOT / 'validation')
    c = json.loads((source / 'capture.json').read_bytes())
    r = json.loads((source / 'report.json').read_bytes())
    assert r['failure'] is None and (r.get('passed') or r.get('room_cleared'))
    assert c['sram_input'] is None
    rom = ROOT / ('input/original.sms' if a.sms else 'gaw-megadrive.bin')
    assert sha(rom.read_bytes()) == c['rom_sha256']
    writes = prefix_writes(source, c, a.assisted_prefix)
    controls = json.loads((source / 'controls.json').read_bytes())
    start = c['frames']
    timeline = [()] * (start + 1)
    for i, row in enumerate(controls):
        end = controls[i + 1]['frame'] - 1 if i + 1 < len(controls) else start
        timeline[row['frame']:end + 1] = [tuple(row['buttons'])] * (end - row['frame'] + 1)
    sy = None if a.sms else symbols(ROOT / 'megadrive/out/release/symbol.txt')
    driver = Path(__file__).read_bytes()
    folder = ROOT / 'validation/natural-service-route' / (('sms-' if a.sms else 'md-') + a.trial)
    assert not folder.exists()
    state = {}
    first = done = failure = None
    seen_menu = False
    observed = 0
    events = []
    captures = {start}

    def observe(f, raw):
        nonlocal first, done, failure, observed, seen_menu
        observed = f
        if f < start:
            return
        if a.sms:
            state.update(room=int.from_bytes(raw[0xb9:0xbb], 'little'), game=raw[0x1d], hero=raw[0x301],
                         x=raw[0x313], y=raw[0x311], health=raw[0x318], max_health=raw[0xda],
                         selected=raw[0xdf], slot=raw[0xa0], basic=raw[0xe0], axe=raw[0xe1],
                         gold=raw[0xdd], keys=raw[0xde], magic=raw[0xdb], items=list(raw[0xe0:0xf1]),
                         crystals=list(raw[0xcf:0xd8]), audio_error=0)
        else:
            observe_md(raw)
        finish_observation(f)

    def observe_md(raw):
        data = lambda n, k: bytes(raw[(sy[n] + i) ^ 1] for i in range(k))
        word = lambda n: int.from_bytes(data(n, 2), 'big')
        state.update(room=word('room_id'), game=word('game_state'), hero=word('hero_state'),
                     x=word('hero_x') >> 8, y=word('hero_y') >> 8, health=word('hero_health'),
                     max_health=word('hero_max_health'), selected=word('hero_selected_item'),
                     slot=word('inventory_slot'), basic=word('hero_basic_level'), axe=word('hero_weapon_level'),
                     gold=word('hero_gold'), keys=word('hero_keys'), magic=word('hero_magic'),
                     items=list(data('hero_items', 17)), crystals=list(data('game_save_state', 592)[0x1f:0x28]),
                     audio_error=word('sound_unhandled_command'))
    def finish_observation(f):
        nonlocal first, done, failure, seen_menu
        if first is None:
            first = dict(state)
            assert first['health'] and first['game'] == 12
            assert first['basic' if a.slot == 0 else 'axe'] > 0
            assert first['selected'] != a.slot
        if state['game'] == 16:
            seen_menu = True
        if not state['health'] or state['game'] == 20:
            failure = 'hero_died'
        if state['audio_error']:
            failure = 'native_audio_error'
        if state['room'] != first['room']:
            failure = 'room_changed'
        if not events or any(state[n] != events[-1][n] for n in ['game', 'selected', 'slot', 'health']):
            events.append(dict(frame=f, **state))
            captures.add(f + 1)
        if seen_menu and state['game'] == 12 and state['hero'] == 1 and state['selected'] == a.slot and done is None:
            done = f
            captures.add(f + 100)

    def controller(f):
        if f <= start:
            return list(timeline[f])
        buttons = []
        if not failure and done is None and f % 20 == 0:
            if state.get('game') == 12 and state.get('hero') == 1:
                buttons = [0]
            elif state.get('game') == 16:
                if state['selected'] == a.slot:
                    buttons = [0]
                elif state['slot']//4 != a.slot//4:
                    buttons = [5 if state['slot']//4 < a.slot//4 else 4]
                elif state['slot'] != a.slot:
                    buttons = [7 if state['slot'] < a.slot else 6]
                else:
                    buttons = [8]
        if not controls or controls[-1]['buttons'] != buttons:
            controls.append(dict(frame=f, buttons=buttons))
        return buttons

    with contextlib.redirect_stdout(io.StringIO()):
        run(rom, start + 2000, folder, captures, c['presses'], skip_intro=False,
            input_provider=controller, ram_observer=observe, ram_writes=FrameWrites(writes),
            core_options=c['core_options'], stop_when=lambda: bool(failure) or done is not None and observed >= done + 100)
    unchanged = all(state[n] == first[n] for n in ['room', 'max_health', 'basic', 'axe', 'gold', 'keys', 'magic', 'items', 'crystals'])
    passed = done is not None and not failure and unchanged
    result = dict(passed=passed, failure=failure or (None if passed else 'menu_not_completed_or_ownership_changed'),
                  source_trace=a.trace, rom_sha256=c['rom_sha256'], complete_frame=done, selected_slot=a.slot,
                  first_state=first, last_state=state, seen_menu=seen_menu, new_assistance_writes=0,
                  ram_injections=bool(writes), assisted_route=bool(writes), sram_checkpoint_injection=False,
                  primary_state_imports=0, driver_sha256=sha(driver),
                  scope='Cold recording, ordinary Start/direction/C menu selection of an already owned weapon. Only inherited approach guard writes; no ownership, actor, HP, money or progression fixture.')
    for name, value in [('report', result), ('controls', controls), ('events', events)]:
        (folder / (name + '.json')).write_bytes((json.dumps(value, indent=2) + '\n').encode())
    (folder / 'weapon_selection_driver.py').write_bytes(driver)
    if writes:
        assist = json.loads((source / 'assistance.json').read_bytes())
        assist['writes'] = [dict(frame=f, address=addr, data_hex=value.hex()) for f, addr, value in writes]
        (folder / 'assistance.json').write_bytes((json.dumps(assist, indent=2) + '\n').encode())
        recording(folder, json.loads((folder / 'capture.json').read_bytes()))
    print(result)


if __name__ == '__main__':
    main()
