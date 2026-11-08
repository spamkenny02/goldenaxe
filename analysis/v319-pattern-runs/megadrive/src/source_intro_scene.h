#ifndef GAW_SOURCE_INTRO_SCENE_H
#define GAW_SOURCE_INTRO_SCENE_H
#include "source_intro_video.h"
#include "source_intro_map.h"
#include "source_pattern_clock.h"
typedef struct {u16 hl,de,bc,source_end,pattern_end,decoded_bytes;u8 skip;} SourceIntroSceneOutput;
/* E50..E72, exit at prefetched E75 or D0B. Header and patterns use bank6.
 * mirror owns16KiB of semantic SMS VRAM. Foreground clear/map OUTs update
 * that mirror and optional sink;032A writes pattern bytes directly.
 * Source IRQ video delivery is the caller's responsibility if required.
 * No physical MD upload or production status binding. Partial failure fatal. */
u8 source_intro_scene_load(SourceClock *clock,SourceIrqContext *context,u16 header,u16 target,
                           u8 *mirror,SourceIntroCallback callback,void *callback_user,
                           SourceIntroRevealSink sink,void *sink_user,SourceIntroSceneOutput *output);
/* Same E50 loader, with dated032A port publication in addition to clear/map
 * outputs. Pattern sink receives11T immediate OUTs; legacy scene sink also
 * includes16T OUTI map writes. Separate sinks let the caller preserve those
 * instruction lengths. A live VDP sink owns a DIFFERENT16KiB mirror from
 * mirror above: otherwise direct decoder writes could precede its raster
 * evaluation. IRQ video, register writes and status reads still require
 * caller wiring. Neither sink may mutate SourceClock or semantic RAM. */
u8 source_intro_scene_load_ports(SourceClock *clock,SourceIrqContext *context,u16 header,u16 target,
 u8 *mirror,SourceIntroCallback callback,void *callback_user,
 SourceIntroRevealSink sink,void *sink_user,SourcePatternPortSink pattern_sink,void *pattern_user,
 SourceIntroSceneOutput *output);
/* Same scene semantics; stable032A byte sequences go to pattern_run while
 * boundary instructions retain pattern_sink. Shared pattern_user. */
u8 source_intro_scene_load_runs(SourceClock *clock,SourceIrqContext *context,u16 header,u16 target,
 u8 *mirror,SourceIntroCallback callback,void *callback_user,
 SourceIntroRevealSink sink,void *sink_user,SourcePatternPortSink pattern_sink,void *pattern_user,
 SourcePatternVideoRunSink pattern_run,SourceIntroSceneOutput *output);
#endif
