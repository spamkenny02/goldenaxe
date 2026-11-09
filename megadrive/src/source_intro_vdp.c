#include "source_intro_vdp.h"
#include "source_video_clock_math.h"

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
 vdp->instruction_raster=source_video_wrap(vdp->instruction_raster,delta,vdp->clock.period);
 vdp->instruction_elapsed=elapsed;
 if(!advance(vdp,elapsed)) {vdp->error=3;return 0;}
 return 1;
}
static u8 reg_write(SourceIntroVdp *vdp,u32 elapsed,u8 index,u8 value)
{
 u16 line=source_video_line(vdp->clock.raster);u32 offset=source_video_phase(vdp->instruction_raster)+(elapsed-vdp->instruction_elapsed);
 u8 old=vdp->registers[index];
 if(index>10) return 1;
 if(index==8)
 {
  u32 delta=elapsed-vdp->clock.elapsed,raster=source_video_wrap(vdp->clock.raster,delta+15,vdp->clock.period);
  if(raster<192UL*3420 && source_video_phase(raster)<15)
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
 raster=source_video_wrap(vdp->instruction_raster,delta,vdp->clock.period);
 if(source_video_wrap(raster,37UL*15,vdp->clock.period)!=entry->entry_raster) return 0;
 return source_intro_vdp_checkpoint(vdp,elapsed-11UL*15) && source_intro_vdp_read(vdp,elapsed,11,0xbf,status);
}
u8 source_intro_vdp_out(SourceIntroVdp *vdp,u32 elapsed,u32 raster,u16 tstates,u8 port,u8 value)
{
 u32 delta;
 if(!vdp || vdp->error || !tstates || tstates>228 || raster>=vdp->clock.period) return 0;
 delta=elapsed-vdp->instruction_elapsed;
 if((s32)delta<0 || delta<(u32)tstates*15 ||
    source_video_wrap(vdp->instruction_raster,delta,vdp->clock.period)!=raster) return 0;
 return source_intro_vdp_checkpoint(vdp,elapsed-(u32)tstates*15) && source_intro_vdp_write(vdp,elapsed,port,value);
}
u8 source_intro_vdp_pattern_run(void *user,const SourcePatternVideoRun *run)
{
 SourceIntroVdp *vdp=user;u32 elapsed,delta,span;u16 address;u8 value=0;
 if(!vdp || !run || !vdp->vram || vdp->error || vdp->pending || !run->bytes ||
    !run->count || run->count>256 || run->period!=vdp->clock.period || run->raster>=run->period ||
    run->address<0x4000 || (u32)run->address+(u32)(run->count-1)*4>=0x6400) return 0;
 delta=run->elapsed-vdp->instruction_elapsed;
 if((s32)delta<0 || source_video_wrap(vdp->instruction_raster,delta,run->period)!=run->raster) return 0;
 span=(u32)run->count*(run->literal?135:134)-(((run->address&255)+(u32)run->count*4)>>8)-(run->terminal?5:0);
 if(span*15>run->period) return 0;
 elapsed=run->elapsed+77UL*15;address=run->address;
 /* A whole run in the opposite8KiB pattern bank cannot affect any sprite
  * pixel or SAT parse. Background pixels are not rendered by this logical
  * status model; their exact write dates remain in the run descriptor. */
 if((vdp->registers[6]&4)?(u32)address+(u32)(run->count-1)*4<0x6000:address>=0x6000)
 {
  elapsed+=(u32)((run->count-1)*(run->literal?135:134)-(((address&255)+(u32)(run->count-1)*4)>>8))*15;
  for(u16 n=0;n<run->count;n++)
  {value=run->bytes[run->literal?n:0];vdp->vram[address&0x3fff]=value;address+=4;}
  if(!advance(vdp,elapsed)) {vdp->error=3;return 0;}
 }
 else
 {
  for(u16 n=0;n<run->count;n++)
  {
   if(!advance(vdp,elapsed)) {vdp->error=3;return 0;}
   value=run->bytes[run->literal?n:0];vdp->vram[address&0x3fff]=value;
   if(n+1<run->count) elapsed+=(u32)((run->literal?135:134)-((address&255)>=252))*15;
   address+=4;
  }
 }
 address-=4;
 vdp->instruction_elapsed=elapsed-165;
 vdp->instruction_raster=vdp->clock.raster>=165?vdp->clock.raster-165:vdp->clock.raster+run->period-165;
 vdp->address=(address&0x3fff)+1;vdp->low=address;vdp->pending=0;vdp->code=1;vdp->buffer=value;
 return 1;
}
u8 source_intro_vdp_map_run(SourceIntroVdp *vdp,u32 elapsed,u32 raster,u32 period,
 u16 address,u16 count,const u8 *bytes,u8 clear)
{
 u32 delta,last;u16 step=clear?4:1,stride=clear?1860:480,duration=clear?165:240;u8 value=255;
 if(!vdp || !vdp->vram || vdp->error || vdp->pending || !count || period!=vdp->clock.period || raster>=period) return 0;
 if(clear)
 {if(address<0x4003 || ((address-0x4003)&3) || (u32)address+(u32)(count-1)*4>=0x6400) return 0;}
 else if(!bytes || address<0x7800 || (u32)address+count>0x7b00 || vdp->code!=1 || vdp->address!=(address&0x3fff)) return 0;
 delta=elapsed-vdp->instruction_elapsed;
 if((s32)delta<0 || source_video_wrap(vdp->instruction_raster,delta,period)!=raster || (u32)count*stride>period) return 0;
 elapsed+=clear?1515:240;last=(u32)address+(u32)(count-1)*step;
 /* No sprite reads from the opposite8KiB bank; SAT is never in these ranges. */
 if((vdp->registers[6]&4)?last<0x6000:address>=0x6000)
 {
  elapsed+=(u32)(count-1)*stride;
  for(u16 n=0;n<count;n++) {value=clear?255:bytes[n];vdp->vram[address&0x3fff]=value;address+=step;}
  if(!advance(vdp,elapsed)) {vdp->error=3;return 0;}
 }
 else
 {
  for(u16 n=0;n<count;n++)
  {
   if(!advance(vdp,elapsed)) {vdp->error=3;return 0;}
   value=clear?255:bytes[n];vdp->vram[address&0x3fff]=value;address+=step;
   if(n+1<count) elapsed+=stride;
  }
 }
 if(clear) {vdp->low=(u8)(address-step);vdp->code=1;}
 vdp->address=((address-step)&0x3fff)+1;vdp->pending=0;vdp->buffer=value;
 vdp->instruction_elapsed=elapsed-duration;
 vdp->instruction_raster=vdp->clock.raster>=duration?vdp->clock.raster-duration:vdp->clock.raster+period-duration;
 return 1;
}

u8 source_intro_vdp_sat_run(SourceIntroVdp *vdp,u32 elapsed,u32 raster,const u8 *bytes,u16 count)
{
 u32 delta;u16 remaining=count;
 if(!vdp || !vdp->vram || !bytes || vdp->error || vdp->pending || vdp->code!=1 ||
    !count || count>128 || vdp->address<0x3f00 || (u32)vdp->address+count>0x4000 ||
    raster>=vdp->clock.period) return 0;
 delta=elapsed-vdp->instruction_elapsed;
 if((s32)delta<0 || delta<240 || source_video_wrap(vdp->instruction_raster,delta,vdp->clock.period)!=raster) return 0;
 if(!source_intro_vdp_checkpoint(vdp,elapsed-240)) return 0;
 while(remaining)
 {
  u16 batch;u32 span;
  if(!advance(vdp,elapsed)) {vdp->error=3;return 0;}
  /* No parse/render/status observation can occur between these byte dates.
   * SAT may alias sprite pattern pixels; those are also read only at edges. */
  batch=(vdp->clock.until_line+239)/240;
  if(batch>remaining) batch=remaining;
  for(u16 n=0;n<batch;n++) vdp->vram[vdp->address++]=*bytes++;
  span=(u32)(batch-1)*240;
  vdp->clock.raster+=span;vdp->clock.until_line-=span;
  vdp->clock.elapsed=elapsed+span;
  remaining-=batch;elapsed+=span;
  if(remaining) elapsed+=240;
 }
 vdp->pending=0;vdp->buffer=bytes[-1];
 vdp->instruction_elapsed=elapsed-240;
 vdp->instruction_raster=vdp->clock.raster>=240?vdp->clock.raster-240:vdp->clock.raster+vdp->clock.period-240;
 return 1;
}
