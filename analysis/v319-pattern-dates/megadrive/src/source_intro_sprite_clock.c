#include "source_intro_sprite_clock.h"

u8 source_intro_sprite_clock_init(SourceIntroSpriteClock *clock,u16 lines,u32 raster,u32 elapsed)
{
 if(!clock || (lines!=262 && lines!=313) || raster>=(u32)lines*3420) return 0;
 source_intro_sprite_status_reset(&clock->sprites);
 clock->lines=lines;clock->period=(u32)lines*3420;
 clock->elapsed=elapsed;clock->raster=raster;clock->until_line=3420-raster%3420;
 clock->vint=clock->error=0;return 1;
}
u8 source_intro_sprite_clock_advance(SourceIntroSpriteClock *clock,u32 elapsed,const u8 *vram,const u8 *registers)
{
 u32 delta;u16 line;
 if(!clock || !vram || !registers || clock->error) return 0;
 delta=elapsed-clock->elapsed;
 if(delta>clock->period) {clock->error=1;return 0;}
 while(delta>=clock->until_line)
 {
  delta-=clock->until_line;clock->raster+=clock->until_line;
  if(clock->raster>=clock->period) clock->raster-=clock->period;
  clock->until_line=3420;line=clock->raster/3420;
  if(line==193) clock->vint=0x80;
  if(registers[0]&4)
  {
   if(registers[1]&3) {clock->error=2;return 0;}
   if(line==clock->lines-1)
   {if(!source_intro_sprite_parse(&clock->sprites,-1,vram,registers)) {clock->error=2;return 0;}}
   else if(line<192)
   {
    if(!source_intro_sprite_render(&clock->sprites,line,vram,registers)) {clock->error=2;return 0;}
    if(line<191 || !(registers[1]&0x40))
     if(!source_intro_sprite_parse(&clock->sprites,line,vram,registers)) {clock->error=2;return 0;}
   }
  }
 }
 clock->raster+=delta;clock->until_line-=delta;clock->elapsed=elapsed;return 1;
}
u8 source_intro_sprite_clock_read(SourceIntroSpriteClock *clock,u32 elapsed,u16 tstates,const u8 *vram,const u8 *registers,u8 *status)
{
 u32 duration=(u32)tstates*15,start;u16 first,last,phase,hcounter;
 if(!clock || !status || !tstates || duration>3420 || elapsed-clock->elapsed<duration) return 0;
 /* Recover the IN's starting line independently of how far back the last
  * stable checkpoint was. A supported IN cannot span more than one line. */
 start=(clock->raster+(elapsed-clock->elapsed)%clock->period)%clock->period;
 start=start>=duration?start-duration:start+clock->period-duration;first=start/3420;
 if(!source_intro_sprite_clock_advance(clock,elapsed,vram,registers)) return 0;
 last=clock->raster/3420;
 if(first!=last && (last<192 || first==192)) first=last;
 /* SMS H32:85..93,E9..FF,00..84,20 master ticks per count.
  * The source's status-read phase adds530+15 master ticks. */
 phase=(clock->raster%3420+545)%3420;
 hcounter=phase/20;
 hcounter=(hcounter<15?hcounter+0x85:hcounter+0xda)&255;
 *status=clock->vint|source_intro_sprite_read(&clock->sprites,first,hcounter)|((registers[0]&4)?0x1f:0);
 clock->vint=0;return 1;
}
u8 source_intro_sprite_clock_irq_status(void *user,const SourceClockIrq *entry,u8 *status)
{
 SourceIntroSpriteClockBinding *binding=user;SourceIntroSpriteClock *clock;u32 elapsed,raster,delta;
 if(!binding || !entry || !status || !binding->clock || !binding->vram || !binding->registers) return 0;
 clock=binding->clock;
 if(clock->error || entry->entry_raster>=clock->period) return 0;
 elapsed=entry->entry_elapsed-37UL*15;delta=elapsed-clock->elapsed;
 if(delta>clock->period) return 0;
 raster=clock->raster+delta;if(raster>=clock->period) raster-=clock->period;
 if((raster+37UL*15)%clock->period!=entry->entry_raster) return 0;
 return source_intro_sprite_clock_read(clock,elapsed,11,binding->vram,binding->registers,status);
}
