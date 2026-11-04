"""Reach Game Over by ordinary input and use Continue, without new RAM writes."""
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
    p.add_argument('--trace', required=True)
    p.add_argument('--trial', required=True)
    p.add_argument('--assisted-prefix', action='store_true')
    p.add_argument('--exposure-trace', help='Use only ordinary recorded buttons to reach an enemy area; never import its RAM writes')
    a = p.parse_args()
    source = (ROOT/'validation'/a.trace).resolve()
    assert source.is_relative_to(ROOT/'validation')
    cap = json.loads((source/'capture.json').read_bytes())
    prior = json.loads((source/'report.json').read_bytes())
    assert prior['failure'] is None and prior['full_dungeon_cleared']
    rom = ROOT/'gaw-megadrive.bin'
    assert cap['rom_sha256'] == sha(rom.read_bytes()) and cap['sram_input'] is None
    writes = prefix_writes(source, cap, a.assisted_prefix)
    sy = symbols(ROOT/'megadrive/out/release/symbol.txt')
    start = cap['frames']; controls = json.loads((source/'controls.json').read_bytes())
    timeline = [()]*(start+1)
    for i, row in enumerate(controls):
        end = controls[i+1]['frame']-1 if i+1 < len(controls) else start
        timeline[row['frame']:end+1] = [tuple(row['buttons'])]*(end-row['frame']+1)
    exposure = None
    if a.exposure_trace:
        other = (ROOT/'validation'/a.exposure_trace).resolve()
        assert other.is_relative_to(ROOT/'validation')
        other_cap = json.loads((other/'capture.json').read_bytes())
        other_report = json.loads((other/'route_report.json').read_bytes())
        assert other_cap['rom_sha256'] == cap['rom_sha256'] and other_cap['sram_input'] is None
        assert other_report['prefix_end'] == start and other_report['reached_entrance']
        exposure = [()]*(other_cap['frames']+1)
        rows = json.loads((other/'controls.json').read_bytes())
        for i, row in enumerate(rows):
            end = rows[i+1]['frame']-1 if i+1 < len(rows) else other_cap['frames']
            exposure[row['frame']:end+1] = [tuple(row['buttons'])]*(end-row['frame']+1)
        assert exposure[:start+1] == timeline
    folder = ROOT/'validation/natural-service-route'/('md-'+a.trial)
    assert not folder.exists()
    first = None; death = None; menu = None; resumed = None; done = None
    state = {}; tilemap = b''; observed = 0; failure = None; last = None
    patrol = 0; direction = 1; events = []; captures = {start}

    def observe(frame, raw):
        nonlocal first, death, menu, resumed, done, state, tilemap, observed, failure, last
        observed = frame
        if frame < start:
            return
        data = lambda name, count: bytes(raw[(sy[name]+i)^1] for i in range(count))
        word = lambda name: int.from_bytes(data(name, 2), 'big')
        state = dict(room=word('room_id'), game=word('game_state'), hero=word('hero_state'),
                     counter=word('hero_counter'), x=word('hero_x')>>8, y=word('hero_y')>>8,
                     health=word('hero_health'), max_health=word('hero_max_health'),
                     magic=word('hero_magic'), max_magic=word('hero_max_magic'), gold=word('hero_gold'),
                     keys=word('hero_keys'), selected=word('hero_selected_item'), hurt=word('hero_hurt'),
                     menu_selection=word('death_menu_selection'), checkpoint=word('save_runtime_checkpoint'),
                     dungeon=word('world_dungeon_number'), resume_phase=word('resume_phase'),
                     audio_error=word('sound_unhandled_command'), items=list(data('hero_items', 17)),
                     crystals=list(data('game_save_state', 592)[0x1f:0x28]))
        tilemap = data('sms_vram', 16384)[0x3800:0x3e00]
        actors = data('world_actor_state', 768)
        state['foes'] = [dict(slot=n, kind=actors[n*48], x=actors[n*48+19], y=actors[n*48+17])
                          for n in range(16) if actors[n*48]>=0x10 and actors[n*48+3]&2 and actors[n*48+28]]
        if first is None:
            first = dict(state)
            assert first['room'] < 256 and first['health'] > 0 and first['checkpoint'] == 0x95
        assert state['hurt'] <= 128, 'The death/Continue extension has no held test guard'
        if state['audio_error']:
            failure = 'native_audio_error'
        if death is None and state['health'] == 0:
            death = dict(frame=frame, **state); captures.add(frame+1)
        if menu is None and state['game'] == 20:
            menu = dict(frame=frame, **state); captures.add(frame+90)
        if menu is not None and resumed is None and state['room'] == first['checkpoint'] and state['game'] == 12 and state['hero'] == 1 and not state['resume_phase']:
            resumed = dict(frame=frame, **state); done = frame+2; captures.add(done)
        key = tuple(state[n] for n in ['room', 'game', 'health', 'gold', 'menu_selection', 'resume_phase'])
        if key != last:
            events.append(dict(frame=frame, **state)); captures.add(frame+1); last = key

    def choose(frame):
        nonlocal patrol, direction
        if frame <= start:
            return list(timeline[frame])
        if failure or resumed is not None:
            return []
        if state['game'] == 20:
            if frame % 40:
                return []
            return [4] if state['menu_selection'] != 1 else [8]
        if death is not None:
            return []
        if exposure is not None:
            if state['game'] == 12 and state['hero'] == 1 and state['foes']:
                if state['counter']:
                    return [4+direction]
                point = state['x'], state['y']
                enemy = min(state['foes'], key=lambda e: abs(e['x']-point[0])+abs(e['y']-point[1]))
                path = walk(tilemap, point, lambda q: abs(q[0]-enemy['x'])<8 and abs(q[1]-enemy['y'])<8)
                if path:
                    direction = path[0]
                    return [4+direction]
                return []
            return list(exposure[frame]) if frame < len(exposure) else []
        if state['room'] != first['room']:
            return []
        if state['game'] != 12 or state['hero'] != 1:
            return []
        if state['counter']:
            return [4+direction]
        points = [(136, 144), (64, 136), (192, 136)]
        point = state['x'], state['y']
        if point == points[patrol]:
            patrol = (patrol+1)%len(points)
        path = walk(tilemap, point, lambda q: q == points[patrol])
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
            stop_when=lambda: bool(failure) or done is not None and observed >= done,
            core_options=cap['core_options'], ram_writes=FrameWrites(writes))
    passed = bool(death and menu and resumed and not failure)
    if passed:
        assert resumed['health'] == resumed['magic'] == 24
        assert resumed['gold'] == (first['gold']>>2)*3
        assert resumed['items'] == first['items'] and resumed['crystals'] == first['crystals']
        assert resumed['keys'] == first['keys'] and resumed['max_health'] == first['max_health']
        assert resumed['max_magic'] == first['max_magic'] and not resumed['dungeon']
    result = dict(passed=passed, failure=failure or (None if passed else 'frame_limit'),
                  rom_sha256=cap['rom_sha256'], source_trace=a.trace, first_state=first,
                  death=death, death_menu=menu, resumed=resumed, last_state=state,
                  normal_deaths=int(death is not None), normal_continues=int(resumed is not None),
                  primary_state_imports=0, new_assistance_writes=0, ram_injections=bool(writes),
                  sram_checkpoint_injection=False, currency_or_inventory_fixtures=False,
                  driver_sha256=sha(Path(__file__).read_bytes()))
    result['exposure_trace'] = a.exposure_trace
    for name, value in [('report', result), ('events', events), ('controls', controls)]:
        (folder/(name+'.json')).write_bytes((json.dumps(value, indent=2)+'\n').encode())
    if writes:
        (folder/'assistance.json').write_bytes((source/'assistance.json').read_bytes())
        recording(folder, json.loads((folder/'capture.json').read_bytes()))
    print(result)


if __name__ == '__main__':
    main()
