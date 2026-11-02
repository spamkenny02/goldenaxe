"""Read a captured room's terrain routes and source mechanisms; never run/write game state."""
import argparse
import json
from pathlib import Path

import natural_dungeon_combat as game
from run_core import ROOT
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from validate_playable_sprite_limit import symbols
from natural_dungeon_route import World


def contact_point(coordinate):
    return next((x,y) for y in range(8,169,8) for x in range(8,249,8)
                if (((y-12)&248)<<3)+(((x-12)&255)>>2&62)+126 == coordinate)


def inspect(trace):
    folder = (ROOT/'validation'/trace).resolve()
    assert folder.is_relative_to(ROOT/'validation')
    cap = json.loads((folder/'capture.json').read_bytes())
    assert cap['rom_sha256'] == sha((ROOT/'gaw-megadrive.bin').read_bytes())
    assert Path(cap['rom']).suffix.lower() != '.sms'
    sy = symbols(ROOT/'megadrive/out/release/symbol.txt')
    raw = evidence(folder/f'ram_{cap["frames"]:05d}.bin')
    assert len(raw) == 65536
    data = lambda name,n: bytes(raw[(sy[name]+i)^1] for i in range(n))
    word = lambda name: int.from_bytes(data(name,2),'big')
    room = word('room_id')
    assert 256 <= room < 512 and word('game_state') == 12
    point = (word('hero_x')>>8,word('hero_y')>>8)
    tilemap = data('sms_vram',16384)[0x3800:0x3e00]
    cells = data('scratch',4096)[0x800:0x8a0]
    items = data('hero_items',17)
    game.CANOE_OWNED,game.SHIP_OWNED = bool(items[12]),bool(items[16])
    exits = []
    for direction,label in enumerate(['north','south','west','east']):
        def goal(q):
            if direction<2:
                return (q[1]<=15 if direction==0 else q[1]>=161) and 128<=q[0]<=143
            return (q[0]<=15 if direction==2 else q[0]>=241) and 80<=q[1]<=88
        path = game.walk(tilemap,point,goal)
        exits.append(dict(direction=label,destination_room=room+[-16,16,-1,1][direction],
                          terrain_reachable=path is not None,steps=None if path is None else len(path)))
    contacts = json.loads((ROOT/'analysis/contact_script_reference.json').read_bytes())
    assert contacts['source_sha256'] == sha((ROOT/'input/original.sms').read_bytes())
    portals = []
    for row in contacts['records']:
        if row['room'] != room or row['kind'] != 'moving_aligned_portal':
            continue
        target = contact_point(row['coordinate'])
        path = game.walk(tilemap,point,lambda q:q==target)
        portals.append(dict(destination_room=row['destination_room'],coordinate=row['coordinate'],point=target,
                            terrain_reachable=path is not None,steps=None if path is None else len(path)))
    world = World()
    meta = world.arrays['world_dungeon_metadata']
    row = next((list(meta[i:i+4]) for i in range(0,len(meta)-1,4) if meta[i] == room&255),None)
    clears = json.loads((ROOT/'analysis/room_clear_reference.json').read_bytes())
    assert clears['source_sha256'] == contacts['source_sha256']
    clear = next((r for r in clears['records'] if r['room']==room),None)
    puzzles = json.loads((ROOT/'analysis/room_puzzles_reference.json').read_bytes())
    assert puzzles['source_sha256'] == contacts['source_sha256']
    return dict(rom_sha256=cap['rom_sha256'],trace=trace,frame=cap['frames'],room=room,hero_point=point,
                room_flags=data('game_save_state',592)[0x50+(room&255)],health=word('hero_health'),
                terrain_sha256=sha(tilemap),exits=exits,portals=portals,source_metadata=row,
                metadata_trigger_live_cell=cells[row[1]] if row and row[1]<160 else None,
                source_room_clear=clear,
                source_contact_mechanisms=[r for r in contacts['records'] if r['room']==room],
                source_puzzles=[r for r in puzzles['records'] if r['room']==room],
                live_metatiles=list(cells),state_writes=0,
                scope='Terrain-only route proposals from captured RAM and original ROM. Actors and moving hazards are ignored. Actual movement, mechanism activation and room transition still require a verified controller run.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--trace',required=True)
    args = parser.parse_args()
    print(json.dumps(inspect(args.trace),indent=2))


if __name__ == '__main__':
    main()
