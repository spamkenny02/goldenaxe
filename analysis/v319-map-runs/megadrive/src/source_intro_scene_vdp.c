#include "source_intro_scene_vdp.h"
#include "source_room_memory.h"
#include "source_video_clock_math.h"

u8 source_intro_scene_vdp_pattern(void *user,u32 elapsed,u32 raster,u8 port,u8 value)
{return source_intro_vdp_out(user,elapsed,raster,11,port,value);}
u8 source_intro_scene_vdp_map(void *user,u32 elapsed,u32 raster,u8 port,u8 value)
{
 SourceIntroVdp *vdp=user;u16 tstates=11;
 if(!vdp) return 0;
 if(port==0xbe && vdp->code==1 && vdp->address>=0x3800 && vdp->address<0x3b00) tstates=16;
 return source_intro_vdp_out(vdp,elapsed,raster,tstates,port,value);
}
u8 source_intro_scene_vdp_run(void *user,const SourceIntroVideoRun *run)
{
 if(!run || (run->kind!=SOURCE_INTRO_VIDEO_CLEAR && run->kind!=SOURCE_INTRO_VIDEO_TRANSFER)) return 0;
 return source_intro_vdp_map_run(user,run->elapsed,run->raster,run->period,run->address,run->count,run->bytes,run->kind==SOURCE_INTRO_VIDEO_CLEAR);
}
static u8 out(SourceIntroVdp *vdp,const SourceClockIrq *entry,u32 ticks,u16 instruction,u8 port,u8 value)
{
 u32 master=ticks*15;
 return source_intro_vdp_out(vdp,entry->entry_elapsed+master,source_video_wrap(entry->entry_raster,master,vdp->clock.period),instruction,port,value);
}
u8 source_intro_scene_vdp_irq(void *user,const SourceIrqContext *context,const SourceClockIrq *entry,u16 *tile_count)
{
 SourceIntroVdp *vdp=user;SourceIrqInput input;SourceIrqOutput irq;SourceClockWork zero={0,0};
 u8 ram[336];u16 n;u32 prefix;
 if(!vdp || !context || !context->ram || !context->audio || !entry || !tile_count || vdp->error) return 0;
 *tile_count=0;
 if(!context->ram[0x2e]) return 1;
 if(context->ram[0x42] || (!context->ram[0x33] && (context->ram[0x45]&3)) ||
    context->ram[80] || (!context->ram[0x33] && !context->full_ram)) return 0;
 for(n=0;n<336;n++) ram[n]=context->ram[n];
 input=context->input;input.raster=entry->entry_raster;input.compensation=context->audio[3];input.tile_count=0;
 /* Canonical stage lengths include the same PAL/NTSC palette polling date.
  * Validate the whole path on a private copy before any publication. */
 if(!source_irq(ram,&input,&zero,&irq) || irq.reset_requested) return 0;
 for(n=0;n<3;n++)
 {
  if(!out(vdp,entry,63+n*28,16,0xbf,context->ram[0x1a-n]) ||
     !out(vdp,entry,75+n*28,12,0xbf,0x8a-n)) return 0;
 }
 if(!out(vdp,entry,166,11,0xbf,0) || !out(vdp,entry,184,11,0xbf,0x7f)) return 0;
 for(n=0;n<64;n++) if(!out(vdp,entry,234+(u32)n*16,16,0xbe,context->ram[144+n])) return 0;
 if(!out(vdp,entry,1267,11,0xbf,0x80) || !out(vdp,entry,1282,11,0xbf,0x7f)) return 0;
 for(n=0;n<128;n++) if(!out(vdp,entry,1315+(u32)n*16,16,0xbe,context->ram[208+n])) return 0;
 if(!context->ram[0x33])
 {
  prefix=0;for(n=0;n<SOURCE_IRQ_PALETTE;n++) prefix+=irq.stages[n].tstates;
  prefix+=13+4+7+10+13+4+(input.compensation?12:11)+(u32)irq.palette_taken*27;
  if(!out(vdp,entry,prefix+37,11,0xbf,0) || !out(vdp,entry,prefix+55,11,0xbf,0xc0)) return 0;
  for(n=0;n<32;n++) if(!out(vdp,entry,prefix+91+(u32)n*29,16,0xbe,source_room_get(context,0x1ca0+n))) return 0;
 }
 return 1;
}
