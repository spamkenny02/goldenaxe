#include "source_title_wait.h"

typedef struct {SourceClock *clock;SourceIrqContext *context;u32 hint;} TitleWait;

static u8 execute(TitleWait *wait,u16 tstates,u8 fetches,u8 effect)
{
    SourceClock *clock=wait->clock;
    if(clock->elapsed>=wait->hint && clock->iff && !clock->blocked)
    {
        /* IM1 accept13T; 0038..0280 prefix67T; callback0280..0292
         * 611T, including33 DEC/JR iterations. Total691T,84 opcode
         * fetches. This interrupt ends well before VINT at line193.
         * Reject an unexpected late/nested case rather than coalescing it.
         */
        if(clock->pending || clock->until_vint<=691UL*15 || clock->first) return 0;
        if(!source_clock_execute(clock,691,84,SOURCE_CLOCK_NONE,source_irq_interrupt,wait->context)) return 0;
        clock->foreground_tstates-=691;clock->foreground_m1-=84;
        clock->irq_tstates+=691;clock->irq_m1+=84;clock->irq_count++;
        wait->hint+=clock->period;
    }
    return source_clock_execute(clock,tstates,fetches,effect,source_irq_interrupt,wait->context);
}

u8 source_title_wait(SourceClock *clock,SourceIrqContext *context,SourceWaitOutput *output)
{
    static const u8 prefix[]={11,11,11,11,4,4,11,11,11,11,15,15,13,11,7,13,4};
    TitleWait wait;u16 n,guard,batch;u8 value=0;u32 hint=187UL*3420,available;
    output->taken=output->error=0;
    if(clock->period!=(u32)context->input.lines*3420 ||
       context->ram[0x2c]!=0x80 || context->ram[0x2d]!=2 ||
       !(context->ram[0x10]&16)) goto reject;
    wait.clock=clock;wait.context=context;
    wait.hint=clock->elapsed+(clock->raster<hint?hint-clock->raster:clock->period-(clock->raster-hint));
    for(n=0;n<17;n++)
    {
        if(!execute(&wait,prefix[n],(n==10 || n==11)?2:1,
                    n==16?SOURCE_CLOCK_EI:SOURCE_CLOCK_NONE)) goto reject;
        if(n==14) value=1;
        if(n==15) context->ram[0x2e]=value;
    }
    for(guard=0;guard<8192;guard++)
    {
        /* Batch only complete stable polls before BOTH interrupt dates.
         * source_clock_repeat also checks EI delay and pending VINT.
         */
        if(context->ram[0x2e] && clock->elapsed<wait.hint)
        {
            available=(wait.hint-clock->elapsed)/(29UL*15);
            if(available>(u32)(8192-guard)) available=8192-guard;
            if(available)
            {
                batch=source_clock_repeat(clock,29,3,(u16)available);
                if(batch) {output->taken+=batch;guard+=batch-1;continue;}
            }
        }
        if(!execute(&wait,13,1,SOURCE_CLOCK_NONE)) goto reject;
        value=context->ram[0x2e];
        if(!execute(&wait,4,1,SOURCE_CLOCK_NONE)) goto reject;
        if(!execute(&wait,value?12:7,1,SOURCE_CLOCK_NONE)) goto reject;
        if(value) output->taken++;
        else return source_clock_checkpoint(clock,source_irq_interrupt,context);
    }
reject:
    output->error=1;return 0;
}

u8 source_title_logo_first_byte(const SourceClock *clock,u32 *raster)
{
    /* BB3 restore149T; 16C3 input check31T (no new action button);
     * 164A..038E setup131T, including the RST28 DI/EI address write.
     * This predicts the first OUTI instruction entry, not its I/O edge.
     */
    u32 delta=311UL*15;
    if(!raster || !clock || clock->pending || clock->until_vint<=delta) return 0;
    *raster=clock->raster+delta;
    if(*raster>=clock->period) *raster-=clock->period;
    return 1;
}
