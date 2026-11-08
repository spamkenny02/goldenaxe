#ifndef GAW_SOURCE_INTRO_VIDEO_H
#define GAW_SOURCE_INTRO_VIDEO_H
#include "source_intro_reveal.h"
typedef struct {u16 writes,palette_end;u8 skip;} SourceIntroMapOutput;
/* EFA..F1D: F1E window/callback, D600..D8FF transfer to logical7800,
 * then fall through F09 for another wait/callback. Includes final RET,
 * or stops at prefetched D0B on skip. Semantic IO sink, no MD uploads.
 * Requires full_ram with live compact aliases and a current DCEC dispatcher. */
u8 source_intro_map_transfer(SourceClock *clock,SourceIrqContext *context,
                             SourceIntroCallback callback,void *callback_user,
                             SourceIntroRevealSink sink,void *sink_user,SourceIntroMapOutput *output);
/* EA5..ED3: initialize D600 blank map, invoke full EFA transfer, clear
 * 16 palette bytes, map bank6 and copy four header colors at palette_address.
 * Includes RET; bank6 is context->bank6, original8000..BFFF ROM window. */
u8 source_intro_map_prepare(SourceClock *clock,SourceIrqContext *context,u16 palette_address,
                            SourceIntroCallback callback,void *callback_user,
                            SourceIntroRevealSink sink,void *sink_user,SourceIntroMapOutput *output);
/* E2B..E3E: set plane3 of logical4000..63FF to FF through original
 * RST28/DI/EI address writes. Includes RET/checkpoint, no physical MD IO. */
u8 source_intro_plane_clear(SourceClock *clock,SourceIrqContext *context,
                            SourceIntroRevealSink sink,void *sink_user,u16 *writes);
#endif
