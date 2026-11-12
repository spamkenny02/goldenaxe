"""Pay the original ten-horn passage and walk through it, using ordinary input."""
import argparse
import contextlib
import io
import json
from run_core import ROOT, run, FrameWrites
from assisted_prefix import prefix_writes, recording
from archive_lossless_evidence import sha
from validate_playable_sprite_limit import symbols


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--prefix', required=True)
    p.add_argument('--outside', type=lambda s: int(s, 0), required=True)
    p.add_argument('--trial', required=True)
    p.add_argument('--assisted-prefix', action='store_true')
    p.add_argument('--sms', action='store_true')
    p.add_argument('--rom');a = p.parse_args()
    source = ROOT/'validation/natural-dungeon-route'/a.prefix
    c = json.loads((source/'capture.json').read_bytes())
    prior = json.loads((source/'route_report.json').read_bytes())
    assert prior['reached_entrance'] and prior['failure'] is None
    assert prior['house_outside'] == a.outside and prior['house_target'] == 0x9f
    assert c['sram_input'] is None
    rom = ROOT/('input/original.sms' if a.sms else (a.rom or 'gaw-megadrive.bin'))
    assert c['rom_sha256'] == sha(rom.read_bytes())
    ref = json.loads((ROOT/'analysis/paid_passage_reference.json').read_bytes())
    assert ref['source_sha256'] == sha((ROOT/'input/original.sms').read_bytes())
    route = next(r for r in ref['routes'] if r[0] == a.outside)
    price = ref['prices'][ref['towns'].index(a.outside)]
    target = route[1]
    writes = prefix_writes(source, c, a.assisted_prefix)
    controls = json.loads((source/'controls.json').read_bytes())
    start = c['frames']
    timeline = [()]*(start+1)
    for i, row in enumerate(controls):
        end = controls[i+1]['frame']-1 if i+1 < len(controls) else start
        timeline[row['frame']:end+1] = [tuple(row['buttons'])]*(end-row['frame']+1)
    folder = ROOT/'validation/natural-service-route'/(('sms-' if a.sms else 'md-')+a.trial)
    assert not folder.exists()
    sy = None if a.sms else symbols(ROOT/'megadrive/out/release/symbol.txt')
    state, events, captures = {}, [], {start}
    first = done = failure = previous = None
    observed = 0

    def observe(f, raw):
        nonlocal first, done, failure, observed, previous
        observed = f
        if f < start:
            return
        if a.sms:
            state.update(room=int.from_bytes(raw[0xb9:0xbb],'little'),game=raw[0x1d],hero=raw[0x301],
                         counter=raw[0x304],x=raw[0x313],y=raw[0x311],health=raw[0x318],max_health=raw[0xda],
                         gold=raw[0xdd],keys=raw[0xde],magic=raw[0xdb],modal=raw[0x1d]==22,audio_error=0,
                         outside_flags=raw[0x100+target],inventory_hex=raw[0xe0:0xf1].hex(),
                         crystals_hex=raw[0xcf:0xd8].hex())
        else:observe_md(raw)
        finish_observation(f)

    def observe_md(raw):
        data = lambda n, k: bytes(raw[(sy[n]+i)^1] for i in range(k))
        word = lambda n: int.from_bytes(data(n, 2), 'big')
        state.update(room=word('room_id'), game=word('game_state'), hero=word('hero_state'),
                     counter=word('hero_counter'), x=word('hero_x')>>8, y=word('hero_y')>>8,
                     health=word('hero_health'), max_health=word('hero_max_health'),
                     gold=word('hero_gold'), keys=word('hero_keys'), magic=word('hero_magic'),
                     modal=word('house_dialogue_active'), audio_error=word('sound_unhandled_command'),
                     outside_flags=data('game_save_state', 592)[0x50+target],
                     inventory_hex=data('hero_items', 17).hex(),
                     crystals_hex=data('game_save_state', 592)[0x1f:0x28].hex())
    def finish_observation(f):
        nonlocal first,done,failure,previous
        if first is None:
            first = dict(state)
            assert first['room'] == 0x9f and first['gold'] >= price and first['health']
        if not state['health'] or state['game'] == 20:
            failure = 'hero_died'
        if state['audio_error']:
            failure = 'native_audio_error'
        key = tuple(state[n] for n in ['room', 'game', 'gold', 'modal', 'outside_flags'])
        if key != previous:
            events.append(dict(frame=f, **state)); captures.add(f+1); previous = key
        if done is None and state['room'] == target and state['game'] == 12 and state['hero'] == 1 and not state['modal']:
            assert state['gold'] == first['gold']-price
            assert state['outside_flags']&1
            for key in ['health', 'max_health', 'keys', 'magic', 'inventory_hex', 'crystals_hex']:
                assert state[key] == first[key], (key, state[key], first[key])
            if done is None:
                done = f; captures.add(f+150)

    def choose(f):
        if f <= start:
            return list(timeline[f])
        if failure or done is not None:
            return []
        if state.get('modal'):
            return [8] if f % 40 == 0 else []
        if state.get('room') != 0x9f:
            return []
        if state['x'] != 136:
            return [7 if state['x'] < 136 else 6]
        # The SMS passage uses an internal confirmation loop without always
        # publishing game22. Send ordinary fresh C edges while facing the NPC.
        return [4,8] if a.sms and f%40==0 else [4]

    def controller(f):
        value = choose(f)
        if f > start and (not controls or controls[-1]['buttons'] != value):
            controls.append(dict(frame=f, buttons=value))
        return value

    with contextlib.redirect_stdout(io.StringIO()):
        run(rom, start+5000, folder, captures, c['presses'], skip_intro=False,
            input_provider=controller, ram_observer=observe,
            stop_when=lambda: bool(failure) or done is not None and observed >= done+150,
            core_options=c['core_options'], ram_writes=FrameWrites(writes))
    result = dict(passed=done is not None and not failure,
                  failure=failure or (None if done else 'frame_limit'),
                  rom_sha256=c['rom_sha256'], source_prefix=a.prefix,
                  outside=a.outside, target=target, price=price, complete_frame=done,
                  first_state=first, last_state=state, new_assistance_writes=0,
                  ram_injections=bool(writes), assisted_route=bool(writes), primary_state_imports=0,
                  currency_or_inventory_fixtures=False, sram_checkpoint_injection=False,
                  driver_sha256=sha((ROOT/'tools/natural_paid_passage.py').read_bytes()))
    for name, value in [('report', result), ('events', events), ('controls', controls)]:
        (folder/(name+'.json')).write_bytes((json.dumps(value, indent=2)+'\n').encode())
    if writes:
        (folder/'assistance.json').write_bytes((source/'assistance.json').read_bytes())
        recording(folder, json.loads((folder/'capture.json').read_bytes()))
    print(result)


if __name__ == '__main__':
    main()
