#include "source_intro_map.h"
#include "source_room_memory.h"
#define S(t,m) do {if(!source_clock_plain(clock,t,m,source_irq_interrupt,context)) return 0;} while(0)
#define GET(a) source_room_get(context,(u16)((a)-0xc000))
#define PUT(a,v) source_room_put(context,(u16)((a)-0xc000),(u8)(v))
#define ROM(a,v) do {if((a)<0x8000 || (a)>0xbfff) return 0;(v)=map_bank[(a)-0x8000];} while(0)
static u8 valid(SourceClock *clock,SourceIrqContext *context,SourceIntroMapDecode *output)
{return clock && context && context->ram && context->audio && context->full_ram && output;}
u8 source_intro_map_decode(SourceClock *clock,SourceIrqContext *context,const u8 *map_bank,u16 address,
                           u16 destination,SourceIntroMapDecode *output)
{
    u16 cursor=address,scratch=0xd100,n,count,plane,write,read;u8 command,value,literal,carry;
    if(!valid(clock,context,output) || !map_bank || destination<0xc900 || destination>=0xd000) return 0;
    output->scratch_bytes=output->decoded_bytes=0;output->source_end=output->destination_end=0;
    S(11,1);S(10,1);
    for(;;)
    {
        S(7,1);ROM(cursor,command);S(6,1);cursor++;S(4,1);S(command?7:12,1);
        if(!command) break;
        S(10,1);literal=command&128;count=command&127;if(!count) count=256;
        if(literal) {S(7,1);S(4,1);}
        else {S(4,1);S(7,1);ROM(cursor,value);}
        for(n=0;n<count;n++)
        {
            if(literal) {S(7,1);ROM(cursor,value);}
            if(scratch>=0xd600) return 0;
            S(7,1);PUT(scratch,value);S(6,1);scratch++;
            if(literal) {S(6,1);cursor++;}
            else {S(4,1);value++;}
            S(n+1<count?13:8,1);
        }
        if(!literal) {S(6,1);cursor++;}
        S(12,1);
    }
    output->source_end=cursor;output->scratch_bytes=scratch-0xd100;
    S(10,1);S(11,1);S(10,1);S(17,1);S(7,1);S(4,1);read=0xd100;
    for(plane=0;plane<2;plane++)
    {
        write=destination+plane;S(11,1);S(11,1);
        for(;;)
        {
            if(read>=scratch) return 0;
            S(7,1);command=GET(read);S(4,1);S(command?7:12,1);
            if(!command) break;
            S(10,1);literal=command&128;count=command&127;if(!count) count=256;
            if(literal) {S(7,1);S(4,1);}
            else {S(4,1);S(6,1);read++;if(read>=scratch) return 0;}
            for(n=0;n<count;n++)
            {
                if(literal) {S(6,1);read++;if(read>=scratch) return 0;S(7,1);value=GET(read);}
                if(!literal) {S(7,1);value=GET(read);}
                if(write<0xc900 || write>=0xd000) return 0;
                S(7,1);PUT(write,value);output->decoded_bytes++;
                S(4,1);S(4,1);carry=(write&255)>=254;S(4,1);S(carry?7:12,1);
                if(carry) S(4,1);
                write+=2;S(n+1<count?13:8,1);
            }
            S(6,1);read++;S(12,1);
        }
        S(10,1);S(10,1);S(6,1);S(6,1);read++;S(plane?8:13,1);
    }
    output->destination_end=destination+2;
    S(10,1);S(10,1);S(10,1);return source_clock_checkpoint(clock,source_irq_interrupt,context);
}
u8 source_intro_map_place(SourceClock *clock,SourceIrqContext *context,u16 source,
                          u16 destination,u8 width,u8 height,SourceIntroMapDecode *output)
{
    u16 row,n,base=destination,read=source;u8 value,carry;
    if(!valid(clock,context,output) || !width || width>64 || !height) return 0;
    output->scratch_bytes=output->decoded_bytes=0;output->source_end=output->destination_end=0;
    for(row=0;row<height;row++)
    {
        S(11,1);S(11,1);S(4,1);
        for(n=0;n<width;n++)
        {
            if(read<0xc900 || read>=0xd000 || (u32)base+n<0xd600 || (u32)base+n>=0xd900) return 0;
            S(16,2);value=GET(read);PUT(base+n,value);read++;output->decoded_bytes++;
            S(n+1<width?13:8,1);
        }
        S(10,1);S(10,1);S(7,1);S(4,1);carry=(base&255)>=192;S(4,1);S(carry?7:12,1);
        if(carry) S(4,1);
        base+=64;S(4,1);S(row+1<height?12:7,1);
    }
    output->source_end=read;output->destination_end=base;
    S(10,1);return source_clock_checkpoint(clock,source_irq_interrupt,context);
}
