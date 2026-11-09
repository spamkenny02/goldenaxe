#ifndef GAW_SOURCE_TITLE_WAIT_H
#define GAW_SOURCE_TITLE_WAIT_H
#include "source_wait.h"

/* Timing-only title B95->BB3 variant for SMS mode4/192, HINT at line187,
 * callback0280. No physical video writes. Caller supplies the current clock,
 * IRQ/audio state and reader DE. The ordinary source_wait remains unchanged.
 * This module is not selected by the published game.
 */
u8 source_title_wait(SourceClock *clock,SourceIrqContext *context,SourceWaitOutput *output);
/* From successful BB3 exit, with no newly pressed title action button:
 * predict the first038E OUTI entry of a logo row. Does not advance state.
 * Reject if an intervening VINT makes the straight-line continuation invalid.
 */
u8 source_title_logo_first_byte(const SourceClock *clock,u32 *raster);
#endif
