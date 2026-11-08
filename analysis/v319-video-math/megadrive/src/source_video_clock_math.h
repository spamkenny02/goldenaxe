#ifndef GAW_SOURCE_VIDEO_CLOCK_MATH_H
#define GAW_SOURCE_VIDEO_CLOCK_MATH_H
#include <types.h>
/* raster<period,period<=313*3420. Common instruction deltas fit one frame;
 * retain generic reduction only for long stable foreground gaps. */
static inline u32 source_video_wrap(u32 raster,u32 delta,u32 period)
{
 if(delta>=period) delta%=period;
 raster+=delta;if(raster>=period) raster-=period;return raster;
}
/* All valid video raster quotients fit313, and the3420 divisor fits16bits.
 * Native DIVU returns remainder:quotient, avoiding libgcc32bit division. */
static inline u16 source_video_line(u32 raster)
{
#ifdef SGDK_GCC
 __asm__("divu.w %1,%0" : "+d"(raster) : "d"((u16)3420) : "cc");
 return (u16)raster;
#else
 return raster/3420;
#endif
}
static inline u16 source_video_phase(u32 raster)
{
#ifdef SGDK_GCC
 __asm__("divu.w %1,%0" : "+d"(raster) : "d"((u16)3420) : "cc");
 return raster>>16;
#else
 return raster%3420;
#endif
}
#endif
