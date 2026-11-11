"""Use the owned Ice Bell at the source CB gravestone, then follow a world route.

The projected map is a path proposal only. Ordinary inventory and C inputs
must produce the real persistent flag and terrain change in the primary game.
"""
import json
import sys
from pathlib import Path
import natural_dungeon_route as game
import assisted_boss_route as guard
from run_core import ROOT
from archive_lossless_evidence import sha
from validate_playable_sprite_limit import symbols
from rebase_natural_campaign import evidence


def project_persisted_cells(world, room, cells, flags, activate_bell=False, bell_room=0xcb):
    cells = bytearray(cells)
    rows = world.arrays['world_room_metadata']
    row = next((rows[i:i+4] for i in range(0, len(rows), 4) if rows[i] == room), None)
    if row and (flags[room] & 1 or room == bell_room and activate_bell):
        _, source, index, kind = row
        if room == 0xcb:
            assert bytes(row) == bytes([0xcb, 0x86, 0x39, 1])
        def put(n, value):
            assert 0 <= n < 160
            cells[n] = value
        direct = {5: [(index,1),(index+16,1)],
                  6: [(0x30,0x30),(0x40,0x31),(0x50,0x1f)],
                  7: [(index,1),(index+16,4)], 8: [(index,8),(index+1,8)],
                  9: [(index,0x4d)], 10: [(index,0x4c)],
                  11: [(index,9),(index+16,6),(0x1b,0x4d)],
                  12: [(index+n,0) for n in range(4)],
                  13: [(index,0x0c)], 14: [(index,0)],
                  15: [(index,9),(source,9)],
                  16: [(index,0),(index+1,0),(index+16,0),(index+17,0),(source,0x4d)],
                  17: [(index,8),(index+1,8),(source,0x4d)],
                  18: [(index,8),(index+1,8),(source,0)],
                  19: [(index,9),(source,0x4d)], 20: [(0x4a,0x0a),(0x5a,0x6b)]}
        if kind in direct:
            for n, value in direct[kind]: put(n, value)
        else:
            assert kind in [0,1,2,3,4]
            n, value = (source,index) if kind == 1 else (index,{0:0,2:0x15,3:3,4:4}.get(kind))
            put(n, value)
            if n+16 < 160:
                cells[n+16] = {0x27:1,0x28:3,0x29:0,0x39:0x3a}.get(cells[n+16],cells[n+16])
    return cells


