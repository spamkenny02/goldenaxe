#ifndef GAW_SOURCE_INTRO_SCENE_VDP_H
#define GAW_SOURCE_INTRO_SCENE_VDP_H
#include "source_intro_vdp.h"
#include "source_irq_context.h"
#include "source_intro_video.h"

/* E50 source_intro_scene_load_ports sink adapters. Logical VDP owns a
 * separate16KiB mirror; caller retains the complete video/status history. */
u8 source_intro_scene_vdp_pattern(void *user,u32 elapsed,u32 raster,u8 port,u8 value);
u8 source_intro_scene_vdp_map(void *user,u32 elapsed,u32 raster,u8 port,u8 value);
u8 source_intro_scene_vdp_run(void *user,const SourceIntroVideoRun *run);
/* Timed intro IRQ register/SAT/palette publication, compatible with compact
 * SourceIrqVideoPublish. Supports the observed intro path with no queued
 * tile/HUD/map requests. Rejects pending requests before publication so they
 * cannot silently disappear. Does not commit canonical IRQ RAM/audio work.
 * Call only through source_irq_interrupt after a real status provider read.
 * Failure may leave earlier output published; stop session, never retry. */
u8 source_intro_scene_vdp_irq(void *user,const SourceIrqContext *context,const SourceClockIrq *entry,u16 *tile_count);
#endif
