#include "source_intro_vdp.h"

static u8 advance(SourceIntroVdp *vdp,u32 elapsed)
{
 u32 delta=elapsed-vdp->clock.elapsed;
 /* HScroll can render the next line15 master ticks early. No IO instruction
  * can finish in that short interval; its next checkpoint may still precede
  * the already rendered line. Retain that history until time catches up. */
 if((s32)delta<0) return (s32)delta>=-15;
 while(delta>vdp->clock.period)
 {
  if(!source_intro_sprite_clock_advance(&vdp->clock,vdp->clock.elapsed+vdp->clock.period,vdp->vram,vdp->registers)) return 0;
  delta=elapsed-vdp->clock.elapsed;
 }
 return source_intro_sprite_clock_advance(&vdp->clock,elapsed,vdp->vram,vdp->registers);
}
static u8 redraw(SourceIntroVdp *vdp,u16 line)
{
 if(!source_intro_sprite_render(&vdp->clock.sprites,line,vdp->vram,vdp->registers)) return 0;
 return (line==191 && (vdp->registers[1]&0x40)) || source_intro_sprite_parse(&vdp->clock.sprites,line,vdp->vram,vdp->registers);
}
u8 source_intro_vdp_init(SourceIntroVdp *vdp,u8 *vram,u16 lines,u32 raster,u32 elapsed)
{
 if(!vdp || !vram) return 0;
 __builtin_memset(vdp,0,sizeof(*vdp));vdp->vram=vram;
 if(!source_intro_sprite_clock_init(&vdp->clock,lines,raster,elapsed)) {vdp->error=1;return 0;}
 __builtin_memset(vram,0,16384);
 vdp->registers[0]=0x36;vdp->registers[1]=0x80;
 for(u16 n=2;n<=6;n++) vdp->registers[n]=255;
 vdp->registers[10]=255;vdp->instruction_elapsed=elapsed;vdp->instruction_raster=raster;return 1;
}
u8 source_intro_vdp_checkpoint(SourceIntroVdp *vdp,u32 elapsed)
{
 u32 delta;
 if(!vdp || !vdp->vram || vdp->error) return 0;
 delta=elapsed-vdp->instruction_elapsed;
 if((s32)delta<0) {vdp->error=2;return 0;}
 vdp->instruction_raster=(vdp->instruction_raster+delta%vdp->clock.period)%vdp->clock.period;
 vdp->instruction_elapsed=elapsed;
 if(!advance(vdp,elapsed)) {vdp->error=3;return 0;}
 return 1;
}
static u8 reg_write(SourceIntroVdp *vdp,u32 elapsed,u8 index,u8 value)
{
 u16 line=vdp->clock.raster/3420;u32 offset=vdp->instruction_raster%3420+(elapsed-vdp->instruction_elapsed);
 u8 old=vdp->registers[index];
 if(index>10) return 1;
 if(index==8)
 {
  u32 delta=elapsed-vdp->clock.elapsed,raster=(vdp->clock.raster+delta+15)%vdp->clock.period;
  if(raster/3420<192 && raster%3420<15)
  {if(!advance(vdp,elapsed+15)) return 0;}
  else if(!advance(vdp,elapsed)) return 0;
 }
 if(index==1) value&=~4; /* SMS cannot enter MD Mode5. */
 vdp->registers[index]=value;
 if(!(vdp->registers[0]&4) || line>=192 || offset>860) return 1;
 if(index==1 && ((old^value)&0x40)) return redraw(vdp,line);
 if(!(vdp->registers[1]&0x40)) return 1;
 if(index>=2 && index<=4) return redraw(vdp,line);
 if(index==5) return source_intro_sprite_parse(&vdp->clock.sprites,line,vdp->vram,vdp->registers);
 return 1;
}
u8 source_intro_vdp_write(SourceIntroVdp *vdp,u32 elapsed,u8 port,u8 value)
{
 if(!vdp || !vdp->vram || vdp->error) return 0;
 if((port&0xc1)==0x81)
 {
  if(!vdp->pending)
  {vdp->address=(vdp->address&0x3f00)|value;vdp->low=value;vdp->pending=1;}
  else
  {
   vdp->pending=0;vdp->code=value>>6;vdp->address=(((u16)value<<8)|vdp->low)&0x3fff;
   if(vdp->code==0) {vdp->buffer=vdp->vram[vdp->address];vdp->address=(vdp->address+1)&0x3fff;}
   else if(vdp->code==2 && !reg_write(vdp,elapsed,value&15,vdp->low)) {vdp->error=4;return 0;}
  }
 }
 else if((port&0xc1)==0x80)
 {
  vdp->pending=0;
  /* SMS VRAM writes render a newly crossed active line BEFORE changing RAM. */
  if(vdp->code<3)
  {
   if(!advance(vdp,elapsed)) {vdp->error=3;return 0;}
   vdp->vram[vdp->address&0x3fff]=value;
  }
  else vdp->palette[vdp->address&31]=value;
  vdp->buffer=value;vdp->address++;
 }
 else {vdp->error=5;return 0;}
 return 1;
}
u8 source_intro_vdp_read(SourceIntroVdp *vdp,u32 elapsed,u16 tstates,u8 port,u8 *value)
{
 if(!vdp || !vdp->vram || !value || vdp->error) return 0;
 vdp->pending=0;
 if((port&0xc1)==0x81)
 {
  if(!source_intro_sprite_clock_read(&vdp->clock,elapsed,tstates,vdp->vram,vdp->registers,value)) {vdp->error=6;return 0;}
 }
 else if((port&0xc1)==0x80)
 {
  *value=vdp->buffer;vdp->buffer=vdp->vram[vdp->address&0x3fff];vdp->address++;
 }
 else {vdp->error=5;return 0;}
 return 1;
}
u8 source_intro_vdp_irq_status(void *user,const SourceClockIrq *entry,u8 *status)
{
 SourceIntroVdp *vdp=user;u32 elapsed,raster,delta;
 if(!vdp || !entry || !status || vdp->error || entry->entry_raster>=vdp->clock.period) return 0;
 elapsed=entry->entry_elapsed-37UL*15;delta=elapsed-vdp->instruction_elapsed;
 if((s32)delta<0) return 0;
 raster=(vdp->instruction_raster+delta%vdp->clock.period)%vdp->clock.period;
 if((raster+37UL*15)%vdp->clock.period!=entry->entry_raster) return 0;
 return source_intro_vdp_checkpoint(vdp,elapsed-11UL*15) && source_intro_vdp_read(vdp,elapsed,11,0xbf,status);
}
