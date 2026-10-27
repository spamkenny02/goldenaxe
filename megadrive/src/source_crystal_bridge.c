#include "source_crystal_bridge.h"

/* 698B..699B,193D: persist class0 bit before the repeat guard. */
u16 source_crystal_bridge(u16 hero_state,u8 fifth_crystal,u8 *room_flags)
{
    u8 already;
    if(!hero_state || !(fifth_crystal&0x80)) return 0;
    already=*room_flags&1;*room_flags|=1;
    return !already;
}
