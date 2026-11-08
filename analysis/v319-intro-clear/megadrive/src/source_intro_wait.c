#include "source_intro_wait.h"
#define S(t) do {if(!source_clock_plain(clock,(t),1,source_irq_interrupt,context)) goto reject;} while(0)
static u8 valid(const SourceClock *clock,const SourceIrqContext *context,const SourceIntroWaitOutput *output)
{
    return clock && context && output && context->ram && context->audio &&
        (context->input.lines==262 || context->input.lines==313) &&
        clock->period==(u32)context->input.lines*3420;
}
static void clear(SourceIntroWaitOutput *output)
{
    output->polls=output->below=output->above=0;
    output->counter=output->skip=output->error=0;
}
static u8 counter(u32 raster,u16 lines)
{
    u16 line=(u16)(raster/3420),maximum=lines==313?242:218;
    return (u8)(line>maximum?line-lines:line);
}
/* Batch failed polls only while their IN samples stay in the same failed
 * range. source_clock_repeat additionally stops before a pending VINT and
 * rejects first-fetch/EI/DI contexts. No status/VDP/RAM side effects occur
 * inside these stable30T/3M1 or44T/5M1 loops. */
static u16 failed_window(SourceClock *clock,u16 lines,u16 remaining,SourceIntroWaitOutput *output)
{
    u32 sample=clock->raster+165,distance,step;u16 ticks,fetches,count;u8 value;
    if(sample>=clock->period) sample-=clock->period;
    value=counter(sample,lines);
    if(value>=112 && value<128) return 0;
    ticks=value<112?30:44;fetches=value<112?3:5;step=(u32)ticks*15;
    distance=value<112?112UL*3420-sample:clock->period-sample;
    count=(u16)((distance+step-1)/step);
    if(count>remaining) count=remaining;
    count=source_clock_repeat(clock,ticks,fetches,count);
    if(!count) return 0;
    output->polls+=count;
    if(value<112) output->below+=count;else output->above+=count;
    output->counter=counter(sample+(u32)(count-1)*step,lines);
    return count;
}
u8 source_intro_wait_callback(SourceClock *clock,SourceIrqContext *context,
                              SourceIntroCallback callback,void *user,SourceIntroWaitOutput *output)
{
    SourceWaitOutput wait;u8 pressed;
    if(!valid(clock,context,output)) return 0;
    clear(output);
    S(17); /* F09 CALL B95; complete wait includes the register/mapper RET. */
    if(!source_wait_complete(clock,context,&wait)) goto reject;
    S(11);S(11);S(11);S(17); /* PUSH BC/DE/HL; CALL F32. */
    S(16);S(4); /* LD HL,(DCEC); JP(HL). */
    if(!source_clock_checkpoint(clock,source_irq_interrupt,context)) goto reject;
    if(callback) {if(!callback(clock,context,user)) goto reject;}
    else S(10); /* F36 RET. */
    S(10);S(10);S(10); /* F12..F14 POP HL/DE/BC. */
    S(13);pressed=context->ram[0x21];S(7);pressed&=0x30;S(10);
    if(pressed) output->skip=1; /* JP NZ,D0B; there is no F1D RET. */
    else S(10);
    if(!source_clock_checkpoint(clock,source_irq_interrupt,context)) goto reject;
    return 1;
reject:
    output->error=1;return 0;
}
u8 source_intro_vcounter_poll(SourceClock *clock,SourceIrqContext *context,SourceIntroWaitOutput *output)
{
    u16 guard,batch;u8 value;
    if(!valid(clock,context,output)) return 0;
    clear(output);
    for(guard=0;guard<8192;guard++)
    {
        batch=failed_window(clock,context->input.lines,8192-guard,output);
        if(batch) {guard+=batch-1;continue;}
        S(11); /* IN A,(7E), sample at completed IN as on the source VDP. */
        value=counter(clock->raster,context->input.lines);
        output->polls++;output->counter=value;
        S(7); /* CP70. */
        if(value<112) {S(12);output->below++;continue;}
        S(7);S(7); /* JR C not taken; CP80. */
        if(value>=128) {S(12);output->above++;continue;}
        S(7); /* JR NC not taken: next opcode is F2B RET. */
        if(!source_clock_checkpoint(clock,source_irq_interrupt,context)) goto reject;
        return 1;
    }
reject:
    output->error=1;return 0;
}
u8 source_intro_wait_window(SourceClock *clock,SourceIrqContext *context,
                            SourceIntroCallback callback,void *user,SourceIntroWaitOutput *output)
{
    if(!valid(clock,context,output)) return 0;
    clear(output);
    S(17); /* F1E CALL F09. */
    if(!source_intro_wait_callback(clock,context,callback,user,output)) goto reject;
    if(output->skip) return 1;
    if(!source_intro_vcounter_poll(clock,context,output)) goto reject;
    S(10); /* F2B RET. */
    if(!source_clock_checkpoint(clock,source_irq_interrupt,context)) goto reject;
    return 1;
reject:
    output->error=1;return 0;
}
