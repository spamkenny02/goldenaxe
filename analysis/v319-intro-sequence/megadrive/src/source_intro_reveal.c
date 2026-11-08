#include "source_intro_reveal.h"
#define S(t,m) do {if(!source_clock_plain(clock,t,m,source_irq_interrupt,context)) return 0;} while(0)
#define EFFECT(e) do {if(!source_clock_execute(clock,4,1,e,source_irq_interrupt,context)) return 0;} while(0)
#define OUT(p,v) do {S(12,2);if(sink && !sink(user,clock->elapsed,clock->raster,p,(u8)(v))) return 0;} while(0)
u8 source_intro_reveal_pass(SourceClock *clock,SourceIrqContext *context,
                            SourceIntroRevealPass *state,SourceIntroRevealSink sink,void *user)
{
    u8 high;u16 guard;
    if(!clock || !context || !context->ram || !context->audio || !state ||
       state->step!=4 || state->address<0x4003 || state->address>=0x6400 ||
       (state->address&3)!=3) return 0;
    state->writes=0;
    for(guard=0;guard<2304;guard++)
    {
        u32 elapsed=clock->elapsed,raster=clock->raster;
        /* The paired DI/EI delay expires within this100T/18M1 loop.
         * Only batch when no VINT or existing IRQ/EI boundary can intervene. */
        if(source_clock_repeat(clock,100,18,1))
        {
            u16 address=state->address;
            state->address+=state->step;
            state->value=(state->value>>2)|(state->value<<6);
            if(sink)
            {
                static const u16 offsets[3]={300,480,1245};
                u8 values[3]={(u8)address,(u8)(address>>8),state->value};
                for(u16 n=0;n<3;n++)
                {
                    u32 sample=raster+offsets[n];
                    if(sample>=clock->period) sample-=clock->period;
                    if(!sink(user,elapsed+offsets[n],sample,n==2?0xbe:0xbf,values[n])) return 0;
                }
            }
            state->writes++;
            if((state->address>>8)==0x64) return source_clock_checkpoint(clock,source_irq_interrupt,context);
            continue;
        }
        S(4,1);EFFECT(SOURCE_CLOCK_DI);
        OUT(0xbf,state->address);OUT(0xbf,state->address>>8);
        EFFECT(SOURCE_CLOCK_EI);S(11,1);state->address+=state->step;
        S(4,1);high=state->address>>8;S(4,1);
        S(8,2);state->value=(state->value>>1)|(state->value<<7);
        S(8,2);state->value=(state->value>>1)|(state->value<<7);
        OUT(0xbe,state->value);state->writes++;
        S(7,1);S(10,1);
        if(high==0x64) return source_clock_checkpoint(clock,source_irq_interrupt,context);
    }
    return 0;
}

u8 source_intro_reveal_sequence(SourceClock *clock,SourceIrqContext *context,u8 mask,
                                SourceIntroCallback callback,void *callback_user,
                                SourceIntroRevealSink sink,void *sink_user,
                                SourceIntroRevealSequenceOutput *output)
{
    SourceIntroWaitOutput wait;u8 carry;u16 guard;
    if(!clock || !context || !context->ram || !context->audio || !output) return 0;
    output->passes=output->writes=0;output->skip=0;output->mask=mask;
    output->last.address=output->last.step=output->last.writes=0;output->last.value=0;
    for(guard=0;guard<9;guard++)
    {
        S(4,1);S(10,1);output->last.address=0x4003;
        S(10,1);output->last.step=4;S(7,1);S(4,1);
        S(4,1);output->last.value=output->mask;
        S(8,2);output->last.value=(output->last.value<<1)|(output->last.value>>7);
        S(8,2);output->last.value=(output->last.value<<1)|(output->last.value>>7);
        S(17,1);
        if(!source_intro_wait_window(clock,context,callback,callback_user,&wait)) return 0;
        if(wait.skip) {output->skip=1;return 1;}
        if(!source_intro_reveal_pass(clock,context,&output->last,sink,sink_user)) return 0;
        output->passes++;output->writes+=output->last.writes;
        S(8,2);carry=output->mask&1;output->mask>>=1;
        S(carry?12:7,1);
        if(!carry) return source_clock_checkpoint(clock,source_irq_interrupt,context);
    }
    return 0;
}
