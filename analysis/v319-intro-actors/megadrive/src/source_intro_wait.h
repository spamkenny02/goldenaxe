#ifndef GAW_SOURCE_INTRO_WAIT_H
#define GAW_SOURCE_INTRO_WAIT_H
#include "source_wait_restore.h"

typedef struct {u16 polls,below,above;u8 counter,skip,error;} SourceIntroWaitOutput;
/* F32's LD HL,(DCEC)/JP(HL) are included by the caller. A supplied native
 * callback models the selected target instruction by instruction, including
 * its RET, and may update semantic actor/palette RAM. Null means F36:RET.
 * No hardware IO or frame waits: SourceClock owns all source IRQ boundaries. */
typedef u8 (*SourceIntroCallback)(SourceClock *clock,SourceIrqContext *context,void *user);
/* Original0F09..0F1D. Entry at CALL0B95; exit at prefetched caller or0D0B
 * when source C021&30 requests skipping. Source wait/IRQ uses live audio.
 * Failure leaves diagnostic partial state and must stop the composition. */
u8 source_intro_wait_callback(SourceClock *clock,SourceIrqContext *context,
                              SourceIntroCallback callback,void *user,SourceIntroWaitOutput *output);
/* Original0F21..0F29 polling only, returning at prefetched0F2B:RET. Supports
 * mode4/192 with262/313 lines and unlatched VCounter. Each IN samples after
 * its11T; all branches keep their original instruction/IRQ boundaries. */
u8 source_intro_vcounter_poll(SourceClock *clock,SourceIrqContext *context,SourceIntroWaitOutput *output);
/* Original0F1E..0F2B, including CALL0F09 and its callback, poll and finalRET.
 * Does not continue polling after the callback's source skip branch. */
u8 source_intro_wait_window(SourceClock *clock,SourceIrqContext *context,
                            SourceIntroCallback callback,void *user,SourceIntroWaitOutput *output);
#endif
