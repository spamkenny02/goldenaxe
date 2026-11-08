#include "source_intro_video.h"
#include "source_room_memory.h"
#define S(t,m) do {if(!source_clock_plain(clock,t,m,source_irq_interrupt,context)) return 0;} while(0)
#define EFFECT(e) do {if(!source_clock_execute(clock,4,1,e,source_irq_interrupt,context)) return 0;} while(0)
#define EMIT(p,v) do {if(sink && !sink(sink_user,clock->elapsed,clock->raster,p,(u8)(v))) return 0;} while(0)
u8 source_intro_map_transfer(SourceClock *clock,SourceIrqContext *context,
                             SourceIntroCallback callback,void *callback_user,
                             SourceIntroRevealSink sink,SourceIntroVideoRunSink run_sink,void *sink_user,SourceIntroMapOutput *output)
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
            u32 elapsed=clock->elapsed,raster=clock->raster;
            u16 batch=source_clock_repeat(clock,32,4,255-n);
            if(batch)
            {
                const u8 *bytes=context->full_ram+0x1600+chunk*256+n;
                if(run_sink)
                {
                    SourceIntroVideoRun run={elapsed,raster,clock->period,bytes,0x7800+chunk*256+n,batch,SOURCE_INTRO_VIDEO_TRANSFER};
                    if(!run_sink(sink_user,&run)) return 0;
                }
                else if(sink) for(u16 k=0;k<batch;k++)
                {
                    u32 sample=raster+240;if(sample>=clock->period) sample-=clock->period;
                    if(!sink(sink_user,elapsed+240,sample,0xbe,bytes[k])) return 0;
                    elapsed+=480;raster+=480;if(raster>=clock->period) raster-=clock->period;
                }
                output->writes+=batch;n+=batch-1;continue;
            }
            S(16,2);value=source_room_get(context,0x1600+chunk*256+n);EMIT(0xbe,value);output->writes++;
            S(4,1);S(n==255?7:12,1);
        }
        S(4,1);S(chunk==2?7:12,1);
    }
    S(10,1); /* 396:RET, directly followed by F09, not an EFA RET. */
    if(!source_intro_wait_callback(clock,context,callback,callback_user,&wait)) return 0;
    output->skip=wait.skip;return 1;
}

/* LDIR aliasing is forward, not memcpy/memmove: D600 -> D602 repeats words. */
static u8 copy_forward(SourceClock *clock,SourceIrqContext *context,u16 source,u16 destination,u16 count)
{
    while(count)
    {
        u16 batch=source_clock_repeat(clock,21,2,count-1);
        if(!batch) {S(count==1?16:21,2);batch=1;}
        for(u16 n=0;n<batch;n++)
            source_room_put(context,destination+n,source_room_get(context,source+n));
        source+=batch;destination+=batch;count-=batch;
    }
    return 1;
}
u8 source_intro_map_prepare(SourceClock *clock,SourceIrqContext *context,u16 palette_address,
                            SourceIntroCallback callback,void *callback_user,
                            SourceIntroRevealSink sink,SourceIntroVideoRunSink run_sink,void *sink_user,SourceIntroMapOutput *output)
{
    u16 n;
    if(!clock || !context || !context->ram || !context->audio || !context->full_ram ||
       !context->bank6 || !output || palette_address<0x8000 || palette_address>0xbffc) return 0;
    output->writes=output->palette_end=0;output->skip=0;
    S(11,1);S(10,1);S(16,1);
    source_room_put(context,0x1600,0xfa);source_room_put(context,0x1601,9);
    S(10,1);S(10,1);S(10,1);
    if(!copy_forward(clock,context,0x1600,0x1602,766)) return 0;
    S(17,1);
    if(!source_intro_map_transfer(clock,context,callback,callback_user,sink,run_sink,sink_user,output)) return 0;
    if(output->skip) return 1;
    S(10,1);S(10,1);S(10,1);S(7,1);source_room_put(context,0x1ca0,0);
    if(!copy_forward(clock,context,0x1ca0,0x1ca1,15)) return 0;
    S(10,1);S(7,1);S(13,1);source_room_put(context,0x1fff,6);
    S(10,1);S(7,1);
    for(n=0;n<4;n++)
    {S(n==3?16:21,2);source_room_put(context,0x1ca0+n,context->bank6[palette_address-0x8000+n]);}
    output->palette_end=palette_address+4;
    S(10,1);return source_clock_checkpoint(clock,source_irq_interrupt,context);
}

u8 source_intro_plane_clear(SourceClock *clock,SourceIrqContext *context,
                            SourceIntroRevealSink sink,SourceIntroVideoRunSink run_sink,void *sink_user,u16 *writes)
{
    u16 address=0x4003;
    if(!clock || !context || !context->ram || !context->audio || !writes) return 0;
    *writes=0;S(11,1);S(10,1);
    while(address<0x6400)
    {
        u16 remaining=(0x6403-address)/4,rows;
        u32 elapsed=clock->elapsed,raster=clock->raster;
        /* All intermediate branches are taken; the last loop is five T
         * shorter. Paired DI/EI has expired before each loop boundary. */
        rows=source_clock_repeat(clock,remaining==1?119:124,17,remaining==1?1:remaining-1);
        if(rows)
        {
            if(run_sink)
            {
                SourceIntroVideoRun run={elapsed,raster,clock->period,0,address,rows,SOURCE_INTRO_VIDEO_CLEAR};
                if(!run_sink(sink_user,&run)) return 0;
                address+=rows*4;(*writes)+=rows;continue;
            }
            for(u16 row=0;row<rows;row++)
            {
                if(sink)
                {
                    static const u16 offsets[3]={450,675,1515};
                    u8 values[3]={(u8)address,(u8)(address>>8),255};
                    for(u16 n=0;n<3;n++)
                    {
                        u32 offset=offsets[n],sample=raster+offset;
                        if(sample>=clock->period) sample-=clock->period;
                        if(!sink(sink_user,elapsed+offset,sample,n==2?0xbe:0xbf,values[n])) return 0;
                    }
                }
                address+=4;(*writes)++;elapsed+=1860;raster+=1860;
                if(raster>=clock->period) raster-=clock->period;
            }
            continue;
        }
        S(11,1);EFFECT(SOURCE_CLOCK_DI);S(4,1);S(11,1);EMIT(0xbf,address);
        S(4,1);S(11,1);EMIT(0xbf,address>>8);EFFECT(SOURCE_CLOCK_EI);S(10,1);
        S(6,1);S(6,1);S(6,1);S(6,1);address+=4;
        S(7,1);S(11,1);EMIT(0xbe,255);(*writes)++;
        S(4,1);S(7,1);S(address<0x6400?12:7,1);
    }
    S(10,1);S(10,1);return source_clock_checkpoint(clock,source_irq_interrupt,context);
}
