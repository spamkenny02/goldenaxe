#include "source_intro_sprite_status.h"
typedef struct {s16 x,y;u16 tile;u8 rows;} IntroSprite;
static u8 opaque(const u8 *vram,u16 tile,u16 row)
{
    const u8 *data=vram+(tile<<5)+(row<<2);
    return data[0]|data[1]|data[2]|data[3];
}
u8 source_intro_sprite_flags(const u8 *vram,const u8 *registers,u8 *flags)
{
    IntroSprite sprites[64];u8 lines[192]={0};u16 total=0,mask,base,pattern_mask;
    if(!vram || !registers || !flags || !(registers[0]&4) || (registers[1]&3)) return 0;
    *flags=0;
    mask=((u16)~0x3f80^((u16)registers[5]<<7))|0x80;base=mask&0x3f00;
    pattern_mask=(((u16)~0x01c0^((u16)registers[6]<<6))|0xc0)&0x1ff;
    for(u16 index=0;index<64;index++)
    {
        u8 raw=vram[base+index],rows=0; s16 top;
        if(raw==208) break;
        top=(raw>208?(s16)raw-256:raw)+1;
        for(u16 row=0;row<8;row++)
        {
            s16 y=top+row;
            if(y>=0 && y<192)
            {
                if(lines[y]<8) rows|=1<<row;
                else if(y>0) *flags|=0x40;
                if(lines[y]<9) lines[y]++;
            }
        }
        if(!rows) continue;
        sprites[total].x=(s16)vram[base+((0x80+index*2)&mask)]-(registers[0]&8);
        sprites[total].y=top;sprites[total].rows=rows;
        sprites[total].tile=(vram[base+((0x81+index*2)&mask)]|0x100)&pattern_mask;total++;
    }
    if(!(registers[1]&0x40)) return 1;
    for(u16 first=0;first<total;first++) for(u16 second=first+1;second<total;second++)
    {
        const IntroSprite *a=sprites+first,*b=sprites+second;
        s16 left=a->x>b->x?a->x:b->x,right=a->x<b->x?a->x+8:b->x+8;
        s16 top=a->y>b->y?a->y:b->y,bottom=a->y<b->y?a->y+8:b->y+8;
        if(left<0) left=0;
        if(right>256) right=256;
        if(top<0) top=0;
        if(bottom>192) bottom=192;
        if(left>=right || top>=bottom) continue;
        for(s16 y=top;y<bottom;y++)
        {
            u16 ar=y-a->y,br=y-b->y;u8 am,bm;
            if(!(a->rows&(1<<ar)) || !(b->rows&(1<<br))) continue;
            am=opaque(vram,a->tile,ar);bm=opaque(vram,b->tile,br);
            for(s16 x=left;x<right;x++) if((am&(128>>(x-a->x))) && (bm&(128>>(x-b->x))))
            {*flags|=0x20;return 1;}
        }
    }
    return 1;
}

void source_intro_sprite_status_reset(SourceIntroSpriteStatus *state)
{__builtin_memset(state,0,sizeof(*state));state->collision_line=-1;}
u8 source_intro_sprite_parse(SourceIntroSpriteStatus *state,s16 line,const u8 *vram,const u8 *registers)
{
    u16 mask,base,count=0,slot=(line+1)&1;
    if(!state || !vram || !registers || !(registers[0]&4) || (registers[1]&3)) return 0;
    mask=((u16)~0x3f80^((u16)registers[5]<<7))|0x80;base=mask&0x3f00;
    for(u16 index=0;index<64;index++)
    {
        u8 raw=vram[base+index];s16 y;
        if(raw==208) break;
        y=line-(raw>208?(s16)raw-256:raw);
        if(y<0 || y>=8) continue;
        if(count==8) {if(line>=0 && line<192) state->pending_overflow=0x40;break;}
        state->objects[slot][count].x=vram[base+((0x80+index*2)&mask)];
        state->objects[slot][count].attribute=vram[base+((0x81+index*2)&mask)];
        state->objects[slot][count].row=y;count++;
    }
    state->count[slot]=count;return 1;
}
u8 source_intro_sprite_render(SourceIntroSpriteStatus *state,s16 line,const u8 *vram,const u8 *registers)
{
    u8 masks[8];s16 x[8];u16 count,slot,pattern_mask;
    if(!state || !vram || !registers || !(registers[0]&4) || (registers[1]&3)) return 0;
    state->flags|=state->pending_overflow;state->pending_overflow=0;
    if(!(registers[1]&0x40) || (state->flags&0x20)) return 1;
    slot=line&1;count=state->count[slot];
    pattern_mask=(((u16)~0x01c0^((u16)registers[6]<<6))|0xc0)&0x1ff;
    for(u16 n=0;n<count;n++)
    {
        SourceIntroCachedSprite *sprite=state->objects[slot]+n;
        x[n]=sprite->x-(registers[0]&8);
        masks[n]=opaque(vram,(sprite->attribute|0x100)&pattern_mask,sprite->row);
    }
    /* Source draw order: the first later sprite that overlaps any earlier
     * sprite latches the leftmost overlap for that sprite, not global X. */
    for(u16 second=1;second<count;second++)
    {
        s16 collision=256;
        for(u16 first=0;first<second;first++)
        {
            s16 delta=x[second]-x[first];u8 overlap;
            if(delta<=-8 || delta>=8) continue;
            overlap=masks[second]&(delta>=0?(u8)(masks[first]<<delta):(masks[first]>>(-delta)));
            for(u16 pixel=0;pixel<8;pixel++) if(overlap&(128>>pixel))
            {
                s16 at=x[second]+pixel;
                if(at>=0 && at<256 && at<collision) collision=at;
            }
        }
        if(collision<256)
        {state->flags|=0x20;state->collision_line=line;state->collision_hcounter=(collision+13)>>1;break;}
    }
    return 1;
}
u8 source_intro_sprite_read(SourceIntroSpriteStatus *state,s16 line,u8 hcounter)
{
    u8 result=state->flags;state->flags=0;
    if((result&0x20) && line==state->collision_line &&
       (hcounter<state->collision_hcounter || hcounter>0xf3))
    {state->flags|=0x20;result&=~0x20;}
    return result;
}
