#ifndef GAW_SOURCE_INTRO_MAP_H
#define GAW_SOURCE_INTRO_MAP_H
#include "source_intro_wait.h"
typedef struct {u16 source_end,destination_end,scratch_bytes,decoded_bytes;} SourceIntroMapDecode;
/* Original BD3/BFE including RET. ROM comes from the immutable currently mapped16KiB bank;
 * scratch D100..D5FF and destination C900..CFFF use live semantic aliases.
 * Valid intro streams only; invalid/capacity failure leaves partial state. */
u8 source_intro_map_decode(SourceClock *clock,SourceIrqContext *context,const u8 *map_bank,u16 address,
                           u16 destination,SourceIntroMapDecode *output);
/* Original7357 strided rows including RET, bounded intro RAM buffers.
 * width1..64, nonzero height; source C900..CFFF, writes D600..D8FF. */
u8 source_intro_map_place(SourceClock *clock,SourceIrqContext *context,u16 source,
                          u16 destination,u8 width,u8 height,SourceIntroMapDecode *output);
#endif
