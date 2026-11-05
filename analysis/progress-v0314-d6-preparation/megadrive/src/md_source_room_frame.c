#include "md_source_room_frame.h"
#include "source_class0_video.h"
#define TILE_BASE 16
#define CLONE_BASE 768
#define SOLID_TILE 832
#define BLANK_TILE 833
#define BORDER_TILE 834
static u16 color(u8 value)
{
 static const u8 levels[4]={0,3,5,7};
 return ((u16)levels[value&3]<<1)|((u16)levels[(value>>2)&3]<<5)|((u16)levels[(value>>4)&3]<<9);
}
static u16 attribute(u16 value)
{return (TILE_BASE+(value&511))|((value&0x200)<<2)|((value&0x400)<<2)|((value&0x800)<<2)|((value&0x1000)<<3);}
u8 md_source_room_frame_upload(MdSourceRoomFrame *s,const u8 *vram,const u8 *cram,
 u8 reg0,u8 reg1,u8 reg6,u8 reg7,u8 reg8,u8 reg9)
{
 u16 n,row,x,word,count;const u8 *source;
 if(!s || !vram || !cram || ((u32)vram&1) || reg8 || reg9 || VDP_isEnable() ||
    VDP_getScreenWidth()!=256 || VDP_getScreenHeight()!=224 || VDP_getPlaneWidth()!=64 || VDP_getPlaneHeight()!=32)return MD_SOURCE_ROOM_INVALID;
 for(n=0;n<64;n++)s->sat[n]=vram[0x3f00+n];
 for(n=0;n<128;n++)s->sat[64+n]=vram[0x3f80+n];
 if(source_sms_sprite8_prepare(&s->sprites,s->sat,reg0,reg1,reg6,CLONE_BASE))return MD_SOURCE_ROOM_INVALID;
 s->error=0;memset(s->background_palette,0,sizeof(s->background_palette));memset(s->pattern_valid,255,sizeof(s->pattern_valid));memset(s->background_metadata,0,sizeof(s->background_metadata));
 for(n=0;n<64;n++)s->palette[n]=0;
 for(n=0;n<32;n++)s->palette[n]=color(cram[n]);
 s->palette[0]=s->palette[16]=0;
 s->palette[33]=color(cram[0]);s->palette[49]=color(cram[16]);s->palette[50]=color(cram[16+(reg7&15)]);
 PAL_setColors(0,s->palette,64,CPU);VDP_setBackgroundColor(0);
 for(n=0;n<512;n+=8){pattern_convert(vram+n*32,s->patterns,64);VDP_loadTileData(s->patterns,TILE_BASE+n,8,CPU);}
 for(n=0;n<8;n++)s->patterns[n]=0x11111111UL;
 VDP_loadTileData(s->patterns,SOLID_TILE,1,CPU);
 for(n=0;n<8;n++)s->patterns[n]=0;
 VDP_loadTileData(s->patterns,BLANK_TILE,1,CPU);
 for(n=0;n<8;n++)s->patterns[n]=0x22222222UL;
 VDP_loadTileData(s->patterns,BORDER_TILE,1,CPU);
 VDP_clearPlane(BG_A,TRUE);VDP_clearPlane(BG_B,TRUE);
 VDP_fillTileMapRect(BG_A,BLANK_TILE,0,0,64,32);
 VDP_fillTileMapRect(BG_B,BLANK_TILE,0,0,64,32);
 VDP_setHorizontalScroll(BG_A,0);VDP_setHorizontalScroll(BG_B,0);
 VDP_setVerticalScroll(BG_A,0);VDP_setVerticalScroll(BG_B,0);
 for(row=0;row<24;row++)
 {
  source=vram+0x3800+row*64;
  for(x=0;x<32;x++)
  {
   word=source[x*2]|((u16)source[x*2+1]<<8);s->foreground[x]=attribute(word);
   if(word&0x800)s->background_palette[(row*32+x)>>3]|=1<<(x&7);
   if((word&511)>=448){n=(word&511)-448;s->background_metadata[n>>3]|=1<<(n&7);}
   s->background[x]=SOLID_TILE|((word&0x800)?0x6000:0x4000);
  }
  if(reg0&32){s->foreground[0]=BLANK_TILE;s->background[0]=0x6000|BORDER_TILE;}
  VDP_setTileMapDataRow(BG_A,s->foreground,row+2,0,32,CPU);
  VDP_setTileMapDataRow(BG_B,s->background,row+2,0,32,CPU);
 }
 count=s->sprites.count;
 for(n=0;n<count;n++)
 {
  pattern_convert(vram+s->sprites.source_tile[n]*32,s->patterns,8);
  for(row=0;row<8;row++)s->patterns[row]=(s->sprites.rows[n]&(1<<row))?s->patterns[row]&s->sprites.columns[n]:0;
  VDP_loadTileData(s->patterns,CLONE_BASE+n,1,CPU);
 }
 VDP_resetSprites();
 for(n=0;n<count;n++)VDP_setSpriteFull(n,(s16)s->sprites.sat[n*4+3]-128,(s16)s->sprites.sat[n*4]-128,
  SPRITE_SIZE(1,1),s->sprites.sat[n*4+2],s->sprites.sat[n*4+1]);
 if(!count){VDP_setSpriteFull(0,0,0,SPRITE_SIZE(1,1),0,0);count=1;}
 VDP_updateSprites(count,CPU);s->ready=0x2002;s->regs[0]=reg0;s->regs[1]=reg1;s->regs[2]=reg6;s->regs[3]=reg7;
 s->uploaded_background=768;s->uploaded_patterns=512;s->uploaded_words=768;s->uploaded_clones=s->sprites.count;return MD_SOURCE_ROOM_OK;
}
typedef u32 __attribute__((may_alias)) DirtyLong;
typedef u16 __attribute__((may_alias)) NameWord;
static u8 has_changes(const SourceVdpDirty *d)
{
 const DirtyLong *p=(const DirtyLong *)d->patterns;u16 n;
 if(d->palette || d->sat)return 1;
 for(n=0;n<40;n+=4)if(p[n]|p[n+1]|p[n+2]|p[n+3])return 1;
 return 0;
}
static u8 palette_bits(const u8 *source)
{
 const NameWord *p=(const NameWord *)source;u16 n,any=0,all=0xffff;u8 bits=0,mask=1;
 for(n=0;n<8;n++)any|=p[n];
 if(!(any&8))return 0;
 for(n=0;n<8;n++)all&=p[n];
 if(all&8)return 255;
 for(n=0;n<8;n++){if(p[n]&8)bits|=mask;mask<<=1;}
 return bits;
}
/* Name-table and SAT storage are also legal mode4 pattern slots. Track
 * references conservatively, and invalidate skipped copies so a later name
 * reference materializes current bytes even without a new pattern write. */
