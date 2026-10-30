"""Read original dungeon edges; propose D8 paths, never claim live traversal."""
import collections
import json
from run_core import ROOT
from extract_title import rle_planes
from archive_lossless_evidence import sha


def main():
    rom=(ROOT/'input/original.sms').read_bytes();maps={}
    for room in range(256,512):
        bank=8+((room*2)>>8);pointer=bank*16384+((room*2)&255)
        address=int.from_bytes(rom[pointer:pointer+2],'little')
        cells=bytearray(160);_,size=rle_planes(rom,bank*16384+(address&16383),cells,0,1)
        assert size==160;maps[room]=cells
    edges={room:[] for room in maps}
    for room,cells in maps.items():
        for other,indices,opposite in [(room-16,[7,8],[151,152]),(room+16,[151,152],[7,8]),(room-1,[64,80],[79,95]),(room+1,[79,95],[64,80])]:
            # Boundary00 is the exterior exit, not an adjacent dungeon room.
            if other in maps and all(cells[p] not in [0,17,38] for p in indices) and all(maps[other][p] not in [0,17,38] for p in opposite):
                edges[room].append(other)
    portals=json.loads((ROOT/'analysis/contact_script_reference.json').read_bytes())
    assert portals['source_sha256']==sha(rom)
    for record in portals['records']:
        if record['kind']=='moving_aligned_portal':edges[record['room']].append(record['destination_room'])
    queue=collections.deque([(0x1ea,[0x1ea])]);paths={}
    while queue:
        room,path=queue.popleft()
        if room in paths:continue
        paths[room]=path
        queue.extend((other,path+[other]) for other in edges[room])
    bosses=[]
    for room in paths:
        kinds=[kind for kind in rom[0x3234e+room*8:0x32356+room*8] if kind>=32 and rom[0x320ea+(kind-32)*4+3]&64]
        if kinds:bosses.append(dict(room=room,kinds=kinds,path=paths[room]))
    assert len(bosses)==1, bosses
    records={}
    for name in ['room_puzzles_reference','contact_script_reference','item_rewards_reference','room_clear_reference']:
        reference=json.loads((ROOT/'analysis'/f'{name}.json').read_bytes());assert reference['source_sha256']==sha(rom)
        records[name]=[r for r in reference['records'] if r['room'] in paths]
    result=dict(source_sha256=sha(rom),entry=0x1ea,bosses=bosses,paths=paths,
                rooms=[dict(room=room,cells=maps[room].hex(),candidate_edges=edges[room],actors=rom[0x3234e+room*8:0x32356+room*8].hex()) for room in sorted(paths)],
                script_records=records,live_progression_proof=False,
                limits=['Reciprocal base-map boundary heuristic with source portal links. Keys,shutters,interior collision,quest transformations and contact conditions can block a proposal. No emulator state or inventory is written.'])
    (ROOT/'analysis/d8_source_route_proposal.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Source D8 candidate',bosses,'rooms',len(paths))


if __name__=='__main__':main()
