#ifndef GAW_SOURCE_MAGIC_ROPE_H
#define GAW_SOURCE_MAGIC_ROPE_H
#include <types.h>
/* 38AC/38F6: cells DC00..DCFF and C098..C09B animation workspace. */
void source_magic_rope_try(u8 direction,u8 graphics_class,u8 owned,u8 x,u8 y,u8 *cells,u8 *work);
/* 6D2C/6D40/6DA6: one two-tile row, returned as SMS map offset +4 bytes. */
u8 source_magic_rope_tick(const u8 *cells,const u8 *metatiles,u8 *work,u16 *offset,u8 *row);
#endif
