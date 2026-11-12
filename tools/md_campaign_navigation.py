"""Shared proposals for real MD house entry; proposals never count as visits."""
from continue_sms_plain_house_census import COMBAT_ENTRANCES
from extract_title import rle_planes
def entry_options(raw,outside,house,direction,world):
    extra=['--house-outside',hex(outside),'--house-target',hex(house),'--persisted-only','--live-prefix-terrain','--door-entry-direction',str(direction)]
    if outside in COMBAT_ENTRANCES and not raw[0x100+outside]&1:extra+=['--fight-for-entrance']
    tool='natural_bell_world_route.py';meta=world.arrays['world_room_metadata'];node=next((meta[i:i+4] for i in range(0,len(meta)-3,4) if meta[i]==outside),None)
    if node and not raw[0x100+outside]&1:
        cells=bytearray(160);ptr=int.from_bytes(world.arrays['world_room_index'][outside*2:outside*2+2],'little');rle_planes(world.arrays['world_room_streams'],ptr,cells,0,1)
        kind=cells[node[1]]
        if kind in (0x13,0x38,0x3d,0x85,0x86):
            if not raw[0xe5] or kind in (0x38,0x3d,0x85) and raw[0xe5]<2:return None
            tool='natural_frozen_earth_world_route.py' if kind==0x38 else 'natural_earth_world_route.py';extra+=['--earth-world-cell',hex(node[1])]
        elif 0x80<=kind<=0x84 and node[1]!=node[2]:extra+=['--required-chop',f'{hex(outside)}:{hex(node[1])}']
    return tool,extra
