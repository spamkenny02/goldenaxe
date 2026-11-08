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
    u16 cursor=address,scratch=0xd100,n,count,plane,write,read;u8 command,value=0,literal,carry;
    if(!valid(clock,context,output) || !map_bank || destination<0xc900 || destination>=0xd000) return 0;
    output->scratch_bytes=output->decoded_bytes=0;output->source_end=output->destination_end=0;
    S(11,1);S(10,1);
    for(;;)
    {
        /* A whole immutable command may commit at once only before VINT.
         * Commands crossing any IRQ/first/EI boundary use the detailed path. */
        if(cursor>=0x8000 && cursor<=0xbfff && (command=map_bank[cursor-0x8000])!=0)
        {
            u16 amount=command&127,packed,ticks,fetches;u8 repeated=!(command&128);
            if(!amount) amount=256;
            packed=1+(repeated?1:amount);ticks=repeated?58+amount*30:52+amount*39;fetches=repeated?9+amount*4:8+amount*5;
            if((u32)cursor+packed<=0xc000 && (u32)scratch+amount<=0xd600 && source_clock_block(clock,ticks,fetches))
            {
                if(repeated) {u8 byte=map_bank[cursor+1-0x8000];for(u16 k=0;k<amount;k++) context->full_ram[scratch-0xc000+k]=byte++;}
                else __builtin_memcpy(context->full_ram+scratch-0xc000,map_bank+cursor+1-0x8000,amount);
                cursor+=packed;scratch+=amount;continue;
            }
        }
        S(7,1);ROM(cursor,command);S(6,1);cursor++;S(4,1);S(command?7:12,1);
        if(!command) break;
        S(10,1);literal=command&128;count=command&127;if(!count) count=256;
        if(literal) {S(7,1);S(4,1);}
        else {S(4,1);S(7,1);ROM(cursor,value);}
        for(n=0;n<count;n++)
        {
            u16 limit=count-n-1,batch;
            if(limit && (u32)scratch+limit<=0xd600 && (!literal || (cursor>=0x8000 && (u32)cursor+limit<=0xc000)))
            {
                batch=source_clock_repeat(clock,literal?39:30,literal?5:4,limit);
                if(batch)
                {
                    if(literal) {__builtin_memcpy(context->full_ram+scratch-0xc000,map_bank+cursor-0x8000,batch);cursor+=batch;}
                    else for(u16 k=0;k<batch;k++) context->full_ram[scratch-0xc000+k]=value++;
                    scratch+=batch;n+=batch-1;continue;
                }
            }
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
            if(read<scratch && (command=GET(read))!=0 && write>=0xc900 && write<0xd000)
            {
                u16 amount=command&127,packed,carries,ticks,fetches;u8 repeated=!(command&128);
                if(!amount) amount=256;
                packed=1+(repeated?1:amount);carries=((write&255)+amount*2)>>8;
                ticks=(repeated?51+amount*51:52+amount*57)-carries;
                fetches=(repeated?8+amount*7:8+amount*8)+carries;
                if((u32)read+packed<=scratch && (u32)write+(u32)(amount-1)*2<0xd000 && source_clock_block(clock,ticks,fetches))
                {
                    u8 *destination_bytes=context->full_ram+write-0xc000;
                    const u8 *source_bytes=context->full_ram+read+1-0xc000;
                    if(repeated) {u8 byte=*source_bytes;for(u16 k=0;k<amount;k++) destination_bytes[k*2]=byte;}
                    else for(u16 k=0;k<amount;k++) destination_bytes[k*2]=source_bytes[k];
                    read+=packed;write+=amount*2;output->decoded_bytes+=amount;continue;
                }
            }
            if(read>=scratch) return 0;
            S(7,1);command=GET(read);S(4,1);S(command?7:12,1);
            if(!command) break;
            S(10,1);literal=command&128;count=command&127;if(!count) count=256;
            if(literal) {S(7,1);S(4,1);}
            else {S(4,1);S(6,1);read++;if(read>=scratch) return 0;}
            for(n=0;n<count;n++)
            {
                u16 limit=count-n-1,window=(255-(write&255))/2,batch;
                if(window>limit) window=limit;
                if(write>=0xc900 && write<0xd000 && window &&
                   (u32)write+(u32)(window-1)*2<0xd000 && (!literal || (u32)read+window<scratch))
                {
                    /* Nonterminal DJNZ and noncarry address updates only.
                     * All scratch data is stable until the next IRQ boundary. */
                    batch=source_clock_repeat(clock,literal?57:51,literal?8:7,window);
                    if(batch)
                    {
                        if(!literal) value=GET(read);
                        for(u16 k=0;k<batch;k++)
                        {if(literal) {read++;value=GET(read);}PUT(write,value);write+=2;}
                        output->decoded_bytes+=batch;n+=batch-1;continue;
                    }
                }
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
            u16 limit=width-n-1,batch;
            if(limit && read>=0xc900 && (u32)read+limit<=0xd000 &&
               (u32)base+n>=0xd600 && (u32)base+n+limit<=0xd900)
            {
                batch=source_clock_repeat(clock,29,3,limit);
                if(batch)
                {
                    __builtin_memcpy(context->full_ram+base+n-0xc000,context->full_ram+read-0xc000,batch);
                    read+=batch;output->decoded_bytes+=batch;n+=batch-1;continue;
                }
            }
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
