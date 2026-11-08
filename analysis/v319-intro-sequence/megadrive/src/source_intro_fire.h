#ifndef GAW_SOURCE_INTRO_FIRE_H
#define GAW_SOURCE_INTRO_FIRE_H
#include "source_intro_wait.h"
/* Original F37..F4E followed by bank5 BDFF..BE12. Compatible with
 * SourceIntroCallback: user points to the18 original palette bytes BE13.
 * Requires full_ram for DCE2,DCA1..DCA3 and the saved mapper byte FFFF.
 * Native semantic writes only; does not upload palette or change hardware.
 * Includes target RET. Failure leaves diagnostic partial state. */
u8 source_intro_fire_callback(SourceClock *clock,SourceIrqContext *context,void *user);
#endif
