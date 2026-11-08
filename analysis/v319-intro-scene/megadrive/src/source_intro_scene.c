#include "source_intro_scene.h"
#include "source_room_memory.h"
#define S(t,m) do {if(!source_clock_plain(clock,t,m,source_irq_interrupt,context)) return 0;} while(0)
typedef struct {u8 *mirror;SourceIntroRevealSink sink;void *user;u16 command;u8 low,latch;} SceneMirror;
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
u8 source_intro_scene_load(SourceClock *clock,SourceIrqContext *context,u16 header,u16 target,
                           u8 *mirror,SourceIntroCallback callback,void *callback_user,
                           SourceIntroRevealSink sink,void *sink_user,SourceIntroSceneOutput *output)
{
    SourceIntroMapOutput map;SourceIntroMapDecode decode;const u8 *patterns;
    SceneMirror video={mirror,sink,sink_user,0,0,0};u16 writes;
    if(!clock || !context || !context->ram || !context->audio || !context->full_ram ||
       !context->bank6 || !mirror || !output || header<0x8000 || header>0xbffc) return 0;
    output->hl=output->de=output->bc=output->source_end=output->pattern_end=output->decoded_bytes=0;output->skip=0;
    S(20,2);source_room_put(context,0x1cec,target);source_room_put(context,0x1ced,target>>8);
    S(17,1);
    if(!source_intro_map_prepare(clock,context,header,callback,callback_user,scene_out,&video,&map)) return 0;
    if(map.skip) {output->skip=1;return 1;}
    S(10,1);S(17,1);patterns=context->bank6+map.palette_end-0x8000;
    if(!source_pattern_decode(clock,context,&patterns,mirror,0x4000,&output->pattern_end)) return 0;
    if(patterns<context->bank6 || patterns>=context->bank6+16384) return 0;
    S(17,1);if(!source_intro_plane_clear(clock,context,scene_out,&video,&writes)) return 0;
    S(10,1);S(17,1);
    if(!source_intro_map_decode(clock,context,context->bank6,0x8000+(u16)(patterns-context->bank6),0xc900,&decode)) return 0;
    output->source_end=decode.source_end;output->decoded_bytes=decode.decoded_bytes;
    S(10,1);S(10,1);S(10,1);S(17,1);
    if(!source_intro_map_place(clock,context,0xc900,0xd608,48,12,&decode)) return 0;
    S(17,1);if(!source_intro_map_transfer(clock,context,callback,callback_user,scene_out,&video,&map)) return 0;
    output->skip=map.skip;
    if(!map.skip) {output->hl=0xd900;output->de=0x7800;output->bc=0x00be;}
    return 1;
}
