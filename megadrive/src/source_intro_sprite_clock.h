#ifndef GAW_SOURCE_INTRO_SPRITE_CLOCK_H
#define GAW_SOURCE_INTRO_SPRITE_CLOCK_H
#include "source_intro_sprite_status.h"
#include "source_clock.h"

typedef struct {
 SourceIntroSpriteStatus sprites;
 u32 elapsed,raster,period,until_line;
 u16 lines;
 u8 vint,error;
} SourceIntroSpriteClock;

/* Logical SMS2 Mode4/192 video calendar, with source master ticks (15/T).
 * Cold history only: init does not reconstruct caches/flags from a snapshot.
 * Raster zero is the start of active line0, as in SourceClock. The reference
 * frame API starts at line192; this is not a second time origin.
 * No overscan sprite processing, zoom, extended height or physical MD I/O.
 * Checkpoint before each observable instruction, then commit its port/memory
 * effects before advancing to its completion. No intervening writes may be
 * omitted when advancing a longer stable block. At most one period per call.
 * A failing session must stop; mutations already made are not rolled back. */
u8 source_intro_sprite_clock_init(SourceIntroSpriteClock *clock,u16 lines,u32 raster,u32 elapsed);
u8 source_intro_sprite_clock_advance(SourceIntroSpriteClock *clock,u32 elapsed,const u8 *vram,const u8 *registers);
/* IN completion, with its full instruction length. Reads crossing a line
 * preserve the source's early-render/status semantics, including line191
 * into blanking. Status includes VINT80 and Mode4 unused bits1F; clears
 * latched flags. Caller separately clears the VDP command-byte latch. */
u8 source_intro_sprite_clock_read(SourceIntroSpriteClock *clock,u32 elapsed,u16 tstates,const u8 *vram,const u8 *registers,u8 *status);
typedef struct {
 SourceIntroSpriteClock *clock;
 const u8 *vram,*registers;
} SourceIntroSpriteClockBinding;
/* SourceIrqStatusRead/SourceGameStatusRead-compatible adapter. The calendar
 * must share the caller's elapsed/raster origin and retain all prior writes
 * and foreground status reads. Samples the original IN37T before0137. */
u8 source_intro_sprite_clock_irq_status(void *user,const SourceClockIrq *entry,u8 *status);
#endif
