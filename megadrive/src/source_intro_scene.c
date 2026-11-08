#include "source_intro_scene.h"
#include "source_room_memory.h"
#include "source_intro_pattern_plans_generated.h"
#define S(t,m) do {if(!source_clock_plain(clock,t,m,source_irq_interrupt,context)) return 0;} while(0)
typedef struct {u8 *mirror;SourceIntroRevealSink sink;void *user;u16 command;u8 low,latch;SourceIntroVideoRunSink run;} SceneMirror;
static u8 scene_out(void *opaque,u32 elapsed,u32 raster,u8 port,u8 value)
{
    SceneMirror *state=opaque;
    if(port==0xbf)
    {
        if(!state->latch) {state->low=value;state->latch=1;}
        else {state->command=state->low|((u16)value<<8);state->latch=0;}
    }
    else if(port==0xbe)
    {
        if(state->latch || (state->command&0xc000)!=0x4000) return 0;
        state->mirror[state->command&0x3fff]=value;
        state->command=0x4000|((state->command+1)&0x3fff);
    }
    else return 0;
    return !state->sink || state->sink(state->user,elapsed,raster,port,value);
}
static u8 scene_run(void *opaque,const SourceIntroVideoRun *run)
{
    SceneMirror *state=opaque;u32 elapsed=run->elapsed,raster=run->raster;u16 address=run->address;
    if(state->latch || !run->count) return 0;
    if(run->kind==SOURCE_INTRO_VIDEO_CLEAR)
    {
        if(address<0x4003 || (u32)address+(u32)(run->count-1)*4>=0x6400) return 0;
        if(!state->sink || state->run)
        {
            for(u16 n=0;n<run->count;n++) state->mirror[(address&0x3fff)+n*4]=255;
            state->low=(u8)(address+(run->count-1)*4);
            state->command=address+(run->count-1)*4+1;
        }
    }
    else if(run->kind==SOURCE_INTRO_VIDEO_TRANSFER)
    {
        if(state->command!=address || !run->bytes || address<0x7800 || (u32)address+run->count>0x7b00) return 0;
        if(!state->sink || state->run)
        {
            __builtin_memcpy(state->mirror+(address&0x3fff),run->bytes,run->count);
            state->command+=run->count;
        }
    }
    else return 0;
    if(state->run) return state->run(state->user,run);
    if(!state->sink) return 1;
    for(u16 n=0;n<run->count;n++)
    {
        if(run->kind==SOURCE_INTRO_VIDEO_CLEAR)
        {
            static const u16 offsets[3]={450,675,1515};
            u8 values[3]={(u8)address,(u8)(address>>8),255};
            for(u16 k=0;k<3;k++)
            {
                u32 sample=raster+offsets[k];if(sample>=run->period) sample-=run->period;
                if(!scene_out(state,elapsed+offsets[k],sample,k==2?0xbe:0xbf,values[k])) return 0;
            }
            address+=4;elapsed+=1860;raster+=1860;
        }
        else
        {
            u32 sample=raster+240;if(sample>=run->period) sample-=run->period;
            if(!scene_out(state,elapsed+240,sample,0xbe,run->bytes[n])) return 0;
            elapsed+=480;raster+=480;
        }
        if(raster>=run->period) raster-=run->period;
    }
    return 1;
}
static u8 scene_load(SourceClock *clock,SourceIrqContext *context,u16 header,u16 target,
                           u8 *mirror,SourceIntroCallback callback,void *callback_user,
                           SourceIntroRevealSink sink,void *sink_user,SourcePatternPortSink pattern_sink,void *pattern_user,SourcePatternVideoRunSink pattern_run,
                           SourceIntroSceneOutput *output,SourceIntroVideoRunSink map_run)
{
    SourceIntroMapOutput map;SourceIntroMapDecode decode;const u8 *patterns;
    SceneMirror video={mirror,sink,sink_user,0,0,0,map_run};u16 writes;
    const SourcePatternPlan *plan=header==0x9d70?&gaw_intro_9d70_plan:header==0xa655?&gaw_intro_a655_plan:0;
    if(!clock || !context || !context->ram || !context->audio || !context->full_ram ||
       !context->bank6 || !mirror || !output || header<0x8000 || header>0xbffc) return 0;
    output->hl=output->de=output->bc=output->source_end=output->pattern_end=output->decoded_bytes=0;output->skip=0;
    S(20,2);source_room_put(context,0x1cec,target);source_room_put(context,0x1ced,target>>8);
    S(17,1);
    if(!source_intro_map_prepare(clock,context,header,callback,callback_user,scene_out,scene_run,&video,&map)) return 0;
    if(map.skip) {output->skip=1;return 1;}
    S(10,1);S(17,1);patterns=context->bank6+map.palette_end-0x8000;
    if(pattern_sink)
    {if(!source_pattern_decode_runs(clock,context,&patterns,mirror,0x4000,&output->pattern_end,plan,pattern_sink,pattern_run,pattern_user)) return 0;}
    else if(!source_pattern_decode_planned(clock,context,&patterns,mirror,0x4000,&output->pattern_end,plan)) return 0;
    if(patterns<context->bank6 || patterns>=context->bank6+16384) return 0;
    S(17,1);if(!source_intro_plane_clear(clock,context,scene_out,scene_run,&video,&writes)) return 0;
    S(10,1);S(17,1);
    if(!source_intro_map_decode(clock,context,context->bank6,0x8000+(u16)(patterns-context->bank6),0xc900,&decode)) return 0;
    output->source_end=decode.source_end;output->decoded_bytes=decode.decoded_bytes;
    S(10,1);S(10,1);S(10,1);S(17,1);
    if(!source_intro_map_place(clock,context,0xc900,0xd608,48,12,&decode)) return 0;
    S(17,1);if(!source_intro_map_transfer(clock,context,callback,callback_user,scene_out,scene_run,&video,&map)) return 0;
    output->skip=map.skip;
    if(!map.skip) {output->hl=0xd900;output->de=0x7800;output->bc=0x00be;}
    return 1;
}
u8 source_intro_scene_load(SourceClock *clock,SourceIrqContext *context,u16 header,u16 target,
 u8 *mirror,SourceIntroCallback callback,void *callback_user,
 SourceIntroRevealSink sink,void *sink_user,SourceIntroSceneOutput *output)
{return scene_load(clock,context,header,target,mirror,callback,callback_user,sink,sink_user,0,0,0,output,0);}
u8 source_intro_scene_load_ports(SourceClock *clock,SourceIrqContext *context,u16 header,u16 target,
 u8 *mirror,SourceIntroCallback callback,void *callback_user,
 SourceIntroRevealSink sink,void *sink_user,SourcePatternPortSink pattern_sink,void *pattern_user,
 SourceIntroSceneOutput *output)
{
 if(!pattern_sink) return 0;
 return scene_load(clock,context,header,target,mirror,callback,callback_user,sink,sink_user,pattern_sink,pattern_user,0,output,0);
}
u8 source_intro_scene_load_runs(SourceClock *clock,SourceIrqContext *context,u16 header,u16 target,
 u8 *mirror,SourceIntroCallback callback,void *callback_user,
 SourceIntroRevealSink sink,void *sink_user,SourcePatternPortSink pattern_sink,void *pattern_user,
 SourcePatternVideoRunSink pattern_run,SourceIntroSceneOutput *output)
{
 if(!pattern_sink || !pattern_run) return 0;
 return scene_load(clock,context,header,target,mirror,callback,callback_user,sink,sink_user,pattern_sink,pattern_user,pattern_run,output,0);
}
u8 source_intro_scene_load_video_runs(SourceClock *clock,SourceIrqContext *context,u16 header,u16 target,
 u8 *mirror,SourceIntroCallback callback,void *callback_user,
 SourceIntroRevealSink sink,void *sink_user,SourcePatternPortSink pattern_sink,void *pattern_user,
 SourcePatternVideoRunSink pattern_run,SourceIntroVideoRunSink map_run,SourceIntroSceneOutput *output)
{
 if(!pattern_sink || !pattern_run || !sink || !map_run) return 0;
 return scene_load(clock,context,header,target,mirror,callback,callback_user,sink,sink_user,pattern_sink,pattern_user,pattern_run,output,map_run);
}
