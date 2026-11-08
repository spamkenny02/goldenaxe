#ifndef GAW_SOURCE_INTRO_VDP_H
#define GAW_SOURCE_INTRO_VDP_H
#include "source_intro_sprite_clock.h"

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
/* SourceIrqStatusRead-compatible; includes command-latch clearing. */
u8 source_intro_vdp_irq_status(void *user,const SourceClockIrq *entry,u8 *status);
#endif
