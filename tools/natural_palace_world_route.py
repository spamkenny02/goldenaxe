"""Propose persisted world terrain and verify the real nine-crystal gate.
Only ordinary controller input traverses the exterior. No map writes.
"""
import json,sys
from pathlib import Path
import natural_dungeon_route as game
import assisted_boss_route as guard
from run_core import ROOT
from validate_playable_sprite_limit import symbols
from rebase_natural_campaign import evidence


def main():
    assert '--world-route' in sys.argv and '--prefix-combat' in sys.argv
    name=sys.argv[sys.argv.index('--prefix-combat')+1]
    prefix=ROOT/'validation/natural-dungeon-combat'/name
    cap=json.loads((prefix/'capture.json').read_bytes());start=cap['frames']
    sy=symbols(ROOT/'megadrive/out/release/symbol.txt');raw=evidence(prefix/f'ram_{start:05d}.bin')
    save=bytes(raw[(sy['game_save_state']+i)^1] for i in range(592));assert all(v&128 for v in save[0x1f:0x28])
    flags=save[0x50:0x150];original_render,original_run=game.World.render_cells,game.run
    result={};events=[];first=None;opened=None;driver=Path(__file__).read_bytes()

    def render(world, room, cells, meta=None):
        cells = bytearray(cells)
        rows = world.arrays['world_room_metadata']
        row = next((rows[i:i+4] for i in range(0, len(rows), 4) if rows[i] == room), None)
        if row and (flags[room] & 1 or room == 0x8b):
            _, source, index, kind = row
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
        return original_render(world, room, cells, meta)

    def wrapped(*args,**kwargs):
        result['folder']=Path(args[2]);base=kwargs['ram_observer']
        def observe(frame,ram):
            nonlocal first,opened
            base(frame,ram)
            if frame<=start:return
            data=lambda n,k:bytes(ram[(sy[n]+i)^1] for i in range(k));w=lambda n:int.from_bytes(data(n,2),'big')
            if w('room_id')!=0x8b:return
            save=data('game_save_state',592);cells=data('scratch',4096)[0x800:0x8a0]
            state=dict(frame=frame,room=0x8b,game=w('game_state'),seen=save[0x48],flag=save[0xdb],cells=[cells[n] for n in [0x30,0x40,0x50]],health=w('hero_health'),magic=w('hero_magic'))
            if first is None and state['seen']:first=state
            if state['seen'] and state['cells']==[0x30,0x31,0x1f] and opened is None:opened=state
            if not events or any(state[k]!=events[-1][k] for k in ['game','seen','flag','cells']):events.append(state);args[3].add(frame+1)
        kwargs['ram_observer']=observe
        return original_run(*args,**kwargs)
    game.World.render_cells,game.run=render,wrapped
    try:guard.main()
    finally:game.World.render_cells,game.run=original_render,original_run
    folder=result['folder'];report=json.loads((folder/'route_report.json').read_bytes())
    report.update(palace_gate_first=first,palace_gate_opened=opened,palace_gate_verified=opened is not None,palace_new_map_or_resource_writes=0)
    assert not report['reached_entrance'] or opened is not None
    for name,value in [('route_report',report),('palace_gate_events',events)]: (folder/(name+'.json')).write_bytes((json.dumps(value,indent=2)+'\n').encode())
    (folder/'palace_world_driver.py').write_bytes(driver)

if __name__=='__main__':main()
