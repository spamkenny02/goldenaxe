#ifndef GAW_SOURCE_INTRO_SPRITE_STATUS_H
#define GAW_SOURCE_INTRO_SPRITE_STATUS_H
#include <types.h>
/* Static-frame Mode4/192/SMS2 sprite flags from a16KiB logical VRAM mirror.
 * Eight-pixel, unzoomed intro sprites only. Collision20, overflow40; no VINT.
 * Does not model mid-frame writes, flag latching or status-read timing. */
u8 source_intro_sprite_flags(const u8 *vram,const u8 *registers,u8 *flags);
/* Live flags use ordered parse/render/read events below. The static helper
 * above cannot reconstruct intervening writes or earlier status reads. */
typedef struct {s16 x;u8 row,attribute;} SourceIntroCachedSprite;
typedef struct {
 SourceIntroCachedSprite objects[2][8];
 u8 count[2],flags,pending_overflow;
 s16 collision_line;u8 collision_hcounter;
} SourceIntroSpriteStatus;
void source_intro_sprite_status_reset(SourceIntroSpriteStatus *state);
u8 source_intro_sprite_parse(SourceIntroSpriteStatus *state,s16 line,const u8 *vram,const u8 *registers);
u8 source_intro_sprite_render(SourceIntroSpriteStatus *state,s16 line,const u8 *vram,const u8 *registers);
u8 source_intro_sprite_read(SourceIntroSpriteStatus *state,s16 line,u8 hcounter);
#endif
