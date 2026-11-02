"""Read-only class0 terrain proposals; live game must perform every change."""
from natural_dungeon_route import World

def render_persisted(world, room, cells, flags, meta=None, project_palace=False):
    cells = bytearray(cells)
    rows = world.arrays['world_room_metadata']
    row = next((rows[i:i+4] for i in range(0, len(rows), 4) if rows[i] == room), None)
    if row and (flags[room] & 1 or project_palace and room == 0x8b):
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
    return World.render_cells(world, room, cells, meta)

