#include "source_magic_rope.h"

void source_magic_rope_try(u8 direction,u8 graphics_class,u8 owned,u8 x,u8 y,u8 *cells,u8 *work)
{
    u8 alignment=((x&8)>>3)|((y&8)>>2),index,count;
    if((x|y)&7) alignment|=128;
    if(graphics_class || !owned || direction>1) return;
    if(!direction)
    {
        if(alignment!=3) return;
        index=((u8)(y-16)&240)|(x>>4);
        if(cells[index]!=2) return;
        cells[index]=0x6d;count=1;
        while(index>=16)
        {
            index-=16;
            if(cells[index]!=12) break;
            cells[index]=0x6c;count++;
        }
        work[0]=3;work[2]=y-16;
    }
    else
    {
        if(alignment!=1) return;
        index=(y&240)|(x>>4);
        if(cells[index]!=12) return;
        count=0;
        do
        {
            u8 old=cells[index];
            cells[index]=0x6c;count++;
            if(old==2) { cells[index]++;break; }
            index+=16;
        } while(index<0xa0);
        work[0]=4;work[2]=y;
    }
    work[1]=count<<1;work[3]=x-8;
}

u8 source_magic_rope_tick(const u8 *cells,const u8 *metatiles,u8 *work,u16 *offset,u8 *row)
{
    u8 x=work[3],y=work[2],cell,n,rotated;
    u16 source;
    if(work[0]!=3 && work[0]!=4) return 0;
    rotated=(x>>2)|(x<<6);
    *offset=((u16)y*8&0xff00)|((u8)(y*8)|rotated);
    cell=cells[(y&240)|(x>>4)];
    source=(u16)cell*8+((y&8)>>1);
    for(n=0;n<4;n++) row[n]=metatiles[source+n];
    work[2]+=work[0]==3?-8:8;
    if(!--work[1]) work[0]=0;
    return 1;
}

void source_magic_rope_arrive(u8 room_high,u8 old_terrain,u8 direction,u8 x,u8 *cells)
{
    s16 index;
    if(room_high || old_terrain!=5) return;
    if(!direction)
    {
        index=144+(x>>4);
        while(index>=0 && cells[index]==12) { cells[index]=0x6c;index-=16; }
    }
    else
    {
        index=x>>4;
        while(index<256 && cells[index]==12) { cells[index]=0x6c;index+=16; }
        if(index<256) cells[index]=0x6d;
    }
}
