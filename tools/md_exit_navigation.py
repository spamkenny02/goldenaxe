"""Read-only axe proposals for an exterior return blocked by vegetation."""
def axe_cells(x,y,direction):
    alignment=((x&8)>>3)|((y&8)>>2)
    slot=direction*4+alignment
    offsets={0:[(-16,-32),(0,-32)],1:[(-8,-32)],2:[(-16,-24),(0,-24)],3:[(-8,-24)],
             4:[(-16,0),(0,0)],5:[(-8,0)],9:[(-24,-16)],10:[(-16,-24),(-16,-8)],
             11:[(-24,-24),(-24,-8)],13:[(8,-16)],14:[(0,-24),(0,-8)],15:[(8,-24),(8,-8)]}
    if slot in (0,1) and y<24 or slot in (4,5) and y>=160:return []
    return [(((y+dy)&255)&240)|(((x+dx)&255)>>4) for dx,dy in offsets.get(slot,[])]

def axe_direction(cells,x,y):
    for direction in (1,2,3,0):
        if any(n<len(cells) and 0x80<=cells[n]<=0x84 for n in axe_cells(x,y,direction)):
            return direction
    return None
