"""Visit the free healer in house0/94 through ordinary buttons, then leave."""
import argparse
import contextlib
import io
import json
from pathlib import Path
from run_core import ROOT, run, FrameWrites
from natural_dungeon_combat import walk
from validate_playable_sprite_limit import symbols
from assisted_prefix import prefix_writes, recording
from archive_lossless_evidence import sha


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--prefix', required=True)
    p.add_argument('--trial', required=True)
    p.add_argument('--assisted-prefix', action='store_true')
    p.add_argument('--sms', action='store_true')
    p.add_argument('--allow-full-health', action='store_true')
    p.add_argument('--rom');a = p.parse_args()
    source = ROOT/'validation/natural-dungeon-route'/a.prefix
    cap = json.loads((source/'capture.json').read_bytes())
    prior = json.loads((source/'route_report.json').read_bytes())
    assert prior['failure'] is None and prior['reached_entrance']
    assert prior['house_outside'] == 0x94 and prior['house_target'] == 0 and cap['sram_input'] is None
    rom = ROOT/('input/original.sms' if a.sms else (a.rom or 'gaw-megadrive.bin'))
    assert cap['rom_sha256'] == sha(rom.read_bytes())
    writes = prefix_writes(source, cap, a.assisted_prefix)
    sy = None if a.sms else symbols(ROOT/'megadrive/out/release/symbol.txt')
    start = cap['frames']; controls = json.loads((source/'controls.json').read_bytes())
    timeline = [()]*(start+1)
    for i, row in enumerate(controls):
        end = controls[i+1]['frame']-1 if i+1 < len(controls) else start
        timeline[row['frame']:end+1] = [tuple(row['buttons'])]*(end-row['frame']+1)
    folder = ROOT/'validation/natural-service-route'/(('sms-' if a.sms else 'md-')+a.trial)
    assert not folder.exists()
    first = None; night = None; healed = None; done = None
    state = {}; tilemap = b''; observed = 0; failure = None; last = None; direction = 0
    events = []; captures = {start}; phases = set()

    def observe(frame, raw):
        nonlocal first, night, healed, done, state, tilemap, observed, failure, last
        observed = frame
        if frame < start:
            return
        if a.sms:
            state=dict(room=int.from_bytes(raw[0xb9:0xbb],'little'),game=raw[0x1d],hero=raw[0x301],
                       counter=raw[0x304],x=raw[0x313],y=raw[0x311],health=raw[0x318],max_health=raw[0xda],
                       magic=raw[0xdb],max_magic=raw[0xdc],gold=raw[0xdd],keys=raw[0xde],selected=raw[0xdf],
                       phase=None,audio_error=0,items=list(raw[0xe0:0xf1]),crystals=list(raw[0xcf:0xd8]))
            tilemap=bytes(raw[0x1600:0x1c00])
        else:
            data = lambda name, count: bytes(raw[(sy[name]+i)^1] for i in range(count))
            word = lambda name: int.from_bytes(data(name, 2), 'big')
            state = dict(room=word('room_id'), game=word('game_state'), hero=word('hero_state'),
                     counter=word('hero_counter'), x=word('hero_x')>>8, y=word('hero_y')>>8,
                     health=word('hero_health'), max_health=word('hero_max_health'),
                     magic=word('hero_magic'), max_magic=word('hero_max_magic'), gold=word('hero_gold'),
                     keys=word('hero_keys'), selected=word('hero_selected_item'), phase=word('healer_phase'),
                     audio_error=word('sound_unhandled_command'), items=list(data('hero_items', 17)),
                     crystals=list(data('game_save_state', 592)[0x1f:0x28]))
            tilemap = data('sms_vram', 16384)[0x3800:0x3e00]
        if first is None:
            first = dict(state)
            assert first['room'] == 0 and 0 < first['health'] <= first['max_health']
            assert a.allow_full_health or first['health'] < first['max_health']
        if state['phase'] is not None:phases.add(state['phase'])
        if night is None and (state['game']==22 if a.sms else state['phase']==2):
            night = dict(frame=frame, **state); captures.add(frame+1)
        if healed is None and night is not None and state['health'] == state['max_health']:
            healed = dict(frame=frame, **state); captures.add(frame+1)
        if not state['health'] or state['game'] == 20:
            failure = 'hero_died'
        if state['audio_error']:
            failure = 'native_audio_error'
        key = tuple(state[n] for n in ['room', 'game', 'health', 'gold', 'phase'])
        if key != last:
            events.append(dict(frame=frame, **state)); captures.add(frame+1); last = key
        if state['room'] == 0x94 and state['game'] == 12 and state['hero'] == 1 and healed is not None and done is None:
            done = frame; captures.add(frame+150)

    def choose(frame):
        nonlocal direction
        if frame <= start:
            return list(timeline[frame])
        if failure:
            return []
        if done is not None:
            return [5] if frame-done<=32 and state['room']==0x94 and state['game']==12 else []
        if state['game'] == 22:
            return [8] if frame%40 == 0 else []
        if a.sms and healed is not None and frame-healed['frame']<160:
            return [8] if frame%40==0 else []
        if state['room'] != 0 or state['game'] != 12 or state['hero'] != 1:
            return []
        if state['counter']:
            return [4+direction]
        point = state['x'], state['y']
        # Same right-hand healer used by the already verified merchant94 route.
        goal = (136, 144) if healed is not None else (216, 88)
        if point == goal or healed is not None and point[0] == 136 and point[1] >= 144:
            direction = 1 if healed is not None else 0
            return [4+direction]
        path = walk(tilemap, point, lambda q: q == goal)
        if path:
            direction = path[0]
            return [4+direction]
        return []

    def controller(frame):
        buttons = choose(frame)
        if frame > start and (not controls or controls[-1]['buttons'] != buttons):
            controls.append(dict(frame=frame, buttons=list(buttons)))
        return buttons

    with contextlib.redirect_stdout(io.StringIO()):
        run(rom, start+6000, folder, captures, cap['presses'], skip_intro=False,
            input_provider=controller, ram_observer=observe,
            stop_when=lambda: bool(failure) or done is not None and observed >= done+150,
            core_options=cap['core_options'], ram_writes=FrameWrites(writes))
    passed = bool(done is not None and healed and not failure)
    if passed:
        assert state['gold'] == first['gold'] and state['magic'] == first['magic']
        assert state['items'] == first['items'] and state['crystals'] == first['crystals']
        assert state['keys'] == first['keys'] and (a.sms or {1,2,3}.issubset(phases))
    result = dict(passed=passed, failure=failure or (None if passed else 'frame_limit'),
                  rom_sha256=cap['rom_sha256'], source_prefix=a.prefix, outside=0x94,
                  first_state=first, night=night, healed=healed, last_state=state,
                  complete_frame=done, observed_healer_phases=sorted(phases),
                  normal_health_refill=healed is not None and state['health']>first['health'], primary_state_imports=0,
                  new_assistance_writes=0, ram_injections=bool(writes), sram_checkpoint_injection=False,
                  currency_or_inventory_fixtures=False, driver_sha256=sha(Path(__file__).read_bytes()))
    if a.sms:
        result['sms_service_entry']=night;result['night']=None
        result['sms_observation_scope']='Service-state entry, actual health/currency/inventory and ordinary exterior exit. Night phase and native healer_phase are unavailable; graphics/audio/timing remain open.'
    for name, value in [('report', result), ('events', events), ('controls', controls)]:
        (folder/(name+'.json')).write_bytes((json.dumps(value, indent=2)+'\n').encode())
    if writes:
        (folder/'assistance.json').write_bytes((source/'assistance.json').read_bytes())
        recording(folder, json.loads((folder/'capture.json').read_bytes()))
    print(result)


if __name__ == '__main__':
    main()