static void background_metadata(MdSourceRoomFrame *s,const u8 *vram)
{
 const NameWord *p=(const NameWord *)(vram+0x3800);const DirtyLong *q=(const DirtyLong *)p;u16 group,n,tile;
 for(group=0;group<96;group++,p+=8,q+=4)
 {
  if(!((q[0]|q[1]|q[2]|q[3])&0x00010001UL))continue;
  for(n=0;n<8;n++)if((p[n]&0xc001)==0xc001){tile=(p[n]>>8)&63;s->background_metadata[tile>>3]|=1<<(tile&7);}
 }
}
u8 md_source_room_frame_update(MdSourceRoomFrame *s,const u8 *vram,const u8 *cram,
 const SourceVdpDirty *dirty,u8 reg0,u8 reg1,u8 reg6,u8 reg7,u8 reg8,u8 reg9)
{
 u8 clone_changed[64];u16 n,row,x,start,length,word,tile,count,group,offset;u8 sprites=0,force_column,bits,changed,upload;u32 row_bits,bg_bits,scan;
 if(!s || !vram || !cram || !dirty || s->ready!=0x2002 || ((u32)vram&1) || reg8 || reg9 || !(reg0&4) || (reg1&0x1b) ||
    VDP_getScreenWidth()!=256 || VDP_getScreenHeight()!=224 || VDP_getPlaneWidth()!=64 || VDP_getPlaneHeight()!=32)return MD_SOURCE_ROOM_INVALID;
 s->uploaded_patterns=s->uploaded_words=s->uploaded_clones=s->uploaded_background=0;
 if(reg0==s->regs[0] && reg1==s->regs[1] && reg6==s->regs[2] && reg7==s->regs[3] && !has_changes(dirty))return MD_SOURCE_ROOM_OK;
 force_column=(reg0^s->regs[0])&32;
 sprites=dirty->sat || reg0!=s->regs[0] || reg1!=s->regs[1] || reg6!=s->regs[2];
 for(n=0;n<s->sprites.count && !sprites;n++){tile=s->sprites.source_tile[n];if(dirty->patterns[tile>>3]&(1<<(tile&7)))sprites=1;}
 if(sprites && source_sms_sprite8_update(&s->sprites,vram+0x3f00,vram+0x3f80,reg0,reg1,reg6,CLONE_BASE,dirty->patterns,clone_changed))return MD_SOURCE_ROOM_INVALID;
 for(n=0;n<96;n++)if(dirty->names[n]){background_metadata(s,vram);break;}
 if(dirty->palette || reg7!=s->regs[3])
 {
  for(n=0;n<32;n++)s->palette[n]=color(cram[n]);
  s->palette[0]=s->palette[16]=0;s->palette[33]=color(cram[0]);s->palette[49]=color(cram[16]);s->palette[50]=color(cram[16+(reg7&15)]);
  PAL_setColors(0,s->palette,64,CPU);
 }
 for(group=0;group<64;group++)
 {
  s->pattern_valid[group]&=~dirty->patterns[group];
  bits=group<56?dirty->patterns[group]:(~s->pattern_valid[group]&s->background_metadata[group-56]);
  if(!bits)continue;
  upload=bits;n=group*8;
  while(bits)
  {
   while(!(bits&1)){bits>>=1;n++;}
   start=n;length=0;do{length++;n++;bits>>=1;}while(bits&1);
   pattern_convert(vram+start*32,s->patterns,length*8);VDP_loadTileData(s->patterns,TILE_BASE+start,length,CPU);s->uploaded_patterns+=length;
  }
  s->pattern_valid[group]|=upload;
 }
 for(row=0;row<24;row++)
 {
  const u8 *flags=dirty->names+row*4;
  row_bits=(u32)flags[0]|((u32)flags[1]<<8)|((u32)flags[2]<<16)|((u32)flags[3]<<24);
  if(force_column)row_bits|=1;
  if(!row_bits)continue;
  scan=row_bits;bg_bits=0;
  for(group=0;group<4;group++,scan>>=8)
  {
   bits=scan&255;if(!bits)continue;offset=row*4+group;
   changed=(s->background_palette[offset]^palette_bits(vram+0x3800+offset*16))&bits;
   s->background_palette[offset]^=changed;bg_bits|=(u32)changed<<(group*8);
  }
  if(force_column)bg_bits|=1;
  x=0;
  while(row_bits)
  {
   while(!(row_bits&1)){row_bits>>=1;x++;}
   start=x;length=0;do{length++;x++;row_bits>>=1;}while(row_bits&1);
   word=row*32+start;source_class0_video_map(vram+0x3800+word*2,s->foreground,length);
   if((reg0&32) && !start)s->foreground[0]=BLANK_TILE;
   VDP_setTileMapDataRow(BG_A,s->foreground,row+2,start,length,CPU);s->uploaded_words+=length;
  }
  x=0;
  while(bg_bits)
  {
   while(!(bg_bits&1)){bg_bits>>=1;x++;}
   start=x;length=0;
   do {
    word=row*32+x;s->background[length]=SOLID_TILE|((vram[0x3801+word*2]&8)?0x6000:0x4000);
    if((reg0&32) && !x)s->background[length]=0x6000|BORDER_TILE;
    length++;x++;bg_bits>>=1;
   } while(bg_bits&1);
   VDP_setTileMapDataRow(BG_B,s->background,row+2,start,length,CPU);s->uploaded_background+=length;
  }
 }
 if(sprites)
 {
  count=s->sprites.count;
  for(n=0;n<count;n++)
  {
   u8 rows;u32 columns;u32 *write;
   if(!clone_changed[n])continue;
   tile=s->sprites.source_tile[n];rows=s->sprites.rows[n];columns=s->sprites.columns[n];
   if(!rows || !columns)memsetU32(s->patterns,0,8);
   else
   {
    pattern_convert(vram+tile*32,s->patterns,8);
    if(rows!=255 || columns!=0xffffffffUL){write=s->patterns;for(row=0;row<8;row++){*write=(rows&1)?*write&columns:0;write++;rows>>=1;}}
   }
   VDP_loadTileData(s->patterns,CLONE_BASE+n,1,CPU);s->uploaded_clones++;
  }
  VDP_resetSprites();
  for(n=0;n<count;n++)VDP_setSpriteFull(n,(s16)s->sprites.sat[n*4+3]-128,(s16)s->sprites.sat[n*4]-128,SPRITE_SIZE(1,1),s->sprites.sat[n*4+2],s->sprites.sat[n*4+1]);
  if(!count){VDP_setSpriteFull(0,0,0,SPRITE_SIZE(1,1),0,0);count=1;}
  VDP_updateSprites(count,CPU);
 }
 s->regs[0]=reg0;s->regs[1]=reg1;s->regs[2]=reg6;s->regs[3]=reg7;return MD_SOURCE_ROOM_OK;
}
