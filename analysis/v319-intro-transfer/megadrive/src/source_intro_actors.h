#ifndef GAW_SOURCE_INTRO_ACTORS_H
#define GAW_SOURCE_INTRO_ACTORS_H
#include "source_intro_wait.h"
typedef struct {const u8 *low,*bank5;} SourceIntroActorData;
/* SourceIntroCallback implementations for1055 (scene2) and104A (scene3).
 * Require live full_ram plus compact IRQ/audio aliases. low is the original
 * immutable0000..7FFF,bank5 is its16KiB palette bank. Includes target RET.
 * All actor, SAT, palette, counter and mapper writes are semantic RAM only.
 * Invalid descriptor/capacity or IRQ failure is fatal/partial, never retry. */
u8 source_intro_actors_second(SourceClock *clock,SourceIrqContext *context,void *user);
u8 source_intro_actors_third(SourceClock *clock,SourceIrqContext *context,void *user);
/* F54 starts with the caller's HL template; F51 additionally loads F95.
 * Includes final RET. Clears all 768 actor bytes at source LDIR boundaries. */
u8 source_intro_actors_initialize(SourceClock *clock,SourceIrqContext *context,
                                  const SourceIntroActorData *data,u16 template_address,u8 entry_f51);
#endif
