#ifndef GAW_SOURCE_INTRO_REVEAL_H
#define GAW_SOURCE_INTRO_REVEAL_H
#include "source_intro_wait.h"
typedef u8 (*SourceIntroRevealSink)(void *user,u32 elapsed,u32 raster,u8 port,u8 value);
typedef struct {u16 address,step,writes;u8 value;} SourceIntroRevealPass;
/* E8B..E9D: one source plane reveal pass, exit at prefetched EA0.
 * address/step are alternate HL/DE; value is foreground E. Sink receives
 * source OUT completion times/raster; it must not run the clock, alter
 * semantic RAM or inject IRQs. Stable loops may be advanced as one block.
 * No MD hardware publication. Failure can leave partial state/output. */
u8 source_intro_reveal_pass(SourceClock *clock,SourceIrqContext *context,
                            SourceIntroRevealPass *state,SourceIntroRevealSink sink,void *user);
typedef struct {SourceIntroRevealPass last;u16 passes,writes;u8 mask,skip;} SourceIntroRevealSequenceOutput;
/* E79..EA2, exit at prefetched EA4 (RET not included), or D0B on skip.
 * Original entry D=7F executes eight passes, including the final zero mask.
 * Supplied callback must dispatch the current semantic DCEC target. */
u8 source_intro_reveal_sequence(SourceClock *clock,SourceIrqContext *context,u8 mask,
                                SourceIntroCallback callback,void *callback_user,
                                SourceIntroRevealSink sink,void *sink_user,
                                SourceIntroRevealSequenceOutput *output);
#endif
