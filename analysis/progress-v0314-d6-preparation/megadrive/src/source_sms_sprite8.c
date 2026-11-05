#include "source_sms_sprite8.h"
#ifdef SGDK_GCC
#include <memory.h>
#define ZERO(p) memset(p,0,sizeof(p))
#else
#define ZERO(p) __builtin_memset(p,0,sizeof(p))
#endif
static u32 visible_columns(s16 x,u8 reg0)
{
 s16 left=reg0&32?8:0;u32 columns=0;
 if(x+8>left && x<256){columns=0xffffffffUL;if(x<left)columns>>=(left-x)*4;if(x>248)columns<<=(x-248)*4;}
 return columns;
}
static u8 visible_rows(s16 y,u8 *used,u8 *overflow)
{
 u16 r,first,last;u8 rows=0;
 if(y<192 && y+8>0){first=y<0?-y:0;last=y>184?192-y:8;
  for(r=first;r<last;r++){if(used[y+r]<8)rows|=1<<r;else *overflow=1;used[y+r]++;}}
 return rows;
}
u8 source_sms_sprite8_prepare(SourceSmsSprite8 *f,const u8 *sat,u8 reg0,u8 reg1,u8 reg6,u16 base)
{
    u8 used[192];u16 n,count=0;u32 columns;s16 x,y;
    if(!f || !sat || !(reg0&4) || (reg1&0x1b) || base>1984) return SOURCE_SMS_SPRITE8_INVALID;
    ZERO(used);
    ZERO(f->columns);
    ZERO(f->source_tile);
    ZERO(f->rows);
    ZERO(f->sat);
    f->tile_base=base;f->overflow=0;
    for(n=0;n<64 && sat[n]!=208;n++) {
        y=(s16)sat[n]+1;if(sat[n]>208) y-=256;
        x=(s16)sat[64+n*2]-(reg0&8?8:0);columns=visible_columns(x,reg0);
        f->columns[n]=columns;
        f->source_tile[n]=(reg6&4?256:0)+sat[65+n*2];
        f->rows[n]=visible_rows(y,used,&f->overflow);
        f->sat[n*4]=(y+144)&511;f->sat[n*4+1]=n+1;
        f->sat[n*4+2]=0x2000|(base+n);f->sat[n*4+3]=(x+128)&511;
        count++;
    }
    f->count=count;if(count) f->sat[(count-1)*4+1]=0;
    return SOURCE_SMS_SPRITE8_OK;
}
u8 source_sms_sprite8_update(SourceSmsSprite8 *f,const u8 *ys,const u8 *xt,
 u8 reg0,u8 reg1,u8 reg6,u16 base,const u8 *dirty,u8 *changed)
{
 u8 used[192],rows,relocated;u16 n,tile,old_count;u32 columns;s16 x,y;
 if(!f || !ys || !xt || !changed || f->count>64 || !(reg0&4) || (reg1&0x1b) || base>1984)return SOURCE_SMS_SPRITE8_INVALID;
 old_count=f->count;relocated=f->tile_base!=base;ZERO(used);f->overflow=0;
 for(n=0;n<64 && ys[n]!=208;n++)
 {
  y=(s16)ys[n]+1;if(ys[n]>208)y-=256;
  x=(s16)xt[n*2]-(reg0&8?8:0);columns=visible_columns(x,reg0);rows=visible_rows(y,used,&f->overflow);tile=(reg6&4?256:0)+xt[n*2+1];
  changed[n]=relocated || n>=old_count || columns!=f->columns[n] || rows!=f->rows[n] || tile!=f->source_tile[n] || (dirty && (dirty[tile>>3]&(1<<(tile&7))));
  if(!relocated && n<old_count && (!columns || !rows) && (!f->columns[n] || !f->rows[n]))changed[n]=0;
  f->columns[n]=columns;f->rows[n]=rows;f->source_tile[n]=tile;
  f->sat[n*4]=(y+144)&511;f->sat[n*4+1]=n+1;f->sat[n*4+2]=0x2000|(base+n);f->sat[n*4+3]=(x+128)&511;
 }
 f->count=n;f->tile_base=base;if(n)f->sat[(n-1)*4+1]=0;return SOURCE_SMS_SPRITE8_OK;
}
u8 source_sms_sprite8_tile(const SourceSmsSprite8 *f,const u32 *patterns,u16 index,u32 *out)
{
    u16 row,tile;
    if(!f || !patterns || !out || f->count>64 || index>=f->count) return SOURCE_SMS_SPRITE8_INVALID;
    tile=f->source_tile[index];if(tile>=512) return SOURCE_SMS_SPRITE8_INVALID;
    for(row=0;row<8;row++) out[row]=(f->rows[index]&(1<<row))?patterns[tile*8+row]&f->columns[index]:0;
    return SOURCE_SMS_SPRITE8_OK;
}

#undef ZERO
