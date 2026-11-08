#include "source_intro_video.h"
#include "source_room_memory.h"
#define S(t,m) do {if(!source_clock_plain(clock,t,m,source_irq_interrupt,context)) return 0;} while(0)
#define EFFECT(e) do {if(!source_clock_execute(clock,4,1,e,source_irq_interrupt,context)) return 0;} while(0)
#define EMIT(p,v) do {if(sink && !sink(sink_user,clock->elapsed,clock->raster,p,(u8)(v))) return 0;} while(0)
u8 source_intro_map_transfer(SourceClock *clock,SourceIrqContext *context,
                             SourceIntroCallback callback,void *callback_user,
                             SourceIntroRevealSink sink,void *sink_user,SourceIntroMapOutput *output)
{
    SourceIntroWaitOutput wait;u16 n,chunk;u8 value;
    if(!clock || !context || !context->ram || !context->audio || !context->full_ram || !output) return 0;
    output->writes=output->palette_end=0;output->skip=0;
    S(17,1);if(!source_intro_wait_window(clock,context,callback,callback_user,&wait)) return 0;
    if(wait.skip) {output->skip=1;return 1;}
    S(10,1);S(10,1);S(10,1);S(17,1);
    S(11,1); /* 384:RST28, with DE=7800. */
    EFFECT(SOURCE_CLOCK_DI);S(4,1);S(11,1);EMIT(0xbf,0);
    S(4,1);S(11,1);EMIT(0xbf,0x78);EFFECT(SOURCE_CLOCK_EI);S(10,1);
    S(4,1);S(4,1);S(12,1);S(4,1);S(4,1);S(7,1);
    for(chunk=0;chunk<3;chunk++)
    {
        for(n=0;n<256;n++)
        {
            S(16,2);value=source_room_get(context,0x1600+chunk*256+n);EMIT(0xbe,value);output->writes++;
            S(4,1);S(n==255?7:12,1);
        }
        S(4,1);S(chunk==2?7:12,1);
    }
    S(10,1); /* 396:RET, directly followed by F09, not an EFA RET. */
    if(!source_intro_wait_callback(clock,context,callback,callback_user,&wait)) return 0;
    output->skip=wait.skip;return 1;
}

u8 source_intro_map_prepare(SourceClock *clock,SourceIrqContext *context,u16 palette_address,
                            SourceIntroCallback callback,void *callback_user,
                            SourceIntroRevealSink sink,void *sink_user,SourceIntroMapOutput *output)
{
    u16 n;
    if(!clock || !context || !context->ram || !context->audio || !context->full_ram ||
       !context->bank6 || !output || palette_address<0x8000 || palette_address>0xbffc) return 0;
    output->writes=output->palette_end=0;output->skip=0;
    S(11,1);S(10,1);S(16,1);
    source_room_put(context,0x1600,0xfa);source_room_put(context,0x1601,9);
    S(10,1);S(10,1);S(10,1);
    for(n=2;n<768;n++)
    {S(n==767?16:21,2);source_room_put(context,0x1600+n,source_room_get(context,0x15fe + n));}
    S(17,1);
    if(!source_intro_map_transfer(clock,context,callback,callback_user,sink,sink_user,output)) return 0;
    if(output->skip) return 1;
    S(10,1);S(10,1);S(10,1);S(7,1);source_room_put(context,0x1ca0,0);
    for(n=1;n<16;n++)
    {S(n==15?16:21,2);source_room_put(context,0x1ca0+n,source_room_get(context,0x1c9f+n));}
    S(10,1);S(7,1);S(13,1);source_room_put(context,0x1fff,6);
    S(10,1);S(7,1);
    for(n=0;n<4;n++)
    {S(n==3?16:21,2);source_room_put(context,0x1ca0+n,context->bank6[palette_address-0x8000+n]);}
    output->palette_end=palette_address+4;
    S(10,1);return source_clock_checkpoint(clock,source_irq_interrupt,context);
}
