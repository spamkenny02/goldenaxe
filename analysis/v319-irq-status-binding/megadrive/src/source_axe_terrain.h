#ifndef GAW_SOURCE_AXE_TERRAIN_H
#define GAW_SOURCE_AXE_TERRAIN_H
#include <types.h>
/* 34D3..358D: zero, one or two DC00 cell indices, in original order. */
u8 source_axe_terrain_probes(u8 graphics_class,u8 phase,u8 direction,u8 x,u8 y,u8 *indices);
#endif
