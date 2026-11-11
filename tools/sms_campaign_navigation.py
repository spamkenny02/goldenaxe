"""Propose an entrance, then require actual cold-played entry and fixed replay."""
import json
from run_core import ROOT
from continue_sms_plain_house_census import census_world,COMBAT_ENTRANCES


def enter(c,outside,house,suffix,new_episode=False):
    completed_exit=c.family+'/'+c.current if new_episode else None
    if c.raw()[0xe1] and c.raw()[0xdf]!=1:c.equip(1,suffix+'-equipaxe')
    raw=c.raw();start=(int.from_bytes(raw[0xb9:0xbb],'little'),raw[0x313],raw[0x311])
    direction=next(d for d in range(4) if census_world(raw,outside,house,d).route(start)[0] is not None)
    w=census_world(raw,outside,house,direction)
    n=1
    while (ROOT/f'validation/natural-dungeon-route/sms-sms-{c.label}-{suffix}-entry{n:02d}').exists():n+=1
    extra=['--house-outside',hex(outside),'--house-target',hex(house),'--persisted-only',
        '--live-prefix-terrain','--door-entry-direction',str(direction)]
    tool='natural_bell_world_route.py';m=w.arrays['world_room_metadata']
    node=next((m[i:i+4] for i in range(0,len(m)-3,4) if m[i]==outside),None)
    if outside in COMBAT_ENTRANCES and not raw[0x100+outside]&1:extra+=['--fight-for-entrance']
    reveal_matches_goal=(node is not None and node[3] in (0,2,3,4,5,7) and
        w.goal['x']==(node[2]&15)*16+8 and w.goal['y']==(node[2]&240)+16)
    if node and not raw[0x100+outside]&1 and reveal_matches_goal:
        cells=w.base_cells(outside)
        if cells[node[1]] in (0x13,0x38,0x3d,0x85,0x86):
            assert raw[0xdb]>=8
            tool='natural_frozen_earth_world_route.py' if raw[0xea] and (cells[node[1]]==0x38 or 0x3e in cells or 0x3f in cells) else 'natural_earth_world_route.py'
            extra+=['--earth-world-cell',hex(node[1])]
        elif 0x80<=cells[node[1]]<=0x84 and node[1]!=node[2]:extra+=['--required-chop',f'{hex(outside)}:{hex(node[1])}']
    c.route(suffix+f'-entry{n:02d}',extra,tool=tool,new_episode=new_episode,
        exit_proof=completed_exit if new_episode and c.family!='natural-dungeon-combat' else None)
    return n