def main():
    assert '--world-route' in sys.argv
    bell_room=0xcb
    if '--bell-room' in sys.argv:
        n=sys.argv.index('--bell-room');bell_room=int(sys.argv[n+1],0);del sys.argv[n:n+2]
    assert bell_room in (0x96,0xaa,0xcb)
    bell_index,bell_value=(0x86,0x39) if bell_room==0xcb else (0x48 if bell_room==0x96 else 0x69,4)
    passive='--persisted-only' in sys.argv
    if passive:sys.argv.remove('--persisted-only')
    sms='--sms' in sys.argv
    flag = '--prefix-combat' if '--prefix-combat' in sys.argv else '--prefix-service'
    family = 'natural-dungeon-combat' if flag == '--prefix-combat' else 'natural-service-route'
    name = sys.argv[sys.argv.index(flag) + 1]
    prefix = ROOT / 'validation' / family / name
    cap = json.loads((prefix / 'capture.json').read_bytes())
    start = cap['frames']
    sy = None if sms else symbols(ROOT / 'megadrive/out/release/symbol.txt')
    raw = evidence(prefix / f'ram_{start:05d}.bin')
    flags = raw[0x100:0x200] if sms else bytes(raw[(sy['game_save_state'] + 0x50 + i) ^ 1] for i in range(256))
    original_render, original_run = game.World.render_cells, game.run
    driver = Path(__file__).read_bytes()
    result, state, actual, events = {}, {}, [], []
    first = opened = None
    sequence = False

    def render(world, room, cells, meta=None):
        return original_render(world, room, project_persisted_cells(world, room, cells, flags, not passive, bell_room), meta)

    def wrapped(*args, **kwargs):
        result['folder'] = Path(args[2])
        observe_base, control_base = kwargs['ram_observer'], kwargs['input_provider']
        def observe(frame, ram):
            nonlocal first, opened, sequence
            observe_base(frame, ram)
            if frame < start or passive:
                return
            if sms:
                state.update(room=int.from_bytes(ram[0xb9:0xbb],'little'),game=ram[0x1d],hero=ram[0x301],
                             counter=ram[0x304],selected=ram[0xdf],slot=ram[0xa0],health=ram[0x318],
                             magic=ram[0xdb],gold=ram[0xdd],keys=ram[0xde],owned=ram[0xea],
                             flag=ram[0x100+bell_room],cell=ram[0x1c00+bell_index],bell=ram[0xac],terrain=ram[0x41])
            else:observe_md(ram)
            finish_observation(frame)
        def observe_md(ram):
            data = lambda n, k: bytes(ram[(sy[n] + i) ^ 1] for i in range(k))
            word = lambda n: int.from_bytes(data(n, 2), 'big')
            state.update(room=word('room_id'), game=word('game_state'), hero=word('hero_state'),
                         counter=word('hero_counter'), selected=word('hero_selected_item'),
                         slot=word('inventory_slot'), health=word('hero_health'),
                         magic=word('hero_magic'), gold=word('hero_gold'), keys=word('hero_keys'),
                         owned=data('hero_items', 17)[10], flag=data('game_save_state', 592)[0x50+bell_room],
                         cell=data('scratch', 4096)[0x800+bell_index], bell=word('ice_bell_state'),terrain=word('hero_terrain_context'))
        def finish_observation(frame):
            nonlocal first,opened,sequence
            if frame > start and state['room'] == bell_room and state['game'] == 12 and first is None:
                first = dict(frame=frame, **state)
                assert state['owned'] and not state['flag'] & 1
            if first and state['room'] == bell_room:
                if not events or any(state[k] != events[-1][k] for k in ['game','selected','slot','flag','cell','bell']):
                    events.append(dict(frame=frame, **state)); args[3].add(frame+1)
                if state['flag'] & 1 and opened is None:
                    opened = dict(frame=frame, **state)
                    assert state['cell'] == bell_value and state['bell'] == 1
            if sequence and opened and state['game'] == 12 and state['hero'] == 1 and state['selected'] == 1:
                sequence = False
        def control(frame):
            nonlocal sequence
            if frame > start and first and opened is None and state['terrain'] not in (3,5):
                sequence = True
            if frame <= start or not sequence:
                buttons = list(control_base(frame))
            else:
                buttons = []
                wanted = 1 if opened else 10
                if frame % 20 == 0:
                    if state['game'] == 12 and state['hero'] == 1 and not state['counter']:
                        buttons = [8] if state['selected'] == wanted else [0]
                    elif state['game'] == 16:
                        if state['selected'] == wanted: buttons = [0]
                        elif state['slot']//4 != wanted//4: buttons = [5 if state['slot']//4 < wanted//4 else 4]
                        elif state['slot']%4 != wanted%4: buttons = [7 if state['slot']%4 < wanted%4 else 6]
                        else: buttons = [8]
            if not actual or actual[-1]['buttons'] != buttons:
                actual.append(dict(frame=frame, buttons=buttons))
            return buttons
        kwargs.update(ram_observer=observe, input_provider=control)
        return original_run(*args, **kwargs)

    game.World.render_cells, game.run = render, wrapped
    try:
        guard.main()
    finally:
        game.World.render_cells, game.run = original_render, original_run
    folder = result['folder']
    (folder/'controls.json').write_bytes((json.dumps(actual, indent=2)+'\n').encode())
    (folder/'bell_events.json').write_bytes((json.dumps(events, indent=2)+'\n').encode())
    (folder/'bell_world_driver.py').write_bytes(driver)
    report = json.loads((folder/'route_report.json').read_bytes())
    report.update(bell_world_activation_room=bell_room,bell_world_driver_sha256=sha(driver), bell_first=first, bell_opened=opened,
                  bell_passage_verified=opened is not None if not passive else None,
                  persisted_flags_only=passive,bell_new_resource_or_terrain_writes=0)
    assert passive or not report['reached_entrance'] or opened is not None
    (folder/'route_report.json').write_bytes((json.dumps(report, indent=2)+'\n').encode())
    print('Persisted-terrain route only; no Bell activation claimed' if passive else
          f'{bell_room:02X} Bell passage verified: '+str(opened is not None))

if __name__ == '__main__':
    main()
