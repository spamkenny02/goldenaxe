#include "source_intro_actors.h"
#include "source_room_memory.h"
#define S(t,m) do {if(!source_clock_plain(clock,t,m,source_irq_interrupt,context)) return 0;} while(0)
#define GET(a) source_room_get(context,(u16)((a)-0xc000))
#define PUT(a,v) source_room_put(context,(u16)((a)-0xc000),(u8)(v))
#define READ(a,v) do {if((u32)(a)>=32768) return 0;(v)=data->low[(u16)(a)];} while(0)
static u16 word(SourceIrqContext *context,u16 address)
{return source_room_get(context,address-0xc000)|((u16)source_room_get(context,address+1-0xc000)<<8);}
static void putword(SourceIrqContext *context,u16 address,u16 value)
{source_room_put(context,address-0xc000,value);source_room_put(context,address+1-0xc000,value>>8);}
static u8 valid(SourceClock *clock,SourceIrqContext *context,const SourceIntroActorData *data)
{return clock && context && context->ram && context->audio && context->full_ram && data && data->low && data->bank5;}
/* RST08 includes the carry-dependent INC H. A retains the first table byte. */
static u8 lookup(SourceClock *clock,SourceIrqContext *context,const SourceIntroActorData *data,
                 u16 table,u8 offset,u16 *result,u8 *first)
{
    u16 sum=(table&255)+offset,address;u8 hi;
    S(11,1);S(4,1);S(4,1);S(sum<256?12:7,1);
    if(sum>=256) {S(4,1);table+=256;}
    address=(table&0xff00)|(sum&255);
    S(7,1);READ(address,*first);S(6,1);address++;
    S(7,1);READ(address,hi);S(4,1);*result=*first|((u16)hi<<8);S(10,1);
    return 1;
}
static u8 relative_frame(SourceClock *clock,SourceIrqContext *context,const SourceIntroActorData *data,
                         u16 actor,u16 frame)
{
    u16 cursor=frame,de,count,n;u8 a,value;
    S(7,1);READ(cursor,value);count=value;
    if(!count || count>64) return 0;
    S(6,1);cursor++;S(20,2);de=word(context,0xc024);
    if(de<0xdd40 || de+count>0xdd80) return 0;
    S(19,2);a=GET(actor+0x11);S(4,1);
    for(n=0;n<count;n++)
    {
        S(7,1);READ(cursor,value);a+=value;S(7,1);PUT(de,a);
        S(6,1);cursor++;S(6,1);de++;S(n+1<count?13:8,1);
    }
    S(7,1);S(7,1);PUT(de,208);S(20,2);putword(context,0xc024,de);
    S(20,2);de=word(context,0xc026);
    if(de<0xdd80 || de+count*2>0xde00) return 0;
    S(19,2);a=GET(actor+0x13);S(4,1);
    for(n=0;n<count;n++)
    {
        S(7,1);READ(cursor,value);a+=value;S(7,1);PUT(de,a);
        S(6,1);cursor++;S(6,1);de++;
        S(16,2);READ(cursor,value);PUT(de,value);cursor++;de++;
        S(n+1<count?13:8,1);
    }
    S(20,2);putword(context,0xc026,de);S(10,1);return 1;
}
static u8 actor_step(SourceClock *clock,SourceIrqContext *context,const SourceIntroActorData *data,
                     u16 actor,u8 state)
{
    u8 a,b,lo,hi,phase;u16 table,frame;
    S(7,1);S(state==2?12:7,1);
    if(state!=2)
    {
        S(13,1);a=GET(0xdce2);S(19,2);b=GET(actor+14);S(a!=b?11:5,1);
        if(a!=b) return 1;
        S(23,2);PUT(actor,GET(actor)+1);
    }
    S(19,2);a=GET(actor+11);S(19,2);lo=GET(actor+8);S(19,2);hi=GET(actor+9);
    table=lo|((u16)hi<<8);S(4,1);a*=2;
    if(!lookup(clock,context,data,table,a,&frame,&lo)) return 0;
    S(17,1);if(!relative_frame(clock,context,data,actor,frame)) return 0;
    S(13,1);phase=GET(0xc02f);S(7,1);phase&=3;S(phase?11:5,1);
    if(phase) return 1;
    S(23,2);PUT(actor+11,GET(actor+11)+1);
    S(19,2);a=GET(actor+12);S(19,2);b=GET(actor+11);S(a!=b?11:5,1);
    if(a!=b) return 1;
    S(23,2);PUT(actor,GET(actor)-1);S(19,2);PUT(actor+11,0);S(10,1);
    return 1;
}
static u8 actors(SourceClock *clock,SourceIrqContext *context,const SourceIntroActorData *data)
{
    u8 phase,a;u16 n,actor;
    S(13,1);phase=GET(0xc02f);S(7,1);phase&=3;S(phase?12:7,1);
    if(!phase) {S(13,1);a=GET(0xdce2);S(4,1);a++;S(13,1);PUT(0xdce2,a);}
    S(17,1); /* CALL A60. */
    S(10,1);S(16,1);putword(context,0xc024,0xdd40);
    S(10,1);S(16,1);putword(context,0xc026,0xdd80);
    S(7,1);S(13,1);PUT(0xffff,12);S(10,1);
    S(14,2);S(7,1);
    for(n=0,actor=0xc300;n<16;n++,actor+=48)
    {
        S(11,1);S(19,2);a=GET(actor);S(4,1);S(a?17:10,1);
        if(a && !actor_step(clock,context,data,actor,a)) return 0;
        S(10,1);S(15,2);S(10,1);S(n+1<16?13:8,1);
    }
    S(10,1);S(16,1);actor=word(context,0xc024);
    if(actor<0xdd40 || actor>0xdd80) return 0;
    S(10,1);PUT(actor,208);S(10,1);return 1;
}
static u8 lightning(SourceClock *clock,SourceIrqContext *context,const SourceIntroActorData *data)
{
    u16 cursor=0x3e57,destination=0xdca1,n,group;u8 a,value;
    S(10,1);S(13,1);a=GET(0xdd40);S(7,1);S(a==208?12:7,1);
    if(a!=208)
    {
        S(10,1);cursor=0x3e5d;S(13,1);a=GET(0xc02f);S(4,1);a=(a>>1)|(a<<7);
        S(7,1);a&=7;S(4,1);value=a;S(4,1);a*=2;S(4,1);a+=value;
        S(4,1);S(7,1);S(11,1);cursor+=a;
    }
    S(10,1);
    for(n=0;n<3;n++) {S(16,2);PUT(destination,data->bank5[cursor]);cursor++;destination++;}
    for(group=0;group<3;group++)
    {
        if(group<2) S(17,1);
        S(7,1);value=data->bank5[cursor];S(6,1);cursor++;S(7,1);
        for(n=0;n<4;n++) {S(7,1);PUT(destination,value);S(6,1);destination++;S(n<3?13:8,1);}
        S(10,1);
    }
    return 1;
}
u8 source_intro_actors_second(SourceClock *clock,SourceIrqContext *context,void *user)
{
    const SourceIntroActorData *data=(const SourceIntroActorData *)user;u8 a,first;u16 ignored;
    if(!valid(clock,context,data)) return 0;
    S(13,1);a=GET(0xc02f);S(7,1);a&=3;S(10,1);
    if(!lookup(clock,context,data,0x10bf,a,&ignored,&first)) return 0;
    S(13,1);PUT(0xdcb2,first);
    if(!actors(clock,context,data)) return 0;
    return source_clock_checkpoint(clock,source_irq_interrupt,context);
}
u8 source_intro_actors_third(SourceClock *clock,SourceIrqContext *context,void *user)
{
    const SourceIntroActorData *data=(const SourceIntroActorData *)user;
    if(!valid(clock,context,data)) return 0;
    S(17,1);if(!actors(clock,context,data)) return 0;
    S(7,1);S(13,1);PUT(0xffff,5);S(10,1);
    if(!lightning(clock,context,data)) return 0;
    return source_clock_checkpoint(clock,source_irq_interrupt,context);
}
