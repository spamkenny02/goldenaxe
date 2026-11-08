#ifndef GAW_SOURCE_INTRO_VDP_H
#define GAW_SOURCE_INTRO_VDP_H
#include "source_intro_sprite_clock.h"
#include "source_pattern_video.h"

typedef struct {
 SourceIntroSpriteClock clock;
 u8 *vram;
 u32 instruction_elapsed,instruction_raster;
 u16 address;
 u8 registers[16],palette[32],low,pending,code,buffer,error;
} SourceIntroVdp;

/* Owned logical SMS2 ports and sprite calendar;16KiB external VRAM storage.
 * Cold SMS2/no-BIOS register defaults, zero VRAM/palette. SourceClock epoch.
 * No physical MD writes. Mode4/192/unzoomed/no overscan sprite processing.
 * Checkpoint at the start of each visible IO instruction, then write/read at
 * its completed OUT/IN time. Stable gaps may span multiple frames. Preserve
 * all port writes, including IRQ SAT and032A pattern bytes. Failure fatal. */
u8 source_intro_vdp_init(SourceIntroVdp *vdp,u8 *vram,u16 lines,u32 raster,u32 elapsed);
u8 source_intro_vdp_checkpoint(SourceIntroVdp *vdp,u32 elapsed);
u8 source_intro_vdp_write(SourceIntroVdp *vdp,u32 elapsed,u8 port,u8 value);
u8 source_intro_vdp_read(SourceIntroVdp *vdp,u32 elapsed,u16 tstates,u8 port,u8 *value);
/* Validate the shared source raster/epoch, checkpoint at OUT instruction
 * start and commit at completion. All callers supply the real instruction
 * length:11T immediate OUT,12T OUT(C),16T OUTI/OUTD. */
u8 source_intro_vdp_out(SourceIntroVdp *vdp,u32 elapsed,u32 raster,u16 tstates,u8 port,u8 value);
/* Exact sprite/status semantics for stable032A runs in logical0000..23FF.
 * BF address writes cannot change sprite evaluation; each BE still advances
 * the calendar BEFORE its own RAM mutation. No status/IRQ may intervene.
 * Does not publish physical MD pixels; run retains every original OUT date. */
u8 source_intro_vdp_pattern_run(void *user,const SourcePatternVideoRun *run);
/* Stable E2B plane-clear or EFA map-transfer run,as described by
 * SourceIntroVideoRun. clear=1:BE101T,stride124T,address+4,valueFF;
 * clear=0:BE16T,stride32T,address+1,borrowed immutable-for-call bytes. */
u8 source_intro_vdp_map_run(SourceIntroVdp *vdp,u32 elapsed,u32 raster,u32 period,
 u16 address,u16 count,const u8 *bytes,u8 clear);
/* SourceIrqStatusRead-compatible; includes command-latch clearing. */
u8 source_intro_vdp_irq_status(void *user,const SourceClockIrq *entry,u8 *status);
#endif
