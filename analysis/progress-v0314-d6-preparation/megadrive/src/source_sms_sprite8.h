#ifndef GAW_SOURCE_SMS_SPRITE8_H
#define GAW_SOURCE_SMS_SPRITE8_H
#include <types.h>
/* Mode4/192,8x8,no zoom. SAT input is64Y bytes then128X/tile bytes,
 * not the64-byte gap in hardware VRAM. Earlier entries win; all Y-visible
 * entries count toward the eight-per-line limit, even transparent/offscreenX.
 * Output/input buffers are disjoint. Frame and source512tile MD shadow stay
 * immutable until all requested clone tiles and the SAT are published. */
typedef struct {
    u32 columns[64];
    u16 sat[256],source_tile[64];
    u8 rows[64];
    u16 count,tile_base;
    u8 overflow;
} SourceSmsSprite8;
enum {SOURCE_SMS_SPRITE8_OK,SOURCE_SMS_SPRITE8_INVALID};
/* Target uses PAL1,low priority,64 reserved clone tiles; viewport Y=16.
 * Invalid arguments/mode/base do not change output. Init is not required. */
u8 source_sms_sprite8_prepare(SourceSmsSprite8 *frame,const u8 *sat,
                              u8 reg0,u8 reg1,u8 reg6,u16 tile_base);
/* Update a valid/zero-initialized frame in place. Separate64Y/128X-tile
 * inputs accept both packed and hardware-gap SAT layouts. changed[0..count)
 * marks clone pixels requiring delivery, including dirty source patterns;
 * optional dirty is a64-byte512tile bitset. Inactive entries are retained:
 * consumers must obey count. Input/output/changed buffers are disjoint.
 * Invalid mode/base/count leaves frame and changed untouched. */
u8 source_sms_sprite8_update(SourceSmsSprite8 *frame,const u8 *y,const u8 *xt,
 u8 reg0,u8 reg1,u8 reg6,u16 tile_base,const u8 *dirty,u8 *changed);
/* Prepare one owned8x8 MD tile; row/column masks reproduce source clipping.
 * Invalid index/source/frame leaves destination unchanged. */
u8 source_sms_sprite8_tile(const SourceSmsSprite8 *frame,const u32 *patterns,
                           u16 index,u32 *destination);
#endif
