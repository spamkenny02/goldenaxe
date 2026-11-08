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
#endif
