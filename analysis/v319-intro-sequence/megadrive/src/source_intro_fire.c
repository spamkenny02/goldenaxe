#include "source_intro_fire.h"
#include "source_room_memory.h"
#define S(t,m) do {if(!source_clock_plain(clock,t,m,source_irq_interrupt,context)) return 0;} while(0)
u8 source_intro_fire_callback(SourceClock *clock,SourceIrqContext *context,void *user)
{
    const u8 *colors=(const u8 *)user;u8 phase,value,index,n;
    if(!clock || !context || !context->ram || !context->audio || !context->full_ram || !colors) return 0;
    S(13,1);phase=context->ram[0x2f];S(7,1);phase&=7;
    if(phase) {S(11,1);return source_clock_checkpoint(clock,source_irq_interrupt,context);}
    S(5,1);S(7,1);S(13,1);source_room_put(context,0x1fff,5);
    S(13,1);value=source_room_get(context,0x1ce2);S(4,1);value++;
    S(7,1);
    if(value<6) S(12,1);
    else {S(7,1);S(4,1);value=0;}
    S(13,1);source_room_put(context,0x1ce2,value);S(10,1);
    /* BDFF uses L to retain the original index while forming3*A. */
    S(4,1);S(4,1);S(4,1);index=value*3;S(4,1);
    S(7,1);S(10,1);S(11,1);S(10,1);
    for(n=0;n<3;n++) {S(16,2);source_room_put(context,0x1ca1+n,colors[index+n]);}
    S(10,1);
    return source_clock_checkpoint(clock,source_irq_interrupt,context);
}
