#ifndef GAW_SOURCE_PATTERN_VIDEO_H
#define GAW_SOURCE_PATTERN_VIDEO_H
#include <types.h>
/* Stable before-IRQ byte sequence,starting immediately before RST28.
 * BF low/high at30/45T,BE at77T. Byte stride135T literal/134T repeat,
 * minus1T at address low>=FC,minus5T only for a terminal final byte.
 * Data pointer is borrowed immutable ROM,valid throughout the sink call.
 * Caller retains the exact times for every output; no averaged cadence. */
typedef struct {
 u32 elapsed,raster,period;
 const u8 *bytes;
 u16 address,count;
 u8 literal,terminal;
} SourcePatternVideoRun;
typedef u8 (*SourcePatternVideoRunSink)(void *user,const SourcePatternVideoRun *run);
#endif
